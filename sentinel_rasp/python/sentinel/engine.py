import ctypes
import os
from pathlib import Path
from .events import SecurityEvent


class NativeEngine:
    def __init__(self, policy):
        self.policy = policy
        self._lib = None

        # Versioned artifact avoids replacing a DLL held open by a running Uvicorn process.
        suffix = ".dll" if os.name == "nt" else ".so"
        library = Path(__file__).with_name("_native") / f"sentinel_core_v4{suffix}"
        if not library.exists():
            try:
                from .build_native import build
                build(library)
            except Exception:
                # C++ compiler (g++) not present on host; fallback gracefully to Python engine
                pass

        if library.exists():
            try:
                self._lib = ctypes.CDLL(str(library))
                self._lib.sentinel_evaluate.argtypes = [ctypes.c_char_p] * 7 + [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
                self._lib.sentinel_evaluate.restype = ctypes.c_int
            except Exception:
                self._lib = None

    def evaluate(self, event: SecurityEvent):
        if self._lib is not None:
            try:
                reason = ctypes.create_string_buffer(128)
                args = [self.policy.name, event.event_type.value, event.request_id, event.resource,
                        event.destination, event.data_classification, event.operation_id]
                blocked = self._lib.sentinel_evaluate(
                    *[x.encode() for x in args],
                    int(self.policy.block_unsafe_sql),
                    int(self.policy.block_xss),
                    reason,
                    len(reason)
                )
                return ("BLOCK" if blocked else "ALLOW", reason.value.decode())
            except Exception:
                pass

        # High-fidelity Pure Python fallback matching C++ sentinel::Engine
        event_type = (event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type)).upper()
        classification = (event.data_classification or "").upper()
        destination = (event.destination or "").upper()

        if self.policy.block_xss and event_type == "HTML_RENDER" and classification == "UNSAFE_HTML":
            return ("BLOCK", "XSS_ATTEMPT")
        if event_type == "PROCESS_EXEC" and classification == "UNSAFE_COMMAND":
            return ("BLOCK", "COMMAND_INJECTION_ATTEMPT")
        if self.policy.block_unsafe_sql and event_type == "DB_QUERY" and classification == "UNSAFE_SQL":
            return ("BLOCK", "SQL_INJECTION_ATTEMPT")
        if event_type == "NETWORK_SEND" and classification == "SECRET" and (destination in ("UNTRUSTED", "", "EXTERNAL")):
            return ("BLOCK", "SECRET_EXFILTRATION")

        return ("ALLOW", "")
