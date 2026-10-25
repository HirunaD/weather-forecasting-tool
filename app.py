import requests
import json
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_weather_forecast(city: str, days: int = 3) -> str:
    """Fetches the live weather forecast for a specified city.
    
    Args:
        city: The name of the city (e.g., 'Colombo', 'Tokyo', 'London').
        days: Number of forecast days to retrieve (default is 3).
    """
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo_res = requests.get(geo_url).json()

    if not geo_res.get("results"):
        return f"Could not find coordinates for {city}."
        
    lat = geo_res["results"][0]["latitude"]
    lon = geo_res["results"][0]["longitude"]
    
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max&timezone=auto&forecast_days={days}"
    weather_res = requests.get(weather_url).json()
    
    daily = weather_res["daily"]
    return f"Weather forecast for {city} over next {days} days: Max Temps: {daily['temperature_2m_max']}"


messages = [{"role": "user", "content": "Will it rain in Colombo over the next 3 days?"}]

print("[STEP 1] Sending User Prompt & Tools Schema to LLM...")

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=messages,
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_weather_forecast",
                "description": "Fetches the live weather forecast for a specified city.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "The name of the city"},
                        "days": {"type": "integer", "description": "Number of forecast days"}
                    },
                    "required": ["city"]
                }
            }
        }
    ]
)

# PRINT THE ACTUAL LLM RESPONSE
print("\n[LLM RESPONSE]")
print(response.choices[0].message)

tool_call = response.choices[0].message.tool_calls[0]

print("\n" + "="*60)
print("[PAUSED] LOOK AT THE LLM DECISION!")
print("The LLM decided NOT to generate a text answer. Instead, it requested a Tool.")
print(f"Tool Name Requested : {tool_call.function.name}")
print(f"Generated Arguments : {tool_call.function.arguments}")
print("="*60)

# The script stops here during your video so you can explain!
input("\n Press Enter to execute this Python Function in our backend...")

if tool_call.function.name == "get_weather_forecast":
    args = json.loads(tool_call.function.arguments)
    print("\n [BACKEND] Executing local Python function...")
    result = get_weather_forecast(city=args.get("city"), days=args.get("days", 3))
    print(f"[BACKEND RESULT]: {result}")
    
    messages.append(response.choices[0].message)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result
    })
    
    print("[STEP 2] Sending the Real Data back to the LLM for the final answer...")
    
    final_response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages
    )

    print("\n[FINAL AGENT RESPONSE]:")
    print(final_response.choices[0].message.content)