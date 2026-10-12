# 美術設定檔 — kingdom-spirits — 繁體中文閱讀副本

版本：**1**（2026-10-12）。英文正本為 [ART_PROFILE.md](ART_PROFILE.md)；兩者一起更新，有差異時以英文正本為準。

這份設定檔記錄本 repo 所有 3D 模型共用的專案層級決定。[blendsmith skill](../.claude/skills/blendsmith/SKILL.zh-TW.md) 把它們視為組長已明確確認的指示。個別資產的細節寫在該資產的製作簡報或 worklog。需求與限制來自 [docs/GDD.md](../docs/GDD.md) §7 與 [docs/DESIGN_PRINCIPLES.md](../docs/DESIGN_PRINCIPLES.md)。

## 風格與目標

| 決定 | 內容 |
| --- | --- |
| 風格模式（R02） | **NPR 卡通＋描邊。**大頭身低多邊形，光帶由引擎 shader 產生，一定要描邊。不需要 Normal／Roughness／Metallic 貼圖。 |
| 主要引擎 | Unity 6000.3.25f1（6.3 LTS）、URP，建置成手機瀏覽器用的 **Web**。 |
| 次要引擎 | Unreal：保留匯出設定供日後使用；在有 Unreal 專案之前，匯入測試為 NOT RUN。 |
| 描邊方法 | **未定，G2 製作 shader 時決定。**Unity URP 的候選是沿法線外推的 shader pass；若零件交界處描邊斷開，再加入平滑過的描邊法線。 |
| 上色方式 | 頂點色屬性 `Mask`（見下方）＋材質參數；8 組配色；從階段 2 起在 UV 上加花紋遮罩貼圖。 |
| 美術界線 | 只借用帕魯的**風格語彙**；絕不複製任何帕魯角色的造型、名稱、配色或標誌特徵。靈獸為原創，以聖經動物為原型；名稱以英文顯示（Lamb、Dove、Lion；擴充 Deer、Eagle、Fish）。 |

## 預算與網格

- 每種靈獸 3 個網格：幼體 Baby（階段 1–2）、成體 Adult（階段 3）、小領袖 Leader（階段 4）。畫面上一次只有一隻。
- **每個網格最多 8,000 個求值後三角形**（算三角形，不算面）。單一材質。貼圖最大 1024²；花紋遮罩最大 512²。
- Web 建置壓縮後總共最多 15 MB。
- 原點在腳底中央（Z = 0），在 Blender 面向 −Y（匯出後是 Unity 的正前方），1 單位 = 1 公尺。
- 嘴保持獨立的子物件（`Mouth`），供「吃到聖靈果子」的動畫使用。

## 配色遮罩慣例（`Mask`，面角的浮點顏色）

| 遮罩數值 | 意義 |
| --- | --- |
| A = 1、R = 1 | 主色槽（例如羊毛） |
| A = 1、G = 1 | 副色槽（臉、耳朵、腳） |
| A = 1、B = 1 | 點綴色槽（臉頰、內耳、披風） |
| A = 1、通道值 = 0.45 | 內襯：該色槽顏色的 45%（深色，換配色時跟著變） |
| A = 0 | 固定色 = RGB（眼睛／鼻子／蹄的深色、眼睛反光的白、象牙色的角、金色、立領的紅） |

色槽的意義依物種不同（小羊：主色＝羊毛、副色＝臉；小獅：主色＝身體的皮、副色＝可愛的肉色、點綴色＝毛）。收尾腳本會依常見的零件名稱對應色槽；造型腳本可以用 `o["mask"] = (R, G, B, A)` 直接指定任何零件，優先於名稱對照。只要某個名稱對這個物種的意義不同，就用這個方式指定。

成長花紋（從階段 2 起，畫在 UV 上的花紋遮罩）：小獅——每個網格都用自然的獅子毛色（幼體的斑點由組長於 2026-10-12 拿掉）（口鼻、下巴、胸口、腿內側較淺，背脊、耳背、尾巴毛球較深，順著身體的毛流筆觸，沒有斑點也沒有條紋），取自 Meshy Lion Cub 參考模型（組長，2026-10-12；細節見 `docs/art-worklog/2026-10-12_010_lion-reference-q-style.md`）。小羊——待定。

所有物種的風格都維持 Q 版。匯入的模型只當輪廓與花紋的參考，不是交付的風格。

引擎公式：`顏色 = A ? (R×主色 + G×副色 + B×點綴色) × 花紋 : RGB`，`花紋` 是在 UV 上取樣的灰階花紋遮罩（沒有花紋的網格當作 1）。造型腳本可以在點上加 `shade` 屬性（0–1），finalize 會把色槽通道乘上它，做出平滑、換配色時會跟著變的深色區（例如背脊較深）。FBX 以 Linear 匯出顏色。重新匯入時固定色會經過 sRGB 轉換而偏移，引擎 shader 要處理這點（G2 待辦）。

