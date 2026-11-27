import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("找不到 GEMINI_API_KEY，請在 .env 檔案中設定你的 API key")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-3.1-flash-lite")

st.set_page_config(page_title="AI 面試練習", page_icon="🎯")
st.title("🎯 AI 面試練習工具")
st.caption("貼上職位描述 → AI 出題 → 你回答 → AI 給回饋")

if "stage" not in st.session_state:
    st.session_state.stage = "input_jd"
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.feedbacks = []
    st.session_state.job_description = ""


def reset():
    st.session_state.stage = "input_jd"
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.feedbacks = []
    st.session_state.job_description = ""


def parse_json_from_response(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
    return json.loads(text)


if st.session_state.stage == "input_jd":
    st.subheader("步驟 1：貼上職位描述")
    jd = st.text_area(
        "Job Description",
        height=220,
        placeholder="例如：後端工程師，需熟悉 Python、FastAPI、PostgreSQL，3 年以上經驗⋯⋯",
    )
    if st.button("產生面試題", type="primary"):
        if not jd.strip():
            st.warning("請先貼上職位描述")
        else:
            with st.spinner("AI 正在出題⋯⋯"):
                prompt = f"""你是一位資深的面試官。請根據以下職位描述，產生 5 道面試題目。
題目分布：
- 技術 / 專業能力相關：2 題
- 行為情境題（STAR 適用）：2 題
- 動機 / 職涯規劃：1 題

請只回傳 JSON 陣列，不要任何其他文字或標記：
["題目1", "題目2", "題目3", "題目4", "題目5"]

職位描述：
{jd}
"""
                try:
                    response = model.generate_content(prompt)
                    questions = parse_json_from_response(response.text)
                    st.session_state.questions = questions
                    st.session_state.answers = [""] * len(questions)
                    st.session_state.job_description = jd
                    st.session_state.stage = "answering"
                    st.rerun()
                except Exception as e:
                    st.error(f"出題失敗：{e}")

elif st.session_state.stage == "answering":
    st.subheader("步驟 2：回答以下 5 題")
    st.info("請認真作答後，點下方「取得 AI 回饋」")
    for i, q in enumerate(st.session_state.questions):
        st.markdown(f"**Q{i + 1}. {q}**")
        st.session_state.answers[i] = st.text_area(
            label=f"answer_{i}",
            value=st.session_state.answers[i],
            key=f"answer_input_{i}",
            height=130,
            label_visibility="collapsed",
            placeholder="在這裡輸入你的回答⋯⋯",
        )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 重新開始"):
            reset()
            st.rerun()
    with col2:
        if st.button("取得 AI 回饋", type="primary"):
            if not all(a.strip() for a in st.session_state.answers):
                st.warning("請先回答完所有題目")
            else:
                with st.spinner("AI 正在分析你的回答⋯⋯"):
                    feedbacks = []
                    progress = st.progress(0)
                    for idx, (q, a) in enumerate(
                        zip(st.session_state.questions, st.session_state.answers)
                    ):
                        prompt = f"""你是一位資深面試官，正在給候選人面試回饋。

【職位描述】
{st.session_state.job_description}

【面試題目】
{q}

【候選人回答】
{a}

請用繁體中文，依以下格式給回饋（總長度約 200 字，語氣鼓勵但誠實）：

👍 **優點**：（這個回答好在哪）

👎 **可改進處**：（哪裡可以加強）

💡 **建議範例**：（用 1-2 句示範更好的回答方向）
"""
                        try:
                            resp = model.generate_content(prompt)
                            feedbacks.append(resp.text)
                        except Exception as e:
                            feedbacks.append(f"⚠️ 此題回饋產生失敗：{e}")
                        progress.progress((idx + 1) / len(st.session_state.questions))
                    st.session_state.feedbacks = feedbacks
                    st.session_state.stage = "feedback"
                    st.rerun()

elif st.session_state.stage == "feedback":
    st.subheader("步驟 3：AI 面試回饋")
    for i, (q, a, f) in enumerate(
        zip(
            st.session_state.questions,
            st.session_state.answers,
            st.session_state.feedbacks,
        )
    ):
        with st.expander(f"Q{i + 1}. {q}", expanded=True):
            st.markdown("**你的回答**")
            st.write(a)
            st.markdown("---")
            st.markdown("**AI 回饋**")
            st.markdown(f)

    if st.button("🔄 重新練習一次", type="primary"):
        reset()
        st.rerun()
