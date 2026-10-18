"""
Generates the demo data for VaultLedger into ./sample_data

  - invoice_001_northwind.pdf   (normal invoice)
  - invoice_002_pixelco.pdf     (normal invoice)
  - invoice_003_northwind_dup.pdf  (DELIBERATE DUPLICATE of invoice 001)
  - sample_bank_statement.csv   (2 charges have receipts, 1 does NOT)

Only needs PyMuPDF (already a dependency of the app):
    python generate_sample_data.py
"""
import csv
import os

import pymupdf  # PyMuPDF

OUT_DIR = "sample_data"

INVOICES = [
    {
        "file": "invoice_001_northwind.pdf",
        "vendor": "Northwind Cloud Services",
        "address": "42 Harbor Street, Austin, TX 78701",
        "number": "NW-2026-0417",
        "date": "2026-10-02",
        "items": [("Cloud hosting (Pro plan, Oct)", 300.00), ("Managed backups", 100.00)],
        "tax_rate": 0.08,
        "currency": "USD",
    },
    {
        "file": "invoice_002_pixelco.pdf",
        "vendor": "Pixel & Co Design Studio",
        "address": "7 Greenway Road, Portland, OR 97201",
        "number": "PX-1093",
        "date": "2026-10-05",
        "items": [("Logo redesign", 800.00), ("Brand guideline PDF", 400.00)],
        "tax_rate": 0.0,
        "currency": "USD",
    },
]

# invoice 3 is an exact copy of invoice 1 (same vendor, number, date, amount)
DUPLICATE = dict(INVOICES[0], file="invoice_003_northwind_dup.pdf")


def money(x: float) -> str:
    return f"{x:,.2f}"


def build_invoice_pdf(inv: dict, path: str) -> float:
    subtotal = sum(price for _, price in inv["items"])
    tax = round(subtotal * inv["tax_rate"], 2)
    total = round(subtotal + tax, 2)

    lines = [
        inv["vendor"],
        inv["address"],
        "",
        "INVOICE",
        f"Invoice No: {inv['number']}",
        f"Invoice Date: {inv['date']}",
        "Bill To: Acme Freelance LLC",
        "",
        "Description                               Amount",
        "-------------------------------------------------",
    ]
    for desc, price in inv["items"]:
        lines.append(f"{desc:<40}  {money(price):>10}")
    lines += [
        "-------------------------------------------------",
        f"Subtotal: {money(subtotal)} {inv['currency']}",
        f"Tax ({int(inv['tax_rate'] * 100)}%): {money(tax)} {inv['currency']}",
        f"TOTAL DUE: {money(total)} {inv['currency']}",
        "",
        "Thank you for your business.",
    ]

    doc = pymupdf.open()
    page = doc.new_page()
    y = 72
    for line in lines:
        page.insert_text((72, y), line, fontsize=11, fontname="cour")
        y += 16
    doc.save(path)
    doc.close()
    return total


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    totals = {}
    for inv in INVOICES + [DUPLICATE]:
        total = build_invoice_pdf(inv, os.path.join(OUT_DIR, inv["file"]))
        totals[inv["file"]] = total
        print(f"wrote {inv['file']}  (total {money(total)})")

    # bank statement: charges for invoices 1 and 2 are present,
    # plus ONE charge (QuickPrint) that has no invoice -> "missing receipt"
    bank_rows = [
        ("2026-10-03", "NORTHWIND CLOUD SVCS AUSTIN TX", -totals["invoice_001_northwind.pdf"]),
        ("2026-10-06", "PIXEL AND CO DESIGN PORTLAND", -totals["invoice_002_pixelco.pdf"]),
        ("2026-10-09", "QUICKPRINT STATIONERY #221", -86.50),
    ]
    csv_path = os.path.join(OUT_DIR, "sample_bank_statement.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Description", "Amount"])
        for date, desc, amount in bank_rows:
            writer.writerow([date, desc, f"{amount:.2f}"])
    print(f"wrote sample_bank_statement.csv")

    print("\ndone. expected audit result:")
    print("  - 3 invoices processed, 2 flagged as duplicates (001 + 003)")
    print("  - 1 bank charge missing a receipt (QUICKPRINT STATIONERY, 86.50)")


if __name__ == "__main__":
    main()