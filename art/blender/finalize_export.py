# 靈獸收尾腳本：metaball 轉網格、減面、套用變換、去除 n-gon、配色遮罩、合併、展 UV、
#               預覽材質、匯出 FBX、存版本化 .blend
# 用法（Blender 介面）：先跑造型腳本（例如 lamb_baby.py），存檔後在同一場景執行本檔；
#                      FBX 與 .blend 會輸出到 .blend 所在資料夾。
# 用法（命令列）：blender -b --python lamb_baby.py --python finalize_export.py -- <輸出資料夾> [--unreal]
# 之後用 verify_blend.py 重新開檔驗證（blendsmith R11）。
# 第 5 課
import bpy, os, sys

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
UNREAL = "--unreal" in ARGS
OUT_DIR = next((a for a in ARGS if not a.startswith("--")), None) or \
          (bpy.path.abspath("//") if bpy.data.filepath else os.path.expanduser("~"))
os.makedirs(OUT_DIR, exist_ok=True)

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
# 造型腳本可在 metaball 物件上設 o["mesh_name"]（例如小獅的 "Fur"）；沒設就叫 "Wool"（小羊）
fur_meshes = []
for o in [o for o in bpy.data.objects if o.type == 'META']:
    mesh_name = o.get("mesh_name", "Wool")
    select_only(o)
    bpy.ops.object.convert(target='MESH')
    m = bpy.context.active_object
    m.name = mesh_name                   # 轉換後名字會變，順手改回好認的
    fur_meshes.append(m)
    print(f"轉換後 {mesh_name}：", tris(m))

# 2) 減面：Decimate（Collapse）—— 用「目標面數」反推比例，毛變多變少都會落在預算內
#    目標是所有毛加起來的面數，依各自大小分配
WOOL_TRI_TARGET = bpy.context.scene.get("wool_tri_target", 3000)   # 造型腳本可自訂（角越大，毛就要越省）
fur_total = sum(tris(m) for m in fur_meshes) or 1
for m in fur_meshes:
    select_only(m)
    dec = m.modifiers.new("Decimate", 'DECIMATE')
    dec.ratio = min(1.0, WOOL_TRI_TARGET / fur_total)
    print(f"減面後 {m.name}：", tris(m))
    bpy.ops.object.modifier_apply(modifier=dec.name)   # 套用 = 真的改掉網格
    bpy.ops.object.shade_smooth()

# 3) 套用旋轉與縮放（Ctrl+A → Rotation & Scale）：把變換「烘」進網格
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# 4) R03：不能有 n-gon（5 邊以上的面）。圓柱、圓錐的蓋子和曲線的封口都是 n-gon。
#    用 Poke 在每個 n-gon 中心加一個點、拉成一圈小三角形（從中心放射，不是從邊上某一點拉長扇形）。
import bmesh
for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    bm = bmesh.new()
    bm.from_mesh(o.data)
    ngons = [f for f in bm.faces if len(f.verts) > 4]
    if ngons:
        bmesh.ops.poke(bm, faces=ngons)
        bm.to_mesh(o.data)
    bm.free()

# 5) 預算檢查
total = sum(tris(o) for o in bpy.data.objects if o.type == 'MESH')
print(f"全身三角形：{total}（成體預算 8000）")

# 第 6 課

# ---------- 1) 每個零件屬於哪個「色槽」 ----------
# 色槽（可換色）：A = 1，RGB 用「哪個通道亮」表示是哪一槽
PRIMARY   = (1, 0, 0, 1)   # 主色   ← 羊毛
SECONDARY = (0, 1, 0, 1)   # 副色   ← 臉、耳朵、腳
ACCENT    = (0, 0, 1, 1)   # 點綴色 ← 臉頰、內耳
# 固定色（永遠不換）：A = 0，RGB 直接就是顏色本身
INK   = (0.02, 0.02, 0.03, 0)   # 眼睛、鼻子、嘴、蹄
WHITE = (1, 1, 1, 0)            # 眼睛反光
HORN  = (0.85, 0.70, 0.45, 0)   # 羊角：固定的象牙色（若放進點綴色槽，會跟臉頰同色）
GOLD  = (0.95, 0.76, 0.30, 0)   # 金扣、角環
LINING = (0.70, 0.12, 0.16, 0)  # 披風立領內裡

