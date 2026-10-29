# 介面圖示：六項服事＋九顆聖靈果子，2D 扁平風（GDD §7.2「圖示」）
# 用法（repo 根目錄）：
#   blender -b --python Tools/make_icons.py -- Assets/Resources/Icons
# 輸出：<資料夾>/Service/<key>.png、<資料夾>/Fruits/<key>.png，128×128、透明背景。
# 檔名對照在 Assets/Core/Catalog.cs（ServiceIcon、Fruit.Icon），有測試。
#
# 做法：每個圖示用平面的圓、橢圓、方塊、曲線拼出來（全部在 XY 平面，Z 決定前後），
# Cycles 自發光材質（顏色取物件顏色）算圖 → 顏色就是指定的顏色，不受燈光影響；
# Freestyle 畫外框當描邊（深棕色，跟遊戲的卡通描邊同色系）。
# 顏色用螢幕上的 sRGB 值寫（跟設計稿一樣），程式裡換成 Blender 要的線性值。
# 果子跟美德的對應只是視覺記號（讓孩子好認），沒有神學上的意思。
import bpy, sys, os, math
from mathutils import Vector

OUT = sys.argv[sys.argv.index("--") + 1]
SIZE = 128
INK = "#3D2B1F"

def lin(hex_):
    h = hex_.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c) + (1.0,)

sc = bpy.context.scene
# Cycles＋自發光材質：顏色＝物件顏色，不受燈光影響（Workbench 要 GPU，命令列沒有）
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 16
sc.cycles.use_denoising = False
sc.view_settings.view_transform = 'Standard'
sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = SIZE * 2      # 先算 256 再縮成 128：邊緣比較細緻
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'
# 描邊：Freestyle 畫每個形狀的外框（深棕色，跟遊戲的卡通描邊同色系）
sc.render.use_freestyle = True
sc.render.line_thickness_mode = 'ABSOLUTE'
sc.render.line_thickness = 3.0
lineset = bpy.context.view_layer.freestyle_settings.linesets[0]
lineset.select_by_visibility = True
lineset.select_by_edge_types = True
lineset.select_border = True
lineset.select_silhouette = True
lineset.select_crease = False
lineset.linestyle.color = lin(INK)[:3]
lineset.linestyle.thickness = 3.0

FLAT = bpy.data.materials.new("Flat")
FLAT.use_nodes = True
_nt = FLAT.node_tree
_nt.nodes.clear()
_info = _nt.nodes.new("ShaderNodeObjectInfo")
_emit = _nt.nodes.new("ShaderNodeEmission")
_out = _nt.nodes.new("ShaderNodeOutputMaterial")
_nt.links.new(_info.outputs["Color"], _emit.inputs["Color"])
_nt.links.new(_emit.outputs["Emission"], _out.inputs["Surface"])

cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 2.4          # 畫面範圍 −1.2 ～ 1.2
cam.location = (0, 0, 10)

def clear():
    for o in list(bpy.data.objects):
        if o is not cam:
            bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    for c in list(bpy.data.curves):
        bpy.data.curves.remove(c)

def _obj(mesh_or_curve, name, color, z, rot=0.0):
    mesh_or_curve.materials.append(FLAT)
    o = bpy.data.objects.new(name, mesh_or_curve)
    sc.collection.objects.link(o)
    o.color = lin(color)
    o.location.z = z
    o.rotation_euler.z = math.radians(rot)
    return o

def poly(name, pts, color, z=0.0, rot=0.0, at=(0, 0)):
    """任意多邊形（點依序繞一圈）。"""
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x, y, 0) for x, y in pts], [], [list(range(len(pts)))])
    o = _obj(me, name, color, z, rot)
    o.location.x, o.location.y = at
    return o

def ellipse(name, cx, cy, rx, ry, color, z=0.0, rot=0.0, n=48):
    pts = [(rx * math.cos(2 * math.pi * i / n), ry * math.sin(2 * math.pi * i / n)) for i in range(n)]
    return poly(name, pts, color, z, rot, (cx, cy))

def circle(name, cx, cy, r, color, z=0.0, n=48):
    return ellipse(name, cx, cy, r, r, color, z, 0.0, n)

