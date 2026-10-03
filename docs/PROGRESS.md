# 進度總覽

> 跨 session／跨協作者的**進度單一事實來源**。每個 Sprint 結案、需求異動、外部設定完成時必更新。

**現況（2026-09-17）**：設計階段——GDD v0.2 完成，組長已裁決 §10 #1–#6；下一步開工 G0（Unity 6 專案骨架）。

## 已完成

- [x] 設計守則搬入（`docs/DESIGN_PRINCIPLES.md`）
- [x] GDD v0.2（`docs/GDD.md`；含組長裁決：等級 `count+1`、老師唯讀、不顯示進度條、幼幼班不納入、命名 Phase 2）
- [x] 專案指引（`CLAUDE.md`）與 karpathy skill

## 尚未實作（依 GDD §9）

- [ ] G0 骨架：Unity 6 專案、asmdef 三層、命令列建置/測試、CI、部署、`index.html` 讀授權片段
- [ ] G1 核心迴圈（占位美術）：Core 邏輯＋測試、Supabase 讀寫、S0–S6
- [ ] G2 美術：3 變體 × 2 網格、動畫、配色遮罩、圖示
  - [x] 小羊幼體造型定稿（Blender 程序化腳本 `art/blender/lamb_baby.py`，2026-10-02）
  - [x] 收尾腳本 `art/blender/finalize_export.py`：轉網格／減面、頂點色配色遮罩、合併、匯出 FBX（小羊幼體約 6.8k 三角形）
  - [x] GDD §3.4、§7.2 改為頂點色遮罩；花紋改為「隨成長出現」的花紋遮罩貼圖（2026-10-02）
  - [x] 小羊成體造型腳本 `art/blender/lamb_adult.py`（脖子、長腿、更蓬的毛、貼在頭側的螺旋捲角；全身約 7.9k 三角形）
  - [ ] 花紋貼圖（展 UV）；小獅幼體／成體；Unity 端讀頂點色的 toon 著色器
- [ ] G3 收尾：慶祝效果、經文池審稿、手冊
- [ ] P1 平台端（於 `kingdom-little-leaders` repo）：migration＋RLS、家長服事卡頁、鼓勵話語、連結

## 外部依賴

- 組長裁決 GDD §10 #4（登錄日期）、#7（美術產製途徑）
- 美術資產來源與授權確認
- 託管帳號（Vercel / Cloudflare Pages）

## Sprint 歷程

| Sprint | 範圍 | 狀態 | 文件 |
| --- | --- | --- | --- |
| 設計 | GDD v0.2、專案 MD、守則搬入、組長裁決 | ✅ | `docs/GDD.md` |
