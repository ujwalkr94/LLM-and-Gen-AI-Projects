#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from crewai import Agent, Task, Crew
from tqdm import tqdm


# In[2]:


load_dotenv() 


# In[3]:


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
GEMINI = os.getenv("GEMINI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def validate_environment():
    missing = []
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not GEMINI:
        missing.append("GEMINI")
    if not SERPER_API_KEY:
        missing.append("SERPER_API_KEY")

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


# In[4]:


# llm = ChatOpenAI( 
#     model="gpt-4o",
#     temperature=0,
#     max_tokens=500,
#     timeout=None,
#     max_retries=10,
# )


# In[5]:


# Initialize LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=500,
    timeout=None,
    max_retries=12,
)

crew_llm = crewai.LLM(
    model="gemini/gemini-1.5-flash",
    api_key=GEMINI,
    max_tokens=500,
    temperature=0.7
)


# In[6]:


crew_llm_search = crewai.LLM(
    model="gemini/gemini-1.5-flash",
    api_key=GEMINI,
    max_tokens=500,
    temperature=0.7
)

crew_llm_scraper = crewai.LLM(
    model="gemini/gemini-1.5-flash",
    api_key=GEMINI,
    max_tokens=500,
    temperature=0.7
)


# In[7]:


def check_local_knowledge(query, context):
    """Router function to determine if we can answer from local knowledge."""
    prompt = """Role: Question-Answering Assistant
Task: Determine whether the system can answer the user's question based on the provided text.
Instructions:
    - Analyze the text and identify if it contains the necessary information to answer the user's question.
    - Provide only one final token that indicates your decision.
Output Format:
    - Yes
    - No
Input:
    User Question: {query}
    Text: {text}
    Final Answer (Yes/No):"""

    formatted_prompt = prompt.format(text=context, query=query)
    response = llm.invoke(formatted_prompt)
    normalized = response.content.strip().lower().replace("answer:", "").strip(" .!\n\t")
    return normalized.startswith("yes")


# In[8]:


def setup_web_scraping_agent():
    """Setup web search + scraping crew with explicit task chaining."""
    search_tool = SerperDevTool()
    scrape_website = ScrapeWebsiteTool()

    web_search_agent = Agent(
        role="Expert Web Search Agent",
        goal="Identify a high-quality source URL for the user topic",
        backstory="Finds reliable and relevant sources quickly",
        allow_delegation=False,
        verbose=False,
        llm=crew_llm_search,
    )

    web_scraper_agent = Agent(
        role="Expert Web Scraper Agent",
        goal="Extract and summarize key information from a provided URL",
        backstory="Specialized in extracting and condensing web content",
        allow_delegation=False,
        verbose=False,
        llm=crew_llm_scraper,
    )

    search_task = Task(
        description=(
            "Find one best URL for the topic: '{topic}'. "
            "Return ONLY a URL in plain text."
        ),
        expected_output="Single URL only, no extra text.",
        tools=[search_tool],
        agent=web_search_agent,
    )

    scraping_task = Task(
        description=(
            "Use the URL from the previous task to scrape and summarize key facts for topic: '{topic}'. "
            "If scraping fails, explain the failure briefly."
        ),
        expected_output="Concise factual summary grounded in scraped content.",
        tools=[scrape_website],
        agent=web_scraper_agent,
        context=[search_task],
    )

    crew = Crew(
        agents=[web_search_agent, web_scraper_agent],
        tasks=[search_task, scraping_task],
        verbose=0,
        memory=False,
    )
    return crew


def get_web_content(query):
    """Get content from web scraping."""
    crew = setup_web_scraping_agent()
    result = crew.kickoff(inputs={"topic": query})
    return getattr(result, "raw", str(result))


# In[18]:


def setup_vector_db_multi(pdf_paths):
    """Setup vector DB with progress tracking for loading, splitting, embedding."""
    all_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)

    print("Loading and splitting PDFs...")
    for pdf_path in tqdm(pdf_paths, desc="Processing PDFs"):
        if not Path(pdf_path).exists():
            print(f"[WARN] Skipping missing file: {pdf_path}")
            continue

        loader = PyPDFLoader(str(pdf_path))
        documents = loader.load()
        chunks = text_splitter.split_documents(documents)
        all_chunks.extend(chunks)

    if not all_chunks:
        raise ValueError("No documents were loaded. Check your PDF paths.")

    print(f"Total chunks: {len(all_chunks)}")
    print("Generating embeddings...")

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    texts = [doc.page_content for doc in all_chunks]

    embedded_vectors = embeddings.embed_documents(texts)

    print("Building FAISS vector DB...")
    text_embedding_pairs = list(zip(texts, embedded_vectors))
    vector_db = FAISS.from_embeddings(text_embedding_pairs, embeddings)

    print("Vector database setup complete.")
    return vector_db


def get_local_content(vector_db, query, k=5):
    """Get top-k relevant content from vector database."""
    effective_query = query if query.strip() else "agentic ai"
    docs = vector_db.similarity_search(effective_query, k=k)
    return "\n\n".join(doc.page_content for doc in docs)


# In[19]:


def generate_final_answer(context, query):
    """Generate final answer using LLM."""
    messages = [
        (
            "system",
            "You are a helpful assistant. Use only the provided context. If context is insufficient, say so clearly.",
        ),
        ("system", f"Context:\n{context}"),
        ("human", query),
    ]
    response = llm.invoke(messages)
    return response.content


def process_query(query, vector_db):
    """Process query with local-first routing and web fallback."""
    print(f"Processing query: {query}")

    routing_context = get_local_content(vector_db, query, k=5)
    can_answer_locally = check_local_knowledge(query, routing_context)
    print(f"Can answer locally: {can_answer_locally}")

    if can_answer_locally:
        context = routing_context
        print("Retrieved context from local documents")
    else:
        context = get_web_content(query)
        print("Retrieved context from web scraping")

    return generate_final_answer(context, query)


# In[22]:


def main():
    validate_environment()

    base = Path.cwd()
    pdf_paths = [
        base / "genai-principles.pdf",
        base / "Agentic_ai.pdf",
        base / "rag.pdf",
    ]

    print("Setting up vector database...")
    vector_db = setup_vector_db_multi(pdf_paths)

    query = "What is Agentic AI?"
    result = process_query(query, vector_db)

    print("\nFinal Answer:")
    print(result)


# In[23]:


if __name__ == "__main__":
    main()


# In[ ]:





# In[ ]:




