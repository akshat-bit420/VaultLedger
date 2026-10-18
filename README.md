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

## 🚀 Quickstart

**You need:** [Python 3](https://www.python.org/) (I used [your version, run `python --version`]) and [Ollama](https://ollama.com/) installed.

**1. Get the code**
```bash
git clone https://github.com/akshat-bit420/VaultLedger.git
cd VaultLedger
```

**2. Pull the model** (this is the only step that needs internet, about 4.7 GB)
```bash
ollama pull qwen2.5:7b
```

**3. Make sure Ollama is running**
Check for the llama icon in the system tray, or run `ollama list`. If the app later says "Failed to connect to Ollama", the server isn't running, so start it and try again.

**4. Install the Python packages**
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (on Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
```

**5. Generate the sample data**
```bash
python sample_data_generator.py
```
This creates a `sample_data` folder with 3 fake invoices (one is a deliberate duplicate) and a bank statement CSV with one charge that has no receipt.

**6. Run the app**
```bash
streamlit run app.py
```
Upload the 3 PDFs and the CSV from `sample_data`, then click **Run Local AI Audit**. The first run is slow while the model loads. Expected result: 3 invoices, 2 flagged as duplicates, 1 bank charge missing a receipt.
