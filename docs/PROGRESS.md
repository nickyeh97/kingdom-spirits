# 進度總覽

> 跨 session／跨協作者的**進度單一事實來源**。每個 Sprint 結案、需求異動、外部設定完成時必更新。

**現況（2026-10-21）**：`main` 上的**離線 Demo 可展示**（小羊、小獅三階段正式模型＋8 色＋服事升等與進化＋還原），
**本週先展示給組長與師母**；分支上 Dove（鴿子）三階段模型已完成（2026-10-21，待驗收）；`main` 的 Demo 仍以幾何體占位。
**組長裁決（2026-10-20）：G1 平台串接驗收往後放，先做 G2 美術。** G2 在分支上進行，**Demo 展示前不合併進 `main`**。

### 下一步（依序）

1. **Demo 展示**（本週，組長、師母，用 `main`）：收集回饋，記進 GDD §10 裁決紀錄
2. **G2 美術**（分支 `claude/spirit-beast-service-game-2yf3il`）：
   1. URP＋卡通著色器＋描邊——完成，URP 設定已 commit（2026-10-20）
   2. Dove 製作簡報（R04）——`art/briefs/Dove_Baby.md`，組長已確認（2026-10-21）
   3. Dove 三階段模型——完成：幼體 v002、成體 v001、小領袖 v002（橄欖葉冠＋長尾羽＋橄欖枝墜子），組長在 Unity 確認（2026-10-29）。
      其他鴿子修改等組長、師母回饋；第 2 階段羽毛鱗紋需要著色器加「階段」開關（幼體網格兩階段共用）
   3b. 渲染模式切換（卡通／Blender 預覽）、配色預覽錄影模式——完成（2026-10-21）
   4. 骨架與動畫（先寫 R10 骨架簡報）：四足（Lamb／Lion）＋鳥（Dove）；待機、開心、進化、揮手、吃果子
   5. 圖示：六項服事、九顆果子、八組配色色票（2D 扁平風）
   6. Web 建置 ≤ 30 MB（2026-10-29 由 15 MB 放寬）＋手機實機檢查（載入秒數、描邊粗細、30 fps）——
      **第一次量測（2026-10-29，組長本機 Unity 6000.3.26f1）：下載 14.2 MB，在預算內**
      （wasm 7.1、data 6.9 MB；素材最大是 Unity 啟動畫面標誌 2.7 MB、URP 後製用的雜訊貼圖約 3 MB、中文字型 1.8 MB）。
      2026-10-29 再瘦身：關 Unity 啟動畫面、URP Renderer 拿掉後製資料（待重新建置看大小）。
      **手機實測發現 Demo 按鈕點了沒反應**：輸入系統設成新版 Input System（套件根本沒裝），IMGUI 收不到觸控 →
      改回舊版 Input Manager（待組長重開 Unity、重新建置後用手機確認）。
      **待手機實機量測**（4G 載入秒數、描邊粗細、30 fps）
   7. 介面改 UGUI（取代 IMGUI）
3. **G1 平台串接驗收**（往後放）：執行平台 migration、填 `supabase.json`、本機端到端測試（`docs/DEVELOPMENT.md`）

## 已完成

- [x] 設計守則搬入（`docs/DESIGN_PRINCIPLES.md`）
- [x] GDD v0.3（`docs/GDD.md`；§10 七項全數裁決：等級 `count+1`、老師唯讀、不顯示進度條、
      紀錄時間＝按下儲存的時刻、幼幼班不納入（10-03：幼童班也暫不開放，只開放兒童班）、命名 Phase 2、美術先試 AI prompt；靈獸名稱英文顯示）
- [x] 美術產製流程研究（`docs/ART_PIPELINE.md`）
- [x] 專案指引（`CLAUDE.md`）與 karpathy skill
- [x] G0 程式骨架：
  - Unity 6.3 LTS 專案設定（`ProjectVersion.txt`、`manifest.json`）、asmdef 四層（Core／Runtime／Editor／Tests）
  - 授權片段解析 `AuthFragment`＋17 項 NUnit 測試（`dotnet test Tools/CoreTests` 全綠；反向驗證可抓錯）
  - 網頁模板：讀片段 → 清網址列 → jslib 交給 C#；載入進度條與載入秒數
  - `Bootstrap`：旋轉方塊＋顯示片段解析結果（不顯示 token）
  - 命令列建置腳本 `SpiritBeast.Editor.Build.Web`（Brotli＋解壓縮後備）
  - CI：core-tests／unity／deploy；Vercel 標頭設定；`docs/DEVELOPMENT.md`

