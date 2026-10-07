"""
不用 Blender、不用 Unity，直接讀 FBX（二進位格式）裡的頂點色，檢查配色遮罩 Mask 是否正確。

  python3 Tools/fbx_mask_report.py Assets/Art/Models/Lamb_Baby.fbx [其他.fbx ...]

對每個網格列出：頂點色層名稱、數量，以及依遮罩規則分類的結果（GDD §7.2）：
  A≈1：可換色，R／G／B 最大者＝主色／副色／點綴色槽
  A≈0：固定色（眼睛、鼻子、蹄…）
  其他：A 不是 0 或 1（匯出時被做了色彩空間轉換）
另外標出：色槽全 0（RGB 全 0、A=1 → Unity 換色後全黑）、多槽混合（如白色 → 過亮），
以及 Unity 實際讀的那一層（TypedIndex 0）是不是 Mask。
"""
import struct
import sys
import zlib

ARRAY_TYPES = {"f": ("f", 4), "d": ("d", 8), "l": ("q", 8), "i": ("i", 4), "b": ("?", 1)}


def read_props(data, pos, count):
    props = []
    for _ in range(count):
        t = chr(data[pos]); pos += 1
        if t == "Y": props.append(struct.unpack_from("<h", data, pos)[0]); pos += 2
        elif t == "C": props.append(bool(data[pos])); pos += 1
        elif t == "I": props.append(struct.unpack_from("<i", data, pos)[0]); pos += 4
        elif t == "F": props.append(struct.unpack_from("<f", data, pos)[0]); pos += 4
        elif t == "D": props.append(struct.unpack_from("<d", data, pos)[0]); pos += 8
        elif t == "L": props.append(struct.unpack_from("<q", data, pos)[0]); pos += 8
        elif t in "SR":
            n = struct.unpack_from("<I", data, pos)[0]; pos += 4
            raw = data[pos:pos + n]; pos += n
            props.append(raw.decode("utf-8", "replace") if t == "S" else raw)
        elif t in ARRAY_TYPES:
            length, encoding, clen = struct.unpack_from("<III", data, pos); pos += 12
            raw = data[pos:pos + clen]; pos += clen
            if encoding == 1:
                raw = zlib.decompress(raw)
            fmt, size = ARRAY_TYPES[t]
            props.append(list(struct.unpack_from("<%d%s" % (length, fmt), raw)))
        else:
            raise ValueError("未知的屬性型別 %r（位置 %d）" % (t, pos))
    return props, pos


def read_node(data, pos, wide):
    if wide:
        end, nprops, _plen = struct.unpack_from("<QQQ", data, pos); pos += 24
    else:
        end, nprops, _plen = struct.unpack_from("<III", data, pos); pos += 12
    if end == 0:
        return None, pos
    nlen = data[pos]; pos += 1
    name = data[pos:pos + nlen].decode("ascii", "replace"); pos += nlen
    props, pos = read_props(data, pos, nprops)
    children = []
    null_len = 25 if wide else 13
    while pos < end - null_len or (pos < end and data[pos:pos + null_len] != b"\0" * null_len):
        child, pos = read_node(data, pos, wide)
        if child is None:
            break
        children.append(child)
    return {"name": name, "props": props, "children": children}, end


def parse(path):
    data = open(path, "rb").read()
    if not data.startswith(b"Kaydara FBX Binary"):
        raise ValueError("不是二進位 FBX（ASCII FBX 不支援）")
    version = struct.unpack_from("<I", data, 23)[0]
    wide = version >= 7500
    pos, nodes = 27, []
    while pos < len(data):
        node, pos = read_node(data, pos, wide)
        if node is None:
            break
        nodes.append(node)
    return version, nodes


def child(node, name):
    return next((c for c in node["children"] if c["name"] == name), None)


def classify(r, g, b, a):
    if a > 0.95 and max(r, g, b) < 1e-4:
        return "色槽全 0"   # 三個色槽權重都是 0 → 換色後是黑的（Blender 新建色層的預設值就是這樣）
    if a > 0.95 and sum(1 for v in (r, g, b) if v > 0.5) > 1:
        return "多槽混合"   # 例如白色 (1,1,1,1)：三個色槽相加，換色後會過亮
    if a > 0.95:
        return "主色" if r >= g and r >= b else "副色" if g >= b else "點綴"
    if a < 0.05:
        return "固定色"
    return "A 異常"


def report(path):
    version, nodes = parse(path)
    print("\n== %s（FBX %d）" % (path, version))
    objects = next((n for n in nodes if n["name"] == "Objects"), None)
    geoms = [g for g in (objects["children"] if objects else []) if g["name"] == "Geometry"]
    if not geoms:
        print("  找不到任何網格")
        return False
    ok, file_primary = True, 0
    for g in geoms:
        gname = g["props"][1].split("\x00")[0] if len(g["props"]) > 1 else "?"
        layers = [c for c in g["children"] if c["name"] == "LayerElementColor"]
        if not layers:
            print("  [錯誤] %s：沒有頂點色" % gname)
            ok = False
            continue
        for layer in layers:
            lname = child(layer, "Name")["props"][0] if child(layer, "Name") else ""
            colors = child(layer, "Colors")["props"][0]
            index = child(layer, "ColorIndex")
            idx = index["props"][0] if index else range(len(colors) // 4)
            counts = {}
            for i in idx:
                kind = classify(*colors[i * 4:i * 4 + 4])
                counts[kind] = counts.get(kind, 0) + 1
            total = sum(counts.values())
            # Unity 只讀 Layer 0 用到的頂點色，也就是 TypedIndex 為 0 的那一層
            used = layer["props"][0] == 0
            if used:
                file_primary += counts.get("主色", 0)
            detail = "、".join("%s %d" % (k, counts[k]) for k in ("主色", "副色", "點綴", "固定色", "色槽全 0", "多槽混合", "A 異常") if k in counts)
            flag = "[OK]"
            if not used:
                flag = "[略過] Unity 不讀這一層（只讀第一層）"
            elif lname != "Mask":
                flag, ok = "[錯誤] Unity 讀到的是「%s」不是 Mask——匯出前刪掉其他頂點色層" % lname, False
            elif counts.get("色槽全 0", 0) == total:
                flag, ok = "[錯誤] 全部是 0（Unity 會整隻黑）", False
            elif counts.get("多槽混合", 0) == total:
                flag, ok = "[錯誤] 全部是多槽混合（多半是白色預設值，不是 Mask）", False
            elif counts.get("色槽全 0", 0) or counts.get("多槽混合", 0) or counts.get("A 異常", 0):
                flag = "[注意] 有色槽全 0、多槽混合或 A 不是 0/1 的角點"
            print("  %s 網格 %s／色層「%s」：%d 個角點；%s" % (flag, gname, lname, total, detail))
    if file_primary == 0:
        print("  [錯誤] 整個檔案沒有任何主色角點，換色時看不出變化")
        ok = False
    return ok


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    results = [report(p) for p in sys.argv[1:]]
    sys.exit(0 if all(results) else 1)
