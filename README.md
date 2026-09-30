# 小領袖靈獸（kingdom-spirits）

> 「各人應當察驗自己的行為；這樣，他所誇的就專在自己，不在別人了。」— 加拉太書 6:4

國度領袖兒童牧區「服事經歷卡」的電子版遊戲：每個孩子有一隻自己的靈獸，隨著孩子真實的服事一起長大。
靈獸不是獎品，是孩子服事之路的見證者與夥伴——只跟自己比，不跟任何人比。

- 🐑 三種原創靈獸（Lamb、Dove、Lion；規劃擴充至六種）、八組配色，孩子自己選
- 🌱 四個成長階段（初生 → 成長 → 茁壯 → 小領袖），由服事總次數決定，永不退階
- 🎯 六項服事各有等級（幾次就幾等）；還沒試過的項目是「等你來探索」
- 💬 家長預先寫的鼓勵話＋內建經文（聖靈的果子），在登錄服事與進化時出現
- 🚫 沒有排行、沒有每日登入、沒有饑餓、沒有抽卡、沒有內購、沒有廣告

本專案隸屬於 [TBOJ（The Book of James）](https://github.com/nickyeh97/TBOJ) 信仰實踐計畫，資料與登入來自
[國度領袖兒童牧區整合平台](https://github.com/nickyeh97/kingdom-little-leaders)（家長從平台的服事卡頁開啟遊戲）。

## 技術棧

- Unity 6.3 LTS（Web 建置，手機瀏覽器開啟）
- 資料：平台的 Supabase（REST ＋ RLS），遊戲無自建後端
- 部署：Vercel / Cloudflare Pages 靜態站

## 必讀文件

| 文件 | 說明 |
| --- | --- |
| [`docs/DESIGN_PRINCIPLES.md`](docs/DESIGN_PRINCIPLES.md) | **最高守則**——任何設計必須先通過檢核 |
| [`docs/GDD.md`](docs/GDD.md) | 遊戲設計開發規格書（需求基準） |
| [`docs/PROGRESS.md`](docs/PROGRESS.md) | **進度總覽**（每個 Sprint 更新） |
| [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) | 開發指南：版本、測試、建置、CI、部署 |
| [`docs/ART_PIPELINE.md`](docs/ART_PIPELINE.md) | 美術產製流程（AI prompt → Blender） |
| [`CLAUDE.md`](CLAUDE.md) | AI 協作指引（守則要點、分工、技術選型、工作流程） |