## 尚未實作（依 GDD §9）

- [x] 本機以 Unity 6000.3.25f1 開啟專案，commit 產生的 `.meta` 與 `ProjectSettings/*.asset`；
      PlayerSettings 已與建置腳本對齊（公司名 TBOJ、模板 `PROJECT:SpiritBeast`、Brotli＋解壓縮後備）
- [x] 本機 Web 建置成功（`SpiritBeast.Editor.Build.Web`），`serve Builds/Web` 開啟看到旋轉方塊（2026-10-02）
- [x] G0 驗收：帶片段開啟顯示 `Fragment OK` 且網址列 `#…` 消失；Unity EditMode 17 項全綠；
      `Assets/Scenes/Main.unity` 已 commit（2026-10-02，組長確認）
- [x] G1 程式：Core（Catalog、GrowthRules、ServiceCard／LogOutcome、Encourager、SupabaseApi）＋測試；
      Runtime（SupabaseClient、BeastView、IMGUI 流程 S0–S6）；中文字型子集；
      免授權的 Runtime 編譯檢查（已抓到 `Display` 撞名、漏掉 UnityWebRequest 模組）
- [ ] **G1 驗收**（Demo 展示後再做）：Unity EditMode 全綠；測試帳號完成「第一次相遇 → ＋1 服事 → 升等 → 第 4 次進化 → 鼓勵語」；
      換成別人孩子的 id 讀不到
- [x] **離線 Demo**（`DemoApp`，2026-10-07）：選靈獸（英文名）、8 色、六項服事 ＋1、升等與第 4／12／24 次進化
      （換幼體 → 成體 → 小領袖模型）、還原到初始；編輯器直接 Play 或網頁 `#demo`。**組長實測小羊、小獅皆正常（2026-10-15）**
- [ ] G2 美術：URP＋toon、3 變體 × 3 網格、動畫、配色遮罩、圖示
  - [x] 美術流程：blendsmith 製作規範（`.claude/skills/blendsmith`）、美術設定檔 `art/ART_PROFILE.md`、
        造型腳本 → `finalize_export.py` → `verify_blend.py`（細節見 `docs/art-worklog/`）
  - [x] 配色遮罩改為頂點色 `Mask`（GDD §7.2）；Unity 換色著色器 `SpiritBeast/PaletteMask`，支援花紋貼圖（色槽顏色 × 花紋）
  - [x] 美術檢查工具：配色預覽（8 組並排、Play 中切換模型、診斷顯示）＋自動規格檢查（`ModelSpecRules`）；
        FBX 頂點色檢查 `Tools/fbx_mask_report.py`（定位小羊幼體全黑＝多一層小寫 mask）
  - [x] **Lamb**：幼體／成體／小領袖（`art/models/Lamb/`，v001）→ 已搬進 `Assets/Art/Resources/Beasts/`（三角形 6824／7936／7992）
  - [x] **Lion**：幼體 v004／成體 v007／小領袖 v001（皇冠＋項鍊）（`art/models/Lion/`）→ 已搬進 Unity（含花紋貼圖；
        三角形 6632／7768／7730）。幼體、小領袖的造型待組長驗收
  - [ ] **Dove：幼體／成體／小領袖**——簡報 `art/briefs/Dove_Baby.md` 已確認（2026-10-21）；
        **幼體 v002／成體 v001／小領袖 v002**（4580／7144／7868 三角形；小領袖 v002 胸前加金項鍊＋橄欖枝墜子，組長在 Unity 確認正常（2026-10-29）；幼體 v002 修正原點，v001 在 Demo 裡會往下沉）已搬進 Unity（`art/models/Dove/`，驗證各 18 項全過），待組長驗收。
        三隻靈獸的正式模型都齊了，Demo 不再有幾何體占位
  - [ ] 骨架＋動畫（待機、開心、進化、揮手、吃果子）：四足共用一套；**Dove 需要另一套鳥骨架**（簡報 Q1）
  - [x] 正式卡通著色器＋描邊（2026-10-20，分支）：URP、兩段明暗（暗面暖色）、反向外殼描邊、占位幾何體同一著色器；
        URP 設定由 Editor 腳本自動建立，組長已在 Unity 套用並 commit（2026-10-20）。固定色經查**不需轉換**（Blender 與 Unity 都用線性原值）
  - [x] 渲染模式切換（2026-10-21，分支）：卡通／Blender 預覽（跟美術算圖一致：同燈光、投影、環境光、背景、
        Blender AgX 查找表）；配色預覽與 Demo 都有按鈕。組長確認顏色與渲染 OK（2026-10-21）
  - [ ] 圖示：六項服事、九顆果子、八組配色色票
  - [ ] Web 建置 ≤ 30 MB＋手機實機檢查（2026-10-29 量測 14.2 MB ✅；手機實機待測）
