"""
產生遊戲用的中文字型子集：Assets/Resources/Fonts/NotoSansTC-Subset.ttf

WebGL 沒有系統字型可用，中文字必須跟著遊戲下載；完整 Noto Sans TC 約 7 MB，太大。
子集包含：
  1. 遊戲程式裡出現的所有字（Assets 底下 .cs 的非 ASCII 字元：介面文案、經文）
  2. Big5 常用字（5401 字）：涵蓋孩子姓名、平台維護的服事項目名稱
  3. ASCII 與常用全形標點
新增文案後重跑即可（需要 pip install fonttools）：

  curl -sS -o /tmp/NotoSansTC-Medium.ttf \
    "https://fonts.gstatic.com/s/notosanstc/v40/-nFuOG829Oofr2wohFbTp9ifNAn722rq0MXz75Ky_Co.ttf"
  python3 Tools/subset-font.py /tmp/NotoSansTC-Medium.ttf

字型授權：SIL Open Font License 1.1（Assets/Resources/Fonts/OFL.txt）。
"""
import pathlib
import sys

from fontTools import subset

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "Assets/Resources/Fonts/NotoSansTC-Subset.ttf"


def big5_common() -> set:
    chars = set()
    for lead in range(0xA4, 0xC7):
        for trail in list(range(0x40, 0x7F)) + list(range(0xA1, 0xFF)):
            if lead == 0xC6 and trail > 0x7E:
                break
            try:
                chars.add(bytes([lead, trail]).decode("big5"))
            except UnicodeDecodeError:
                pass
    return chars


def source_chars() -> set:
    chars = set()
    for path in (ROOT / "Assets").rglob("*.cs"):
        chars |= {c for c in path.read_text(encoding="utf-8") if ord(c) > 0x7F}
    return chars


def main(src: str) -> None:
    text = set(chr(c) for c in range(0x20, 0x7F))
    text |= set("，。、；：？！「」『』（）《》〈〉…—～·＋－／　")
    text |= big5_common() | source_chars()
    options = subset.Options()
    options.layout_features = ["*"]
    options.name_IDs = ["*"]
    options.notdef_outline = True
    font = subset.load_font(src, options)
    subsetter = subset.Subsetter(options)
    subsetter.populate(text="".join(sorted(text)))
    subsetter.subset(font)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    subset.save_font(font, str(OUT), options)
    print(f"{len(text)} chars -> {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main(sys.argv[1])
