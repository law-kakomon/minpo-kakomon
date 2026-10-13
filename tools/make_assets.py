#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ホーム画面アイコン・PWA アイコン・共有用 OG 画像をヘッドレス Chrome で描き出す。

六法ビューアと同じ構図（縦書きの題字＋左に一本の色帯）で、背景色だけ変えて見分けがつくようにしてある。
    python3 tools/make_assets.py
"""
import subprocess, tempfile, time, os, signal, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

BG_FROM, BG_TO = "#35715c", "#1b4132"      # 深緑のグラデーション（六法ビューアは藍）
BAR = "#e0a436"                             # 帯の色（六法ビューアは赤）
MINCHO = "'Hiragino Mincho ProN','Yu Mincho',serif"
GOTHIC = "'Hiragino Sans','Hiragino Kaku Gothic ProN',sans-serif"


def icon_html(size, pad_ratio=0.0):
    """縦書き「過去問」＋左の帯。pad_ratio は maskable 用の安全余白。"""
    inset = size * pad_ratio
    inner = size - inset * 2
    return f"""<body style="margin:0;width:{size}px;height:{size}px;
  background:linear-gradient(145deg,{BG_FROM},{BG_TO});overflow:hidden">
<div style="position:absolute;left:{inset}px;top:{inset}px;width:{inner}px;height:{inner}px;
     display:flex;align-items:center;justify-content:center;gap:{inner*0.085}px">
  <div style="width:{inner*0.072}px;height:{inner*0.70}px;background:{BAR};
       border-radius:{inner*0.036}px"></div>
  <div style="font-family:{MINCHO};color:#fff;font-size:{inner*0.265}px;line-height:1.02;
       letter-spacing:0;text-align:center;font-weight:600">
    過<br>去<br>問
  </div>
</div></body>"""


def favicon_html(size):
    """タブ用。16〜32px まで縮むので文字は入れず、色と帯だけのマークにする。
    「過去問」3文字はもちろん「過」一文字でも 16px では潰れて読めないため
    （実測で比較して決めた。CLAUDE.md「実装メモ」参照）。
    帯はホーム画面アイコンにも入っているので、並べたときに同じアプリだと分かる。"""
    return f"""<body style="margin:0;width:{size}px;height:{size}px;overflow:hidden;
  background:linear-gradient(145deg,{BG_FROM},{BG_TO});
  display:flex;align-items:center;justify-content:center">
  <div style="width:{size*0.17}px;height:{size*0.60}px;background:{BAR};
       border-radius:{size*0.085}px"></div>
</body>"""


OG_HTML = f"""<body style="margin:0;width:1200px;height:630px;
  background:linear-gradient(135deg,{BG_FROM},{BG_TO});color:#fff;
  font-family:{GOTHIC};overflow:hidden">
<div style="position:absolute;inset:0;padding:74px 86px;display:flex;flex-direction:column;
     justify-content:center;gap:0">
  <div style="display:flex;align-items:center;gap:30px">
    <div style="width:13px;height:132px;background:{BAR};border-radius:7px"></div>
    <div style="font-family:{MINCHO};font-size:106px;font-weight:600;letter-spacing:.04em;
         line-height:1.1">民法過去問帳</div>
  </div>
  <div style="font-size:37px;margin:36px 0 0 43px;line-height:1.6;opacity:.94">
    ロー入試（既修者）の民法過去問を、単元ごとに引く
  </div>
  <div style="font-size:26px;margin:30px 0 0 43px;line-height:1.75;opacity:.78">
    同志社・立命館・関学・慶應・中央／2005〜2027年度の91回を収録<br>
    総則・物権・債権・契約・親族・相続などの単元から絞り込み<br>
    問題と解説は各大学の公式ページをそのまま開く
  </div>
