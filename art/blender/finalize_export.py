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
    "Fur": ACCENT, "Chest": SECONDARY, "EyeRim": SECONDARY, "TailTuft": ACCENT,
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
    # 淺色漸層：造型腳本在點上寫了 light（0–1），往副色混過去（例如獅子的喉嚨、胸口、肚子）
    if "light" in mesh.attributes and slot[3] == 1:
        light = mesh.attributes["light"].data
        for poly in mesh.polygons:
            for li, vi in zip(poly.loop_indices, poly.vertices):
                c = attr.data[li].color
                k = light[vi].value
                attr.data[li].color = (c[0] * (1 - k), c[1] * (1 - k) + k, c[2] * (1 - k), 1)
    # 深淺漸層：造型腳本在點上寫了 shade（0–1），色槽通道就乘上它（例如獅子背脊比較深）。
    # 跟內襯同一個原理（通道值 < 1 ＝ 同色系的深色），只是每個點不一樣、會平滑漸變。
    if "shade" in mesh.attributes and slot[3] == 1:
        shade = mesh.attributes["shade"].data
        for poly in mesh.polygons:
            for li, vi in zip(poly.loop_indices, poly.vertices):
                c = attr.data[li].color
                k = shade[vi].value
                attr.data[li].color = (c[0] * k, c[1] * k, c[2] * k, 1)

# ---------- 2) 合併：除了嘴以外全部合成一個網格 ----------
# 匯入的現成模型（例如 lion_adult_meshy.py）沒有獨立的嘴：造型腳本設 scene["has_mouth"] = False
HAS_MOUTH = bpy.context.scene.get("has_mouth", True)
mouth = bpy.data.objects["Mouth"] if HAS_MOUTH else None
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.type == 'MESH' and o is not mouth:
        o.select_set(True)
body = max((o for o in bpy.data.objects if o.type == 'MESH' and o is not mouth), key=tris)   # 以最大的零件為主體
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()
body.name = NAME
# 原點一律放回世界原點（腳底中央）：合併後的原點是「主體零件」的原點，
# 主體若是建在別處的零件（例如小鴿幼體最大的零件是頭，原點在頭中心），進引擎後整隻會往下沉
bpy.context.scene.cursor.location = (0, 0, 0)
select_only(body)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

# 嘴保持獨立（要做張嘴動畫），設成身體的子物件，一起移動
if mouth:
    mouth.parent = body
    mouth.matrix_parent_inverse = body.matrix_world.inverted()
parts = [o for o in (body, mouth) if o]

# ---------- 3) Blender 裡的預覽材質：用跟 Unity 一樣的公式上色 ----------
def make_preview_material(primary, secondary, accent, texture=None):
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
    bsdf = node("ShaderNodeBsdfPrincipled", "Preview BSDF", 380, 60, f_out)
    bsdf.inputs["Roughness"].default_value = 0.8
    if texture:                                  # 貼圖（烘焙的顏色或花紋遮罩）× 色槽顏色；固定色不受影響
        tex = node("ShaderNodeTexImage", "Texture (albedo or pattern)", -680, -260, f_in); tex.image = texture
        mul = node("ShaderNodeMix", "Texture x palette", 120, -160, f_pal)
        mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs["Factor"].default_value = 1
        nt.links.new(palette, mul.inputs[6]); nt.links.new(tex.outputs["Color"], mul.inputs[7])
        palette = mul.outputs[2]
    nt.links.new(palette, mix.inputs[7])                          # B：色槽混出來的顏色
    nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    out = node("ShaderNodeOutputMaterial", "Output", 680, 60, f_out)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m

# ---------- 4) R03：每個網格都要展 UV（NPR、PBR 都需要；之後的花紋遮罩就畫在這組 UV 上） ----------
for o in parts:
    if o.get("keep_uv"):                         # 已烘焙貼圖的 UV 不能重展，不然貼圖會對不上
        continue
    select_only(o)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.01)   # 約 66°；島與島之間留間距
    bpy.ops.object.mode_set(mode='OBJECT')

