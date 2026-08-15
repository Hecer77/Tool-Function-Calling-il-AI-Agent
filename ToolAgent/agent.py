import json
from typing import Any
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageToolCall

# Groq API müştərisi (Tamamilə pulsuz və OpenAI SDK ilə uyğundur)
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key="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",
)


# --- CHECKPOINT 1: Aydın sxemli funksiyaların tərifi ---
def get_weather(city: str):
  weather_data = {
      "Bakı": {"temperature": 26, "condition": "Günəşli"},
      "Gəncə": {"temperature": 22, "condition": "Buludlu"},
  }
  return json.dumps(weather_data.get(city, {"error": "Şəhər tapılmadı"}))


def convert_temperature(value: float, to_unit: str):
  if to_unit == "F":
    result = (value * 9 / 5) + 32
    return json.dumps({"converted_temp": f"{result}°F"})
  return json.dumps({"converted_temp": f"{value}°C"})


available_tools = {
    "get_weather": get_weather,
    "convert_temperature": convert_temperature,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Verilmiş şəhər üzrə cari hava proqnozunu əldə edir.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Şəhərin adı, məsələn: Bakı",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_temperature",
            "description": "Temperaturu Celsius və Fahrenheit arasında çevirir.",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "number",
                        "description": "Çevriləcək temperatur dəyəri",
                    },
                    "to_unit": {
                        "type": "string",
                        "enum": ["F", "C"],
                        "description": "Hansı vahidə çevriləcək ('F' və ya 'C')",
                    },
                },
                "required": ["value", "to_unit"],
            },
        },
    },
]

# İstifadəçi sorğusu (Zəncirvari tool tələb edən nümunə)
messages: list[dict[str, Any]] = [{
    "role": "user",
    "content": "Bakıda hava necədir? Həmin temperaturu Fahrenheit-ə çevir.",
}]

# --- CHECKPOINT 5: Sonsuz dövrə qarşı qoruma (Max Iterations) ---
max_iterations = 5
current_iteration = 0

print("[LOG] Agent işə düşdü...\n")

while current_iteration < max_iterations:
  current_iteration += 1

  # --- CHECKPOINT 2: LLM-in sorğuya əsasən düzgün tool seçimi ---
  response = client.chat.completions.create(
      model="llama-3.3-70b-versatile",
      messages=messages,  # type: ignore
      tools=tools,  # type: ignore
      tool_choice="auto",
  )

  response_message = response.choices[0].message

  # --- CHECKPOINT 6: Reasoning və tool izinin aydın loglanması ---
  print(f"[LOG] Addım {current_iteration}: Model cavabı alındı.")

  if not response_message.tool_calls:
    messages.append({"role": "assistant", "content": response_message.content})
    print(f"\n[YEKUN CAVAB]:\n{response_message.content}")
    break

  # Assistentin mesajını tarixçəyə əlavə edirik
  messages.append({
      "role": "assistant",
      "content": response_message.content,
      "tool_calls": response_message.tool_calls,
  }) #type: ignore

  # --- CHECKPOINT 3 & 4: Tool icrası, nəticənin modelə qayıtması və zəncirvari dövr ---
  for tool_call in response_message.tool_calls:
    if isinstance(tool_call, ChatCompletionMessageToolCall):
      func_name = tool_call.function.name
      args = json.loads(tool_call.function.arguments)

      print(f"[TOOL CALL] Çağrılan alət: {func_name} | Arqumentlər: {args}")

      if func_name in available_tools:
        tool_function = available_tools[func_name]
        tool_result = tool_function(**args)
      else:
        tool_result = json.dumps({"error": "Alət tapılmadı"})

      print(f"[TOOL RESULT] Alətin qaytardığı nəticə: {tool_result}")

      # Nəticəni modelə 'tool' rolu ilə geri göndəririk
      messages.append({
          "role": "tool",
          "name": func_name,
          "content": tool_result,
          "tool_call_id": tool_call.id,
      })
else:
  print("[XƏBƏRDARLIQ] Maksimum təkrar limitinə çatıldı (Sonsuz dövr qorunması).")