def rect(name, cx, cy, w, h, color, z=0.0, rot=0.0, r=0.0):
    """長方形；r > 0 時四個角是圓角。"""
    if r <= 0:
        pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    else:
        pts = []
        for (sx, sy, a0) in ((1, -1, -90), (1, 1, 0), (-1, 1, 90), (-1, -1, 180)):
            ccx, ccy = sx * (w / 2 - r), sy * (h / 2 - r)
            for k in range(7):
                a = math.radians(a0 + 15 * k)
                pts.append((ccx + r * math.cos(a), ccy + r * math.sin(a)))
    return poly(name, pts, color, z, rot, (cx, cy))

def stroke(name, pts, width, color, z=0.0):
    """沿著點走的粗線（曲線＋2D 倒角）。"""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '2D'
    cu.bevel_depth = width / 2
    cu.fill_mode = 'BOTH'
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, (x, y) in enumerate(pts):
        sp.points[i].co = (x, y, 0, 1)
    return _obj(cu, name, color, z)

def heart(name, cx, cy, s, color, z=0.0):
    pts = []
    for i in range(64):
        t = 2 * math.pi * i / 64
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x * s / 17, y * s / 17))
    return poly(name, pts, color, z, 0.0, (cx, cy))

def leaf(name, cx, cy, length, width, color, rot, z=0.0):
    """兩端尖的葉子（兩段圓弧）。"""
    pts = []
    for i in range(17):
        t = i / 16
        pts.append((length * (t - 0.5), width / 2 * math.sin(math.pi * t)))
    for i in range(1, 16):
        t = 1 - i / 16
        pts.append((length * (t - 0.5), -width / 2 * math.sin(math.pi * t)))
    return poly(name, pts, color, z, rot, (cx, cy))

