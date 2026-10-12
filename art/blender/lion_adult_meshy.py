# 小獅（成體，階段 3）—— v004：改用 CC0 的 Meshy「Lion Cub」模型，處理成遊戲規格
# 來源：art/source/Meshy_AI_Lion_Cub_1012072324_texture.blend（授權見 art/source/LICENSE.md）
# 用法（命令列，在 repo 根目錄）：
#   blender -b --python art/blender/lion_adult_meshy.py --python art/blender/finalize_export.py -- art/models/Lion --unreal
#
# 這支腳本不是「從零捏」，而是「重拓樸＋烘焙」（retopology + baking）的簡化版：
#   1) 把高面數模型（34 萬個三角形）原封不動借進來，叫它 High
#   2) 複製一份 Low，用 Decimate 減到 8000 以內（剪影保留，細節丟掉）
#   3) 幫 Low 重新展 UV（減面後原本的 UV 會被扯壞）
#   4) 烘焙（Bake）：從 Low 的每個點往外射光線，打到 High 的表面，把那裡的顏色抄到 Low 的貼圖上
#      → 細節（毛的紋路、臉）變成一張 1024² 的顏色貼圖，三角形卻只剩幾千個
#   5) 刪掉 High，交給 finalize_export.py 收尾
import bpy, os, math
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "art", "source", "Meshy_AI_Lion_Cub_1012072324_texture.blend")
TEX_DIR = os.path.join(REPO, "art", "models", "Lion", "textures")
TEX_NAME = "Lion_Adult_Albedo"
TEX_SIZE = 1024            # 美術設定檔：貼圖最大 1024²
TRI_TARGET = 7600          # 預算 8000，留一點餘裕給去除 n-gon
TARGET_HEIGHT = 1.42       # 跟 v003 成體同高（幼體約 1.1）

# ---------- 0) 清空場景 ----------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
    for d in list(coll):
        if d.users == 0:
            coll.remove(d)

# ---------- 1) 借入高面數模型（Append）：只拿物件，不執行來源檔裡的任何腳本 ----------
with bpy.data.libraries.load(SRC, link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n == "Mesh_0"]
high = dst.objects[0]
bpy.context.scene.collection.objects.link(high)
high.name = "High"

# 方向：來源檔的頭已經朝 −Y（= Unity 正前方），只要調大小、把腳底放到 Z=0、置中
bpy.context.view_layer.update()
high.select_set(True)
bpy.context.view_layer.objects.active = high
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
# 17 萬個點用 Python 一個一個算太慢，用 numpy 一次讀進陣列（foreach_get）
co = np.empty(len(high.data.vertices) * 3, dtype=np.float32)
high.data.vertices.foreach_get("co", co)
co = co.reshape(-1, 3)
(xmin, ymin, zmin), (xmax, ymax, zmax) = co.min(0), co.max(0)
xmid, ymid = (xmin + xmax) / 2, (ymin + ymax) / 2
s = TARGET_HEIGHT / (zmax - zmin)
high.location = (-xmid * s, -ymid * s, -zmin * s)
high.scale = (s, s, s)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# 烘焙只要「原本的顏色」：把來源材質改成「貼圖 → 自發光」，不受光線、金屬度影響
src_mat = high.data.materials[0]
base_tex = next(l.from_node for l in src_mat.node_tree.links
                if l.to_socket.name == "Base Color" and l.from_node.type == 'TEX_IMAGE')
nt = src_mat.node_tree
emit = nt.nodes.new("ShaderNodeEmission")
out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
nt.links.new(base_tex.outputs["Color"], emit.inputs["Color"])
nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])

# ---------- 2) 複製一份 Low，減面到預算內 ----------
low = high.copy(); low.data = high.data.copy()
bpy.context.scene.collection.objects.link(low)
low.name = "Body"
n_tris = sum(len(p.vertices) - 2 for p in high.data.polygons)
dec = low.modifiers.new("Decimate", 'DECIMATE')
dec.ratio = TRI_TARGET / n_tris
dec.use_symmetry = True          # 左右對稱地減面，臉不會一邊歪
dec.symmetry_axis = 'X'
bpy.ops.object.select_all(action='DESELECT')
low.select_set(True)
bpy.context.view_layer.objects.active = low
bpy.ops.object.modifier_apply(modifier=dec.name)
bpy.ops.object.shade_smooth()
print("減面：", n_tris, "→", sum(len(p.vertices) - 2 for p in low.data.polygons))

# ---------- 3) Low 重新展 UV ----------
for uv in list(low.data.uv_layers):
    low.data.uv_layers.remove(uv)
low.data.uv_layers.new(name="UVMap")
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

# ---------- 4) 烘焙：High 的顏色 → Low 的貼圖 ----------
img = bpy.data.images.new(TEX_NAME, TEX_SIZE, TEX_SIZE)
bake_mat = bpy.data.materials.new("BakeTarget"); bake_mat.use_nodes = True
tex = bake_mat.node_tree.nodes.new("ShaderNodeTexImage"); tex.image = img
bake_mat.node_tree.nodes.active = tex          # 烘焙會寫進「目前選取的」貼圖節點
low.data.materials.clear(); low.data.materials.append(bake_mat)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 1                       # 自發光不需要多次取樣
bpy.ops.object.select_all(action='DESELECT')
high.select_set(True); low.select_set(True)
bpy.context.view_layer.objects.active = low    # 選取的(High) → 作用中的(Low)
bpy.ops.object.bake(type='EMIT', use_selected_to_active=True,
                    cage_extrusion=0.03,       # 從 Low 表面外 3 公分往內射，才打得到稍微凸出去的 High
                    max_ray_distance=0.08,
                    margin=16)                 # 島的邊緣往外多塗 16 像素，避免縫線露出底色

os.makedirs(TEX_DIR, exist_ok=True)
path = os.path.join(TEX_DIR, TEX_NAME + ".png")
img.filepath_raw = path
img.file_format = 'PNG'
img.save()
img.pack()                                     # 也包進 .blend，換電腦打開不會掉貼圖
print("已烘焙：", path)

# ---------- 5) 刪掉 High 和來源資料，交給 finalize ----------
bpy.data.objects.remove(high)
for d in list(bpy.data.meshes):
    if d.users == 0: bpy.data.meshes.remove(d)
for d in list(bpy.data.materials):
    if d.users == 0: bpy.data.materials.remove(d)
for d in list(bpy.data.images):
    if d.users == 0: bpy.data.images.remove(d)

low["mask"] = (1, 0, 0, 1)        # 整隻都是主色槽：主色白色 = 貼圖原色；換配色 = 貼圖乘上顏色（例如白獅）
low["keep_uv"] = True             # 告訴 finalize：UV 已經烘焙好，不要重展
low["albedo"] = img.name          # 告訴 finalize：預覽材質要乘上這張貼圖
scene["spirit_name"] = "Lion_Adult"
scene["has_mouth"] = False        # 偏差：沒有獨立的嘴（嘴畫在貼圖上），張嘴動畫之後用 shape key 或另做
