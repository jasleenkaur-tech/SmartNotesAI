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
genai.configure(api_key="AIzaSyCw_ksO9MdnAGEqnSoOCTMhSlawair2yDE")  # Replace with your actual key

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
    prompt = f"Summarize this note concisely:\n\n{note_text}"
    response = model.generate_content(prompt)
    return response.text.strip()

# --------------------------
# 📄 EXPORT SUMMARY TO PDF
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
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# --------------------------
# 🎨 DYNAMIC THEME + BACKGROUND
# --------------------------
if st.session_state.dark_mode:
    background_style = """
        background: linear-gradient(135deg, #2e2e2e, #1c1c1c);
        color: #f5f5f5;
    """
    note_bg = "#333333"
    note_color = "#ffffff"
else:
    background_style = """
        background: linear-gradient(135deg, #d9d9d9, #bfbfbf, #e6e6e6);
        color: #000000;
    """
    note_bg = "#ffffff"
    note_color = "#000000"

st.markdown(f"""
<style>
body {{
    {background_style}
    background-attachment: fixed;
    background-repeat: no-repeat;
    background-size: cover;
}}
.note-box {{
    border: 1px solid #ccc;
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 10px;
    background-color: {note_bg};
    color: {note_color};
    box-shadow: 0px 3px 8px rgba(0,0,0,0.2);
}}
.summary-box {{
    border-left: 4px solid #4CAF50;
    background-color: #f9f9f9;
    color: #000;
    padding: 10px;
    border-radius: 5px;
    margin-top: 10px;
    margin-bottom: 15px;
}}
.stTextArea textarea {{
    border: 1px solid #000 !important;
}}
.stButton button {{
    font-size: 14px !important;
    padding: 6px 12px !important;
    border-radius: 8px !important;
}}
</style>
""", unsafe_allow_html=True)

# --------------------------
# 📝 PAGE TITLE
# --------------------------
st.markdown("<h1 style='text-align:center;'>📝 SmartNotes AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#555;'>Enhance Your Productivity with Smart AI Notes</p>", unsafe_allow_html=True)

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
            st.experimental_rerun()
        else:
            st.error("⚠️ Please write something before adding!")

# --------------------------
# 🔍 SEARCH BAR
# --------------------------
search_query = st.text_input("🔍 Search Notes", "", placeholder="Type here to search your notes...").lower()

# --------------------------
# 📚 HEADER + THEME TOGGLE
# --------------------------
st.markdown("---")
col_title, col_btn = st.columns([5, 1])
with col_title:
    st.subheader("Your Notes")
with col_btn:
    if st.button("🌙 Toggle Theme"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.experimental_rerun()

# --------------------------
# 📚 DISPLAY NOTES
# --------------------------
filtered_notes = [n for n in st.session_state.notes if search_query in n["text"].lower()]

if not filtered_notes:
    st.info("No matching notes found.")
else:
    for i, note in enumerate(reversed(filtered_notes)):
        note_index = len(st.session_state.notes) - 1 - i
        font_size = st.session_state.font_sizes.get(note_index, 16)

        # ✏️ EDIT MODE
        if st.session_state.edit_mode == note_index:
            st.session_state.edited_text = st.text_area(
                "✏️ Edit Note:",
                value=st.session_state.notes[note_index]["text"],
                height=180,
                key=f"edit_text_{note_index}"
            )

            if st.button("✅ Save Changes", key=f"save_{note_index}"):
                st.session_state.notes[note_index]["text"] = st.session_state.edited_text
                save_notes(st.session_state.notes)
                st.session_state.edit_mode = None
                st.experimental_rerun()

        else:
            # Apply the same font size to both note and summary
            st.markdown(
                f"<div class='note-box' style='font-size:{font_size}px'>{note['text']}</div>",
                unsafe_allow_html=True
            )

            cols = st.columns([1, 1, 1, 1, 1, 1])
            with cols[0]:
                if st.button("✏️ Edit", key=f"edit_{note_index}"):
                    st.session_state.edit_mode = note_index
                    st.experimental_rerun()

            with cols[1]:
                if st.button("✨ Summarize", key=f"sum_{note_index}") and note_index not in st.session_state.summaries:
                    st.session_state.summaries[note_index] = summarize_note(note["text"])
                    st.experimental_rerun()

            with cols[2]:
                if st.button("🗑️ Delete", key=f"del_{note_index}"):
                    st.session_state.notes.pop(note_index)
                    save_notes(st.session_state.notes)
                    st.experimental_rerun()

            with cols[3]:
                if st.button("⭐ Favorite", key=f"fav_{note_index}") and note_index not in st.session_state.favorites:
                    st.session_state.favorites.append(note_index)
                    st.success("Added to favorites!")
                    save_notes(st.session_state.notes)

            with cols[4]:
                if st.button("➕", key=f"plus_{note_index}"):
                    st.session_state.font_sizes[note_index] = font_size + 2
                    st.experimental_rerun()

            with cols[5]:
                if st.button("➖", key=f"minus_{note_index}"):
                    if font_size > 10:
                        st.session_state.font_sizes[note_index] = font_size - 2
                        st.experimental_rerun()

            # 🧾 SHOW SUMMARY WITH SAME FONT SIZE + PDF DOWNLOAD
            if note_index in st.session_state.summaries:
                summary_text = st.session_state.summaries[note_index]
                st.markdown(
                    f"<div class='summary-box' style='font-size:{font_size}px'>{summary_text}</div>",
                    unsafe_allow_html=True
                )

                title_words = note["text"].split()[:2]
                pdf_title = "_".join(title_words) if title_words else "Note_Summary"
                pdf_filename = f"{pdf_title}.pdf"

                pdf_data = export_pdf_bytes(pdf_title, summary_text)
                st.download_button(
                    label="📄 Download Summary as PDF",
                    data=pdf_data,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    key=f"pdf_{note_index}",
                )

# --------------------------
# 🌟 FAVORITE NOTES SECTION
# --------------------------
if st.session_state.favorites:
    st.markdown("---")
    st.subheader("⭐ Favorite Notes")
    for fav_index in st.session_state.favorites:
        if fav_index < len(st.session_state.notes):
            note = st.session_state.notes[fav_index]
            font_size = st.session_state.font_sizes.get(fav_index, 16)
            st.markdown(f"<div class='note-box' style='font-size:{font_size}px'>{note['text']}</div>", unsafe_allow_html=True)
