import streamlit as st
import pymupdf  # PyMuPDF
import ollama
import pandas as pd
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import json
import io

# ---------------------------------------------------------
# 1. DEFINE STRICT JSON SCHEMA FOR OLLAMA
# ---------------------------------------------------------
class InvoiceData(BaseModel):
    vendor_name: str = Field(description="Name of the company or freelancer issuing the invoice")
    invoice_number: str = Field(description="Invoice ID or reference number")
    invoice_date: str = Field(description="Date of invoice in YYYY-MM-DD format")
    subtotal: float = Field(description="Amount before tax")
    tax_amount: float = Field(description="Tax, GST, or VAT amount (0.0 if none)")
    total_amount: float = Field(description="Final total amount charged")
    currency: str = Field(description="3-letter currency code like USD, INR, EUR")
    category: Literal["Software", "Hardware", "Travel", "Marketing", "Contractor", "Office"] = Field(
        description="Expense category"
    )

# ---------------------------------------------------------
# 2. PDF EXTRACTION & LOCAL OLLAMA INFERENCE
# ---------------------------------------------------------
def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    doc.close()
    return text.strip()

def parse_invoice_with_ollama(raw_text: str, model_name: str = "qwen2.5:7b") -> dict:
    prompt = f"""
    You are an expert financial auditor. Extract the exact invoice details from the text below.
    Convert any dates into YYYY-MM-DD format. If tax is not explicitly stated, set tax_amount to 0.0.
    
    INVOICE TEXT:
    {raw_text}
    """
    
    response = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        format=InvoiceData.model_json_schema(),  # Enforces strict JSON schema!
        options={"temperature": 0.0}             # Zero temperature for factual accuracy
    )
    
    return json.loads(response["message"]["content"])

# ---------------------------------------------------------
# 3. BANK STATEMENT RECONCILIATION ENGINE
# ---------------------------------------------------------
def reconcile_data(invoices_df: pd.DataFrame, bank_df: pd.DataFrame):
    """
    Matches extracted PDF invoices against a Bank Statement CSV
    Expected Bank CSV columns: Date, Description, Amount
    """
    invoices_df["Duplicate_Flag"] = invoices_df.duplicated(
        subset=["vendor_name", "total_amount", "invoice_date"], keep=False
    )
    
    # Match by exact amount
    bank_amounts = set(bank_df["Amount"].abs().round(2))
    invoices_df["Matched_in_Bank"] = invoices_df["total_amount"].round(2).isin(bank_amounts)
    
    invoice_amounts = set(invoices_df["total_amount"].round(2))
    bank_df["Missing_Receipt"] = ~bank_df["Amount"].abs().round(2).isin(invoice_amounts)
    
    return invoices_df, bank_df

# ---------------------------------------------------------
# 4. STREAMLIT DASHBOARD UI & SESSION STATE
# ---------------------------------------------------------
st.set_page_config(page_title="VaultLedger | Local AI Auditor", layout="wide")
st.title("🔒 VaultLedger: 100% Offline PDF Invoice & Bank Auditor")
st.caption("Powered by Local Open-Weight Models via Ollama — Zero Cloud APIs, Zero Data Leaks.")

# Initialize session state so results stay on screen when clicking Download
if "audit_complete" not in st.session_state:
    st.session_state.audit_complete = False
    st.session_state.invoices_df = None
    st.session_state.bank_df = None

with st.sidebar:
    st.header("⚙️ Local AI Settings")
    model_choice = st.selectbox("Select Ollama Model", ["qwen2.5:7b", "llama3.2:3b", "mistral:latest"])
    st.info("💡 All PDF parsing and AI inference run locally on your machine. No financial data leaves your device.")
    
    if st.session_state.audit_complete:
        if st.button("🗑️ Clear Audit Results", use_container_width=True):
            st.session_state.audit_complete = False
            st.session_state.invoices_df = None
            st.session_state.bank_df = None
            st.rerun()

col1, col2 = st.columns(2)

with col1:
    uploaded_pdfs = st.file_uploader("📄 Upload PDF Invoices/Receipts", type=["pdf"], accept_multiple_files=True)

with col2:
    uploaded_bank = st.file_uploader("🏦 Upload Bank Statement (CSV with 'Date', 'Description', 'Amount')", type=["csv"])

# ---------------------------------------------------------
# 5. RUN AUDIT & STORE IN SESSION STATE
# ---------------------------------------------------------
if st.button("🚀 Run Local AI Audit", type="primary"):
    if not uploaded_pdfs:
        st.warning("⚠️ Please upload at least one PDF invoice first.")
    else:
        extracted_records = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, pdf_file in enumerate(uploaded_pdfs):
            status_text.text(f"Auditing {pdf_file.name} locally with {model_choice}...")
            pdf_file.seek(0)  # Reset file pointer in case of re-runs
            raw_text = extract_text_from_pdf(pdf_file.read())
            
            try:
                parsed_data = parse_invoice_with_ollama(raw_text, model_name=model_choice)
                parsed_data["file_name"] = pdf_file.name
                extracted_records.append(parsed_data)
            except Exception as e:
                st.error(f"Failed to parse {pdf_file.name}: {e}")
                
            progress_bar.progress((idx + 1) / len(uploaded_pdfs))

        if extracted_records:
            status_text.success("✅ Audit Complete!")
            invoices_df = pd.DataFrame(extracted_records)
            bank_df = None

            if uploaded_bank is not None:
                uploaded_bank.seek(0)
                bank_df = pd.read_csv(uploaded_bank)
                invoices_df, bank_df = reconcile_data(invoices_df, bank_df)

            # Save results persistently in session_state
            st.session_state.invoices_df = invoices_df
            st.session_state.bank_df = bank_df
            st.session_state.audit_complete = True

# ---------------------------------------------------------
# 6. DISPLAY PERSISTENT RESULTS & EXCEL DOWNLOAD
# ---------------------------------------------------------
if st.session_state.audit_complete and st.session_state.invoices_df is not None:
    invoices_df = st.session_state.invoices_df
    bank_df = st.session_state.bank_df

    if bank_df is not None:
        st.subheader("🔍 Audit Summary")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Invoices Processed", len(invoices_df))
        m2.metric("Duplicate Invoices Flagged", int(invoices_df["Duplicate_Flag"].sum()))
        m3.metric("Bank Charges Missing Receipts", int(bank_df["Missing_Receipt"].sum()))

        st.subheader("🚨 Unreceipted Bank Charges (Action Required)")
        st.dataframe(bank_df[bank_df["Missing_Receipt"] == True], use_container_width=True)

    st.subheader("📊 Extracted Invoice Ledger")
    st.dataframe(invoices_df, use_container_width=True)

    # Generate Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        invoices_df.to_excel(writer, sheet_name="Audited_Invoices", index=False)
        if bank_df is not None:
            bank_df.to_excel(writer, sheet_name="Bank_Reconciliation", index=False)
            
    st.download_button(
        label="📥 Download Audited Excel Report",
        data=output.getvalue(),
        file_name="VaultLedger_Audit_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )