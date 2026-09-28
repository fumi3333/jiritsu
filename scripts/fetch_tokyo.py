"""東京都の指定自立支援医療機関（精神通院）一覧を取得して保存する。

使い方:
  python scripts/fetch_tokyo.py            # 都のページに今載っている版を取る
  python scripts/fetch_tokyo.py 20260401   # ファイル名の日付を指定して取る（過去分の回収用）

保存先:
  data/raw/tokyo/YYYY-MM/   都が配っている元ファイル（そのまま）
  data/tokyo/YYYY-MM/       共通の形にそろえた CSV
"""
import csv
import datetime
import io
import re
import sys
import urllib.request
from pathlib import Path

import openpyxl
import xlrd

PAGE = "https://www.fukushi.metro.tokyo.lg.jp/shougai/jigyo/shougaifukushi/iryoshiteijoho_s"
BASE = "https://www.fukushi.metro.tokyo.lg.jp/documents/d/fukushi/"
ROOT = Path(__file__).resolve().parent.parent
UA = {"User-Agent": "Mozilla/5.0 (shinsei archive; https://github.com/fumi3333)"}

# 種別 -> 都のファイル名の末尾（月によって "-1" が付くことがあるので候補を並べる）
KINDS = {
    "byouin": ["seishin_byouin-xlsx-xlsx"],
    "yakkyoku": ["seishin_yakkyoku-xlsx-xlsx"],
    "houkan": ["seishin_houkan-xlsx-xlsx", "seishin_houkan-xlsx-xlsx-1"],
    "shinki_byouin": ["byouinshinki-xls-xls"],
    "shinki_yakkyoku": ["yakkyokushinki-xlsx-xlsx"],
    "shinki_houkan": ["houkanshinki-xls-xls"],
}
MAIN = ("byouin", "yakkyoku", "houkan")
COLUMNS = ["code", "name", "postal_code", "municipality", "address", "phone",
           "designated_on", "renewed_on", "kind", "as_of", "source_url"]

ZEN = str.maketrans("０１２３４５６７８９", "0123456789")
ERA = {"令和": 2018, "平成": 1988, "昭和": 1925}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def wareki_to_iso(s):
    """「令和７年１月１日」→「2025-01-01」。読めなければ空文字。"""
    if s is None:
        return ""
    if isinstance(s, datetime.datetime):
        return s.date().isoformat()
    m = re.match(r"(令和|平成|昭和)(元|\d+)年(\d+)月(\d+)日", str(s).translate(ZEN).replace(" ", ""))
    if not m:
        return ""
    year = 1 if m.group(2) == "元" else int(m.group(2))
    return datetime.date(ERA[m.group(1)] + year, int(m.group(3)), int(m.group(4))).isoformat()


def read_rows(blob):
    if blob[:2] == b"PK":
        ws = openpyxl.load_workbook(io.BytesIO(blob), read_only=True, data_only=True).worksheets[0]
        return [list(r) for r in ws.iter_rows(values_only=True)]
    sh = xlrd.open_workbook(file_contents=blob).sheet_by_index(0)
    return [sh.row_values(i) for i in range(sh.nrows)]


def normalize(rows, kind, as_of, url):
    out = []
    for r in rows:
        if not r or not isinstance(r[0], (int, float)) or r[1] in (None, ""):
            continue
        muni = str(r[4] or "").strip()
        out.append({
            "code": str(int(r[1])) if isinstance(r[1], float) else str(r[1]).strip(),
            "name": str(r[2] or "").replace("　", " ").strip(),
            "postal_code": str(r[3] or "").strip(),
            "municipality": re.sub(r"^\d+", "", muni),
            "address": str(r[5] or "").strip(),
            "phone": str(r[6] or "").strip(),
            "designated_on": wareki_to_iso(r[7]),
            "renewed_on": wareki_to_iso(r[8]) if len(r) > 8 else "",
            "kind": kind,
            "as_of": as_of,
            "source_url": url,
        })
    return out


def current_stamp():
    html = get(PAGE).decode("utf-8", "ignore")
    m = re.search(r"/documents/d/fukushi/(\d{8})_seishin_byouin", html)
    if not m:
        sys.exit("都のページからファイル名の日付を見つけられませんでした")
    return m.group(1)


def fetch(stamp):
    as_of = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:]}"
    month = as_of[:7]
    raw_dir = ROOT / "data/raw/tokyo" / month
    out_dir = ROOT / "data/tokyo" / month
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    for kind, suffixes in KINDS.items():
        for suffix in suffixes:
            url = BASE + f"{stamp}_{suffix}"
            try:
                blob = get(url)
            except Exception:
                continue
            ext = "xlsx" if blob[:2] == b"PK" else "xls"
            (raw_dir / f"{kind}.{ext}").write_bytes(blob)
            if kind in MAIN:
                rows = normalize(read_rows(blob), kind, as_of, url)
                with open(out_dir / f"{kind}.csv", "w", encoding="utf-8", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=COLUMNS)
                    w.writeheader()
                    w.writerows(rows)
                print(f"{month} {kind}: {len(rows)}件")
            else:
                print(f"{month} {kind}: 元ファイルを保存")
            break
        else:
            print(f"{month} {kind}: 取得できませんでした")


if __name__ == "__main__":
    fetch(sys.argv[1] if len(sys.argv) > 1 else current_stamp())
