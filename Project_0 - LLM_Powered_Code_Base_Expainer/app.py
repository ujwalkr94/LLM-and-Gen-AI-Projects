import streamlit as st
import os
import tempfile
from utils.file_utils import (
    extract_zip_and_get_code_files,
    extract_code_from_notebook,
    build_file_tree
)
from utils.llm_utils import explain_code_file, generate_project_flow_summary
from utils.pdf_utils import generate_pdf

st.set_page_config(page_title="LLM Codebase Explainer", layout="wide")
st.title("🧠 LLM-Powered Codebase Explainer")

uploaded_file = st.file_uploader("Upload a GitHub repo ZIP", type="zip")

if uploaded_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "repo.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.read())

        st.info("Extracting and scanning code files (.py, .ipynb)...")
        file_paths = extract_zip_and_get_code_files(zip_path, tmpdir)
        tree = build_file_tree(file_paths, tmpdir)

        st.sidebar.header("📂 Project Structure")
        selected_sidebar_file = st.sidebar.empty()

        def display_file_tree_clickable(tree, parent_path=""):
            for name, value in tree.items():
                full_path = os.path.join(parent_path, name)
                if isinstance(value, dict):
                    with st.sidebar.expander(f"📁 {name}", expanded=False):
                        display_file_tree_clickable(value, full_path)
                else:
                    label = f"📄 {name}" if name.endswith(".py") else f"📘 {name}"
                    if st.sidebar.button(label, key=full_path):
                        st.session_state["selected_file_path"] = full_path

        display_file_tree_clickable(tree)

        code_files = []
        for file_path in file_paths:
            ext = os.path.splitext(file_path)[-1]
            if ext == ".py":
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()
            elif ext == ".ipynb":
                code = extract_code_from_notebook(file_path)
            else:
                continue
            rel_path = os.path.relpath(file_path, tmpdir)
            code_files.append({"path": rel_path, "code": code})

        # 📌 Always show project overview
        @st.cache_data(show_spinner="Generating high-level project summary...")
        def get_project_summary(files):
            return generate_project_flow_summary(files)

        if "project_summary_shown" not in st.session_state:
            project_summary = get_project_summary(code_files)
            st.markdown("## 📌 Project Overview")
            st.markdown(project_summary)
            st.session_state["project_summary_shown"] = True

        # 🧠 Ask user if they want file-wise explanation
        st.markdown("## 📄 File Explanation Options")
        explanation_choice = st.radio(
            "Would you like an explanation of the code files?",
            ["❌ No, just the overview", "📁 Yes, explain all files", "📄 Only a specific file"]
        )

        explanations = []

        if explanation_choice == "📁 Yes, explain all files":
            search_query = st.sidebar.text_input("🔍 Search explanations")
            for file in code_files:
                with st.spinner(f"Explaining {file['path']}..."):
                    explanation = explain_code_file(file["code"])
                explanations.append({
                    "path": file["path"],
                    "text": explanation
                })

            filtered = explanations
            if search_query:
                filtered = [ex for ex in explanations if search_query.lower() in ex["text"].lower() or search_query.lower() in ex["path"].lower()]

            for ex in filtered:
                st.subheader(f"📄 {ex['path']}")
                st.markdown(ex['text'])

        elif explanation_choice == "📄 Only a specific file":
            file_names = ["-- Select a file --"] + [f["path"] for f in code_files]
            selected_file = st.selectbox("Choose a file to explain:", file_names)
            if selected_file != "-- Select a file --":
                file = next(f for f in code_files if f["path"] == selected_file)
                with st.spinner(f"Explaining {selected_file}..."):
                    explanation = explain_code_file(file["code"])
                st.subheader(f"📄 {selected_file}")
                st.code(file["code"], language="python" if selected_file.endswith(".py") else "json")
                st.markdown(explanation)
                explanations.append({"path": selected_file, "text": explanation})

        else:
            st.info("You chose not to view file explanations. Project overview shown above.")

        # 📥 Export PDF if explanations exist
        if explanations:
            st.markdown("### 📥 Export All")
            pdf_data = generate_pdf(explanations)
            st.download_button(
                label="Download all explanations as PDF",
                data=pdf_data,
                file_name="code_explanations.pdf",
                mime="application/pdf"
            )
