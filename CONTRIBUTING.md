# Contributing to Shipcheck

First off, thank you for considering contributing to **Shipcheck**! Open source projects thrive when people like you help improve code, report bugs, and write documentation.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Fork and Clone
```bash
git clone https://github.com/your-username/Shipcheck.git
cd Shipcheck
```

### 3. Set Up Development Environment
Create and activate a virtual environment:
```bash
# On Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

# On Windows:
python -m venv .venv
.\.venv\Scripts\activate
```

Install development dependencies:
```bash
pip install -r requirements.txt
```

---

## 🧪 Running Tests

Ensure all tests pass before submitting code:
```bash
pytest
```

---

## 💻 Running the Application Locally

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Start the FastAPI server:
   ```bash
   python -m backend.main
   ```
3. Open your browser at `http://localhost:8000`.

---

## 📝 Guidelines

1. **Keep Pull Requests Focused**: A PR should address one bug or add one cohesive feature.
2. **Add Tests**: If you are adding or changing scanner logic, add corresponding unit tests under `tests/`.
3. **Follow PEP 8**: Keep code clean, formatted, and type-annotated where applicable.
4. **Security Concerns**: If you discover a security flaw in Shipcheck itself, please follow our [SECURITY.md](SECURITY.md) policy instead of opening a public issue.

---

## 🤝 Code of Conduct
Please review and adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) in all project spaces.
