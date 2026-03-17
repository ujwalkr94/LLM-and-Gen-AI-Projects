# Complex Multi-Agent Notebook (`multiaiagent_complex.ipynb`)

This notebook builds a supervisor-driven multi-agent workflow with three role-based agents.

## What It Does

- Defines `SupervisorState` with fields:
- `research_data`
- `analysis`
- `final_report`
- `next_agent`, `current_task`, `task_complete`
- Creates a supervisor decision chain (`create_supervisor_chain`) using a prompt that selects:
- `researcher`
- `analyst`
- `writer`
- or `DONE`
- Implements three agents:
- `researcher_agent` gathers background facts and data.
- `analyst_agent` produces insights/recommendations from research.
- `writer_agent` composes a structured executive report.
- Uses a router to cycle nodes until supervisor sets `next_agent = "end"`.
- Compiles and invokes the graph, then reads:
- `response["final_report"]`

## Requirements

```bash
pip install -U langchain langchain-openai langgraph langchain-community python-dotenv
```

## How To Run

1. Open `multiaiagent_complex.ipynb`.
2. Run all cells top-to-bottom.
3. Run the sample invocation (AI in healthcare task) or replace with your own query.
4. Check full state object in `response`.
5. Read final report from `response["final_report"]`.

## Notes

- Model is initialized with `init_chat_model("openai:gpt-4o-mini")`.
- The notebook prints supervisor progress and routing decisions while running.
- Some imported modules/tools (for example Tavily/ToolNode) are not central to the final execution path.
