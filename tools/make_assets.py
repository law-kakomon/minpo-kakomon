#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ホーム画面アイコン・PWA アイコン・共有用 OG 画像をヘッドレス Chrome で描き出す。

六法ビューアと同じ構図（縦書きの題字＋左に一本の色帯）で、背景色だけ変えて見分けがつくようにしてある。
    python3 tools/make_assets.py
"""
import subprocess, tempfile, time, os, signal
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


def main():
    for name, w, h, html in TARGETS:
        n = shoot(html, ROOT / name, w, h)
        print(f"{name}  {w}x{h}  {n:,} バイト")


if __name__ == "__main__":
    main()
