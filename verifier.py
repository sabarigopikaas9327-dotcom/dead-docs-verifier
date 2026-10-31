import ast
import glob
import json
import os
import re
import sys
from openai import OpenAI

def extract_signatures(directory="src"):
    signatures = []
    for filepath in glob.glob(f"{directory}/**/*.py", recursive=True):
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                args = [arg.arg for arg in node.args.args]
                signatures.append({
                    "file": filepath,
                    "function": node.name,
                    "parameters": args
                })
    return signatures

def extract_readme_snippets(readme_path="README.md"):
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = r"```python\n(.*?)```"
    return re.findall(pattern, content, re.DOTALL)

def verify_docs_with_ai(signatures, snippets):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set.")
        sys.exit(1)

    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=token,
    )

    prompt = f"""
    Compare the live Python function signatures against the README code snippets.
    Identify any function calls in the README that use wrong parameter names or missing required arguments.
    
    Live Code Signatures:
    {json.dumps(signatures, indent=2)}
    
    README Code Snippets:
    {json.dumps(snippets, indent=2)}
    
    Respond ONLY in valid JSON with this exact schema:
    {{"has_errors": true, "issues": [{{"function": "name", "problem": "description", "fixed_snippet": "corrected code"}}]}}
    """

    response = client.chat.completions.create(
        model="Meta-Llama-3.1-8B-Instruct",
        messages=[
            {"role": "system", "content": "You are a strict code documentation verifier. Output raw JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

if __name__ == "__main__":
    sigs = extract_signatures()
    snips = extract_readme_snippets()
    result = verify_docs_with_ai(sigs, snips)
    
    with open("verification_report.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        
    print(json.dumps(result, indent=2))
    if result.get("has_errors"):
        sys.exit(1)
