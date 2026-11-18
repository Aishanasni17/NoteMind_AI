import json
import os

import streamlit as st
from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash"

st.set_page_config(page_title="Study Buddy", page_icon="📚")


# ---------- Setup: read API key from Streamlit secrets or environment ----------
def get_client():
    key = None
    try:
        key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        key = os.environ.get("GEMINI_API_KEY")
    if not key:
        st.error("API key not found. Add GEMINI_API_KEY to Streamlit secrets or your environment.")
        st.stop()
    return genai.Client(api_key=key)


client = get_client()

QA_SYSTEM = (
    "You are a helpful study assistant. Answer ONLY using the provided notes. "
    "If the answer is not in the notes, say clearly that the notes don't cover it. "
    "Keep answers short and simple."
)

SUMMARY_SYSTEM = (
    "You summarize study notes. Write 5 to 7 short bullet points a student can "
    "revise quickly. Use only information from the notes."
)

QUIZ_SYSTEM = (
    "You create quizzes from study notes. Return ONLY a JSON array of 5 objects. "
    "Each object must have: 'question' (string), 'options' (list of exactly 4 strings), "
    "and 'answer' (a string that exactly matches one of the options). "
    "Base every question strictly on the notes."
)


def ask_ai(system, user, as_json=False):
    config = types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json" if as_json else "text/plain",
    )
    response = client.models.generate_content(model=MODEL, contents=user, config=config)
    return response.text


def parse_quiz(raw):
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    quiz = json.loads(cleaned)
    if not isinstance(quiz, list) or not quiz:
        raise ValueError("Empty quiz")
    return quiz


# ---------- UI ----------
st.title("📚 Study Buddy")
st.caption("Paste your notes, then ask questions, get a summary, or take a quiz made from them.")

notes = st.text_area("Your study notes", height=220, placeholder="Paste a few paragraphs here...")

tab_ask, tab_sum, tab_quiz = st.tabs(["❓ Ask", "📝 Summary", "🎯 Quiz"])

# Ask
with tab_ask:
    question = st.text_input("Your question")
    if st.button("Get answer"):
        if not notes.strip() or not question.strip():
            st.warning("Please add notes and a question first.")
        else:
            try:
                with st.spinner("Thinking..."):
                    answer = ask_ai(QA_SYSTEM, f"Notes:\n{notes}\n\nQuestion: {question}")
                st.write(answer)
            except Exception as e:
                st.error(f"Something went wrong: {e}")

# Summary
with tab_sum:
    if st.button("Summarize"):
        if not notes.strip():
            st.warning("Please paste your notes first.")
        else:
            try:
                with st.spinner("Summarizing..."):
                    summary = ask_ai(SUMMARY_SYSTEM, f"Notes:\n{notes}")
                st.write(summary)
            except Exception as e:
                st.error(f"Something went wrong: {e}")

# Quiz
with tab_quiz:
    if st.button("Generate 5 questions"):
        if not notes.strip():
            st.warning("Please paste your notes first.")
        else:
            try:
                with st.spinner("Creating quiz..."):
                    raw = ask_ai(QUIZ_SYSTEM, f"Notes:\n{notes}", as_json=True)
                st.session_state.quiz = parse_quiz(raw)
                for k in [k for k in st.session_state if str(k).startswith("q") and k != "quiz"]:
                    del st.session_state[k]
            except (json.JSONDecodeError, ValueError):
                st.error("Couldn't read the quiz. Please try again.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

    quiz = st.session_state.get("quiz")
    if quiz:
        score = 0
        answered = 0
        for i, q in enumerate(quiz):
            choice = st.radio(f"{i + 1}. {q['question']}", q["options"], index=None, key=f"q{i}")
            if choice is not None:
                answered += 1
                if choice == q["answer"]:
                    score += 1
                    st.success("Correct! ✅")
                else:
                    st.error(f"Not quite. Correct answer: {q['answer']}")
        if answered == len(quiz):
            st.markdown(f"### 🎉 Your score: {score} / {len(quiz)}")

st.caption("Answers are limited to your notes. Always double-check important facts.")
