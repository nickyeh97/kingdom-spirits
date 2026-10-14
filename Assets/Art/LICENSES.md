# 美術素材來源與授權

每個進到遊戲的模型、貼圖都記在這裡，出處要能追溯（docs/ART_PIPELINE.md §3）。

| 檔案 | 來源 | 授權 | 備註 |
| --- | --- | --- | --- |
| `Resources/Beasts/Lion_Baby.fbx`、`Lion_Adult.fbx`、`Lion_Leader.fbx` | 本專案以 Blender 程序化腳本建模（分支 `claude/nice-pasteur-ubt4t1` 的 `art/blender/lion_*.py`＋`finalize_export.py`，commit `b0bc82d`，2026-10-14 搬入） | 本專案原創 | Q 版造型；Meshy 社群的 CC0「Lion Cub」模型只當輪廓與毛色參考，未收進遊戲（見該分支 `art/source/LICENSE.md`） |
| `Resources/Beasts/Lion_*_Pattern.png` | 同上，收尾腳本以程序化雜訊烘焙的花紋遮罩（512²，灰階，sRGB） | 本專案原創 | 著色器把它乘在色槽顏色上，做出獅子毛色的深淺 |
