# 美術素材來源與授權

每個進到遊戲的模型、貼圖都記在這裡，出處要能追溯（docs/ART_PIPELINE.md §3）。

| 檔案 | 來源 | 授權 | 備註 |
| --- | --- | --- | --- |
| `Resources/Beasts/Lamb_Baby.fbx`、`Lamb_Adult.fbx`、`Lamb_Leader.fbx` | 本專案以 Blender 程序化腳本建模（美術分支 `claude/nice-pasteur-ubt4t1` 的 `art/blender/lamb_*.py`＋`finalize_export.py`，v001 交付 commit `c2558da`，2026-10-14 搬入） | 本專案原創 | 沒有花紋貼圖 |
| `Resources/Beasts/Lion_Baby.fbx`、`Lion_Adult.fbx`、`Lion_Leader.fbx`（2026-10-29 起含骨架與六個動作，`rig_quadruped.py`） | 本專案以 Blender 程序化腳本建模（分支 `claude/nice-pasteur-ubt4t1` 的 `art/blender/lion_*.py`＋`finalize_export.py`，commit `b0bc82d`，2026-10-14 搬入） | 本專案原創 | Q 版造型；Meshy 社群的 CC0「Lion Cub」模型只當輪廓與毛色參考，未收進遊戲（見該分支 `art/source/LICENSE.md`） |
| `Resources/Beasts/Lion_*_Pattern.png` | 同上，收尾腳本以程序化雜訊烘焙的花紋遮罩（512²，灰階，sRGB） | 本專案原創 | 著色器把它乘在色槽顏色上，做出獅子毛色的深淺 |
| `Resources/Beasts/Dove_Baby.fbx`、`Dove_Adult.fbx`、`Dove_Leader.fbx` | 本專案以 Blender 程序化腳本建模（`art/blender/dove_baby.py`、`dove_adult.py`、`dove_leader.py`＋`finalize_export.py`，幼體 v004、成體 v003、小領袖 v004，2026-10-21／10-29） | 本專案原創 | 沒有參考任何外部模型 |
| `Assets/Resources/Icons/Service/*.png`、`Icons/Fruits/*.png`（六項服事、九顆果子） | 本專案以 Blender 程序化腳本繪製（`Tools/make_icons.py`，2026-10-29） | 本專案原創 | 128×128 透明背景；果子與美德的對應只是視覺記號 |
| `Resources/Beasts/Dove_*_Pattern.png` | 收尾腳本以程序畫在翅膀與尾羽上的羽毛圓弧遮罩（512²，灰階） | 本專案原創 | 遊戲從階段 2 才顯示（`BeastForms.PatternStrength`） |