# ---------- 4b) 花紋遮罩：用程序化雜訊「烘」成一張灰階貼圖（例如獅子的毛流紋理） ----------
# 造型腳本設 scene["pattern"] = {"size": 512, "scale": (x, y, z), "low": 0.8, "high": 1.0}
#   kind："noise"（預設，毛流）或 "scales"（羽毛鱗紋，只畫在副色上；參數見 bake_feather_scales）
#   scale：雜訊在 x、y、z 方向的密度。z 小 → 雜訊沿上下方向拉長 → 看起來像往下梳的毛
#   low/high：最暗、最亮的倍率（1 = 不變暗）。引擎裡「色槽顏色 × 花紋」，固定色不受影響
# 3D 雜訊不會重複，不會有「同一塊圖複製貼上」的感覺；貼圖只是把它記錄在 UV 上給引擎用。
def bake_feather_scales(body, img, P):
    """
    羽毛鱗紋（小鴿）：一排一排的小圓弧（像插畫裡的鳥翅膀），只畫在副色（翅膀、尾羽）上。
    不用節點烘焙：直接在 Python 裡把每個三角形「畫」到 UV 貼圖上（光柵化），
    每個像素用它在模型上的 3D 位置算出圖案 → 圓弧大小以公分計，不受 UV 拉伸影響。
      spacing：一片羽毛的寬度（公尺）；rim：圓弧線的粗細（佔羽片寬度的比例）；low：圓弧最深的倍率
    圖案：前面一排蓋住後面一排（像屋瓦），看得到的是每片羽毛「往後的那道圓弧」→ 羽毛尖朝尾巴。
    """
    import numpy as np
    size = img.size[0]
    sp = float(P.get("spacing", 0.045))
    r = sp * 0.62                                  # 每片羽毛是半徑 r 的圓
    rows = sp * 0.55                               # 排與排的間距（比寬度小 → 互相重疊）
    rim = sp * float(P.get("rim", 0.16))
    low = float(P.get("low", 0.72))
    me = body.data
    me.calc_loop_triangles()
    n_loops = len(me.loops)
    uv = np.zeros(n_loops * 2); me.uv_layers.active.data.foreach_get("uv", uv); uv = uv.reshape(-1, 2)
    col = np.zeros(n_loops * 4); me.color_attributes["Mask"].data.foreach_get("color", col); col = col.reshape(-1, 4)
    co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    vidx = np.zeros(n_loops, dtype=np.int64); me.loops.foreach_get("vertex_index", vidx)
    out = np.ones((size, size), dtype=np.float32)

    def pattern(a, b):
        """a：沿著羽片排列的方向；b：往後（−b＝往前）。回傳 1（沒有線）～ low（圓弧線上）。"""
        val = np.ones_like(a)
        done = np.zeros(a.shape, dtype=bool)
        k0 = np.floor(b / rows)
        for dk in (-1, 0, 1, 2):                   # 前面的排（b 小）先畫、會蓋住後面的 → 由前往後找第一個蓋住這點的圓
            k = k0 + dk - 1
            off = np.where(np.mod(k, 2) == 0, 0.0, sp / 2)
            ac = np.round((a - off) / sp) * sp + off
            bc = k * rows
            d = np.hypot(a - ac, b - bc)
            inside = (d < r) & ~done
            line = np.clip((d - (r - rim)) / (rim * 0.5), 0.0, 1.0)     # 圓的外緣那一圈變深（邊緣柔和）
            val = np.where(inside, 1.0 - (1.0 - low) * line, val)
            done |= inside
        return val

    for tri in me.loop_triangles:
        L = list(tri.loops)
        c = col[L]
        if not (c[:, 3].mean() > 0.5 and c[:, 1].mean() > 0.6 and c[:, 0].mean() < 0.3 and c[:, 2].mean() < 0.3):
            continue                               # 只畫副色（翅膀、尾羽）
        t = uv[L] * size
        p = co[vidx[L]]
        n = np.cross(p[1] - p[0], p[2] - p[0]); n = np.abs(n)
        # 依面的朝向選投影平面：側面（翅膀）用 YZ、上下（尾巴）用 YX、正背面用 XZ
        if n[0] >= n[1] and n[0] >= n[2]:
            A, Bv = p[:, 2], p[:, 1]
        elif n[2] >= n[1]:
            A, Bv = p[:, 0], p[:, 1]
        else:
            A, Bv = p[:, 0], p[:, 2]
        x0, y0 = np.floor(t.min(0)).astype(int); x1, y1 = np.ceil(t.max(0)).astype(int)
        x0, y0 = max(x0 - 1, 0), max(y0 - 1, 0); x1, y1 = min(x1 + 1, size - 1), min(y1 + 1, size - 1)
        if x1 < x0 or y1 < y0:
            continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        (ax, ay), (bx, by), (cx, cy) = t
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-12:
            continue
        w0 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / den
        w1 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / den
        w2 = 1 - w0 - w1
        m = (w0 >= -0.02) & (w1 >= -0.02) & (w2 >= -0.02)   # 稍微往外多畫一點，接縫不會露白
        if not m.any():
            continue
        a = w0 * A[0] + w1 * A[1] + w2 * A[2]
        b = w0 * Bv[0] + w1 * Bv[1] + w2 * Bv[2]
        v = pattern(a[m], b[m])
        yy, xx = (ys[m] - 0.5).astype(int), (xs[m] - 0.5).astype(int)
        out[yy, xx] = np.minimum(out[yy, xx], v)
    rgba = np.repeat(out.reshape(-1, 1), 4, axis=1); rgba[:, 3] = 1.0
    img.pixels.foreach_set(rgba.ravel())


