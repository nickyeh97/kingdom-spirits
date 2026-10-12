# 進度總覽

> 跨 session／跨協作者的**進度單一事實來源**。每個 Sprint 結案、需求異動、外部設定完成時必更新。

**現況（2026-10-02）**：**G0 結案**（組長確認）——本機 Web 建置成功、旋轉方塊與 `Fragment OK` 顯示正常、
網址列片段清除、Unity EditMode 17 項全綠。手機 4G 載入時間待部署後量測（見外部依賴）。下一步：G1。

## 已完成

- [x] 設計守則搬入（`docs/DESIGN_PRINCIPLES.md`）
- [x] GDD v0.3（`docs/GDD.md`；§10 七項全數裁決：等級 `count+1`、老師唯讀、不顯示進度條、
      紀錄時間＝按下儲存的時刻、幼幼班不納入、命名 Phase 2、美術先試 AI prompt；靈獸名稱英文顯示）
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
- [ ] G1 核心迴圈（占位美術）：等級/階段/進化規則＋測試、Supabase 讀寫、S0–S6
- [ ] G2 美術：URP＋toon、3 變體 × 3 網格、動畫、配色遮罩、圖示（先試 AI prompt，見 `docs/ART_PIPELINE.md`）
  - [x] 小羊幼體造型定稿（Blender 程序化腳本 `art/blender/lamb_baby.py`，2026-10-02）
  - [x] 收尾腳本 `art/blender/finalize_export.py`：轉網格／減面、頂點色配色遮罩、合併、匯出 FBX（小羊幼體約 6.8k 三角形）
  - [x] GDD §3.4、§7.2 改為頂點色遮罩；花紋改為「隨成長出現」的花紋遮罩貼圖（2026-10-02）
  - [x] 小羊成體造型腳本 `art/blender/lamb_adult.py`（脖子、長腿、更蓬的毛、貼在頭側的螺旋捲角；全身約 7.9k 三角形）
  - [x] 小羊・小領袖造型腳本 `art/blender/lamb_leader.py`（沉著眼神、微笑、淡腮紅、光滑對數螺旋角＋金角環、領袖披風；約 7.9k 三角形）
  - [x] GDD 改為每種 3 個網格（幼體／成體／小領袖，2026-10-06 決定）
  - [x] 採用 blendsmith 製作規範（修改版放 `.claude/skills/blendsmith`，GPL-3.0-only）：NPR 卡通＋描邊、每個網格展 UV、
        腳本＋已驗證 `.blend` 雙交付、Unity／Unreal 匯出；美術設定檔 `art/ART_PROFILE.md`；術語表；CLAUDE.md 改英文正本＋繁中副本（2026-10-12）
  - [x] 小羊三階段 v001 交付：`art/models/Lamb/`（`.blend`＋Unity FBX＋Unreal FBX），重新開檔驗證各 16 項全 PASS；
        三角形 6,824／7,936／7,992；Unity／Unreal 實際匯入 NOT RUN
  - [ ] 描邊方法與 Unity toon shader（讀 `Mask` 頂點色）；花紋遮罩貼圖；小獅幼體／成體／小領袖
- [ ] G3 收尾：慶祝效果、經文池審稿、手冊
- [ ] P1 平台端（於 `kingdom-little-leaders` repo）：migration＋RLS（`service_card_entries` 不含聚會日欄位、
      該班老師唯讀）、家長服事卡頁、鼓勵話語、「去看靈獸」連結（僅兒童班／幼童班）

## 外部依賴

- **Unity 6000.3.25f1 的 WebGL 模組**：本機建置前確認已安裝（Hub →「安裝」→ 6000.3.25f1 →「新增模組」）
- **GitHub Secrets**：`UNITY_LICENSE`、`UNITY_EMAIL`、`UNITY_PASSWORD`（Unity 建置）；
  `VERCEL_TOKEN`、`VERCEL_ORG_ID`、`VERCEL_PROJECT_ID`（部署）。步驟見 `docs/DEVELOPMENT.md`
- **手機 4G 首次載入 ≤ 10 秒**（G0 遺留驗收）：Vercel 部署設定完成後，以手機開部署網址看右下角秒數
- 美術：Lamb 幼體 AI 試做（兩個晚上為限），結果決定 AI 或買素材

## Sprint 歷程

| Sprint | 範圍 | 狀態 | 文件 |
| --- | --- | --- | --- |
| 設計 | GDD v0.3、專案 MD、守則搬入、組長裁決、美術流程研究 | ✅ | `docs/GDD.md`、`docs/ART_PIPELINE.md` |
| G0 | Unity 骨架、授權片段交接、命令列建置、CI、部署設定 | ✅ 結案（手機載入時間待部署後量測） | `docs/DEVELOPMENT.md` |