- [ ] G3 收尾：慶祝效果、經文池審稿、手冊
- [x] P1 平台端第一部分（kingdom-little-leaders v0.6.0，PR #45）：migration＋RLS（本機 Postgres 33 項行為測試全過）、
      「我的 → 小領袖靈獸」入口（只對兒童班顯示）
- [x] 修正：Unity 編譯錯誤「找不到 UnityWebRequest」——manifest 補 `com.unity.modules.unitywebrequest`
      （另加 `animation` 給 FBX 模型）；Runtime 編譯檢查改為只引用 manifest 啟用的模組，已能重現同一組錯誤（2026-10-03）
- [ ] P1 平台端第二部分：家長服事卡頁（鼓勵話語編輯、歷史檢視與誤登刪除）、手冊章節

## 外部依賴

- **Unity 6000.3.25f1 的 WebGL 模組**：本機建置前確認已安裝（Hub →「安裝」→ 6000.3.25f1 →「新增模組」）
- **GitHub Secrets**：`UNITY_LICENSE`、`UNITY_EMAIL`、`UNITY_PASSWORD`（Unity 建置）；
  `VERCEL_TOKEN`、`VERCEL_ORG_ID`、`VERCEL_PROJECT_ID`（部署）。步驟見 `docs/DEVELOPMENT.md`
- **平台 migration `2026-10-02_service_card` 執行**（Supabase SQL Editor）：G1 讀寫的資料表
- **`Assets/Resources/supabase.json` 填入平台的 Supabase URL 與 anon key**
- **手機 4G 首次載入 ≤ 10 秒**（G0 遺留驗收）：Vercel 部署設定完成後，以手機開部署網址看右下角秒數

## Sprint 歷程

| Sprint | 範圍 | 狀態 | 文件 |
| --- | --- | --- | --- |
| 設計 | GDD v0.3、專案 MD、守則搬入、組長裁決、美術流程研究 | ✅ | `docs/GDD.md`、`docs/ART_PIPELINE.md` |
| G0 | Unity 骨架、授權片段交接、命令列建置、CI、部署設定 | ✅ 結案（手機載入時間待部署後量測） | `docs/DEVELOPMENT.md` |
| G1 | 核心迴圈（占位美術）：規則、Supabase 讀寫、S0–S6；平台資料層與入口 | ⏸ 程式完成，實機驗收往後放（2026-10-20） | `docs/GDD.md` §9.1 |
| Demo | 離線展演：選靈獸、8 色、服事 ＋1、進化、還原；小羊／小獅正式模型 | ✅ 組長實測正常，本週展示（缺 Dove） | `docs/DEVELOPMENT.md`「離線 Demo」 |
| 整合 | 遊戲分支＋美術分支合併進 `main`（2026-10-15） | ✅ | — |
| G2 | 美術：URP 卡通著色器＋描邊 → Dove → 骨架動畫 → 圖示 → 建置與手機檢查 → UGUI（G1 驗收往後放，2026-10-20 組長裁決） | 🟡 進行中（URP 已在 Unity 設定完成；Dove 三階段 v001 待驗收） | `art/ART_PROFILE.md`、`docs/art-worklog/` |
