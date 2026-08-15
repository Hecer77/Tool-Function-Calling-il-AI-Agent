#Məqsəd: max_iterations mexanizmi ilə sonsuz dövrlərin və resurs israfının qarşısını almaq.
import json
from openai import OpenAI

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key="SİZİN_GROQ_APİ_AÇARINIZ",
)


def get_weather(city: str):
  return json.dumps({"temperature": "26°C"})


tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Hava proqnozu əldə edir.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
}]

messages = [{"role": "user", "content": "Bakıda hava necədir?"}]

# --- CHECKPOINT 5: Sonsuz dövrə qarşı qoruma (Max Iterations) ---
max_iterations = 5
current_iteration = 0

while current_iteration < max_iterations:
  current_iteration += 1
  print(f"[LOG] Addım: {current_iteration}")

  response = client.chat.completions.create(
      model="llama-3.3-70b-versatile",
      messages=messages,  # type: ignore
      tools=tools,# type: ignore
      tool_choice="auto",
  )
  response_message = response.choices[0].message

  if not response_message.tool_calls:
    print(f"\n[YEKUN CAVAB]:\n{response_message.content}")
    break

  messages.append({
      "role": "assistant",
      "content": response_message.content,
      "tool_calls": response_message.tool_calls,
  })  # type: ignore

  for tool_call in response_message.tool_calls:
    func_name = tool_call.function.name # pyright: ignore[reportAttributeAccessIssue]
    args = json.loads(tool_call.function.arguments) # pyright: ignore[reportAttributeAccessIssue]
    tool_result = get_weather(**args)

    messages.append({
        "role": "tool",
        "name": func_name,
        "content": tool_result,
        "tool_call_id": tool_call.id,
    })  # type: ignore
else:
  print("[XƏBƏRDARLIQ] Maksimum təkrar limitinə çatıldı.")