</div></body>"""

TARGETS = [
    ("favicon-src.png", 256, 256, favicon_html(256)),   # ← favicon.ico / icon-32 等の元画像
    ("icon-192.png", 192, 192, icon_html(192)),
    ("icon-512.png", 512, 512, icon_html(512)),
    ("icon-maskable-512.png", 512, 512, icon_html(512, pad_ratio=0.105)),
    ("apple-touch-icon.png", 180, 180, icon_html(180)),
    ("og.png", 1200, 630, OG_HTML),
]


def shoot(html, out, w, h):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        src = f.name
    if out.exists():
        out.unlink()
    p = subprocess.Popen(
        [CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
         f"--screenshot={out}", f"--window-size={w},{h}", f"file://{src}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # ヘッドレス Chrome は書き出し後もプロセスが残ることがあるので、ファイルの安定を見て終了させる
    last, stable = -1, 0
    for _ in range(60):
        time.sleep(0.3)
        size = out.stat().st_size if out.exists() else 0
        if size and size == last:
            stable += 1
            if stable >= 2:
                break
        else:
            stable = 0
        last = size
    try:
        p.send_signal(signal.SIGTERM)
        p.wait(timeout=5)
    except Exception:
        p.kill()
    os.unlink(src)
    if not out.exists() or out.stat().st_size == 0:
        raise SystemExit(f"描き出しに失敗: {out.name}")
    return out.stat().st_size


def write_ico(images, path):
    """ICO を自前で組み立てる。

    Pillow の save(format="ICO") は使えない:
      - 既定では中身が PNG 圧縮になり、Safari が読まない
      - bitmap_format="bmp" にしても **AND マスクを書かない**。ヘッダーの biHeight は
        「高さ×2（= マスクあり）」と宣言しているのにデータが足りず、厳密なパーサーが弾く
    ここでは BITMAPINFOHEADER + XOR ビットマップ（BGRA・下から上）+ AND マスク
    （1bpp・4バイト境界・全ゼロ＝全部不透明）を規格どおりに書く。
    """
    entries, blobs = [], []
    for im in images:
        w, h = im.size
        px = im.convert("RGBA").load()
        xor = bytearray()
        for y in range(h - 1, -1, -1):              # BMP は下から上
            for x in range(w):
                r, g, b, a = px[x, y]
                xor += bytes((b, g, r, a))          # BGRA
        row = ((w + 31) // 32) * 4                  # AND マスクの1行は4バイト境界
        andmask = bytes(row * h)                    # 全ゼロ＝全ピクセル不透明
        header = struct.pack("<IiiHHIIiiII", 40, w, h * 2, 1, 32, 0,
                             len(xor) + len(andmask), 0, 0, 0, 0)
        blobs.append(header + bytes(xor) + andmask)
        entries.append((w, h))
    out = bytearray(struct.pack("<HHH", 0, 1, len(blobs)))
    offset = 6 + 16 * len(blobs)
    for (w, h), blob in zip(entries, blobs):
        out += struct.pack("<BBBBHHII", w % 256, h % 256, 0, 0, 1, 32, len(blob), offset)
        offset += len(blob)
    for blob in blobs:
        out += blob
    path.write_bytes(bytes(out))


def make_favicons():
    """タブ用の小さいアイコンを元画像から作る。
    ブラウザのタブは 16〜32px。192px の PNG だけだと Safari 等が拾わず、
    頭文字の代替アイコン（丸に「G」）が出てしまうので favicon.ico も置く。"""
    from PIL import Image
    src = ROOT / "favicon-src.png"
    im = Image.open(src).convert("RGBA")
    sizes = (16, 32, 48)
    small = {}
    for size in sizes:
        small[size] = im.resize((size, size), Image.LANCZOS)
        out = ROOT / f"icon-{size}.png"
        small[size].save(out)
        print(f"icon-{size}.png  {size}x{size}  {out.stat().st_size:,} バイト")
    ico = ROOT / "favicon.ico"
    write_ico([small[s] for s in sizes], ico)
    print(f"favicon.ico  16/32/48（BMP＋ANDマスク）  {ico.stat().st_size:,} バイト")
    src.unlink()


def main():
    for name, w, h, html in TARGETS:
        n = shoot(html, ROOT / name, w, h)
        print(f"{name}  {w}x{h}  {n:,} バイト")
    make_favicons()


if __name__ == "__main__":
    main()