SLOT = {
    "Wool": PRIMARY,
    "Head": SECONDARY, "Ear": SECONDARY, "Leg": SECONDARY,
    "Cheek": ACCENT, "EarInner": ACCENT,
    "Horn": HORN,
    "Cape": ACCENT, "Capelet": ACCENT,             # 小領袖披風、肩披：跟著配色換
    "CapeCollar": LINING,                          # 立領內裡：固定紅
    "Clasp": GOLD, "CapeCord": GOLD, "HornBand": GOLD,   # 金扣、飾繩、角環：固定金色
    "Eye": INK, "Nose": INK, "Mouth": INK, "MouthLine": INK, "Hoof": INK,
    "EyeShine": WHITE,
    # 小獅：主色＝身體的皮；副色＝可愛的肉色；點綴色＝毛（頭頂、兩頰、尾巴毛球）
    "Body": PRIMARY, "Tail": PRIMARY,
    "Belly": SECONDARY, "Muzzle": SECONDARY, "Chin": SECONDARY, "Paw": SECONDARY,
    "Fur": ACCENT,
}

for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    base = o.name.split(".")[0]            # "Ear.001" → "Ear"
    # 造型腳本可以直接在物件上寫 o["mask"] = (R, G, B, A)，優先於下面的名稱對照表
    # （例如小獅的腮紅、肉球是固定粉紅，跟小羊用點綴色的 Cheek 不同）
    if "mask" in o:
        slot = tuple(o["mask"])
    elif base in SLOT:
        slot = SLOT[base]
    else:
        raise ValueError(f"不知道 {o.name} 屬於哪個色槽，請加進 SLOT 或在造型腳本設定 o['mask']")
    mesh = o.data
    if "Mask" in mesh.color_attributes:
        mesh.color_attributes.remove(mesh.color_attributes["Mask"])
    attr = mesh.color_attributes.new("Mask", 'FLOAT_COLOR', 'CORNER')
    for c in attr.data:
        c.color = slot
    # 內襯：造型腳本標了 lining = 1 的面，改用「同一個色槽 × 0.45」。
    # 公式是 R×主色 + G×副色 + B×點綴色，所以通道值給 0.45 就是那個顏色的 45% 亮度＝深色系，
    # 不用新增色槽，換配色時內襯也會自動變成新顏色的深色。
    if "lining" in mesh.attributes and slot[3] == 1:
        dark = tuple(v * 0.45 for v in slot[:3]) + (1,)
        lining = mesh.attributes["lining"].data
        for poly in mesh.polygons:
            if lining[poly.index].value:
                for li in poly.loop_indices:
                    attr.data[li].color = dark

# ---------- 2) 合併：除了嘴以外全部合成一個網格 ----------
mouth = bpy.data.objects["Mouth"]
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.type == 'MESH' and o is not mouth:
        o.select_set(True)
body = max((o for o in bpy.data.objects if o.type == 'MESH' and o is not mouth), key=tris)   # 以最大的零件為主體
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()
body.name = NAME

# 嘴保持獨立（要做張嘴動畫），設成身體的子物件，一起移動
mouth.parent = body
mouth.matrix_parent_inverse = body.matrix_world.inverted()

