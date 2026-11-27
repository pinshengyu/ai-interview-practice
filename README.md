# AI 面試練習工具

用 Gemini API 幫求職者練習面試的小工具。貼上職位描述 → AI 出 5 題 → 你回答 → AI 給回饋。

## 功能

- **依職缺出題**：貼上職位描述，Gemini 依職缺產生 5 題（技術 2 題、行為情境 STAR 2 題、動機 1 題）。
- **逐題回饋**：作答後，AI 以面試官角度給出優點、可改進處與示範回答方向。
- **穩定解析**：要求模型只回傳 JSON 陣列，並處理模型包上 Markdown 程式碼區塊的情況。
- **流程管理**：以 Streamlit session state 管理「輸入職缺 → 作答 → 回饋」三階段，可隨時重新開始。

技術：Python、Streamlit、Gemini API、python-dotenv

## 安裝

```powershell
pip install -r requirements.txt
```

## 設定 API Key

1. 到 https://aistudio.google.com/apikey 申請一把 Gemini API key
2. 複製 `.env.example` 為 `.env`，把 key 填進去：
   ```
   GEMINI_API_KEY=你的key貼這裡
   ```

## 啟動

```powershell
streamlit run app.py
```

啟動後會自動開啟瀏覽器（通常是 http://localhost:8501）。

## 檔案結構

- `app.py` — 主程式（Streamlit 介面 + Gemini 呼叫）
- `.env` — 放 API key（不要上傳到 GitHub）
- `.gitignore` — 已排除 `.env`
- `requirements.txt` — 套件清單
