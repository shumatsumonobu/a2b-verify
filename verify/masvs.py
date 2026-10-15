"""OWASP MASVS の全コントロールを取得し、サーバー側（remote endpoint）に触れているものを列挙する。

README に載せている引用: 認可の強制をサーバー側に置くと書いてあるのは MASVS-AUTH-1 だけ。

使い方: python -I verify/masvs.py
"""

import json
import pathlib
import sys
import urllib.request
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

API = "https://api.github.com/repos/OWASP/masvs/contents/controls"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data"

# 「サーバー側の責務に触れているか」の判定語。増やすと拾う範囲が広がる
KEYWORDS = ["remote endpoint", "server", "backend"]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "a2b-verify"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    items = json.loads(get(API))
    controls = [i for i in items if i["name"].endswith(".md")]
    print(f"コントロール数 {len(controls)}\n")

    result = []
    for item in controls:
        text = get(item["download_url"])
        hits = [l.strip() for l in text.split("\n") if any(k in l.lower() for k in KEYWORDS)]
        if hits:
            result.append({"control": item["name"], "lines": hits})
            print(f"### {item['name']}")
            for h in hits:
                print("   " + h)
            print()

    enforcement = [r["control"] for r in result if any("enforcement" in l.lower() for l in r["lines"])]
    print(f"判定語に当たったコントロール {len(result)} 件")
    print(f"認可の強制をサーバー側に置いているもの {enforcement}")

    path = OUT / f"masvs-{date.today().isoformat()}.json"
    path.write_text(json.dumps({"total": len(controls), "matched": result, "enforcement": enforcement},
                               ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"保存 {path}")


if __name__ == "__main__":
    main()
