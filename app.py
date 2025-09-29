import streamlit as st
import google.generativeai as genai
import PyPDF2
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.utils import ImageReader
import io
from datetime import datetime

# -----------------------------
# 🔑 Multi API Key Setup
# -----------------------------
import streamlit as st
import google.generativeai as genai

# Load API keys from Streamlit secrets
API_KEYS = [
    st.secrets.get("GOOGLE_API_KEY_1", ""),
    st.secrets.get("GOOGLE_API_KEY_2", ""),
    st.secrets.get("GOOGLE_API_KEY_3", "")
]

current_index = 0

def get_model():
    """Return a configured GenerativeModel, rotating keys if quota is exceeded."""
    global current_index
    for _ in range(len(API_KEYS)):
        try:
            genai.configure(api_key=API_KEYS[current_index])
            return genai.GenerativeModel("gemini-1.5-flash-latest")
        except Exception as e:
            if "ResourceExhausted" in str(e):
                # Rotate key if quota exceeded
                current_index = (current_index + 1) % len(API_KEYS)
            else:
                raise e
    raise RuntimeError("⚠️ All API keys exhausted. Please try later.")

# -----------------------------
# 📂 Extract Text from PDF
# -----------------------------
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# -----------------------------
# 🤖 AI Functions
# -----------------------------
def summarize_text(text):
    model = get_model()
    response = model.generate_content(f"Summarize this legal document:\n\n{text}")
    return getattr(response, "text", str(response))

def explain_clauses(text):
    model = get_model()
    response = model.generate_content(f"Explain the important clauses in this legal document:\n\n{text}")
    return getattr(response, "text", str(response))

def answer_query(text, query):
    model = get_model()
    response = model.generate_content(
        f"Answer the following question based on this legal document:\n\n{text}\n\nQuestion: {query}"
    )
    return getattr(response, "text", str(response))

# -----------------------------
# 🖼️ Add logo function
# -----------------------------
def add_logo(canvas, doc, logo_path="8379.png"):
    try:
        logo = ImageReader(logo_path)
        page_width, page_height = LETTER
        logo_width = 180
        logo_height = 80
        canvas.drawImage(
            logo,
            40,
            page_height - logo_height - 20,
            width=logo_width,
            height=logo_height,
            preserveAspectRatio=True,
            mask='auto'
        )
    except Exception as e:
        print("Logo error:", e)

# -----------------------------
# 📄 Create PDF (Summary / Clauses / QA individually)
# -----------------------------
def create_pdf(content, title="AI Output", logo_path="8379.png", sticker_path="warning.png"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"<b>{title}</b>", styles['Title']))
    story.append(Spacer(1, 12))

    story.append(Paragraph(content.replace("\n", "<br/>"), styles['Normal']))
    story.append(Spacer(1, 12))

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"<i>Generated on: {timestamp}</i>", styles['Normal']))
    story.append(Spacer(1, 12))

    try:
        story.append(Image(sticker_path, width=25, height=25))
    except Exception:
        pass

    disclaimer = (
        "Disclaimer: This AI-generated document is intended for educational and "
        "informational purposes only. It is not legal advice. The content may be "
        "incomplete, inaccurate, or outdated. For legal decisions, consult a qualified "
        "legal professional."
    )
    story.append(Paragraph(disclaimer, styles['Italic']))

    doc.build(story, onFirstPage=lambda c, d: add_logo(c, d, logo_path),
                     onLaterPages=lambda c, d: add_logo(c, d, logo_path))
    buffer.seek(0)
    return buffer

# -----------------------------
# 📘 Create Full Report
# -----------------------------
def create_full_report_pdf(logo_path="8379.png", sticker_path="warning.png"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>Legal Final Report</b>", styles['Title']))
    story.append(Spacer(1, 20))

    summary = st.session_state.get("summary", "")
    clauses = st.session_state.get("clauses", "")
    qa_answer = st.session_state.get("qa_answer", "")

    if summary:
        try:
            img = Image("summary.png", width=20, height=20)
        except Exception:
            img = Paragraph("", styles['Normal'])
        title = Paragraph("<b>Simplified Summary</b>", styles['Heading2'])
        table = Table([[img, title]], colWidths=[30, 450])
        table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        story.append(table)
        story.append(Spacer(1, 8))
        story.append(Paragraph(summary.replace("\n", "<br/>"), styles['Normal']))
        story.append(Spacer(1, 12))

    if clauses:
        try:
            img = Image("clauses.png", width=20, height=20)
        except Exception:
            img = Paragraph("", styles['Normal'])
        title = Paragraph("<b>Clause Explanations</b>", styles['Heading2'])
        table = Table([[img, title]], colWidths=[30, 450])
        table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        story.append(table)
        story.append(Spacer(1, 8))
        story.append(Paragraph(clauses.replace("\n", "<br/>"), styles['Normal']))
        story.append(Spacer(1, 12))

    if qa_answer:
        try:
            img = Image("qa.png", width=20, height=20)
        except Exception:
            img = Paragraph("", styles['Normal'])
        title = Paragraph("<b>Q&A</b>", styles['Heading2'])
        table = Table([[img, title]], colWidths=[30, 450])
        table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        story.append(table)
        story.append(Spacer(1, 8))
        story.append(Paragraph(qa_answer.replace("\n", "<br/>"), styles['Normal']))
        story.append(Spacer(1, 12))

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"<i>Generated on: {timestamp}</i>", styles['Normal']))
    story.append(Spacer(1, 12))

    try:
        story.append(Image(sticker_path, width=25, height=25))
    except Exception:
        pass

    disclaimer = (
        "Disclaimer: This AI-generated document is intended for educational and "
        "informational purposes only. It is not legal advice. The content may be "
        "incomplete, inaccurate, or outdated. For legal decisions, consult a qualified "
        "legal professional."
    )
    story.append(Paragraph(disclaimer, styles['Italic']))

    doc.build(story, onFirstPage=lambda c, d: add_logo(c, d, logo_path),
                     onLaterPages=lambda c, d: add_logo(c, d, logo_path))
    buffer.seek(0)
    return buffer

