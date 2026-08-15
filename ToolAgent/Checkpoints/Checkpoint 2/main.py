#---Məqsəd: İstifadəçi sorğusuna əsasən tool_choice="auto" vasitəsilə LLM-in düzgün aləti avtomatik seçməsini təmin etmək.
import json
from openai import OpenAI

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key="SİZİN_GROQ_APİ_AÇARINIZ",
)

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Verilmiş şəhər üzrə cari hava proqnozunu əldə edir.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Şəhərin adı",
                }
            },
            "required": ["city"],
        },
    },
}]

messages = [{"role": "user", "content": "Bakıda hava necədir?"}]

# --- CHECKPOINT 2: tool_choice="auto" ilə modelin alət seçməsi ---
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=messages,  # type: ignore
    tools=tools,# type: ignore
    tool_choice="auto",
)

response_message = response.choices[0].message

print("Checkpoint 2: Modelin seçdiyi alət çağırışı (Tool Call):")
print(response_message.tool_calls)