# ---------- 3) Blender 裡的預覽材質：用跟 Unity 一樣的公式上色 ----------
def make_preview_material(primary, secondary, accent):
    """R01：節點由左到右排列（遮罩 → 拆通道 → 乘上色槽顏色 → 相加 → 選固定色或色槽 → BSDF → 輸出），
    用 Frame 分區、每個節點都有名字，打開 Shader Editor 一看就懂。"""
    m = bpy.data.materials.get("SpiritPreview") or bpy.data.materials.new("SpiritPreview")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()

    def node(kind, label, x, y, frame=None):
        n = nt.nodes.new(kind)
        n.label = n.name = label
        n.location = (x, y)
        if frame:
            n.parent = frame
        return n

    f_in = node("NodeFrame", "1 Colour mask (vertex colour)", 0, 0)
    f_pal = node("NodeFrame", "2 Palette slots: R=primary G=secondary B=accent", 0, 0)
    f_out = node("NodeFrame", "3 Fixed colour vs palette, shading", 0, 0)

    attr = node("ShaderNodeVertexColor", "Mask", -900, 0, f_in); attr.layer_name = "Mask"
    sep = node("ShaderNodeSeparateColor", "Split RGB", -680, 120, f_in)
    nt.links.new(attr.outputs["Color"], sep.inputs["Color"])

    def scaled(color, channel, label, y):        # 通道值 × 該槽顏色
        n = node("ShaderNodeVectorMath", label, -440, y, f_pal); n.operation = 'SCALE'
        n.inputs[0].default_value = color[:3]
        nt.links.new(sep.outputs[channel], n.inputs["Scale"])
        return n.outputs[0]
    def add(a, b, label, x, y):
        n = node("ShaderNodeVectorMath", label, x, y, f_pal); n.operation = 'ADD'
        nt.links.new(a, n.inputs[0]); nt.links.new(b, n.inputs[1])
        return n.outputs[0]
    p = scaled(primary, "Red", "Primary colour", 260)
    s_ = scaled(secondary, "Green", "Secondary colour", 80)
    a = scaled(accent, "Blue", "Accent colour", -100)
    palette = add(add(p, s_, "Primary + Secondary", -220, 180), a, "+ Accent", -40, 80)

    mix = node("ShaderNodeMix", "Fixed or palette (alpha)", 160, 60, f_out); mix.data_type = 'RGBA'
    nt.links.new(attr.outputs["Alpha"], mix.inputs["Factor"])
    nt.links.new(attr.outputs["Color"], mix.inputs[6])            # A：固定色
    nt.links.new(palette, mix.inputs[7])                          # B：色槽混出來的顏色
    bsdf = node("ShaderNodeBsdfPrincipled", "Preview BSDF", 380, 60, f_out)
    bsdf.inputs["Roughness"].default_value = 0.8
    nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    out = node("ShaderNodeOutputMaterial", "Output", 680, 60, f_out)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m

mat = make_preview_material((0.96, 0.93, 0.86), (1.0, 0.95, 0.90), (0.95, 0.55, 0.65))
for o in (body, mouth):
    o.data.materials.clear()
    o.data.materials.append(mat)

# ---------- 4) R03：每個網格都要展 UV（NPR、PBR 都需要；之後的花紋遮罩就畫在這組 UV 上） ----------
for o in (body, mouth):
    select_only(o)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.01)   # 約 66°；島與島之間留間距
    bpy.ops.object.mode_set(mode='OBJECT')

# ---------- 5) R06：交付時物件都能選取、每個 3D 視窗的 Overlays 與 Extras 都開著 ----------
for o in bpy.data.objects:
    o.hide_select = False
for c in bpy.data.collections:
    c.hide_select = False
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            sp = area.spaces.active
            sp.overlay.show_overlays = True
            sp.overlay.show_extras = True

# ---------- 6) R12：匯出 FBX 給遊戲引擎 ----------
def export_fbx(path, preset):
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True); mouth.select_set(True)
    common = dict(filepath=path, use_selection=True, object_types={'MESH'},
                  colors_type='LINEAR',            # 遮罩數值原封不動（不做 sRGB 轉換）
                  mesh_smooth_type='FACE',         # 寫入平滑群組，引擎不會警告
                  add_leaf_bones=False)
    if preset == "unity":
        bpy.ops.export_scene.fbx(**common,
            apply_scale_options='FBX_SCALE_ALL',   # 1 Blender 公尺 = 1 Unity 單位
            axis_forward='-Z', axis_up='Y',        # 換成 Unity 的座標軸
            bake_space_transform=True)             # 進 Unity 後不會多出 -90° 的 X 旋轉
    else:
        # Unreal：保留 Blender 預設軸向，由 Unreal 匯入器換算；FBX 內記錄公尺，Unreal 會換成公分。
        # 尚未在 Unreal 實際匯入驗證（R12：NOT RUN），第一次使用時要檢查朝向與比例。
        bpy.ops.export_scene.fbx(**common, apply_scale_options='FBX_SCALE_NONE',
                                 axis_forward='-Z', axis_up='Y')
    print("已匯出：", path)

export_fbx(os.path.join(OUT_DIR, f"{NAME}.fbx"), "unity")
if UNREAL:
    export_fbx(os.path.join(OUT_DIR, f"{NAME}_UE.fbx"), "unreal")

# ---------- 7) R11：存成版本化的 .blend（不覆蓋舊版） ----------
v = 1
while os.path.exists(os.path.join(OUT_DIR, f"{NAME}_v{v:03d}.blend")):
    v += 1
blend_path = os.path.join(OUT_DIR, f"{NAME}_v{v:03d}.blend")
bpy.context.scene["spirit_built_with"] = bpy.app.version_string
bpy.ops.wm.save_as_mainfile(filepath=blend_path, copy=True)   # copy=True：目前開著的檔案不會被換掉
print("已存檔：", blend_path)
