# 小獅（小領袖，階段 4）完整腳本 —— v001
# 用法（命令列，在 repo 根目錄）：
#   blender -b --python art/blender/lion_leader.py --python art/blender/finalize_export.py -- art/models/Lion --unreal
# 用法（Blender 介面）：Scripting → Open 這個檔案（不要用貼上的：它要找同一個資料夾裡的 lion_adult.py）→ ▶
#
# 做法：先「整支執行」成體腳本 lion_adult.py（v007，組長驗收過）蓋出成體，再在上面加小領袖的東西。
#   這樣成體以後再改，小領袖會自動跟著變 —— 不用維護兩份一樣的身體（程式的「重用」）。
# 小領袖（組長，2026-10-12）：不穿披風，改成「皇冠＋項鍊」。另外鬃毛更豐厚（長大的獅王）。
import bpy, os, math
from mathutils import Vector

# ---------- 1) 先蓋出成體 ----------
try:
    HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:                                   # 在 Blender 文字編輯器裡貼上執行時沒有 __file__
    HERE = bpy.path.abspath("//")
ADULT = os.path.join(HERE, "lion_adult.py")
exec(compile(open(ADULT, encoding="utf-8").read(), ADULT, "exec"))
# exec 之後，成體腳本裡的變數都能直接用：HEAD_C、HEAD_HALF、ball()（加鬃毛球）、curve()、sphere()…

scene = bpy.context.scene
scene["spirit_name"] = "Lion_Leader"
scene["wool_tri_target"] = 1150                     # 鬃毛毛球變多，但預算要讓給皇冠和項鍊 → 減面減多一點（毛球大，看不太出差別）

# 預算：皇冠＋項鍊大約多 900 個三角形。身體的放樣網格很平順，減掉 25% 看不出差別 → 把面數讓給飾品
body_obj = bpy.data.objects["Body"]
bpy.ops.object.select_all(action='DESELECT')
body_obj.select_set(True); bpy.context.view_layer.objects.active = body_obj
dec = body_obj.modifiers.new("Decimate", 'DECIMATE'); dec.ratio = 0.75
bpy.ops.object.modifier_apply(modifier=dec.name)

GOLD_C = (0.95, 0.76, 0.30, 1)
RUBY_C = (0.80, 0.12, 0.20, 1)
MASK_GOLD = (0.95, 0.76, 0.30, 0)                   # 固定金色（跟小羊領袖的金扣同一個顏色）
MASK_RUBY = (0.80, 0.12, 0.20, 0)                   # 固定紅寶石色

# ---------- 2) 鬃毛更豐厚：在成體兩圈外面再加一圈更大的（同一個 metaball，會融在一起） ----------
for k in range(16):
    a = 2 * math.pi * (k + 0.25) / 16
    r = 0.07 * (1.0 if k % 2 == 0 else 0.85)
    ball(Vector((0.43 * math.sin(a), HEAD_C.y + 0.10 + 0.13, HEAD_C.z + 0.40 * math.cos(a) - 0.03)), r)

# ---------- 3) 皇冠：一圈金色的冠帶＋五個尖角（尖端一顆小金球）＋正前方一顆紅寶石 ----------
# 戴在兩隻耳朵中間的頭頂，往前傾一點點（Q 版角色的皇冠常常小小的、歪歪的戴著，比較可愛）
TILT = math.radians(10)
CROWN_C = HEAD_C + Vector((0, -0.04, HEAD_HALF.z - 0.015))   # 冠帶底部稍微陷進頭裡，不會浮著
CROWN_R, BAND_H = 0.12, 0.06

def crown_pt(local):
    """皇冠自己的座標（以冠帶底部中心為原點）→ 世界座標：先繞 X 軸往前傾 TILT，再搬到頭頂。"""
    x, y, z = local
    return CROWN_C + Vector((x, y * math.cos(TILT) - z * math.sin(TILT), y * math.sin(TILT) + z * math.cos(TILT)))