PATTERN = bpy.context.scene.get("pattern")
if PATTERN:
    size = int(PATTERN.get("size", 512))
    img = bpy.data.images.new(f"{NAME}_Pattern", size, size)
    if PATTERN.get("kind") == "scales":
        bake_feather_scales(body, img, PATTERN)
    else:
        tmp = bpy.data.materials.new("PatternBake"); tmp.use_nodes = True
        nt = tmp.node_tree; nt.nodes.clear()
        coord = nt.nodes.new("ShaderNodeTexCoord")
        mapping = nt.nodes.new("ShaderNodeMapping"); mapping.inputs["Scale"].default_value = tuple(PATTERN["scale"])
        nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
        ramp = nt.nodes.new("ShaderNodeMapRange")
        ramp.inputs["To Min"].default_value = float(PATTERN.get("low", 0.8))
        ramp.inputs["To Max"].default_value = float(PATTERN.get("high", 1.0))
        # 程序化雜訊（小獅的毛流）
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 1.0
        noise.inputs["Detail"].default_value = float(PATTERN.get("detail", 4))
        ramp.inputs["From Min"].default_value, ramp.inputs["From Max"].default_value = 0.3, 0.7   # 雜訊 0.3–0.7 → low–high
        nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
        nt.links.new(noise.outputs["Fac"], ramp.inputs["Value"])
        value = ramp.outputs["Result"]
        emit = nt.nodes.new("ShaderNodeEmission"); out = nt.nodes.new("ShaderNodeOutputMaterial")
        target = nt.nodes.new("ShaderNodeTexImage"); target.image = img; nt.nodes.active = target
        nt.links.new(value, emit.inputs["Color"])
        nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
        body.data.materials.clear(); body.data.materials.append(tmp)
        scene = bpy.context.scene
        engine = scene.render.engine
        scene.render.engine = 'CYCLES'; scene.cycles.samples = 1
        select_only(body)
        bpy.ops.object.bake(type='EMIT', margin=8)             # 島的邊緣往外多塗 8 像素
        scene.render.engine = engine
        bpy.data.materials.remove(tmp)

    tex_dir = os.path.join(OUT_DIR, "textures"); os.makedirs(tex_dir, exist_ok=True)
    img.filepath_raw = os.path.join(tex_dir, img.name + ".png"); img.file_format = 'PNG'
    img.save(); img.pack()
    body["pattern"] = img.name
    print("花紋遮罩：", img.filepath_raw)

# ---------- 4c) 預覽材質（用跟 Unity 一樣的公式上色；有貼圖就乘上去） ----------
texture = bpy.data.images.get(body.get("albedo", "") or body.get("pattern", ""))
albedo = "albedo" in body
# 預覽用的配色：造型腳本可設 scene["preview_palette"] = (主色, 副色, 點綴色)；沒設就用小羊的預設
# （造型腳本寫的是螢幕上看到的 sRGB 顏色；材質節點吃的是 Linear，所以要換算，不然會變得很淡）
def srgb_to_linear(c):
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)
pal = [srgb_to_linear(tuple(c)[:3]) for c in bpy.context.scene.get("preview_palette", [])] or \
      [(0.96, 0.93, 0.86), (1.0, 0.95, 0.90), (0.95, 0.55, 0.65)]
if albedo:
    pal[0] = (1, 1, 1)                           # 烘焙的顏色貼圖：主色白色 = 貼圖原色
mat = make_preview_material(pal[0], pal[1], pal[2], texture)
for o in parts:
    o.data.materials.clear()
    o.data.materials.append(mat)

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
    for o in parts:
        o.select_set(True)
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
