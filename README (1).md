# 📚 Study Buddy

A simple Generative AI app. Paste your study notes, then:
- **Ask** questions answered only from your notes (grounded answers)
- **Summarize** notes into revision bullet points
- **Quiz** yourself with 5 AI-generated multiple-choice questions

Built with Python, Streamlit, and the Google Gemini API (free tier).

## Gen AI concepts used
- **System prompts**: instructions that control the model's behaviour
- **Grounding**: answers restricted to the provided notes to reduce hallucination
- **Structured output**: quiz requested as JSON so the app can display and score it

## Run locally
```bash
pip install -r requirements.txt
```
Get a free key at https://aistudio.google.com (Get API key), then set it:

- Windows PowerShell: `setx GEMINI_API_KEY "your-key"` (then reopen the terminal)
- Mac/Linux: `export GEMINI_API_KEY="your-key"`

```bash
streamlit run app.py
```

## Deploy for free (public link)
1. Push this folder to a GitHub repository (do NOT commit your API key).
2. Go to https://share.streamlit.io and click **New app**.
3. Select your repo, branch, and `app.py`.
4. In **Advanced settings → Secrets**, add:
   ```
   GEMINI_API_KEY = "your-key"
   ```
5. Click **Deploy** to get a public link.

## Limitations
- Free tier has rate limits; do not paste private notes
- Notes must fit within the model's context window
- AI can make mistakes, so verify important facts
