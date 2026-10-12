# CLAUDE.md

本文件提供給 Claude Code（及所有 AI 協作者）在此 repo 工作時的指引。

## 語言慣例

- 與使用者的對話、文件、commit 說明主體，一律使用**繁體中文**（台灣用語）。
- 程式碼識別字（類別、方法、欄位、資產檔名）使用英文；註解可用中文。

## 專案概觀

**小領袖靈獸（kingdom-spirits）**——國度領袖兒童牧區「服事經歷卡」的電子版遊戲（Unity 6，建置為手機瀏覽器可開的 Web）。
隸屬於 TBOJ（The Book of James）信仰實踐計畫；牧區平台本體在 [`nickyeh97/kingdom-little-leaders`](https://github.com/nickyeh97/kingdom-little-leaders)，總計畫在 [`nickyeh97/TBOJ`](https://github.com/nickyeh97/TBOJ)。

每個孩子有一隻自己的靈獸，隨著孩子真實的服事一起長大：家長看到老師簽名的紙本服事卡後，在遊戲裡登錄一次服事 → 該項目等級 +1 → 靈獸慶祝、跨門檻就進化 → 出現家長預先寫的鼓勵話。

> 完整設計：`docs/GDD.md`（需求基準，開發前必讀）。

### 國度領袖兒童異象（計畫核心，最上位）

> **培育神國小領袖，活出天父美好的計畫。**

1. **自我形象**：確信天父孩子的身分——所以**靈獸從第一天就有**，不是服事之後才給。
2. **品格塑造**：鼓勵話語以經文與聖靈果子為底，不用比較、不用罪惡感。
3. **活出計畫**：服事的累積看得見（項目等級、靈獸階段），但只跟自己比。

## 最高守則（開發前必讀）

`docs/DESIGN_PRINCIPLES.md` 是本 repo 的**最高守則**（與平台、TBOJ 共用同一份），任何設計必須先通過其檢核。對「遊戲」這種形式特別要盯的地方：

1. **沒有比較**（紅燈 #1）：畫面上永遠只有自己的靈獸；不做排行、展示牆、分享他人。
2. **沒有留存機制**（紅燈 #2）：沒有每日登入、連續簽到、饑餓/衰弱、倒數、推播。**靈獸永遠不會退階、不會因為沒開遊戲而難過。**
3. **沒有隨機獎勵、內購、廣告**（紅燈 #3、#4）。
4. **不以停留時間為指標**（紅燈 #5）：開 3 分鐘看完關掉是正確用法。
5. **兒童個資最小化**（紅燈 #6）：只取平台已有的最少資料；不接任何分析或第三方 SDK。
6. **不羞辱**（紅燈 #7）：一等（尚未服事）不是「弱」；未探索的項目是「等你來探索」，不是「缺少」。**不顯示「距下一階段還差幾次」**。
7. 若設計與守則衝突：**立即停下、提出討論**，不得便宜行事。

## 與牧區平台的關係（分工）

- **文字輸入在平台、觸控互動在遊戲**（Unity Web 的手機中文輸入體驗差）。
- 資料只有一份：平台的 Supabase（`service_card_entries`、`beast_profiles`），遊戲以家長的 access token 直呼 REST，**安全邊界是 RLS**，遊戲端的角色判斷只是 UX。
- 授權交接：平台以 `#at=<access_token>&child=<child_id>` 片段開啟遊戲；只傳 access token、不傳 refresh token，過期就回平台重開。
- 服事項目字典沿用平台 `child_service_items`，遊戲不自建清單。
- 命名一律用 `gathering`（聚會日），文案寫「聚會日」不寫「主日」；本教會聚會在週六下午且不固定週幾，**不得寫死 Sunday／週日**。

## 技術選型（已決定）

| 層 | 選型 |
| --- | --- |
| 引擎 | **Unity 6000.3.25f1（Unity 6.3 LTS）**，建置目標 **Web**；URP ＋ 簡易 toon 著色器於 G2 導入。不用 Beta 版（CI 無映像） |
| UI | UGUI ＋ TextMeshPro（靜態字型圖集，Noto Sans TC 子集） |
| 資料 | UnityWebRequest → Supabase REST；JSON 用 Newtonsoft |
| 測試 | 核心邏輯放在無 UnityEngine 依賴的 `SpiritBeast.Core`；同一批 NUnit 測試由 `dotnet test Tools/CoreTests`（免授權）與 Unity Test Framework（EditMode）各跑一次 |
| 命令列 | Unity CLI（`unity install …`）裝編輯器；Editor `-batchmode` 建置與測試（指令見 `docs/DEVELOPMENT.md`） |
| 託管 / CI | Vercel 或 Cloudflare Pages 靜態站；GitHub Actions（game-ci） |

### 硬性約束（手機 Web）

- Web 建置壓縮後 **≤ 15 MB**；4G 首次載入 ≤ 10 秒。
- 場景同時只有一隻靈獸；成體 ≤ 8k 三角形、貼圖 ≤ 1024²、單一材質。
- 直式、單手操作、按鈕 ≥ 44pt；遊戲內**不做任何文字輸入**。

### 美術界線

參考《幻獸帕魯》的**風格語彙**（圓潤低多邊形、大頭身比、cel-shading、可愛表情），**不得複製任何帕魯角色的造型、名稱、配色或標誌特徵**。靈獸為原創，以聖經動物為原型，**名稱一律以英文顯示**（Lamb、Dove、Lion；擴充：Deer、Eagle、Fish）。所有資產須原創或授權合規；產製流程見 `docs/ART_PIPELINE.md`（先試 AI prompt＋Blender，不佳再買素材）。

## Repo 結構

```
README.md                              # 專案簡介與必讀文件索引（不放開發設定）
CLAUDE.md                              # 本文件
.claude/skills/karpathy-guidelines/    # 程式撰寫行為守則 skill（先想再寫、簡單優先、外科手術式修改、目標驅動）
docs/DESIGN_PRINCIPLES.md              # 最高守則（與平台共用，必讀）
docs/GDD.md                            # 遊戲設計開發規格書（需求基準）
docs/ART_PIPELINE.md                   # 美術產製流程（AI prompt → Blender；不佳改買素材）
docs/DEVELOPMENT.md                    # 開發指南：Unity 版本、命令列測試/建置、CI Secrets、Vercel 部署
docs/PROGRESS.md                       # 進度總覽（單一事實來源；每個 Sprint 結束必更新）
Assets/Config                          # 階段門檻、配色、經文池（資料，不寫死在程式）
Assets/Core                            # 純 C# 核心邏輯（可測）
Assets/Runtime                         # MonoBehaviour：畫面、動畫、Supabase 客戶端
Assets/Editor                          # 命令列建置腳本（SpiritBeast.Editor.Build.Web）
Assets/Plugins/WebGL                   # jslib：從網頁取走授權片段
Assets/Tests/EditMode                  # 核心邏輯單元測試（只用 NUnit）
Assets/WebGLTemplates                  # 自訂 index.html（讀授權片段、清網址列、載入畫面）
Tools/CoreTests                        # dotnet 測試專案：編譯 Assets/Core＋Assets/Tests，免 Unity 授權
.github/workflows/ci.yml               # core-tests／unity（需授權）／deploy（main → Vercel）
```

## 工作流程慣例

- **先想再寫**：寫/改程式一律套用 `.claude/skills/karpathy-guidelines`——說明假設、簡單優先、只動該動的、先定可驗證的成功準則再動手。
- **進度文件（必遵守）**：`docs/PROGRESS.md` 是跨 session 的進度單一事實來源；每個 Sprint 結案、需求異動、外部設定完成時必更新；新 session 開工前先讀它。
- **測試**：核心規則（等級、階段、進化判定、片段解析、鼓勵語挑選）**必須**有 EditMode 測試，含邊際案例；送 PR 前至少跑 `dotnet test Tools/CoreTests`；能開 Unity 時再跑 EditMode 測試與 Web 建置；CI 於 push/PR 自動執行。
- **設定值不寫死**：階段門檻、配色、經文池放 `Assets/Config` 的 ScriptableObject。
- **收尾檢查（每次需求實作完畢後必跑）**：
  1. 守則檢查清單（`docs/DESIGN_PRINCIPLES.md` §4）七項重過一次。
  2. 用測試帳號在**手機實機**開一輪（載入時間、觸控、字型）。
  3. 使用者看得到的操作有變 → 同步平台 repo 的 `docs/HANDBOOK.md` 家長章節。
- **分支**：功能開發在 `claude/*` 或 feature 分支，不直接 push `main`。
- **Commit**：訊息以繁體中文為主，清楚描述「做了什麼、為什麼」。
- **機密**：Supabase URL 與 anon key 屬公開值可進設定檔；任何 service key、token、兒童個資都不得進版控。測試一律用假名。
