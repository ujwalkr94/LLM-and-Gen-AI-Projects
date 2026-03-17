# Simple Multi-Agent Notebook (`multiaiagent_simple.ipynb`)

This notebook implements a basic 2-agent LangGraph workflow.

## What It Does

- Defines `AgentState` based on `MessagesState`.
- Adds two tools:
- `search_web(query)` using Tavily search.
- `write_summary(content)` for simple summary formatting.
- Creates two agents:
- `researcher_agent` (LLM + `search_web` tool binding).
- `writer_agent` (LLM-only final summarization).
- Adds a `tools` execution node (`ToolNode`) for pending tool calls.
- Builds and compiles a graph:
- `researcher -> (tools or writer) -> writer -> END`

## Requirements

```bash
pip install -U langchain langchain-openai langgraph langchain-community python-dotenv tavily-python
```

## Environment Setup

The notebook loads `.env` from:

`E:\Desktop\Data_Science\Gen_AI\Projects\.env`

Required keys:

```env
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

## How To Run

1. Open `multiaiagent_simple.ipynb`.
2. Run all cells in sequence.
3. Run the invocation cell:
4. `final_workflow.invoke({"messages": "Research about the usecase of agentic ai in business"})`
5. Read final output from:
6. `response["messages"][-1].content`

## Notes

- Model is initialized with `init_chat_model("openai:gpt-4o-mini")`.
- `write_summary` tool is defined, but the current writer flow mainly uses direct LLM response.