# 冠帶：圓柱（側面＋上下蓋子；蓋子是 n-gon，finalize 會自動 poke 成三角形）
bpy.ops.mesh.primitive_cylinder_add(vertices=15, radius=CROWN_R, depth=BAND_H, location=crown_pt((0, 0, BAND_H / 2)))
put(bpy.context.active_object, "Crown", (1, 1, 1), (10, 0, 0), GOLD_C, mask=MASK_GOLD)
# 五個尖角：三角錐，沿著冠帶上緣平均排，前面那個最高
for k in range(5):
    a = 2 * math.pi * k / 5                          # k = 0 在正前方（−Y）
    h = 0.095 if k == 0 else 0.075
    base = (CROWN_R * 0.92 * math.sin(a), -CROWN_R * 0.92 * math.cos(a), BAND_H)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.036, radius2=0.0, depth=h,
                                    location=crown_pt((base[0], base[1], base[2] + h / 2 - 0.005)))
    put(bpy.context.active_object, "Crown", (1, 1, 1), (10, 0, 0), GOLD_C, mask=MASK_GOLD)
    sphere("Crown", crown_pt((base[0], base[1], base[2] + h + 0.004)), (0.016, 0.016, 0.016),
           color=GOLD_C, seg=6, rings=3, mask=MASK_GOLD)
# 正前方的紅寶石：嵌在冠帶上
sphere("Ruby", crown_pt((0, -CROWN_R - 0.004, BAND_H * 0.5)), (0.026, 0.013, 0.026), (10, 0, 0),
       RUBY_C, seg=8, rings=4, mask=MASK_RUBY)

# ---------- 4) 項鍊：一圈金鍊子掛在脖子上，前面垂到胸口，掛一個圓形的金墜子 ----------
# 鍊子的路徑是一個「斜放的圓圈」：後面高（肩膀上，被鬃毛蓋住）、前面低（胸口，露在鬃毛下面）。
# 圓圈上每一點，從外面往圓心打射線，打到身體表面就是鍊子的位置（跟 v002 的斑點同一招），
# 再往外推一點點 → 鍊子貼著身體繞一圈，不會穿進去也不會浮著。
bpy.context.view_layer.update()
body_obj = bpy.data.objects["Body"]
FRONT, BACK = Vector((0, -0.40, 0.62)), Vector((0, -0.16, 1.02))
C = (FRONT + BACK) / 2
hn = (FRONT - C).normalized()                       # 圓圈平面上「往前下」的方向
side = Vector((1, 0, 0))                            # 圓圈平面上「往旁邊」的方向
mwi = body_obj.matrix_world.inverted()
chain, normals = [], []
N = 22
for i in range(N + 1):
    a = 2 * math.pi * i / N                         # a = 0 在正前方（墜子的位置）
    radial = (hn * math.cos(a) + side * math.sin(a)).normalized()
    start = C + radial * 1.0
    ok, loc, nor, _ = body_obj.ray_cast(mwi @ start, mwi.to_3x3() @ -radial)
    if not ok:
        continue
    p = body_obj.matrix_world @ loc
    n = (body_obj.matrix_world.to_3x3() @ nor).normalized()
    chain.append(p + n * 0.012)
    normals.append(n)
chain[-1] = chain[0]                                # 頭尾接起來成一圈
curve("Necklace", chain, [1.0] * len(chain), 0.011, GOLD_C, round_steps=0, mask=MASK_GOLD)

# 墜子：金色圓牌（圓柱壓扁、朝向胸口外面），中間一顆紅寶石
p0, n0 = chain[0], normals[0]
pend_c = p0 + Vector((0, 0, -0.055)) + n0 * 0.01    # 掛在鍊子最低點下面
bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.055, depth=0.016, location=pend_c)
pend = put(bpy.context.active_object, "Pendant", (1, 1, 1), (0, 0, 0), GOLD_C, mask=MASK_GOLD)
pend.rotation_mode = 'QUATERNION'
pend.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(n0)   # 圓牌的面朝外
sphere("Ruby", pend_c + n0 * 0.01, (0.024, 0.024, 0.024), color=RUBY_C, seg=8, rings=4, mask=MASK_RUBY)
# 掛環：連接鍊子和圓牌
sphere("Pendant", (p0 + pend_c) / 2 + n0 * 0.004, (0.012, 0.012, 0.02), color=GOLD_C, seg=8, rings=4, mask=MASK_GOLD)

print("小獅小領袖 v001 完成")
