# 民法過去問帳

ロースクール既修者入試（民法）の過去問を、**民法の単元ごとに**引ける学習帳。

**https://law-kakomon.github.io/minpo-kakomon/**

短縮: **https://law-kakomon.github.io/**

- **単元から引く** — 総則／物権／担保物権／債権総論／契約総論／契約各論／法定債権／親族／相続。さらに「代理」「物権変動・登記」などの単元に分かれていて、件数つきで並ぶ
- **条文から引く** — 検索欄に `177` と入れると、177条が論じられている回だけが並ぶ
- **論点・判例で探す** — 「表見代理」「最判平成5年1月21日」などで検索
- **問題と解説をその場で読む** — 同志社・立命館は PDF をページ内に表示。慶應はサーバー側の設定で埋め込めないため新しいタブで開く
- **解いた回に印をつける** — チェックはこの端末のブラウザにだけ残る

収録は同志社・立命館・関学・慶應・中央の5校、計 92 回（2005〜2027年度）。
**PDF は各大学の公式ページをそのまま開きます**（このリポジトリに複製は置いていません）。

## 使い方

上の URL をブラウザで開くだけ。スマホでは「ホーム画面に追加」するとアプリのように使える。

手元で動かすとき:

```bash
open 開く.command
```

Finder でダブルクリックしても起動する（port 8129）。`index.html` を直接開いても動く。

## 更新

新年度が公開されたら:

```bash
python3 tools/fetch_sources.py   # 新規項目を検知
# tools/classify.py に単元・論点を追記
python3 tools/build_data.py
```

くわしくは [CLAUDE.md](CLAUDE.md)。

## 出典

- [同志社大学法科大学院 過去の入試・履修免除試験問題](https://law-school.doshisha.ac.jp/entrance_ex/question/)
- [立命館大学法科大学院 過去の入試問題・講評](https://www.ritsumei.ac.jp/lawschool/admission/past.html/)
- [関西学院大学法科大学院 入試過去問題（解答例・出題の意図）](https://www.kwansei.ac.jp/lawschool/admissions/kakomon/)
- [慶應義塾大学法科大学院 過去の入試問題](https://www.ls.keio.ac.jp/nyushi/examination.html)
- [中央大学法科大学院 入学者選抜の過去問題等の情報公開](https://www.chuo-u.ac.jp/academics/pro_graduateschool/law/orientation/selection/past/)

単元・論点・条文の整理は、各大学が公開している解説・入試講評・出題趣旨の本文にもとづく。

## 姉妹サイト

科目の入口は **https://law-kakomon.github.io/** 。

- [民事訴訟法過去問帳](https://law-kakomon.github.io/minso-kakomon/)
- [会社法過去問帳](https://law-kakomon.github.io/kaisha-kakomon/)
- [行政法過去問帳](https://law-kakomon.github.io/gyosei-kakomon/)
- [刑法過去問帳](https://law-kakomon.github.io/keiho-kakomon/)
- [刑事訴訟法過去問帳](https://law-kakomon.github.io/keiso-kakomon/)
- [憲法過去問帳](https://law-kakomon.github.io/kenpo-kakomon/)
