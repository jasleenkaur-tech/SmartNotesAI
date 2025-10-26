import streamlit as st
import json
import google.generativeai as genai
from fpdf import FPDF
from io import BytesIO

# --------------------------
# 🌐 PAGE CONFIGURATION
# --------------------------
st.set_page_config(page_title="SmartNotes AI", page_icon="📝", layout="wide")

# --------------------------
# 🔑 GEMINI API KEY
# --------------------------
genai.configure(api_key="AIzaSyCw_ksO9MdnAGEqnSoOCTMhSlawair2yDE") 

# --------------------------
# 🧩 LOAD & SAVE NOTES
# --------------------------
def load_notes():
    try:
        with open("notes.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_notes(notes):
    with open("notes.json", "w") as f:
        json.dump(notes, f, indent=4)

# --------------------------
# 🤖 SUMMARIZE NOTE FUNCTION
# --------------------------
def summarize_note(note_text):
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    prompt = f"Summarize this note clearly and concisely:\n\n{note_text}"
    response = model.generate_content(prompt)
    return response.text.strip()

# --------------------------
# 📄 EXPORT TO PDF
# --------------------------
def export_pdf_bytes(title, text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"{title}\n\n{text}")
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    return BytesIO(pdf_bytes)

# --------------------------
# 🧠 SESSION STATE SETUP
# --------------------------
if "notes" not in st.session_state:
    st.session_state.notes = load_notes()
if "summaries" not in st.session_state:
    st.session_state.summaries = {}
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = None
if "edited_text" not in st.session_state:
    st.session_state.edited_text = ""
if "font_sizes" not in st.session_state:
    st.session_state.font_sizes = {}

# --------------------------
# 🎨 CUSTOM CSS
# --------------------------
st.markdown("""
<style>
.note-box {
    border: 1px solid #ddd; 
    padding: 15px; 
    margin-bottom: 15px; 
    border-radius: 10px;
    background-color: #fff;
    box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
}
.summary-box {
    border-left: 4px solid #4CAF50;
    background-color: #f9f9f9;
    padding: 10px;
    border-radius: 5px;
    margin-top: 10px;
    margin-bottom: 15px;
}
.stTextArea textarea {
    border: 1px solid black !important;
}
.stButton button {
    font-size: 14px !important;
    padding: 6px 12px !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------
# 📝 PAGE TITLE
st.markdown("<h1 style='text-align: center;'>📝 SmartNotes AI</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #555; font-size:16px; font-weight: normal;'>Transforming Your Notes into Insights with AI Precision</p>",
    unsafe_allow_html=True
)

# --------------------------
# ✍️ ADD NEW NOTE
# --------------------------
st.subheader("Add a New Note")
with st.form("add_note_form", clear_on_submit=True):
    note_input = st.text_area("Write your note here:", height=180)
    submitted = st.form_submit_button("✚ Add Note")
    if submitted:
        if note_input.strip():
            st.session_state.notes.append({"text": note_input})
            save_notes(st.session_state.notes)
            st.success("✅ Note added successfully!")
        else:
            st.error("⚠️ Please write something before adding!")

st.markdown("---")

# --------------------------
# 📚 YOUR NOTES SECTION
# --------------------------
st.subheader("Your Notes")
if not st.session_state.notes:
    st.info("No notes added yet! Start by writing your first note above.")

for i, note in enumerate(reversed(st.session_state.notes)):
    note_index = len(st.session_state.notes) - 1 - i
    if note_index not in st.session_state.font_sizes:
        st.session_state.font_sizes[note_index] = 16
    font_size = st.session_state.font_sizes[note_index]

    # EDIT MODE
    if st.session_state.edit_mode == note_index:
        st.session_state.edited_text = st.text_area(
            "Edit your note:",
            value=st.session_state.notes[note_index]["text"],
            height=180,
            key=f"edit_text_{note_index}"
        )
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("✅ Save", key=f"save_{note_index}"):
                st.session_state.notes[note_index]["text"] = st.session_state.edited_text
                save_notes(st.session_state.notes)
                st.session_state.edit_mode = None
        with col2:
            if st.button("❌ Cancel", key=f"cancel_{note_index}"):
                st.session_state.edit_mode = None

    # NORMAL VIEW
    else:
        st.markdown(
            f"<div class='note-box' style='font-size:{font_size}px'>{note['text']}</div>",
            unsafe_allow_html=True
        )

        # BUTTONS
        cols = st.columns([1,1,1,1,1,1])

        with cols[0]:
            if st.button("✏️ Edit", key=f"edit_{note_index}"):
                st.session_state.edit_mode = note_index

        with cols[1]:
            if st.button("✨ Summarize", key=f"sum_{note_index}"):
                try:
                    st.session_state.summaries[note_index] = summarize_note(note["text"])
                except Exception as e:
                    st.error(f"Error: {e}")

        with cols[2]:
            if st.button("🗑️ Delete", key=f"del_{note_index}"):
                st.session_state.notes.pop(note_index)
                st.session_state.font_sizes.pop(note_index, None)
                st.session_state.summaries.pop(note_index, None)
                save_notes(st.session_state.notes)

        with cols[3]:
            if st.button("➕", key=f"plus_{note_index}"):
                st.session_state.font_sizes[note_index] += 2

        with cols[4]:
            if st.button("➖", key=f"minus_{note_index}"):
                if st.session_state.font_sizes[note_index] > 10:
                    st.session_state.font_sizes[note_index] -= 2

        with cols[5]:
            if note_index in st.session_state.summaries:
                title = note["text"].split("\n")[0][:30].replace(" ", "_")
                pdf_bytes = export_pdf_bytes(title, st.session_state.summaries[note_index])
                st.download_button(
                    label="📄 PDF",
                    data=pdf_bytes,
                    file_name=f"{title}.pdf",
                    mime="application/pdf",
                    key=f"pdf_{note_index}"
                )

        if note_index in st.session_state.summaries:
            st.markdown(
                f"<div class='summary-box'>{st.session_state.summaries[note_index]}</div>",
                unsafe_allow_html=True
            )
