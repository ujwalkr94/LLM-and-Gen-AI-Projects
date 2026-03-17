import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_code_explanation(code: str, prompt: str = None) -> str:
    system_prompt = prompt or "Explain what the following Python code does."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": code}
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

def explain_code_file(code: str) -> str:
    return get_code_explanation(code)

def generate_project_flow_summary(files: list[dict]) -> str:
    combined_code = ""
    for f in files:
        combined_code += f"# File: {f['path']}\n{f['code']}\n\n"

    prompt = (
        "You are a senior software architect. Carefully analyze the following multi-file Python codebase and provide a clear, structured, and detailed flow of execution. "
        "Your output should include:\n"
        "1. Which file is the entry point and why (look for __main__, script-like behavior, or CLI usage).\n"
        "2. The exact sequence of function or class calls across files.\n"
        "3. How different modules interact (i.e., file A imports file B and calls X function).\n"
        "4. What each file is responsible for (roles like utility, configuration, logic, orchestration).\n"
        "5. If it's a Streamlit or Flask app, describe the routing, UI flow, and user interaction path.\n"
        "6. Describe any dependency injection, shared data structures, or file-level orchestration.\n\n"
        "Be precise and explain like you’re onboarding a new developer to this project."
    )

    return get_code_explanation(combined_code[:12000], prompt=prompt)

