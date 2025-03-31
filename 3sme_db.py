
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ✅ Set page config at the very top
st.set_page_config(page_title="Aaro7 MSME Dashboard", layout="wide")

# Then continue with everything else
@st.cache_data
def load_data():
    return pd.read_csv("payroll data_onboarding.csv")



pdata = load_data()

# Session state init

if "edited_pdata" not in st.session_state:
    st.session_state.edited_pdata = pdata.copy()
if "od_limit" not in st.session_state:
    st.session_state.od_limit = 500000
if "od_used" not in st.session_state:
    st.session_state.od_used = 0

# Helpers
def calculate_compliance(df):
    pf = len(df) * 1800
    esi = (df["Net Salary (INR) [Monthly] 🔁"] * 0.0375).sum()
    pt = len(df) * 200
    tds = (df["Net Salary (INR) [Monthly] 🔁"] * 0.10).sum()
    return int(pf), int(esi), int(pt), int(tds)

def update_od_used(amount):
    st.session_state.od_used += amount
    st.session_state.od_used = min(st.session_state.od_used, st.session_state.od_limit)

def reduce_od_used(amount):
    st.session_state.od_used -= amount
    if st.session_state.od_used < 0:
        st.session_state.od_used = 0

def generate_disbursal_report(df):
    report = df.copy()
    report["UTR"] = ["UTR" + str(np.random.randint(1000000, 9999999)) for _ in range(len(report))]
    report["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return report

# Sidebar – Credit Summary
with st.sidebar:
    st.title("💳 Credit Usage")
    od_used = st.session_state.od_used
    od_limit = st.session_state.od_limit
    od_remaining = max(od_limit - od_used, 0)
    st.metric("Approved OD Limit", f"₹{od_limit}")
    st.metric("OD Used", f"₹{od_used}")
    st.metric("OD Remaining", f"₹{od_remaining}")

# Header
st.title("📊 Aaro7 MSME Payroll Dashboard")

# Tabs
tabs = st.tabs(["👥 Payroll Summary", "💸 Disburse Payroll", "🧾 Compliance", "↩️ Repayments", "📈 Insights"])

# 1. Payroll Summary Tab
with tabs[0]:
    st.subheader("👥 MSLG Projects Employee Payroll Data")
    st.caption("Edit your payroll below and click Save when done.")
    edited_df = st.data_editor(
        st.session_state.edited_pdata,
        num_rows="dynamic",
        use_container_width=True,
        key="editor"
    )
    if st.button("💾 Save Payroll Changes"):
        st.session_state.edited_pdata = edited_df
        st.success("Payroll data saved!")

# 2. Disbursement Tab
with tabs[1]:
    st.subheader("💸 Pay Instantly")
    pay_df = st.session_state.edited_pdata[
        ["Employee ID [One-time] ✅", "Employee Name [One-time] ✅",
         "Designation [One-time] ✅", "Department [One-time] ✅",
         "Net Salary (INR) [Monthly] 🔁", "Mobile Number [One-time] ✅"]
    ].copy()
    pay_df["Select"] = False
    pay_df["Mobile Number [One-time] ✅"] = pay_df["Mobile Number [One-time] ✅"].astype(str)

    selected_df = st.data_editor(
        pay_df,
        disabled=pay_df.columns[:-1],
        use_container_width=True,
        key="pay_selector"
    )

    selected = selected_df[selected_df["Select"] == True]
    total = selected["Net Salary (INR) [Monthly] 🔁"].sum()
    st.markdown(f"**Total Net Salary for Selected Employees:** ₹{int(total)}")

    if st.button("✅ Pay Selected Employees"):
        update_od_used(total)
        report = generate_disbursal_report(selected)
        st.success("Payment processed!")
        st.download_button("📄 Download Disbursal Report", report.to_csv(index=False), "disbursal_report.csv")

# 3. Compliance Tab
with tabs[2]:
    st.subheader("🧾 Compliance Payments")
    pf, esi, pt, tds = calculate_compliance(st.session_state.edited_pdata)
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"💼 PF Payable: ₹{pf}")
        if st.button("💰 Pay PF"):
            update_od_used(pf)
        st.text_input("Other PF Amount", key="pf_other")
        st.info(f"🏛️ PT Payable: ₹{pt}")
        if st.button("💰 Pay PT"):
            update_od_used(pt)
        st.text_input("Other PT Amount", key="pt_other")
    with col2:
        st.info(f"🏥 ESI Payable: ₹{esi}")
        if st.button("💰 Pay ESI"):
            update_od_used(esi)
        st.text_input("Other ESI Amount", key="esi_other")
        st.info(f"💰 TDS Payable: ₹{tds}")
        if st.button("💰 Pay TDS"):
            update_od_used(tds)
        st.text_input("Other TDS Amount", key="tds_other")

# 4. Repayment Tab
with tabs[3]:
    st.subheader("↩️ Repayments")
    repayment_total = st.session_state.od_used
    min_due = int(repayment_total * 0.25)
    st.info(f"Total Outstanding: ₹{repayment_total}")
    st.info(f"Minimum Due: ₹{min_due}")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("✅ Pay Full"):
            reduce_od_used(repayment_total)
            st.success("OD fully repaid.")
    with c2:
        if st.button("💸 Pay Minimum"):
            reduce_od_used(min_due)
            st.success("Minimum payment made.")
    with c3:
        amt = st.number_input("Enter custom amount", min_value=0)
        if st.button("📤 Pay Custom Amount"):
            reduce_od_used(amt)
            st.success(f"Paid ₹{amt} successfully!")

# 5. Insights Tab
with tabs[4]:
    st.subheader("📈 Payroll Insights")
    c1, c2 = st.columns(2)
    with c1:
        st.bar_chart(
            st.session_state.edited_pdata.groupby("Department [One-time] ✅")["Net Salary (INR) [Monthly] 🔁"].sum()
        )
    with c2:
        st.bar_chart(
            st.session_state.edited_pdata.groupby("Designation [One-time] ✅")["Net Salary (INR) [Monthly] 🔁"].mean()
        )
