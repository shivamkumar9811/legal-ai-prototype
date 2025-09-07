import os
import streamlit as st
import google.generativeai as genai
import PyPDF2
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.utils import ImageReader
import io
from datetime import datetime

# -----------------------------
# 🔑 Configure Google API
# -----------------------------
# Secret API Key (from GitHub / Streamlit Cloud)
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

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
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"Summarize this legal document:\n\n{text}")
    return response.text

def explain_clauses(text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"Explain the important clauses in this legal document:\n\n{text}")
    return response.text

def answer_query(text, query):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        f"Answer the following question based on this legal document:\n\n{text}\n\nQuestion: {query}"
    )
    return response.text

# -----------------------------
# 📄 Create PDF (Logo + Disclaimer Sticker)
# -----------------------------
def create_pdf(content, title="AI Output"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(f"<b>{title}</b>", styles['Title']))
    story.append(Spacer(1, 12))

    # Content
    story.append(Paragraph(content.replace("\n", "<br/>"), styles['Normal']))
    story.append(Spacer(1, 12))

    # Timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"<i>Generated on: {timestamp}</i>", styles['Normal']))
    story.append(Spacer(1, 12))

    # Disclaimer with sticker
    try:
        story.append(Image("warning.png", width=25, height=25))  # sticker image
    except:
        pass
    disclaimer = (
        "Disclaimer: This AI-generated document is intended for educational and "
        "informational purposes only. It is not legal advice. The content may be "
        "incomplete, inaccurate, or outdated. For legal decisions, consult a qualified "
        "legal professional."
    )
    story.append(Paragraph(disclaimer, styles['Italic']))

    # Function to add logo (top-left corner, bigger)
    def add_logo(canvas, doc):
        try:
            logo = ImageReader("8379.png")   # <-- apna logo file
            width, height = LETTER
            logo_width = 180
            logo_height = 80
            canvas.drawImage(
                logo,
                40, height - logo_height - 20,
                width=logo_width,
                height=logo_height,
                preserveAspectRatio=True,
                mask='auto'
            )
        except Exception as e:
            print("Logo error:", e)

    # Build PDF
    doc.build(story, onFirstPage=add_logo, onLaterPages=add_logo)
    buffer.seek(0)
    return buffer

# -----------------------------
# 🎨 Sidebar
# -----------------------------
st.sidebar.image("8379.png", width=200) # <-- Sidebar ke top par 8379.png logo
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
    st.image("ai.png", width=150)  # Left side logo

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

summary, clauses, qa_answer = "", "", ""

if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    st.success("✅ Document uploaded and extracted successfully!")

    if st.button("📄 Summarize Document"):
        summary = summarize_text(text)
        st.subheader("📝 Simplified Summary")
        st.write(summary)

        pdf_buffer = create_pdf(summary, title="Legal Document Summary")
        st.download_button(
            label="📥 Download Summary as PDF",
            data=pdf_buffer,
            file_name="Legal_Summary.pdf",
            mime="application/pdf",
        )

    if st.button("📌 Explain Clauses"):
        clauses = explain_clauses(text)
        st.subheader("📑 Clause Explanations")
        st.write(clauses)

        pdf_buffer = create_pdf(clauses, title="Clause Explanations")
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
            qa_answer = answer_query(text, user_query)
            st.subheader("🤖 AI Answer")
            st.write(qa_answer)

            pdf_buffer = create_pdf(qa_answer, title=f"Answer to: {user_query}")
            st.download_button(
                label="📥 Download Answer as PDF",
                data=pdf_buffer,
                file_name="AI_Answer.pdf",
                mime="application/pdf",
            )

    # -----------------------------
    # 📘 Generate Full Report (Summary + Clauses + Q&A)
    # -----------------------------
    if st.button("📘 Generate Full Report"):
        full_report = ""

        if summary:
            full_report += "📄 Summary:\n" + summary + "\n\n"
        else:
            full_report += "📄 Summary: (Not generated)\n\n"

        if clauses:
            full_report += "📑 Clause Explanations:\n" + clauses + "\n\n"
        else:
            full_report += "📑 Clause Explanations: (Not generated)\n\n"

        if qa_answer:
            full_report += "💬 Q&A:\n" + qa_answer + "\n\n"
        else:
            full_report += "💬 Q&A: (No question asked)\n\n"

        st.subheader("📘 Full Report Preview")
        st.write(full_report)

        pdf_buffer = create_pdf(full_report, title="Full Legal Report")
        st.download_button(
            label="📥 Download Full Report as PDF",
            data=pdf_buffer,
            file_name="Full_Legal_Report.pdf",
            mime="application/pdf",
        )


        