def save(folder, key):
    # Freestyle 只認網格：曲線（粗線）先轉成網格
    for o in [o for o in sc.objects if o.type == 'CURVE']:
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.convert(target='MESH')
    path = os.path.join(OUT, folder, key + ".png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(path)
    img.scale(SIZE, SIZE)
    img.save()
    bpy.data.images.remove(img)
    print("icon", path)

# ================= 服事 =================

def offering():
    # 收奉獻：木頭奉獻盒＋投進去的金色愛心
    rect("Box", 0, -0.45, 1.5, 0.95, "#B9824F", 0, r=0.12)
    rect("Lid", 0, 0.07, 1.7, 0.22, "#8E5E36", 0.01, r=0.08)
    rect("Slot", 0, 0.07, 0.7, 0.07, "#4A3222", 0.02, r=0.03)
    heart("Heart", 0, 0.62, 0.42, "#F2B33D", 0.03)

def piano():
    # 司琴：琴鍵（白鍵＋黑鍵）
    rect("Base", 0, 0, 2.0, 1.25, "#5B4636", 0, r=0.14)
    for i in range(7):
        rect("White", -0.78 + i * 0.26, -0.07, 0.24, 0.95, "#FFFDF6", 0.01, r=0.04)
    for i in (0, 1, 3, 4, 5):
        rect("Black", -0.65 + i * 0.26, 0.17, 0.15, 0.55, "#2E2620", 0.02, r=0.03)

def instrument():
    # 小樂器：鈴鼓（圓框＋鼓面＋四對小鈸片）
    circle("Rim", 0, 0, 0.95, "#C98A3E", 0)
    circle("Head", 0, 0, 0.72, "#FBEFD5", 0.01)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        ellipse("Jingle", 0.84 * math.cos(a), 0.84 * math.sin(a), 0.2, 0.13, "#D9DEE3", 0.02, math.degrees(a) + 90)
    heart("Heart", 0, 0, 0.3, "#F497A9", 0.03)

def vocal():
    # Vocal：麥克風＋音符
    rect("Handle", -0.15, -0.55, 0.32, 0.95, "#5C6670", 0, -20, r=0.12)
    circle("Head", 0.07, 0.15, 0.48, "#9AA6B2", 0.01)
    for k in (-1, 0, 1):
        rect("Grill", 0.07 + 0.17 * k, 0.15, 0.04, 0.62 - abs(k) * 0.18, "#6F7A85", 0.02, -20)
    circle("Note", 0.72, 0.52, 0.16, "#7FB6E8", 0.02)
    rect("NoteStem", 0.85, 0.8, 0.06, 0.6, "#7FB6E8", 0.02)
    poly("Flag", [(0, 0), (0.3, -0.12), (0.3, -0.26), (0, -0.16)], "#7FB6E8", 0.02, 0, (0.85, 1.1))

def reading():
    # 領讀天使：打開的書（宣言／讀經／禱告）＋書籤
    poly("Left", [(-1.0, -0.6), (-0.03, -0.75), (-0.03, 0.55), (-1.0, 0.7)], "#FFFDF6", 0)
    poly("Right", [(0.03, -0.75), (1.0, -0.6), (1.0, 0.7), (0.03, 0.55)], "#FFFDF6", 0)
    rect("Spine", 0, -0.1, 0.12, 1.32, "#8E5E36", 0.01)
    for k in range(3):
        y = 0.35 - 0.3 * k
        stroke("LineL", [(-0.82, y), (-0.2, y - 0.08)], 0.06, "#C9B79C", 0.01)
        stroke("LineR", [(0.2, y - 0.08), (0.82, y)], 0.06, "#C9B79C", 0.01)
    poly("Bookmark", [(-0.08, 0), (0.08, 0), (0.08, -0.45), (0, -0.35), (-0.08, -0.45)], "#E85D5D", 0.02, 0, (0.55, 0.62))

def tidy():
    # 環境稽核：掃把＋閃亮亮（整潔）
    stroke("Stick", [(0.55, 0.95), (-0.2, -0.2)], 0.14, "#B9824F", 0)
    poly("Bristle", [(-0.62, -0.05), (-0.05, -0.42), (-0.25, -0.95), (-0.95, -0.65)], "#F2C14E", 0.01)
    rect("Band", -0.33, -0.23, 0.55, 0.12, "#C0392B", 0.02, -33)
    for (x, y, s) in ((0.55, 0.0, 0.32), (0.85, -0.55, 0.2)):
        poly("Sparkle", [(0, s), (s * 0.25, s * 0.25), (s, 0), (s * 0.25, -s * 0.25), (0, -s),
                         (-s * 0.25, -s * 0.25), (-s, 0), (-s * 0.25, s * 0.25)], "#7FB6E8", 0.02, 0, (x, y))

# ================= 果子（加拉太書 5:22–23）=================

def stem_leaf(x, y, rot=-30, color="#6BAE4F"):
    stroke("Stem", [(x, y), (x + 0.05, y + 0.25)], 0.09, "#7A5236", 0.02)
    leaf("Leaf", x + 0.3, y + 0.22, 0.5, 0.24, color, rot, 0.02)

def apple_shape(name, cx, cy, r, color, z=0.0, dent=0.18):
    """蘋果／桃子的外形：一個圓，頂端中間往下凹一點（單一形狀，描邊不會穿過中間）。"""
    pts = []
    for i in range(64):
        t = 2 * math.pi * i / 64
        d = 1.0 - dent * math.exp(-((t - math.pi / 2) / 0.35) ** 2)   # 頂端（90°）凹進去
        pts.append((r * d * math.cos(t) * 1.06, r * d * math.sin(t)))
    return poly(name, pts, color, z, 0.0, (cx, cy))

def love():      # 仁愛：紅蘋果（亮面一顆小愛心）
    apple_shape("Apple", 0, -0.12, 0.85, "#E0473E")
    heart("Shine", -0.35, 0.12, 0.2, "#FF9A8F", 0.01)
    stem_leaf(0.0, 0.55)

def joy():       # 喜樂：橘子
    circle("Orange", 0, -0.08, 0.85, "#F5963C", 0)
    for (x, y) in ((-0.3, 0.2), (0.25, -0.35), (0.35, 0.25), (-0.2, -0.45)):
        circle("Dot", x, y, 0.04, "#E07F26", 0.01)
    stem_leaf(0.0, 0.72)

def peace():     # 和平：橄欖枝（跟鴿子小領袖的葉冠同一個符號）
    stroke("Branch", [(-0.9, -0.8), (-0.2, -0.1), (0.7, 0.85)], 0.09, "#7A5236", 0)
    for (x, y, r) in ((-0.55, -0.25, 120), (-0.2, -0.55, -20), (0.15, 0.45, 130), (0.45, 0.2, -10), (0.65, 0.95, 60)):
        leaf("Leaf", x, y, 0.62, 0.26, "#6BAE4F", r, 0.01)
    for (x, y) in ((-0.05, 0.1), (0.3, -0.15)):
        ellipse("Olive", x, y, 0.2, 0.27, "#556B2F", 0.02, 25)

def patience():  # 忍耐：葡萄（一顆一顆慢慢長）
    for (x, y) in ((-0.45, 0.35), (0, 0.4), (0.45, 0.35), (-0.25, 0.0), (0.25, 0.0), (0, -0.38), (-0.45, -0.3), (0.45, -0.3), (0, -0.75)):
        circle("Grape", x, y, 0.28, "#7D4BA8", 0.0 + y * 0.001)
    stroke("Stem", [(0, 0.65), (0.05, 1.0)], 0.1, "#7A5236", 0.02)
    leaf("Leaf", 0.4, 0.85, 0.6, 0.3, "#6BAE4F", -20, 0.02)

def kindness():  # 恩慈：桃子（圓圓的，中間一道淺淺的線，旁邊一片葉子）
    apple_shape("Peach", 0, -0.1, 0.85, "#F7A8A0", dent=0.1)
    stroke("Cleft", [(0.0, 0.66), (-0.18, 0.15), (-0.08, -0.55)], 0.05, "#E58A82", 0.01)
    stem_leaf(0.02, 0.62, -20)

def goodness():  # 良善：香蕉
    pts = []
    for i in range(21):
        a = math.radians(200 + 140 * i / 20)
        pts.append((1.0 * math.cos(a), 1.0 * math.sin(a) + 0.55))
    for i in range(21):
        a = math.radians(340 - 140 * i / 20)
        pts.append((0.68 * math.cos(a), 0.62 * math.sin(a) + 0.5))
    poly("Banana", pts, "#F7D34A", 0)
    rect("Tip", 0.92, 0.25, 0.14, 0.16, "#7A5236", 0.01, 30)

def faithfulness():  # 信實：石榴（聖經裡常出現的果子；頭上有小冠）
    circle("Pomegranate", 0, -0.12, 0.82, "#B83A4B", 0)
    poly("Crown", [(-0.25, 0), (-0.18, 0.3), (-0.06, 0.12), (0, 0.34), (0.06, 0.12), (0.18, 0.3), (0.25, 0)], "#8E2A38", 0.01, 0, (0, 0.62))
    circle("Shine", -0.35, 0.15, 0.14, "#E07080", 0.01)

def gentleness():  # 溫柔：藍莓（小小三顆）
    for (x, y) in ((-0.42, -0.25), (0.42, -0.25), (0, 0.35)):
        circle("Berry", x, y, 0.5, "#5B7FC7", 0.0 + y * 0.001)
        poly("Star", [(0, 0.1), (0.04, 0.03), (0.1, 0), (0.04, -0.03), (0, -0.1), (-0.04, -0.03), (-0.1, 0), (-0.04, 0.03)],
             "#2F4F8A", 0.01, 0, (x, y + 0.2))

def selfcontrol():  # 節制：無花果（聖經裡的果子，水滴形）
    pts = []
    for i in range(48):
        t = 2 * math.pi * i / 48
        r = 0.78 * (1 - 0.35 * max(0.0, math.sin(t)))
        pts.append((r * math.cos(t), 0.85 * math.sin(t) * (1.15 if math.sin(t) > 0 else 0.85)))
    poly("Fig", pts, "#7E4A6E", 0, 0, (0, -0.1))
    stroke("Stem", [(0, 0.78), (0.08, 1.02)], 0.1, "#6B8E3A", 0.01)
    circle("Shine", -0.3, -0.05, 0.12, "#A86C93", 0.01)

ICONS = {
    "Service": {"offering": offering, "piano": piano, "instrument": instrument,
                "vocal": vocal, "reading": reading, "tidy": tidy},
    "Fruits": {"love": love, "joy": joy, "peace": peace, "patience": patience, "kindness": kindness,
               "goodness": goodness, "faithfulness": faithfulness, "gentleness": gentleness,
               "selfcontrol": selfcontrol},
}
for folder, icons in ICONS.items():
    for key, draw in icons.items():
        clear()
        draw()
        save(folder, key)
