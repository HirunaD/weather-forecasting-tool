import traceback
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

prompt = """
Write a Python code block to calculate the average temperature from a dictionary.
The dictionary is: data = {'days': ['Mon', 'Tue', 'Wed'], 'temps': [30, 32, 'thirty']}
Print the average temperature. Return ONLY raw executable Python code.
"""

prompt_2 = """
Write a naive, simple Python code block to calculate the average temperature from a dict
The dictionary is: data = {'days': ['Mon', 'Tue', 'Wed'], 'temps': [30, 32, 'thirty']}

Requirements:
1. Directly calculate average using sum(data['temps']) / len(data['temps']).
2. Do NOT write any try-except blocks, if-conditions, or data type checks in Draft 1. Wr
3. Return ONLY raw executable Python code.
"""

print("[STEP 1] Prompting LLM to generate Code Draft 1...")

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": prompt}]
)

# PRINT THE ACTUAL LLM RESPONSE
print("\n[STEP 1 - LLM RESPONSE]")
print(response.choices[0].message)

code_draft = response.choices[0].message.content.replace("```python", "").replace("```", "").strip()

print("\n [GENERATED CODE DRAFT 1]:")
print("-" * 40)
print(code_draft)
print("-" * 40)

def run_code_safely(code: str):
    print("\n [PYTHON ENGINE] Attempting to execute code...")
    try:
        local_scope = {}
        exec(code, {}, local_scope)
        return True, "Code executed successfully!"
    except Exception as e:
        error_log = traceback.format_exc()
        return False, error_log

success, log = run_code_safely(code_draft)

print(f"SUCCESS: {success}")
print(f"LOG: {log}")

if not success:
    print("\n [CRASH!] Python Interpreter caught an exception.")
    
    reflection_prompt = f"""
    The Python code you generated failed with the following execution error:
    
    --- ERROR LOG ---
    {log}
    
    --- ORIGINAL CODE ---
    {code_draft}
    
    Please analyze the error log, fix the data type handling bug, and return ONLY the corrected code.
    """
    
    print("\n" + "="*60)
    print("[PAUSED] LOOK AT THE REFLECTION PROMPT!")
    print("We are NOT telling the AI 'Try again'. We are sending the EXACT Traceback:")
    print("="*60)
    
    # The script stops here during your video so you can explain!
    input("\n Press Enter to send this Traceback Error to the LLM for Auto-Fix...")
    
    fixed_response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": reflection_prompt}]
    )
    
    # PRINT THE ACTUAL LLM RESPONSE
    print("\n[CRASH! - LLM RESPONSE]")
    print(fixed_response.choices[0].message)
    
    fixed_code = fixed_response.choices[0].message.content.replace("```python", "").replace("```", "").strip()
    
    print("\n [AI REFLECTED & FIXED CODE]:")
    print("-" * 40)
    print(fixed_code)
    print("-" * 40)
    
    print("\n [PYTHON ENGINE] Re-executing Fixed Code...")
    final_success, final_log = run_code_safely(fixed_code)
    
    print("\n [FINAL STATUS]:", "SUCCESS! Code Self-Healed!" if final_success else "FAIL")