## 流程與交付（R11、R12）

組長正在學習程式化建模，所以腳本與已驗證的 `.blend` **兩者都是交付物**。

1. **造型腳本**（可編輯的原稿，註解用繁體中文方便學習）：`art/blender/<物種>_<階段>.py`，例如 `lamb_baby.py`。腳本會設定 `scene["spirit_name"]`，必要時也設定 `scene["wool_tri_target"]`。
2. **收尾** `art/blender/finalize_export.py`：metaball／曲線轉網格、羊毛減到目標面數、套用旋轉與縮放、去除 n-gon、寫入 `Mask`（含 `shade`）、除了 `Mouth` 全部合併、每個網格展 UV、有設 `scene["pattern"]` 時烘焙花紋遮罩（程序化雜訊 → `textures/<名稱>_Pattern.png`，並包進檔案）、建立可讀的預覽材質（`scene["preview_palette"]`，sRGB）、開啟選取與 Extras、匯出 FBX、存版本化 `.blend`。
3. **驗證** `art/blender/verify_blend.py`：用全新的 Blender 程序打開存好的檔案檢查，必須全部 PASS。

命令列（在 repo 根目錄執行）：

```
blender -b --python art/blender/lamb_baby.py --python art/blender/finalize_export.py -- art/models/Lamb --unreal
blender -b art/models/Lamb/Lamb_Baby_v001.blend --python-exit-code 1 --python art/blender/verify_blend.py
```

成品放在 `art/models/<物種>/`**匯入有授權的現成模型**（例如小獅成體 v004）：用處理腳本（`art/blender/lion_adult_meshy.py`）取代造型腳本——減面、重展 UV、烘焙 ≤ 1024² 的顏色貼圖到 `art/models/<物種>/textures/`（也包進 `.blend`），並設定 `o["keep_uv"]`、`o["albedo"]`；沒有獨立的嘴時設 `scene["has_mouth"] = False`。來源與授權記在 `art/source/LICENSE.md`，所有違反設定檔的偏差寫進 worklog。

：`<名稱>_vNNN.blend`（永不覆蓋）、`<名稱>.fbx`（Unity 設定）、`<名稱>_UE.fbx`（Unreal 設定）。不要把 `.blend` 放進 Unity 的 `Assets/`。

| 設定 | 座標軸 | 比例 | 其他 |
| --- | --- | --- | --- |
| Unity | Forward −Z、Up Y、bake space transform | FBX_SCALE_ALL（1 公尺 = 1 單位） | 平滑 Face、顏色 Linear、不加 leaf bone |
| Unreal | Blender 預設（Forward −Z、Up Y），由 Unreal 匯入器換算 | FBX_SCALE_NONE（寫入公尺，Unreal 轉成公分） | 平滑 Face；頂點色匯入設為 Replace；光照貼圖 UV 於匯入時自動產生 |

## 版本

- 組長桌機：Blender 5.2。助手（雲端、無頭模式）：Blender 4.2.23 LTS。腳本必須兩個版本都能跑。每個 `.blend` 會記錄 `scene["spirit_built_with"]`。

## 流程決定

- **R04：**只有每個新資產或新網格階段第一次製作時需要完整複述；之後依回饋調整，用一句話說明後直接做。
- **R07：**CLAUDE.md、skill 文件、模板、本設定檔與 worklog 以英文為正本；繁體中文副本在同一次修改中一起更新。對話使用組長的語言（台灣繁體中文）。腳本註解維持繁體中文，方便學習。
- **進度：**`docs/PROGRESS.md` 只記美術大項目——每種動物、每個階段是否完成，以及流程／shader／骨架的里程碑。各版本的美術改動只寫在 worklog。
- **Worklog：**`docs/art-worklog/YYYY-MM-DD_NNN_<主題>.md`，英文，進版控，讓每台電腦、每個 session 都看得到。
- **教學：**組長一步一步學習；遇到新技巧與新術語要解釋（見[術語表](../.claude/skills/blendsmith/references/glossary.zh-TW.md)）。

## 專案經驗（摘要；細節見回饋登錄）

- 造型層次：大形 → 少量中形起伏 → 少量小細節。用 metaball 讓起伏融成一體。
- 先校正 metaball 大小：門檻 0.6 時，表面 = 0.574 × 半徑（stiffness 2）、0.66 ×（stiffness 3.5）。
- 有顆粒感的羊毛：毛球間距 ÷ 半徑 ≈ 2.4；每圈的顆數由周長算出來。
- 先做封閉的殼，再用負元素挖掉（例如毛帽挖出臉的窗口）。
- 配件用 Shrinkwrap 貼身：草稿要從「比毛還大的外殼」裡面開始。
- 三角形花在剪影上；畫面上很小的零件用低解析度的基本體。
