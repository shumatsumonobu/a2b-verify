"""総務省の注意喚起のページを取得し、日付と A2B攻撃に触れた箇所を表示する。

README に載せている記載: 総務省も NICT と同じ日（2026-10-13、令和8年10月13日）に注意喚起を出している。

使い方: python -I verify/soumu.py
"""

import html
import pathlib
import re
import sys
import urllib.request
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

URL = "https://www.soumu.go.jp/menu_kyotsuu/important/kinkyu02_000680.html"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data"

# 抜き出す語と、それが支える記載
TARGETS = [
    ("令和8年10月13日", "ページの日付"),
    ("A2B攻撃", "A2B攻撃に触れた箇所"),
]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (a2b-verify)"})
    with urllib.request.urlopen(req, timeout=30) as res:
        body = res.read()
    # 総務省のページは Shift_JIS で配信される
    for enc in ("utf-8", "cp932"):
        try:
            return body.decode(enc)
        except UnicodeDecodeError:
            pass
    return body.decode("cp932", errors="replace")


def to_lines(page):
    page = re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S | re.I)
    text = html.unescape(re.sub(r"<[^>]+>", "\n", page))
    return [l.strip() for l in text.split("\n") if l.strip()]


def main():
    OUT.mkdir(exist_ok=True)
    page = get(URL)
    path = OUT / f"soumu-{date.today().isoformat()}.html"
    path.write_text(page, encoding="utf-8")
    lines = to_lines(page)

    for needle, claim in TARGETS:
        print(f"--- {claim} ---")
        hits = [l for l in lines if needle in l]
        for h in hits:
            print("   " + h)
        if not hits:
            print("   該当なし（ページが改訂された可能性あり）")
        print()
    print(f"保存 {path}")


if __name__ == "__main__":
    main()
