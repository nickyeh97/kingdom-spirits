# 美術檢查用的 Cycles 預覽算圖（art-worklog 裡的圖都是用這支算的）
# 用法（repo 根目錄）：
#   blender -b art/models/Dove/Dove_Baby_v001.blend --python Tools/render_preview.py -- <輸出前綴> [--zoom 1.3]
#   並排比較：再加上「其他 .blend:X 位移」，例如
#   blender -b A.blend --python Tools/render_preview.py -- out --zoom 1.25 B.blend:-1.2 C.blend:1.25
#
# 這裡的燈光、世界、色調設定就是 Unity「Blender 預覽」渲染模式的基準（Assets/Runtime/RenderStyle.cs）：
#   太陽：強度 3、旋轉 (50°, 0, −30°)、白光
#   世界：顏色 (0.55, 0.60, 0.65)、強度 0.6（當作均勻環境光）
#   色調：Blender 預設的 AgX（Unity 端用 Tools/bake_agx_lut.py 烘的查找表重現）
# 改了這裡的任何一個數字，RenderStyle.cs 的常數也要一起改，兩邊才會一致。
import bpy, sys, math
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
zoom = 1.0
if "--zoom" in args:
    zoom = float(args[args.index("--zoom") + 1])
extras = [a for a in args[1:] if ":" in a]
sc = bpy.context.scene
for extra in extras:
    path, dx = extra.rsplit(":", 1)
    with bpy.data.libraries.load(path) as (src, dst):
        dst.objects = [n for n in src.objects]
    for o in dst.objects:
        if o and o.type == 'MESH':
            sc.collection.objects.link(o)
            if o.parent is None:
                o.location.x += float(dx)
sc.render.engine = 'CYCLES'; sc.cycles.samples = 24; sc.cycles.device = 'CPU'
sc.render.resolution_x = sc.render.resolution_y = 640
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.6, 0.65, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", 'SUN')); sun.data.energy = 3
sun.rotation_euler = (math.radians(50), 0, math.radians(-30)); sc.collection.objects.link(sun)
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 60
target = Vector((0, 0, 0.5 * zoom))
views = {"front": (0, -1, 0.15), "34": (0.75, -0.75, 0.3), "side": (1, 0, 0.1), "back": (-0.6, 0.8, 0.4), "top": (0.3, -0.4, 1.2)}
if extras:
    views = {"lineup": (0, -1, 0.15)}
for name, d in views.items():
    dist = (6.0 if extras else 3.6) * zoom
    cam.location = target + Vector(d).normalized() * dist
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = f"{out}_{name}.png"
    bpy.ops.render.render(write_still=True)
