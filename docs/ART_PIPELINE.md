# 美術產製流程：AI prompt 生成 → Blender 整理

> GDD §10 #7 裁決（2026-09-30）：**先試 AI 以文字 prompt 生成模型、在 Blender 整理；成果不好再買模型素材。**
> 本文件整理可行工具、操作步驟、授權注意事項，以及「成果好不好」的判斷標準。

## 0. 關於「astro」

查詢時找不到名為「astro」的 3D 生成工具（Astro 是一個網頁框架，與 3D 建模無關）。
以下列出「在 Blender 用 prompt 生成模型」最接近的兩條路。若你指的是某個特定工具，告訴我名稱，我再補上。

## 1. 兩條路比較

| | A. Blender MCP（Claude 直接操作 Blender） | B. 網頁 text-to-3D（Meshy／Tripo）＋ Blender 整理 |
| --- | --- | --- |
| 做法 | 在 Claude Desktop 用文字下指令，Claude 透過 MCP 在你的 Blender 裡建物件、上材質、跑 Python；也可呼叫 Hyper3D Rodin／Hunyuan3D 生成模型 | 在網站輸入 prompt 生成模型，下載 FBX／GLB，再進 Blender 減面、貼圖、綁骨 |
| 適合 | 整理與重複性工作（減面、改色、批次匯出）；也能從零生成 | 從零生出造型，速度最快 |
| 門檻 | 需裝 uv、Blender 外掛、Claude Desktop 設定 | 只要瀏覽器 |
| 費用 | 軟體免費（MIT）；生成服務需各自的金鑰或額度 | 有免費額度；免費方案授權有限制（見 §3） |

**建議組合**：用 B 生出造型（每隻先生幼體），用 A 在 Blender 做整理與規格檢查。

## 2. 操作步驟

### 2.1 B：Meshy／Tripo 生成

1. 開 [Meshy](https://www.meshy.ai/features/text-to-3d) 或 [Tripo](https://www.tripo3d.ai/features/text-to-3d-model)，選 Text to 3D。
2. 貼上 §4 的 prompt 範本（英文效果較好），每隻生 3–4 個候選，挑最可愛、最接近三隻一致風格的。
3. 下載 **FBX 或 GLB**（含貼圖）。
4. 在 Blender 匯入，照 §5 的規格檢查清單整理。

### 2.2 A：Blender MCP

依官方說明安裝（步驟可能更新，以 repo 為準）：[ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp)

1. 安裝 [uv](https://docs.astral.sh/uv/)。
2. 安裝 Blender 外掛（repo 說明的 `install-addon` 指令），在 Blender 偏好設定啟用。
3. 在 Claude Desktop 的 MCP 設定加入該伺服器，重開 Claude Desktop。
4. Blender 側邊欄按「Connect」，回 Claude Desktop 下指令，例如：
   「把選取的模型減面到 8000 三角形以內，合併成單一材質，檢查 UV 有沒有重疊」
5. 若要用它內建的 Hyper3D Rodin 生成，需在外掛設定填入該服務的金鑰。

## 3. 授權注意事項（生成前必讀）

- **Meshy 免費方案**：產出以 **CC BY 4.0** 授權，可使用但**必須標註 Meshy**；付費方案才是私有。
- **Tripo 免費方案**：同為 CC BY 4.0，完整商用權在付費方案。
- 本專案是教會非營利使用，CC BY 4.0 可用，但**一律在遊戲的「製作名單」標註來源**，並把每個模型的來源、方案、授權記在 `Assets/Art/LICENSES.md`。
- 授權條款會變動，**生成當下再到官網確認一次**。
- Prompt 與成品都**不得提及或模仿帕魯的任何角色名稱、造型**；只寫風格形容詞（§4）。

## 4. Prompt 範本

共用風格尾句（三隻都加，確保風格一致）：

```
original cute creature design for a children's game, chibi proportions,
big round head, small round body, large friendly eyes, soft rounded shapes,
stylized low poly, cel shaded, clean simple materials, pastel colors,
neutral standing pose, game-ready, no text, no logo
```

各隻主體（幼體）：

```
Lamb:  a baby lamb spirit creature with fluffy cloud-like wool and tiny round horns, 
Dove:  a baby dove spirit creature with a round fluffy body and small soft wings, 
Lion:  a baby lion cub spirit creature with a small soft mane and a gentle smile, 
```

成體：把 `baby` 換成 `young adult`，並加上該隻的標誌特徵
（Lamb：`fuller wool and a small curled horn`；Dove：`longer elegant tail feathers`；Lion：`fuller flowing mane`）。

## 5. Blender 整理規格（對應 GDD §7.3）

- [ ] 成體 ≤ 8k 三角形、幼體 ≤ 6k（Decimate 修改器）
- [ ] 單一材質、貼圖 ≤ 1024²
- [ ] 另烘一張**配色遮罩貼圖**（R＝主色、G＝副色、B＝點綴色），讓一組網格套八種配色
- [ ] 原點在腳底、面向 +Z、比例 1 單位＝1 公尺
- [ ] 綁骨：四足（Lamb、Lion）共用一套、鳥類（Dove）一套，動畫才能跨變體重用
- [ ] 匯出 FBX 到 `Assets/Art/Beasts/<id>/`，檔名 `<id>_baby.fbx`、`<id>_adult.fbx`

## 6. 什麼叫「成果不好」→ 改買素材

以 **Lamb 幼體一隻、兩個晚上**為試做時限，達不到以下任一項就改買：

1. 組長／師母看了覺得可愛，而且看不出是哪個現成遊戲角色。
2. 整理後能符合 §5 規格，拓撲不會綁骨一動就破。
3. 用同一套 prompt 生出的 Dove、Lion，放在一起風格一致。

改買時的來源：Unity Asset Store、Sketchfab Store、itch.io（搜尋 `cute low poly animals`）。
挑**允許修改與遊戲內使用**的授權，同樣記入 `Assets/Art/LICENSES.md`。
