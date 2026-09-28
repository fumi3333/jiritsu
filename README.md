# jiritsu

自立支援医療（精神通院）を使っている人の手続きを手伝うためのツールと、そのもとになるデータです。

## 今あるもの：東京都の指定自立支援医療機関（精神通院）一覧の月次アーカイブ

東京都は、精神通院医療の指定を受けた病院・診療所、薬局、訪問看護事業者の一覧を毎月差し替えて公開しています。差し替え前の一覧はページからたどれなくなるため、このリポジトリで月ごとに保存しています。

| 場所 | 中身 |
|---|---|
| `data/tokyo/YYYY-MM/byouin.csv` | 病院・診療所 |
| `data/tokyo/YYYY-MM/yakkyoku.csv` | 薬局 |
| `data/tokyo/YYYY-MM/houkan.csv` | 訪問看護事業者等 |
| `data/raw/tokyo/YYYY-MM/` | 東京都が配っている元ファイル（新規指定・廃止の一覧を含む） |

- 保存しているのは 2026年4月1日時点の版から。それより前の版は、東京都のページから取得できませんでした
- GitHub Actions で毎日確認し、中身が変わった時だけコミットします
- CSV の列：`code, name, postal_code, municipality, address, phone, designated_on, renewed_on, kind, as_of, source_url`。日付は和暦から西暦（YYYY-MM-DD）に変換しています
- 医療機関の評価や順位は付けていません。一覧をそのまま保存しているだけです

## 出典

東京都福祉局「指定自立支援医療機関の情報提供（精神通院医療）」
https://www.fukushi.metro.tokyo.lg.jp/shougai/jigyo/shougaifukushi/iryoshiteijoho_s
（東京都オープンデータカタログサイト、クリエイティブ・コモンズ 表示 4.0 国際（CC BY 4.0））

このリポジトリのデータは、上の元データを列の名前と日付の書き方をそろえるなど加工したものです。最新の正確な情報は東京都のページで確認してください。

## ライセンス

- コード：MIT
- データ：元データのライセンス（CC BY 4.0）に従います。使う時は上の出典を表示してください

## 作っている人

ZAX（https://fumiproject.dev/ ）
