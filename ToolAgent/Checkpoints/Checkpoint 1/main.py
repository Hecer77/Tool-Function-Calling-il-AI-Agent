import json

# --- CHECKPOINT 1: Alətlərin (Tools) strukturu və funksiyaların tərifi ---
#----Məqsəd: Modelə funksiyaların adını, təsvirini və JSON Schema parametrlərini (strukturunu) tanıtmaq.


def get_weather(city: str):
  """Sadə hava məlumatı qaytaran funksiya."""
  weather_data = {
      "Bakı": {"temperature": 26, "condition": "Günəşli"},
      "Gəncə": {"temperature": 22, "condition": "Buludlu"},
  }
  return json.dumps(weather_data.get(city, {"error": "Şəhər tapılmadı"}))


# OpenAI/Groq API-yə ötürüləcək JSON Schema formatında alət tərifləri
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
    }
]

print("Checkpoint 1: Funksiyalar və JSON Schema uğurla tərif olundu.")
print(json.dumps(tools, indent=2, ensure_ascii=False))