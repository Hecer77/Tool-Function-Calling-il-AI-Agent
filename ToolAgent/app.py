import json
from typing import Any
import httpx
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageToolCall
import streamlit as st
import os
from dotenv import load_dotenv

# .env faylındakı gizli açarı yükləyirik
load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),  # <--- Artıq gizli oxunur
)

# Saytın səhifə başlığı
st.set_page_config(page_title="Global AI Tool Agent", page_icon="🌍")
st.title("🌍 Qlobal AI Tool Agent (Bütün Dünya Üzrə)")
st.write(
    "Bu agent istənilən dünya şəhərinin havasını real vaxtda yoxlaya və"
    " temperaturu çevirə bilir."
)

# Groq API müştərisi
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)


# --- Qlobal Hava Aləti (wttr.in vasitəsilə) ---
def get_weather(city: str):
  try:
    url = f"https://wttr.in/{city}?format=j1"
    response = httpx.get(url, timeout=10.0)

    if response.status_code == 200:
      data = response.json()
      current = data["current_condition"][0]
      temp_c = current["temp_C"]
      desc = current["weatherDesc"][0]["value"]
      humidity = current["humidity"]
      wind_kmph = current["windspeedKmph"]

      return json.dumps({
          "city": city,
          "temperature_c": f"{temp_c}°C",
          "condition": desc,
          "humidity": f"{humidity}%",
          "wind": f"{wind_kmph} km/s",
      })
    else:
      return json.dumps(
          {"error": "Şəhər üzrə hava məlumatı tapılmadı və ya xəta baş verdi."}
      )
  except Exception as e:
    return json.dumps({"error": f"Sorğu zamanı xəta: {str(e)}"})


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
            "description": (
                "Dünyanın istənilən şəhəri və ya ölkəsi üzrə cari hava"
                " proqnozunu internetdən əldə edir."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Şəhərin adı, məsələn: London, Baku",
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

# Söhbət tarixçəsini Streamlit state-də saxlayırıq
# Söhbət tarixçəsini Streamlit state-də saxlayırıq
if "messages" not in st.session_state:
  st.session_state.messages = [
      {
          "role": "system",
          "content": (
              "Sən yüksək səviyyəli, peşəkar və dostcanlı AI Köməkçisən."
              " İstifadəçinin suallarını diqqətlə təhlil et və ehtiyac"
              " yaranarsa, mövcud alətlərdən (get_weather,"
              " convert_temperature) dəqiq istifadə et. Cavablarını hər zaman"
              " səliqəli, strukturlaşdırılmış və aydın dildə təqdim et. Əgər"
              " hər hansı texniki problem və ya məlumat tapılmama durumu olarsa,"
              " bunu heç vaxt texniki xəta kimi deyil, sadə və insani dildə"
              " izah et."
          ),
      }
  ]  # type: ignore

# Əvvəlki mesajları ekranda göstəririk (system mesajını istifadəçiyə göstərmirik)
for message in st.session_state.messages:
  if message["role"] not in ["tool", "system"]:
    with st.chat_message(message["role"]):
      if message.get("content"):
        st.markdown(message["content"])

# İstifadəçidən input alırıq
if prompt := st.chat_input("Məsələn: London-da hava necədir?"):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  # Agentin cavab mərhələsi
  with st.chat_message("assistant"):
    with st.spinner("Agent dünyanı gəzir..."):
      max_iterations = 5
      current_iteration = 0
      final_answer = ""

      while current_iteration < max_iterations:
        current_iteration += 1

        # Xətanı qırmızı qutu ilə göstərmək əvəzinə, sadəcə sorğunu icra edirik
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,  # type: ignore
            tools=tools,  # type: ignore
            tool_choice="auto",
        )

        response_message = response.choices[0].message

        if not response_message.tool_calls:
          final_answer = response_message.content or ""
          st.session_state.messages.append(
              {"role": "assistant", "content": final_answer}
          )
          break

        st.session_state.messages.append({
            "role": "assistant",
            "content": response_message.content,
            "tool_calls": response_message.tool_calls,
        }) #type: ignore

        for tool_call in response_message.tool_calls:
          if isinstance(tool_call, ChatCompletionMessageToolCall):
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            if func_name in available_tools:
              tool_result = available_tools[func_name](**args)
            else:
              tool_result = json.dumps({"error": "Alət tapılmadı"})

            st.session_state.messages.append({
                "role": "tool",
                "name": func_name,
                "content": tool_result,
                "tool_call_id": tool_call.id,
            })

      st.markdown(final_answer)