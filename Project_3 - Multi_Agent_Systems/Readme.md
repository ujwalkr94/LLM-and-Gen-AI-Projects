This notebook builds a hierarchical multi-agent workflow using `LangGraph` + `LangChain` + `OpenAI`.

## What It Does

- Creates a **research team**:
- `search` agent uses Tavily web search.
- `web_scrapper` agent loads webpage content with `WebBaseLoader`.
- Supervisor decides which research worker runs next.

- Creates a **writing team**:
- `note_taker` creates outlines.
- `doc_writer` writes/edits text files.
- `chart_generator` can generate charts using a Python REPL tool.
- Supervisor decides which writing worker runs next.

- Creates a **top-level supervisor**:
- Routes user requests between `research_team` and `writing_team`.
- Stops when work is complete (`FINISH`).

## How To Run

1. Open `code_v1.ipynb`.
2. Run cells top-to-bottom.
3. Execute sample prompts in the notebook to:
4. Test research graph (`weather in Porto` example).
5. Test writing graph (`poem about dogs` example).
6. Test the full super graph (`gold price 2025` report example).

## Notes

- The notebook visualizes the final graph using Mermaid (`draw_mermaid_png()`).
- Recursion limits are set per stream call (`20`, `30`, `1000` in examples).
- If APIs fail, verify keys and package versions first.
