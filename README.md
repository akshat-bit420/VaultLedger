# 🔒 VaultLedger: 100% Offline PDF Invoice & Bank Auditor

**VaultLedger** is a local-first AI financial reconciliation tool built for freelancers, independent consultants, and small agencies. It uses open-weight models via **Ollama** (`qwen2.5:7b` / `llama3.2:3b`) to parse unstructured PDF invoices, cross-check them against bank statement CSVs, flag duplicate bills, and catch missing tax receipts—all running **100% offline on `localhost` with zero cloud APIs and zero data leaks**.

Built for the **DEV Open-Source AI Challenge (Week 2: Side Hustle)**.

---

## ✨ Key Features

- **100% Air-Gapped Privacy:** Sensitive financial PDFs, client names, tax IDs, and bank statements never leave your machine. Works completely without an internet connection.
- **Deterministic JSON Extraction:** Pairs **Pydantic** with Ollama's native structured output API (`temperature=0.0`) to extract `vendor_name`, `invoice_number`, `invoice_date`, `subtotal`, `tax_amount`, `total_amount`, `currency`, and expense `category` without hallucinations.
- **Duplicate Invoice Detection:** Automatically flags duplicate bills (same vendor, date, and total) so you never double-pay a vendor.
- **Missing Receipt Discovery:** Reconciles extracted PDF totals against your bank CSV and highlights unreceipted bank charges requiring action before tax filing.
- **One-Click Excel Audit Export:** Exports a clean, two-tab `.xlsx` workbook (`Audited_Invoices` and `Bank_Reconciliation`).

---

## 🛠️ Tech Stack

- **Local AI Inference:** [Ollama](https://ollama.com/) (`qwen2.5:7b`, `llama3.2:3b`, `mistral:latest`)
- **Schema Validation:** `Pydantic`
- **PDF Text Extraction:** `PyMuPDF` (`pymupdf`)
- **Reconciliation Engine:** `Pandas` & `OpenPyXL`
- **Frontend UI:** `Streamlit`[cite: 2]

---

## 🚀 Quickstart (Run Locally in 60 Seconds)

### 1. Prerequisites
Make sure you have [Python 3.9+](https://www.python.org/) and [Ollama](https://ollama.com/) installed on your system.

Pull the open-weight model via Ollama:
```bash
ollama pull qwen2.5:7b
