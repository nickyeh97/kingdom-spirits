# 靈獸收尾腳本：metaball 轉網格、減面、套用變換、配色遮罩、合併、預覽材質、匯出 FBX
# 用法：先跑 lamb_baby.py（或其他靈獸造型腳本），存檔後在同一場景執行本檔。
# 第 5 課
import bpy

def tris(o):
    """數一個物件「實際顯示」的三角形數（含 modifier 的效果）。"""
    dg = bpy.context.evaluated_depsgraph_get()
    m = o.evaluated_get(dg).to_mesh()
    m.calc_loop_triangles()
    n = len(m.loop_triangles)
    o.evaluated_get(dg).to_mesh_clear()
    return n

def select_only(o):
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o

NAME = bpy.context.scene.get("spirit_name", "Lamb_Baby")   # 造型腳本會寫入輸出名稱

# 1) 曲線（羊角）→ 網格：曲線跟 metaball 一樣是「算出來的」，Unity 看不懂
for o in [o for o in bpy.data.objects if o.type == 'CURVE']:
    base = o.name.split(".")[0]
    select_only(o)
    bpy.ops.object.convert(target='MESH')
    bpy.context.active_object.name = base

# Metaball → 一般網格（Unity 只看得懂網格）
wool = bpy.data.objects["WoolCloud"]
select_only(wool)
bpy.ops.object.convert(target='MESH')
wool = bpy.context.active_object
wool.name = "Wool"                       # 轉換後名字會變，順手改回好認的
print("轉換後羊毛：", tris(wool))

# 2) 減面：Decimate（Collapse）只保留 15% 的面
dec = wool.modifiers.new("Decimate", 'DECIMATE')
dec.ratio = 0.15
print("減面後羊毛：", tris(wool))
bpy.ops.object.modifier_apply(modifier=dec.name)   # 套用 = 真的改掉網格
bpy.ops.object.shade_smooth()

# 3) 套用旋轉與縮放（Ctrl+A → Rotation & Scale）：把變換「烘」進網格
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# 4) 預算檢查
total = sum(tris(o) for o in bpy.data.objects if o.type == 'MESH')
print(f"全身三角形：{total}（成體預算 8000）")

# 第 6 課
import bpy, os

# ---------- 1) 每個零件屬於哪個「色槽」 ----------
# 色槽（可換色）：A = 1，RGB 用「哪個通道亮」表示是哪一槽
PRIMARY   = (1, 0, 0, 1)   # 主色   ← 羊毛
SECONDARY = (0, 1, 0, 1)   # 副色   ← 臉、耳朵、腳
ACCENT    = (0, 0, 1, 1)   # 點綴色 ← 臉頰、內耳
# 固定色（永遠不換）：A = 0，RGB 直接就是顏色本身
INK   = (0.02, 0.02, 0.03, 0)   # 眼睛、鼻子、嘴、蹄
WHITE = (1, 1, 1, 0)            # 眼睛反光

SLOT = {
    "Wool": PRIMARY,
    "Head": SECONDARY, "Ear": SECONDARY, "Leg": SECONDARY,
    "Cheek": ACCENT, "EarInner": ACCENT, "Horn": ACCENT,
    "Eye": INK, "Nose": INK, "Mouth": INK, "MouthLine": INK, "Hoof": INK,
    "EyeShine": WHITE,
}

for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    base = o.name.split(".")[0]            # "Ear.001" → "Ear"
    if base not in SLOT:
        raise ValueError(f"不知道 {o.name} 屬於哪個色槽，請加進 SLOT")
    mesh = o.data
    if "Mask" in mesh.color_attributes:
        mesh.color_attributes.remove(mesh.color_attributes["Mask"])
    attr = mesh.color_attributes.new("Mask", 'FLOAT_COLOR', 'CORNER')
    for c in attr.data:
        c.color = SLOT[base]

# ---------- 2) 合併：除了嘴以外全部合成一個網格 ----------
mouth = bpy.data.objects["Mouth"]
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.type == 'MESH' and o is not mouth:
        o.select_set(True)
body = bpy.data.objects["Wool"]
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()
body.name = NAME

# 嘴保持獨立（要做張嘴動畫），設成身體的子物件，一起移動
mouth.parent = body
mouth.matrix_parent_inverse = body.matrix_world.inverted()

# ---------- 3) Blender 裡的預覽材質：用跟 Unity 一樣的公式上色 ----------
def make_preview_material(primary, secondary, accent):
    m = bpy.data.materials.get("SpiritPreview") or bpy.data.materials.new("SpiritPreview")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    attr = nt.nodes.new("ShaderNodeVertexColor"); attr.layer_name = "Mask"
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(attr.outputs["Color"], sep.inputs["Color"])

    def scaled(color, channel):                 # 通道值 × 該槽顏色
        n = nt.nodes.new("ShaderNodeVectorMath"); n.operation = 'SCALE'
        n.inputs[0].default_value = color[:3]
        nt.links.new(sep.outputs[channel], n.inputs["Scale"])
        return n.outputs[0]
    def add(a, b):
        n = nt.nodes.new("ShaderNodeVectorMath"); n.operation = 'ADD'
        nt.links.new(a, n.inputs[0]); nt.links.new(b, n.inputs[1])
        return n.outputs[0]
    palette = add(add(scaled(primary, "Red"), scaled(secondary, "Green")), scaled(accent, "Blue"))

    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'   # A=0 用固定色、A=1 用色槽
    nt.links.new(attr.outputs["Alpha"], mix.inputs["Factor"])
    nt.links.new(attr.outputs["Color"], mix.inputs[6])            # A：固定色
    nt.links.new(palette, mix.inputs[7])                          # B：色槽混出來的顏色
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.8
    nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m

mat = make_preview_material((0.96, 0.93, 0.86), (1.0, 0.95, 0.90), (0.95, 0.55, 0.65))
for o in (body, mouth):
    o.data.materials.clear()
    o.data.materials.append(mat)

# ---------- 4) 匯出 FBX 給 Unity ----------
path = bpy.path.abspath(f"//{NAME}.fbx") if bpy.data.filepath else os.path.join(os.path.expanduser("~"), f"{NAME}.fbx")
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True); mouth.select_set(True)
bpy.ops.export_scene.fbx(
    filepath=path,
    use_selection=True,
    object_types={'MESH'},
    apply_scale_options='FBX_SCALE_ALL',   # 1 Blender 公尺 = 1 Unity 單位
    axis_forward='-Z', axis_up='Y',        # 換成 Unity 的座標軸
    bake_space_transform=True,             # 進 Unity 後不會多出 -90° 的 X 旋轉
    colors_type='LINEAR',                  # 遮罩數值原封不動（不做 sRGB 轉換）
    mesh_smooth_type='FACE',
    add_leaf_bones=False,
)
print("已匯出：", path)