# -----------------------------
# 🎨 Sidebar
# -----------------------------
st.sidebar.image("8379.png", width=200)
st.sidebar.markdown(
    "<h3 style='color:#555; text-align:center; margin-top:5px;'>LegalEaseAI Prototype v1.0</h3>",
    unsafe_allow_html=True
)
st.sidebar.title("ℹ️ About This App")
st.sidebar.write(
    """
    This prototype uses **Google Gemini AI** to simplify and explain legal documents.
    Upload a PDF and interact with AI to get insights.
    """
)
st.sidebar.markdown("---")
st.sidebar.subheader("📖 How to Use")
st.sidebar.write(
    """
    1. **Upload** a legal PDF document  
    2. Click **Summarize** to get a simplified version  
    3. Click **Explain Clauses** for clause explanations  
    4. Ask a question in the text box  
    5. Generate a **Full Report PDF**  
    """
)
st.sidebar.markdown("---")
st.sidebar.subheader("⚠️ Disclaimer")
st.sidebar.write(
    """
    This project uses Generative AI to simplify and explain legal documents.  
    It is for **educational and informational purposes only** and not legal advice.  

    Always consult a qualified legal professional before making decisions.  
    Developers are **not responsible** for consequences of using AI-generated output.  
    """
)

# -----------------------------
# 🎨 Main UI
# -----------------------------
col1, col2 = st.columns([1, 5])
with col1:
    try:
        st.image("ai.png", width=150)
    except Exception:
        pass

with col2:
    st.markdown(
        """
        <h1 style="
            color:#000000;
            font-size:40px;
            font-weight:900;
            font-family: 'Trebuchet MS', 'Helvetica Neue', sans-serif;
            letter-spacing: 1px;
            margin-bottom:0;">
            AI for Demystifying Legal Documents
        </h1>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# 📂 File Upload + Features
# -----------------------------
uploaded_file = st.file_uploader("📂 Upload a legal document (PDF)", type=["pdf"])

if "summary" not in st.session_state:
    st.session_state.summary = ""
if "clauses" not in st.session_state:
    st.session_state.clauses = ""
if "qa_answer" not in st.session_state:
    st.session_state.qa_answer = ""

if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    st.success("✅ Document uploaded and extracted successfully!")

    if st.button("📄 Summarize Document"):
        st.session_state.summary = summarize_text(text)
        st.subheader("📝 Simplified Summary")
        st.write(st.session_state.summary)

        pdf_buffer = create_pdf(st.session_state.summary, title="Legal Document Summary")
        st.download_button(
            label="📥 Download Summary as PDF",
            data=pdf_buffer,
            file_name="Legal_Summary.pdf",
            mime="application/pdf",
        )

    if st.button("📌 Explain Clauses"):
        st.session_state.clauses = explain_clauses(text)
        st.subheader("📑 Clause Explanations")
        st.write(st.session_state.clauses)

        pdf_buffer = create_pdf(st.session_state.clauses, title="Clause Explanations")
        st.download_button(
            label="📥 Download Clauses as PDF",
            data=pdf_buffer,
            file_name="Clause_Explanations.pdf",
            mime="application/pdf",
        )

    st.subheader("💬 Ask a Question")
    user_query = st.text_input("Type your question here (e.g., 'Are there hidden fees?')")
    if st.button("Get Answer"):
        if user_query:
            st.session_state.qa_answer = answer_query(text, user_query)
            st.subheader("🤖 AI Answer")
            st.write(st.session_state.qa_answer)

            pdf_buffer = create_pdf(st.session_state.qa_answer, title=f"Answer to: {user_query}")
            st.download_button(
                label="📥 Download Answer as PDF",
                data=pdf_buffer,
                file_name="AI_Answer.pdf",
                mime="application/pdf",
            )

# -----------------------------
# 📘 Generate Full Report
# -----------------------------
if uploaded_file:
    if st.button("📘 Generate Full Report"):
        pdf_buffer = create_full_report_pdf()
        st.subheader("📘 Full Report Preview")
        st.write("Full report generated ✅")

        st.download_button(
            label="📥 Download Full Report as PDF",
            data=pdf_buffer,
            file_name="Full_Legal_Report.pdf",
            mime="application/pdf",
        )


