#Məqsəd: Bütün yuxarıdakı məntiqləri özündə birləşdirən, real qlobal hava API (wttr.in) və Streamlit veb interfeysi olan yekun tətbiq.
import json
from typing import Any
import httpx
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageToolCall
import streamlit as st

st.set_page_config(page_title="Global AI Tool Agent", page_icon="🌍")
st.title("🌍 Qlobal AI Tool Agent (Checkpoint 6)")
st.write(
    "Streamlit və Llama 3.3 əsasında qurulmuş tam funksional AI Tool Agent."
)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key="SİZİN_GROQ_APİ_AÇARINIZ",
)


def get_weather(city: str):
  try:
    url = f"https://wttr.in/{city}?format=j1"
    response = httpx.get(url, timeout=10.0)
    if response.status_code == 200:
      data = response.json()
      current = data["current_condition"][0]
      return json.dumps({
          "city": city,
          "temperature_c": f"{current['temp_C']}°C",
          "condition": current["weatherDesc"][0]["value"],
          "humidity": f"{current['humidity']}%",
      })
    return json.dumps({"error": "Şəhər tapılmadı."})
  except Exception:
    return json.dumps({"error": "Hava məlumatını əldə etmək mümkün olmadı."})


def convert_temperature(value: float, to_unit: str):
  if to_unit == "F":
    return json.dumps({"converted_temp": f"{(value * 9/5) + 32}°F"})
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
            "description": "Dünyanın istənilən şəhəri üzrə cari hava proqnozu.",
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
            "description": "Temperaturu Celsius və Fahrenheit arasında çevirir.",
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

if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "system",
      "content": (
          "Sən peşəkar AI köməkçisən. İstifadəçi sorğularında mövcud"
          " alətlərdən istifadə et və hər zaman səliqəli cavab ver."
      ),
  }]  # type: ignore

for message in st.session_state.messages:
  if message["role"] not in ["tool", "system"]:
    with st.chat_message(message["role"]):
      if message.get("content"):
        st.markdown(message["content"])

if prompt := st.chat_input("Məsələn: London-da hava necədir?"):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  with st.chat_message("assistant"):
    with st.spinner("Agent işləyir..."):
      max_iterations = 5
      current_iteration = 0
      final_answer = ""

      while current_iteration < max_iterations:
        current_iteration += 1
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,  # type: ignore
            tools=tools,# type: ignore
            tool_choice="auto",
        )
        response_message = response.choices[0].message

        if not response_message.tool_calls:
          final_answer = response_message.content or ""
          st.session_state.messages.append(
              {"role": "assistant", "content": final_answer}
          )  # type: ignore
          break

        st.session_state.messages.append({
            "role": "assistant",
            "content": response_message.content,
            "tool_calls": response_message.tool_calls,
        })  # type: ignore

        for tool_call in response_message.tool_calls:
          if isinstance(tool_call, ChatCompletionMessageToolCall):
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            tool_result = (
                available_tools[func_name](**args)
                if func_name in available_tools
                else json.dumps({"error": "Alət tapılmadı"})
            )

            st.session_state.messages.append({
                "role": "tool",
                "name": func_name,
                "content": tool_result,
                "tool_call_id": tool_call.id,
            })  # type: ignore

      st.markdown(final_answer)