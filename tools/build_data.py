#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""data/sources.json（PDF の在りか）+ tools/classify.py（単元分類）→ data/kakomon.json"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import classify as C

TERM_ORDER = {'前期': 0, '中期': 1, '後期': 2, '本試験': 0, '追試験': 1, '転入学': 3}
UNIV_ORDER = {'同志社': 0, '立命館': 1, '慶應': 2}

def main():
    src = json.load(open(ROOT / 'data' / 'sources.json', encoding='utf-8'))
    items = []
    for s in src['items']:
        cls = C.CLASS.get(s['id'])
        units, topics, arts, hanrei = cls if cls else ([], [], [], [])
        items.append({
            **s,
            # 改正民法（債権法改正）は 2020年4月1日施行。2021年度入試以降が新法下の出題
            'law': '新法' if s['year'] >= 2021 else '旧法',
            'units': units, 'topics': topics, 'articles': arts, 'hanrei': hanrei,
            'classified': bool(units),
        })
    items.sort(key=lambda x: (-x['year'], UNIV_ORDER.get(x['univ'], 9), TERM_ORDER.get(x['term'], 9)))
    # 単元ごとの件数
    counts = {}
    for it in items:
        for u in it['units']:
            counts[u] = counts.get(u, 0) + 1
            top = u.split('/')[0]
            counts[top] = counts.get(top, 0) + 1
    taxonomy = []
    for top, subs in C.TAXONOMY:
        taxonomy.append({
            'name': top, 'count': counts.get(top, 0),
            'subs': [{'name': s, 'key': f'{top}/{s}', 'count': counts.get(f'{top}/{s}', 0)} for s in subs],
        })
    out = {
        'generated': True,
        'sources': src['fetched'],
        'taxonomy': taxonomy,
        'items': items,
    }
    json.dump(out, open(ROOT / 'data' / 'kakomon.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # index.html にも埋め込む（file:// で直接開いても動くようにするため）
    import re as _re
    html_path = ROOT / 'index.html'
    if html_path.exists():
        h = html_path.read_text(encoding='utf-8')
        payload = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
        payload = payload.replace('</', '<\\/')   # </script> で閉じないように
        h2, n = _re.subn(
            r'(<script id="kakomon-data" type="application/json">).*?(</script>)',
            lambda m: m.group(1) + payload + m.group(2), h, flags=_re.S)
        if n:
            html_path.write_text(h2, encoding='utf-8')
            print(f'index.html にデータを埋め込み（{len(payload):,} バイト）')
        else:
            print('警告: index.html の埋め込み先が見つかりません')
    nc = [i['id'] for i in items if not i['classified']]
    print(f"{len(items)} 件 → data/kakomon.json")
    print(f"単元分類済み {len(items)-len(nc)} 件 / 未分類 {len(nc)} 件: {nc}")
    miss = [i['id'] for i in items if not i.get('kaisetsu')]
    print(f"解説・講評なし {len(miss)} 件: {miss}")

if __name__ == '__main__':
    main()
