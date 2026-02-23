import streamlit as st
import pandas as pd

st.title("PAN-Wise NCD Summary Report")

# --------------------------------------------------------------
# 1. LOAD THE MASTER EXCEL FILE (CONTAINING ALL 8 SHEETS MERGED)
# --------------------------------------------------------------

MASTER_FILE = r"C:\Users\USER\Desktop\NCD_MASTER.xlsx"     # <-- keep your file name here

try:
    df = pd.read_excel(MASTER_FILE)
except Exception as e:
    st.error(f"Error loading master file: {e}")
    st.stop()

# Clean column names (remove spaces, uppercase everything)
df.columns = df.columns.str.strip().str.lower()

# --------------------------------------------------------------
# 2. VERIFY IMPORTANT COLUMNS EXIST
# --------------------------------------------------------------

required_columns = [
    "bfitpan", "unit_code", "princ_amt",
    "gross_amt", "tdsamt", "netamt", "int_type"
]

missing = [c for c in required_columns if c not in df.columns]

if missing:
    st.error(f"Missing columns in Excel: {missing}")
    st.stop()

# --------------------------------------------------------------
# 3. USER PAN INPUT
# --------------------------------------------------------------

pan_input = st.text_input("Enter PAN Number").strip().upper()

if pan_input:

    # Filter PAN records
    result = df[df["bfitpan"].str.upper() == pan_input]

    if result.empty:
        st.warning("No records found for this PAN.")
        st.stop()

    st.success("Records found!")

    # ----------------------------------------------------------
    # 4. SHOW CUSTOMER FULL DATA TABLE
    # ----------------------------------------------------------
    st.subheader("Detailed Customer Records")
    st.dataframe(result)

    # ----------------------------------------------------------
    # 5. NCD-WISE SUMMARY (Group by security_code)
    # ----------------------------------------------------------

    st.subheader("📌 NCD-Wise Summary")

    ncd_summary = (
        result.groupby("unit_code")
        .agg(
            Total_Principal=("princ_amt", "sum"),
            Total_Interest=("gross_amt", "sum"),
            Total_TDS=("tdsamt", "sum"),
            Net_Amount=("netamt", "sum"),
        )
        .reset_index()
    )

    st.dataframe(ncd_summary)
     # --------------------------
    # BANK DETAILS
    # --------------------------
    st.subheader("🏦 Customer Bank Details")

    bank_name = result["bank_name"].dropna().unique()
    bank_acc = result["bank_accno"].dropna().unique()
    ifsc = result["ifsc_code"].dropna().unique()

    st.write(f"**Bank Name:** {bank_name[0] if len(bank_name)>0 else 'NA'}")
    st.write(f"**Account Number:** {bank_acc[0] if len(bank_acc)>0 else 'NA'}")
    st.write(f"**IFSC Code:** {ifsc[0] if len(ifsc)>0 else 'NA'}")

    st.divider()

    # ----------------------------------------------------------
    # 6. GRAND TOTAL SUMMARY
    # ----------------------------------------------------------

    st.subheader("📌 GRAND TOTAL")

    total_principal = result["princ_amt"].sum()
    total_interest = result["gross_amt"].sum()
    total_tds = result["tdsamt"].sum()
    total_net = result["netamt"].sum()

    st.write(f"**Total Principal Amount:** {total_principal:,.2f}")
    st.write(f"**Total Interest Amount:** {total_interest:,.2f}")
    st.write(f"**Total TDS Deducted:** {total_tds:,.2f}")
    st.write(f"**Total Net Paid Amount:** {total_net:,.2f}")