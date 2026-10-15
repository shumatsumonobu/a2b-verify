"""OWASP API Security Top 10 の API1:2023 (BOLA) から How To Prevent を抜き出す。

README に載せている引用: 認可の原則として How To Prevent に並ぶ4件。

使い方: python -I verify/owasp_api.py
"""

import html
import pathlib
import re
import sys
import urllib.request
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

URL = "https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (a2b-verify)"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8", errors="replace")


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def main():
    OUT.mkdir(exist_ok=True)
    page = get(URL)
    path = OUT / f"owasp-api1-{date.today().isoformat()}.html"
    path.write_text(page, encoding="utf-8")

    # 見出しタグそのものを探す。目次のリンク文字列に当たらないようにする
    m = re.search(r"<h[1-3][^>]*>\s*How\s+To\s+Prevent\s*</h[1-3]>(.*?)<h[1-3]", page, re.S | re.I)
    if not m:
        print("How To Prevent の節が見つからない。ページ構成が変わった可能性あり")
        print(f"保存 {path}")
        return

    section = m.group(1)
    bullets = [strip_tags(li) for li in re.findall(r"<li[^>]*>(.*?)</li>", section, re.S)]
    bullets = [b for b in bullets if b]

    print("How To Prevent")
    for b in bullets:
        print("  - " + re.sub(r"\s+", " ", b))
    print(f"\n{len(bullets)} 件")
    print(f"保存 {path}")


if __name__ == "__main__":
    main()
