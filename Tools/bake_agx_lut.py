# 烘焙 Blender AgX 查找表：讓 Unity 的「Blender 預覽」渲染模式跟 Cycles 預覽圖的顏色一致
# 用法（repo 根目錄）：
#   blender -b --python Tools/bake_agx_lut.py -- Assets/Resources/Shaders/AgX_Lut.png
#
# 做法：做一張 32³ 個顏色的浮點圖（1024×32 橫條：32 片藍 × 每片 32 紅 × 32 綠，數值用 log2 編碼，
# 涵蓋 2^-12 ～ 2^4），貼在自發光平面上，用正交相機「真的用 Cycles 算一次」，view transform＝AgX。
# 這樣查找表就是 Cycles 輸出的同一條路（不是另外用公式模仿）。
# 注意：降噪一定要關——降噪會把這種小圖的顏色弄偏（實測差到 25 階）。
# 常數 N、MINEV、MAXEV 要跟 PaletteMask.shader 的 AGX_N、AGX_MINEV、AGX_MAXEV 一致。
# 2026-10-21 以 Blender 4.2.23 LTS 烘焙；用 6 組顏色比對 Cycles 直接輸出，8-bit 下完全相同。
import bpy, sys
N, MINEV, MAXEV = 32, -12.0, 4.0
out = sys.argv[sys.argv.index("--") + 1]
def val(i): return 2.0 ** (MINEV + (MAXEV - MINEV) * i / (N - 1))
sc = bpy.context.scene
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
src = bpy.data.images.new("src", N * N, N, float_buffer=True, alpha=False)
src.colorspace_settings.name = 'Linear Rec.709'
px = []
for g in range(N):
    for b in range(N):
        for r in range(N):
            px += [val(r), val(g), val(b), 1.0]
src.pixels = px
W, H = N * N, N
bpy.ops.mesh.primitive_plane_add(size=1)
pl = bpy.context.active_object; pl.scale = (W / H, 1, 1)
m = bpy.data.materials.new("E"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = src; tex.interpolation = 'Closest'
em = nt.nodes.new("ShaderNodeEmission"); outn = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(tex.outputs[0], em.inputs[0]); nt.links.new(em.outputs[0], outn.inputs[0]); pl.data.materials.append(m)
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = W / H; cam.location = (0, 0, 2)
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.render.engine = 'CYCLES'; sc.cycles.samples = 1; sc.cycles.filter_width = 0.01; sc.render.dither_intensity = 0
sc.cycles.use_denoising = False
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'None'; sc.view_settings.exposure = 0; sc.view_settings.gamma = 1
sc.world = bpy.data.worlds.new("W")
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'; sc.render.image_settings.color_depth = '8'
sc.render.filepath = out; bpy.ops.render.render(write_still=True); print("saved", out)
