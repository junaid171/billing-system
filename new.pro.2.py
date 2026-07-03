import streamlit as st
import pandas as pd
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Page configuration
st.set_page_config(
    page_title="S.A. Mobile Billing",
    page_icon="📲",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 👤 MULTI-USER LOGIN SYSTEM ---
st.sidebar.markdown("### 🔑 User Account")
user_choice = st.sidebar.selectbox("Select User", ["User_A", "User_B"])

# Har user ki alag data file hogi taaki data mix na ho
DATA_FILE = f"billing_data_{user_choice}.csv"

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame([{"total_sales": 0, "pending_udhaari": 0}])
    df.to_csv(DATA_FILE, index=False)

def load_data():
    df = pd.read_csv(DATA_FILE)
    return int(df.iloc[0]["total_sales"]), int(df.iloc[0]["pending_udhaari"])

def save_data(sales, udhaari):
    df = pd.DataFrame([{"total_sales": sales, "pending_udhaari": udhaari}])
    df.to_csv(DATA_FILE, index=False)

# Load data based on selected user
saved_sales, saved_udhaari = load_data()

# Session state ko user ke mutabik refresh karna
st.session_state.total_sales = saved_sales
st.session_state.pending_udhaari = saved_udhaari

if 'pdf_buffer' not in st.session_state:
    st.session_state.pdf_buffer = None
if 'last_party' not in st.session_state:
    st.session_state.last_party = ""

# --- SIMPLE BUT PROFESSIONAL PDF GENERATOR ---
def generate_simple_pro_pdf(name, item, inv_date, base_amt, tax_amt, total_amt, gst_status):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, leading=26, textColor=colors.HexColor('#007bff'), alignment=1)
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.gray, alignment=1)
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=11, leading=15, fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('NormalText', parent=styles['Normal'], fontSize=11, leading=15)
    right_style = ParagraphStyle('RightText', parent=styles['Normal'], fontSize=11, leading=15, alignment=2)
    right_bold = ParagraphStyle('RightBold', parent=styles['Normal'], fontSize=11, leading=15, fontName='Helvetica-Bold', alignment=2)
    
    story.append(Paragraph("<b>S.A. DIGITAL BILLING</b>", title_style))
    story.append(Paragraph("Bhiwandi Mobile Business Hub", sub_style))
    story.append(Spacer(1, 15))
    
    formatted_date = inv_date.strftime('%d-%b-%Y')
    meta_data = [
        [Paragraph(f"<b>Billed To (Party):</b> {name}", normal_style), Paragraph(f"<b>Date:</b> {formatted_date}", right_style)],
        [Paragraph(f"<b>Invoice Type:</b> {gst_status}", normal_style), Paragraph(f"<b>Billed By:</b> {user_choice}", right_style)]
    ]
    t_meta = Table(meta_data, colWidths=[300, 250])
    t_meta.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(t_meta)
    story.append(Spacer(1, 15))
    
    is_gst = "5%" in gst_status
    cgst_sgst_val = tax_amt / 2 if is_gst else 0
    
    table_data = [
        [Paragraph("<b>Sl No.</b>", header_style), Paragraph("<b>Item / Description</b>", header_style), Paragraph("<b>Base Amount (₹)</b>", right_bold)],
        [Paragraph("1", normal_style), Paragraph(f"{item}", normal_style), Paragraph(f"{base_amt:,.2f}", right_style)],
    ]
    
    if is_gst:
        table_data.append(["", Paragraph("CGST @ 2.5%", normal_style), Paragraph(f"{cgst_sgst_val:,.2f}", right_style)])
        table_data.append(["", Paragraph("SGST @ 2.5%", normal_style), Paragraph(f"{cgst_sgst_val:,.2f}", right_style)])
        
    table_data.append(["", Paragraph("<b>Grand Total:</b>", header_style), Paragraph(f"<b>₹ {total_amt:,.2f}</b>", right_bold)])
    
    t_items = Table(table_data, colWidths=[50, 350, 150])
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F8F9FA')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#333333')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_items)
    story.append(Spacer(1, 30))
    
    story.append(Paragraph("<i>This is a computer-generated invoice document.</i>", sub_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>For S.A. ELECTRICAL & AUTOMATION</b>", right_bold))
    story.append(Spacer(1, 30))
    story.append(Paragraph("Authorised Signatory", right_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Custom Interface CSS Styling
st.markdown("""
    <style>
    .block-container { padding-top: 2.5rem !important; padding-bottom: 1rem !important; padding-left: 12px !important; padding-right: 12px !important; }
    .mobile-title { text-align: center; background: linear-gradient(45deg, #00FFCC, #007bff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 22px; }
    .mobile-subtitle { text-align: center; color: var(--text-color); opacity: 0.6; font-size: 12px; margin-top: 4px; margin-bottom: 15px; }
    .mobile-card { background-color: var(--background-color); color: var(--text-color); border: 1px solid rgba(128, 128, 128, 0.2); padding: 14px; border-radius: 10px; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05); margin-bottom: 12px; }
    .m-badge-success { background-color: rgba(46, 160, 67, 0.15); color: #2EA043; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }
    .m-badge-pending { background-color: rgba(255, 193, 7, 0.15); color: #FFC107; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }
    
    div[data-testid="stForm"] { border: none !important; padding: 0px !important; }
    .stButton>button { width: 100% !important; padding: 12px !important; font-size: 16px !important; border-radius: 8px !important; }
    
    .gst-btn button { background-color: #2EA043 !important; color: white !important; font-weight: bold !important; }
    .nogst-btn button { background-color: #6c757d !important; color: white !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown(f"<h1 class='mobile-title'>DIGITAL BILLING ({user_choice})</h1>", unsafe_allow_html=True)
st.markdown("<p class='mobile-subtitle'>Bhiwandi Mobile Business Hub</p>", unsafe_allow_html=True)
st.write("---")

# --- LIVE CARDS ---
st.markdown(f"""
    <div class="mobile-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <b style="font-size: 15px;">📊 Aaj Ki Sales ({user_choice})</b>
            <span class="m-badge-success">₹ {st.session_state.total_sales:,}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="mobile-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <b style="font-size: 15px;">⏳ Udhaari / Pending ({user_choice})</b>
            <span class="m-badge-pending">₹ {st.session_state.pending_udhaari:,}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

st.write("")

# --- SHOW DOWNLOAD LINK IF GENERATED ---
if st.session_state.pdf_buffer is not None:
    st.success(f"🎉 Professional Invoice Ready for {st.session_state.last_party}!")
    st.download_button(
        label="📥 DOWNLOAD INVOICE (PDF)",
        data=st.session_state.pdf_buffer,
        file_name=f"Invoice_{st.session_state.last_party}.pdf",
        mime="application/pdf"
    )
    st.write("---")

# --- POPUP DIALOG FUNCTION ---
@st.dialog("📋 Choose Invoice Type")
def tax_selection_popup(name, item, inv_date, amt, p_type):
    st.write(f"👤 **Party Name:** {name}")
    st.write(f"📦 **Product:** {item}")
    st.write(f"📅 **Invoice Date:** {inv_date.strftime('%d-%b-%Y')}")
    st.write(f"💰 **Base Amount:** ₹ {amt:,}")
    st.write("---")
    st.write("Is bill par **GST (5%)** apply karna hai ya **Without GST** rakhna hai?")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="gst-btn">', unsafe_allow_html=True)
        with_gst = st.button("With GST (5%)")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="nogst-btn">', unsafe_allow_html=True)
        without_gst = st.button("Without GST")
        st.markdown('</div>', unsafe_allow_html=True)
        
    if with_gst:
        tax = amt * 0.05
        final_amount = amt + tax
        st.session_state.pdf_buffer = generate_simple_pro_pdf(name, item, inv_date, amt, tax, final_amount, f"Tax Invoice (5% GST) - {user_choice}")
        st.session_state.last_party = name
        process_and_save(name, final_amount, p_type)
        
    if without_gst:
        st.session_state.pdf_buffer = generate_simple_pro_pdf(name, item, inv_date, amt, 0, amt, f"Bill of Supply (0% GST) - {user_choice}")
        st.session_state.last_party = name
        process_and_save(name, amt, p_type)

def process_and_save(name, final_amt, p_type):
    if p_type == "Cash / Online Received (Sales)":
        st.session_state.total_sales += final_amt
    else:
        st.session_state.pending_udhaari += final_amt
        
    save_data(st.session_state.total_sales, st.session_state.pending_udhaari)
    st.rerun()

# --- QUICK ENTRY FORM ---
st.markdown("### ➕ Quick Entry")

with st.form(key="billing_form", clear_on_submit=True):
    customer_name = st.text_input("Party Name", placeholder="e.g., Al-Fahad Textiles", max_chars=20)
    product_item = st.selectbox("Select Item / Quality", ["Powder Coated Box (KGS)", "Grey Fabric (Cotton)", "Yarn 40s Count", "Ready Garments"])
    invoice_date = st.date_input("Invoice Date", value=pd.Timestamp.now().date())
    amount = st.number_input("Bill Amount (₹)", min_value=0, value=0, step=500, max_value=20000)
    payment_status = st.radio("Payment Type", ["Cash / Online Received (Sales)", "Udhaari / Pending"])
    
    st.write("")
    submit_button = st.form_submit_button(label="🚀 SAVE BILL", type="primary")

if submit_button:
    if any(char.isdigit() for char in customer_name):
        st.error("Please enter a valid Party Name without numbers!")
    elif customer_name == "":
        st.error("Please enter a valid Party Name!")
    elif amount <= 0 or amount > 20000:
        st.error("Please enter a valid amount between ₹0 and ₹20,000!")
    else:
        st.session_state.pdf_buffer = None
        tax_selection_popup(customer_name, product_item, invoice_date, amount, payment_status)
