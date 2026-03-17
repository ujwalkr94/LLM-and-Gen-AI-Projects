# 🧠 LLM Codebase Explainer

A **Streamlit-based application** that uses LLMs (like OpenAI GPT) to automatically **analyze and explain the structure and logic** of complex codebases — including `.py` and `.ipynb` files — directly from a GitHub project ZIP.

---

## 🚀 Features

✅ Upload a zipped GitHub repository  
✅ Auto-extract and scan Python and Jupyter Notebook files  
✅ Get smart, human-readable explanations using LLMs  
✅ Visual file tree in sidebar  
✅ Full-text search over all code summaries  
✅ Export all explanations as a nicely formatted **PDF**

---

## 🔧 Project Structure

```
llm-code-explainer/
├── app.py                        # Streamlit frontend
├── requirements.txt              # Dependencies
├── .env                          # OpenAI API key (optional)
├── utils/
│   ├── file_utils.py             # File extraction, .ipynb handling
│   ├── llm_utils.py              # LLM prompt and response logic
│   ├── pdf_utils.py              # PDF generation
```

---

## 🛠️ Installation & Setup

1. **Clone the repo** or download the ZIP:

```bash
git clone https://github.com/your-username/llm-code-explainer.git
cd LLM_Powered_Code_Base_Expainer
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set your OpenAI API key:**

Create a `.env` file:

```
OPENAI_API_KEY=your_openai_key_here
```

Or set it directly in your terminal:

```bash
export OPENAI_API_KEY=your_openai_key_here
```

4. **Run the app:**

```bash
streamlit run app.py
```

---

## 🖼️ Example Use Case

- Upload a ZIP of any GitHub repo
- View the code hierarchy and file summaries
- Search across all explanations
- Download all results as a single PDF

---

## 📌 Future Enhancements

- 🧠 Dependency graph using `ast` + `graphviz`
- 📝 Export as Markdown
- 🔍 Filter files by type/tags
- 🌐 Optional integration with GitHub URL directly

---

## 📄 License

MIT License. Feel free to fork, contribute, or reuse.

---

## 👨‍💻 Author

Built by [Ujwal K R](https://www.linkedin.com/in/ujwal-k-r-758baba7/)
