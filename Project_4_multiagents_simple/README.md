This notebook builds a simple supervisor-based multi-agent workflow to fetch UK GDP data and generate a line chart.

## What It Does

- Defines a `research_agent`:
- Uses Tavily search to find recent UK GDP values.
- Returns concise numeric data only.

- Defines a `code_agent`:
- Uses a Python REPL tool to execute plotting code.
- Generates a Matplotlib chart and saves it as `uk_gdp.png`.

- Defines a `supervisor`:
- Routes research tasks to `research_agent`.
- Routes chart/code tasks to `code_agent`.
- Ensures plotting requests are handled by code execution, not text-only responses.

## How To Run

1. Open `code_v2.ipynb`.
2. Run all cells in order.
3. Execute the final `app.invoke(...)` cell with a prompt like:
4. `"what's the GDP of UK in past three years, draw a line chart?"`

## Expected Output

- Final `result` object from the supervisor workflow.
- Generated chart file: `uk_gdp.png` (saved by the Python REPL tool).

## Notes

- The `python_repl_tool` is wrapped with exception handling and returns traceback text on failure.
- The model used is `gpt-4o`.
- If execution fails, verify API keys, package installation, and write permissions in the notebook working directory.
