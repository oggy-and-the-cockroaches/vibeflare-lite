# 🛡️ Vibeflare Lite — Local Security Auditor & Mock Port Shield

[![Platform: Windows | Linux](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-blue.svg)](#-downloads--instant-run-no-setup-required)
[![Tier: Free Forever](https://img.shields.io/badge/Tier-Free%20Forever%20(Local)-brightgreen.svg)](#-vibeflare-lite-vs-vibeflare-startup-platform)
[![Version: v1.0.0](https://img.shields.io/badge/Version-1.0.0-orange.svg)](#-downloads--instant-run-no-setup-required)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Grade%20Desktop-teal.svg)](#-core-capabilities)

**Vibeflare Lite** is the free, 100% local community edition of **Vibeflare**, our upcoming DevSecOps and runtime application defense startup platform.

Vibeflare Lite empowers developers and security engineers to audit codebases for critical vulnerabilities, synthesize verified AI remediations, and instantly protect local applications behind a zero-configuration **Mock Shield Port WAF**—completely offline on your own system without cloud servers, external databases, or mandatory API keys.

---

## ⚡ Vibeflare Lite vs. Vibeflare Startup Platform

While **Vibeflare Lite** is dedicated to individual developers running local security audits and port protection on their personal workstations, our upcoming **Vibeflare Cloud / Enterprise Platform** brings centralized governance, automated GitHub PR bot remediations, and globally distributed edge WAF protection to engineering teams.

| Capability | 🛡️ Vibeflare Lite *(Free Community Edition)* | 🚀 Vibeflare *(Commercial Startup Platform — Coming Soon)* |
| :--- | :--- | :--- |
| **Target Audience** | Individual developers, security researchers, hobbyists | Engineering teams, startups, enterprises |
| **Pricing & Licensing** | **100% Free Forever** (Unlimited local evaluations) | Flexible SaaS per-seat & Enterprise tiers |
| **Deployment Model** | **100% Localhost / Offline** (Air-gapped desktop binary) | Multi-tenant Cloud SaaS & Isolated Private VPCs |
| **Pre-Shipment Code Scanner** | AST & signature engine (Security, Privacy, Reliability, Prod) | Distributed Deep AST, Semantic Code Graphs & Secret Hunting |
| **AI Remediation Engine** | Offline deterministic diff synthesis + optional local Gemma/Gemini | Hosted fine-tuned reasoning models + Automated GitHub/GitLab PRs |
| **Shield Gateway / WAF** | Localhost Mock Port reverse-proxy (drops SQLi, XSS, Path Traversal, RCE) | Globally distributed Anycast Edge WAF with automated DDoS protection |
| **Runtime RASP Defense** | Embedded in-memory process monitoring & local event tracking | Fleet-wide distributed RASP with real-time policy sync & blocking |
| **Telemetry & SIEM** | Local SQLite event log & browser dashboard | Real-time SIEM streaming (Datadog, Splunk, Sumo Logic, Webhooks) |
| **CI/CD Integration** | Local desktop CLI & one-click runner | Native GitHub Actions, GitLab CI, Bitbucket, CircleCI integration |
| **Team Collaboration** | Single-user local workstation storage | Multi-tenant RBAC, Single Sign-On (SAML/Okta), Team Roles |
| **Compliance & Audits** | One-click downloadable JSON/HTML executive reports | Continuous SOC 2 Type II, ISO 27001, HIPAA & PCI-DSS compliance audits |

---

## 📦 Downloads & Instant Run (No Setup Required)

Vibeflare Lite is packaged as a self-contained, pre-compiled binary. **You do not need Python, compilers, Node.js, or external databases installed.**

### 🪟 Windows (64-bit)
1. Download **[`vibeflare-lite-v1.0.0-windows-x64.zip`](https://github.com/oggy-and-the-cockroaches/vibeflare-lite/releases)** from the [Releases](https://github.com/oggy-and-the-cockroaches/vibeflare-lite/releases) page.
2. Extract the ZIP folder.
3. Double-click **`VibeflareLite.exe`** (or launch from Command Prompt / PowerShell).
4. Your browser will automatically open the dashboard at **`http://127.0.0.1:8000`**.

### 🐧 Linux (Debian / Ubuntu / Kali / Mint)
1. Download **[`vibeflare-lite_1.0.0_amd64.deb`](https://github.com/oggy-and-the-cockroaches/vibeflare-lite/releases)** from the [Releases](https://github.com/oggy-and-the-cockroaches/vibeflare-lite/releases) page.
2. Install via dpkg:
   ```bash
   sudo dpkg -i vibeflare-lite_1.0.0_amd64.deb
   ```
3. Run `vibeflare-lite` from your terminal or application launcher.

---

## 🌟 Core Capabilities

### 1. 🛡️ Mock Shield Port Gateway (Zero-Config Reverse Proxy)
Ever wanted an instant security firewall in front of your developer server before exposing it?
* Enter your actual server port (e.g. `8001` or `5000`) or localhost URL.
* Vibeflare Lite binds an OS-assigned, dedicated **Mock Shield Port** (e.g. `http://127.0.0.1:54321`).
* All traffic sent to the mock port is inspected before forwarding. Malicious attack vectors are dropped with **`HTTP 403 Forbidden`** before ever touching your real application:
  * **SQL Injection**: `' OR 1=1--`, `UNION SELECT`, time-based blind SQLi (`sleep()`).
  * **Path Traversal**: `../../etc/passwd`, relative root bypasses.
  * **Remote Code Execution (RCE)**: `; whoami`, `| dir`, command concatenation.
  * **Cross-Site Scripting (XSS)**: `<script>`, `onerror=`, reflected payload markers.
  * **Rate Abuse / DoS**: Sliding-window rate limiter preventing flood anomalies.
* Includes a **Live Attack Testing Suite** in the UI with 1-click test buttons (`🟢 Safe Request`, `🔴 SQL Injection`, `🔴 Path Traversal`, `🔴 RCE`) to watch live attack interception.

### 2. ⚡ Zero-Friction Pre-Loaded Sample Evaluation
No need to zip or upload code to try the product. Vibeflare Lite automatically seeds a complete **Sample E-Commerce Service** with **35 real security, privacy, and production findings** right on launch.

### 3. 🤖 Verified AI Remediation (100% Offline Capable)
* Every finding includes root-cause analysis, impact estimation, and actionable developer guidance.
* Generates clean **unified patch diffs** for vulnerable code.
* Works completely offline using a deterministic synthesis engine.

### 4. ⚙️ Custom Gemini API Key & Gemma 4 Configuration
* **Configurable in UI**: Open the **Settings** tab (or click the Gemma badge in the header) to enter your own Google Gemini API key.
* **Default Model**: Configured out of the box with **`gemma-4-31b-it`** (also supporting `gemma-2-27b-it`, `gemini-2.5-flash`, and custom local Ollama/vLLM endpoints).
* **Live Connection Test**: Click **Test Connection** directly in the Settings view to verify your API key and latency in real time.
* **Local Persistence**: Your API key is stored securely in your local workstation SQLite database and is never transmitted to external services.
* **Zero-Friction Fallback**: Leaving the API key blank keeps Vibeflare Lite running seamlessly in 100% offline deterministic fallback mode.

### 5. 📊 Downloadable Executive Security Reports
Generate and export full-fidelity security audits in JSON and HTML formats for stakeholders or compliance documentation.

---

## 🔒 Security & Privacy Guarantee

* **100% Local**: All scans, logs, findings, and reverse-proxy traffic remain strictly on your local machine.
* **No Telemetry**: Vibeflare Lite does not collect, transmit, or phone home any proprietary code, IP addresses, or project data.

---

## 🤝 Community & Support

* 🐛 **Bug Reports & Feedback**: Please open an issue in the [GitHub Issue Tracker](https://github.com/oggy-and-the-cockroaches/vibeflare-lite/issues).
* 💼 **Enterprise Inquiries**: For early access to the upcoming Vibeflare Cloud & Enterprise Startup Platform, stay tuned to our repository announcements.

---

## 📄 License

Vibeflare Lite is provided free of charge for individual and community evaluation. Copyright © 2026 Vibeflare Security. All rights reserved.
