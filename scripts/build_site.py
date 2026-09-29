"""data/tokyo の最新月から、画面用の JSON を作る。

出力: site/data.json
  {"as_of": "YYYY-MM-DD", "kinds": {...}, "munis": [...], "rows": [[kind, muni_idx, name, address, phone, designated_on], ...]}
区市町村ごとに分けず1ファイルにしているのは、選んだ区がサーバーに伝わらないようにするため。
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KINDS = {"yakkyoku": "薬局", "byouin": "病院・診療所", "houkan": "訪問看護"}


def main():
    latest = sorted(p for p in (ROOT / "data/tokyo").iterdir() if p.is_dir())[-1]
    rows, munis, as_of = [], [], ""
    for kind in KINDS:
        with open(latest / f"{kind}.csv", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                as_of = r["as_of"]
                if r["municipality"] not in munis:
                    munis.append(r["municipality"])
                rows.append([kind, munis.index(r["municipality"]), r["name"], r["address"],
                             r["phone"], r["designated_on"]])
    out = {"as_of": as_of, "kinds": KINDS, "munis": munis, "rows": rows}
    dest = ROOT / "site/data.json"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{as_of} {len(rows)}件 {len(munis)}区市町村 {dest.stat().st_size // 1024}KB")


if __name__ == "__main__":
    main()
