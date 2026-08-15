# 🌍 Global AI Tool Agent (Llama 3.3 & Streamlit)

Bu layihə Llama 3.3 modeli və Groq API üzərindən işləyən, real vaxtda xarici alətlərdən (tool calling) istifadə edə bilən qabaqcıl **AI Agent** tətbiqidir. Layihənin əsas məqsədi LLM-lərin sadəcə mətn yazmaqla kifayətlənməyib, funksiyaları necə icra edə biləcəyini addım-addım (checkpoint-lərlə) nümayiş etdirməkdir.

---

## 🚀 Layihənin Xüsusiyyətləri

- **Tool Calling (Alət Çağırışı):** Modelin istifadəçi sorğusuna əsasən düzgün funksiyanı (`get_weather`, `convert_temperature`) avtomatik seçməsi.
- **Multi-Step Agent Loop:** Zəncirvari sorğuların dəstəklənməsi (məsələn: əvvəl havanı öyrənmək, sonra həmin dərəcəni Fahrenheit-ə çevirmək).
- **Max Iterations Qoruması:** Sonsuz dövrlərin və resurs israfının qarşısını alan iterasiya limiti.
- **Streamlit Veb İnterfeysi:** İstifadəçi dostu və interaktiv çat interfeysi.
- **Təhlükəsizlik:** API açarlarının `.env` vasitəsilə qorunması.

---

## 📂 Layihə Strukturu (Checkpoints)

Layihə öyrənmə mərhələlərinə uyğun olaraq aşağıdakı strukturda bölünüb:

- `checkpoint-1-definition/` - Alətlərin JSON Schema formatında tərifi.
- `checkpoint-2-tool-choice/` - `tool_choice="auto"` ilə modelin alət seçməsi.
- `checkpoint-3-execution/` - Alətin icra olunub nəticənin modelə qayıtması.
- `checkpoint-4-multistep/` - Çoxaddımlı (`while` dövrü) agent məntiqi.
- `checkpoint-5-max-iterations/` - Təhlükəsizlik limitləri.
- `checkpoint-6-streamlit-agent/` - Ən son tam funksional veb tətbiq (`app.py`).

---

## ⚙️ Quraşdırma və İşə Salma

1. **Repozitoriyanı klonlayın:**
   ```bash
   git clone [https://github.com/Hecer77/ai-tool-agent.git](https://github.com/Hecer77/ai-tool-agent.git)
   cd ai-tool-agent
   ```
