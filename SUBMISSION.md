# 作業繳交文字（將 [方括號] 內容改成自己的資訊與公開網址）

**繳交標題：** [學校] [學號] [系級] [姓名] RAG 是什麼？從 LLM Wiki 到 HTML 教學簡報

## 1. LLM Wiki 主題與介紹

我的主題是 **RAG（Retrieval-Augmented Generation，檢索增強生成）**。希望讓沒有 AI 技術背景的同學理解：為什麼 LLM 需要查詢外部知識、RAG 的三個主要步驟，以及如何檢查生成答案有沒有來源。

我先討論學習對象與教學大綱，再蒐集並整理 6 篇可靠資料（RAG 原始論文、Microsoft、Anthropic、IBM、RAGAS、AWS）。每篇來源都保存 URL 和重點，並整理成具有交叉連結與來源追溯的 Wiki 條目。

## 2. LLM Wiki 成果連結

**Wiki：** [請貼上自己 GitHub Pages 的 wiki.html 網址]

Wiki 共 10 個概念條目，內容包含 RAG 定義、問題背景、資料切段、三步驟、檢索方式、回答引用、案例、錯誤與評估。來源編號為 S01–S06，可從每個條目連回原始資料。

## 3. 教學 HTML 簡報

**簡報：** [請貼上自己 GitHub Pages 的 slides.html 網址]

共 15 頁（12 頁教學，3 頁附錄）。使用開卷考試比喻講解 RAG，再以「虛構供應商延誤 5 天」情境展示檢索與有來源的回答。每頁能連到相關 Wiki 與資料來源。

## 4. Loop / Graph 流程

**討論教學目標 → 蒐集與整理來源 → Ingest 來源筆記（6 篇）→ LLM 整理 Wiki → Lint 檢查 → 生成教學 HTML → 人工審查**。

如果 Lint 發現來源不存在、Wiki 交叉連結無效，或投影片引用不屬於對應的 Wiki 條目，就回到 Wiki／簡報資料修正並重新檢查。若人工審查發現內容不清楚或出處不支持結論，也回到前面修改。這樣可避免錯誤流到最後的成品。

**Graph 與執行紀錄：** [請貼上自己 GitHub Pages 的 workflow.html 網址]

## 5. 一次實際執行與檢查紀錄

我對 6 份資料筆記執行本地 ingest，生成含來源 ID、檔名、SHA-256 的 manifest；整理成 10 個 Wiki 條目與 15 頁簡報。結構檢查結果 PASS。

另外，我刻意在投影片測試副本中加入不存在的來源 ID `S99`，檢查程式回傳：

`FAIL UNKNOWN_SLIDE_SOURCE case: S99`（exit code 1）。

修正後重跑得到：

`PASS SOURCE_LINEAGE_AND_STRUCTURE`（exit code 0）。

接著成功生成 HTML。需注意，這是**結構與來源對應驗證**，不是自動證明每個知識主張的語意正確性。

## 6. 反思與流程調整

我認為高風險節點是 **Wiki 整理後轉成投影片時的來源對應**。在設計階段發現，如果等到生成 HTML 才檢查，會容易漏掉來源，或讓不正確的來源 ID 出現在最後成品。

因此，我修改成 **在 HTML 生成前設置 Lint gate**：驗證來源 ID、Wiki lineage 與 crosslinks；若不通過，就先修正再生成。人工仍需逐段比對原始資料，以避免雖然編號正確、但內容解釋錯誤的情況。

---

**注意**：本作品採用 LLM Wiki 的本地 Markdown 維護概念和自行執行的 ingest/lint 腳本。如果老師明確規定必須在特定 LLM Wiki 平台做 ingest，仍須使用指定工具再執行並補上證據，不應宣稱本地原型等於已在該平台完成。
