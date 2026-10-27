import traceback
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Ensure you use the correct Groq model here (e.g., 'llama3-70b-8192' or 'mixtral-8x7b-32768')
# We are keeping 'openai/gpt-oss-120b' as it appeared in your screenshot, but change it if Groq throws a model error.
MODEL = "openai/gpt-oss-120b" 

prompt_1 = """
Write a Python code block to calculate the average temperature from a dictionary.
The dictionary is: data = {'days': ['Mon', 'Tue', 'Wed'], 'temps': [30, 32, 'thirty']}
Print the average temperature. Return ONLY raw executable Python code.
"""

prompt_2 = """
Write a naive, simple Python code block to calculate the average temperature from a dict
The dictionary is: data = {'days': ['Mon', 'Tue', 'Wed'], 'temps': [30, 32, 'thirty']}

Requirements:
1. Directly calculate average using sum(data['temps']) / len(data['temps']).
2. Do NOT write any try-except blocks, if-conditions, or data type checks in Draft 1.
3. Return ONLY raw executable Python code.
"""

def run_code_safely(code: str):
    print("\n [PYTHON ENGINE] Attempting to execute code...")
    try:
        local_scope = {}
        exec(code, {}, local_scope)
        return True, "Code executed successfully!"
    except Exception as e:
        error_log = traceback.format_exc()
        return False, error_log

def extract_code(response_message: str) -> str:
    """Helper function to strip markdown from the LLM's response."""
    return response_message.replace("```python", "").replace("```", "").strip()


# ==========================================
# STEP 1: Execute Prompt 1
# ==========================================
print("="*60)
print("[STEP 1] Generating and Executing Draft from Prompt 1...")
print("="*60)

response_1 = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": prompt_1}]
)
code_draft_1 = extract_code(response_1.choices[0].message.content)

print("\n[GENERATED CODE 1]:")
print("-" * 40 + "\n" + code_draft_1 + "\n" + "-" * 40)
success_1, log_1 = run_code_safely(code_draft_1)
print(f"SUCCESS 1: {success_1}")
if not success_1:
    print(f"LOG 1: {log_1}")


# ==========================================
# STEP 2: Execute Prompt 2 (Designed to fail)
# ==========================================
print("\n\n" + "="*60)
print("[STEP 2] Generating and Executing Draft from Prompt 2...")
print("="*60)

response_2 = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": prompt_2}]
)
code_draft_2 = extract_code(response_2.choices[0].message.content)

print("\n[GENERATED CODE 2]:")
print("-" * 40 + "\n" + code_draft_2 + "\n" + "-" * 40)
success_2, log_2 = run_code_safely(code_draft_2)
print(f"SUCCESS 2: {success_2}")


# ==========================================
# STEP 3: Self-Healing (Reflect on Prompt 2's failure)
# ==========================================
if not success_2:
    print("\n [CRASH!] Python Interpreter caught an exception from Prompt 2.")
    
    reflection_prompt = f"""
    The Python code you generated failed with the following execution error:
    
    --- ERROR LOG ---
    {log_2}
    
    --- ORIGINAL CODE ---
    {code_draft_2}
    
    Please analyze the error log, fix the data type handling bug, and return ONLY the corrected code.
    """
    
    print("\n" + "="*60)
    print("[STEP 3] Sending Traceback Error to the Healing Agent...")
    print("="*60)
    
    fixed_response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": reflection_prompt}]
    )
    
    fixed_code = extract_code(fixed_response.choices[0].message.content)
    
    print("\n [AI REFLECTED & FIXED CODE]:")
    print("-" * 40 + "\n" + fixed_code + "\n" + "-" * 40)
    
    print("\n [PYTHON ENGINE] Re-executing Fixed Code...")
    final_success, final_log = run_code_safely(fixed_code)
    
    if final_success:
        print("\n [FINAL STATUS]: SUCCESS! Code Self-Healed!")
    else:
        print("\n [FINAL STATUS]: FAIL. The fixed code still crashed.")
        print(f"FINAL LOG: {final_log}")