# 進度總覽

> 跨 session／跨協作者的**進度單一事實來源**。每個 Sprint 結案、需求異動、外部設定完成時必更新。

**現況（2026-10-02）**：G0 骨架完成；**本機 Web 建置成功，瀏覽器看到旋轉方塊**（Unity 端程式首次編譯即通過）。
剩下的 G0 驗收：確認授權片段顯示、部署到 Vercel 後以手機 4G 量載入時間、CI 設好 Unity 授權。

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
- [ ] **G0 驗收（剩餘）**：本機帶片段開啟顯示 `Fragment OK` 且網址列 `#…` 消失；EditMode 測試在 Unity 跑綠；
      部署網址在手機開啟、4G 首次載入 ≤ 10 秒；commit 建置時產生的 `Assets/Scenes/Main.unity`
- [ ] G1 核心迴圈（占位美術）：等級/階段/進化規則＋測試、Supabase 讀寫、S0–S6
- [ ] G2 美術：URP＋toon、3 變體 × 2 網格、動畫、配色遮罩、圖示（先試 AI prompt，見 `docs/ART_PIPELINE.md`）
- [ ] G3 收尾：慶祝效果、經文池審稿、手冊
- [ ] P1 平台端（於 `kingdom-little-leaders` repo）：migration＋RLS（`service_card_entries` 不含聚會日欄位、
      該班老師唯讀）、家長服事卡頁、鼓勵話語、「去看靈獸」連結（僅兒童班／幼童班）

## 外部依賴

- **Unity 6000.3.25f1 的 WebGL 模組**：本機建置前確認已安裝（Hub →「安裝」→ 6000.3.25f1 →「新增模組」）
- **GitHub Secrets**：`UNITY_LICENSE`、`UNITY_EMAIL`、`UNITY_PASSWORD`（Unity 建置）；
  `VERCEL_TOKEN`、`VERCEL_ORG_ID`、`VERCEL_PROJECT_ID`（部署）。步驟見 `docs/DEVELOPMENT.md`
- 美術：Lamb 幼體 AI 試做（兩個晚上為限），結果決定 AI 或買素材

## Sprint 歷程

| Sprint | 範圍 | 狀態 | 文件 |
| --- | --- | --- | --- |
| 設計 | GDD v0.3、專案 MD、守則搬入、組長裁決、美術流程研究 | ✅ | `docs/GDD.md`、`docs/ART_PIPELINE.md` |
| G0 | Unity 骨架、授權片段交接、命令列建置、CI、部署設定 | 🟡 本機建置成功，待手機與部署驗收 | `docs/DEVELOPMENT.md` |
