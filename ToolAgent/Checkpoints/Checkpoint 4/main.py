#Məqsəd: Çoxaddımlı while dövrü vasitəsilə zəncirvari alət çağırışlarını (məsələn: əvvəl havanı tapmaq, sonra onu Fahrenheit-ə çevirmək) dəstəkləmək.
import json
from openai import OpenAI


def get_weather(city: str):
  return json.dumps({"city": city, "temperature_c": 26})


def convert_temperature(value: float, to_unit: str):
  if to_unit == "F":
    return json.dumps({"converted_temp": f"{(value * 9/5) + 32}°F"})
  return json.dumps({"converted_temp": f"{value}°C"})


available_tools = {
    "get_weather": get_weather,
    "convert_temperature": convert_temperature,
}

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key="SİZİN_GROQ_APİ_AÇARINIZ",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Şəhərin hava dərəcəsini Celsius ilə qaytarır.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_temperature",
            "description": "Temperaturu vahidlər arası çevirir.",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "number"},
                    "to_unit": {"type": "string", "enum": ["F", "C"]},
                },
                "required": ["value", "to_unit"],
            },
        },
    },
]

messages = [{
    "role": "user",
    "content": "Bakıda hava necədir? Həmin temperaturu Fahrenheit-ə çevir.",
}]

# --- CHECKPOINT 4: Çoxaddımlzi while dövrü (Multi-step Agent Loop) ---
while True:
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
    print(f"[TOOL CALL] {func_name} çağrıldı, arqumentlər: {args}")

    tool_result = available_tools[func_name](**args)
    print(f"[TOOL RESULT] {tool_result}")

    messages.append({
        "role": "tool",
        "name": func_name,
        "content": tool_result,
        "tool_call_id": tool_call.id,
    })  # type: ignore