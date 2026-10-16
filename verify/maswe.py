"""OWASP MASWE からアプリ側の対策に当たる弱点を取得し、requirement と該当箇所を表示する。

MASWE は弱点の列挙、MASVS は要求事項で、別の文書。
認可の判定をアプリ内で完結させない、は MASWE ではなく MASVS-AUTH-1 なので verify/masvs.py で確かめる。

使い方: python -I verify/maswe.py
"""

import json
import pathlib
import re
import sys
import urllib.request
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

RAW = "https://raw.githubusercontent.com/OWASP/maswe/main/weaknesses"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data"

# 取得する弱点と、本文から抜き出す語と、それが支える記載
TARGETS = [
    ("MASVS-STORAGE/MASWE-0004", ["API keys and secrets", "staging or integration URLs"], "鍵をハードコードしない、検証用のURLをリリースに入れない"),
    ("MASVS-STORAGE/MASWE-0005", ["Verbose Logging in Production"], "デバッグログを残さない"),
    ("MASVS-RESILIENCE/MASWE-0061", ["leftover debug and test code", "hidden switches enabling debug menus"],
     "デバッグ用のコードや隠しスイッチを残さない、MASWE-0004 との役割の違い"),
    ("MASVS-RESILIENCE/MASWE-0063", ["android:debuggable"], "表から外した弱点（デバッグ機能を本番で有効にしたまま）"),
]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "a2b-verify"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8")


def field(text, name):
    m = re.search(rf'^{name}:\s*"?(.*?)"?\s*$', text, re.M)
    return m.group(1) if m else None


def main():
    OUT.mkdir(exist_ok=True)
    result = []
    for path, needles, claim in TARGETS:
        url = f"{RAW}/{path}.md"
        text = get(url)
        title = field(text, "title")
        requirement = field(text, "requirement")

        print(f"### {field(text, 'id')} {title}")
        print(f"   記載 {claim}")
        print(f"   requirement {requirement}")
        hits = []
        for needle in needles:
            lines = [l.strip() for l in text.split("\n") if needle in l]
            if not lines:
                print(f"   {needle!r} が見つからない（文書が改訂された可能性あり）")
            # 複数の語が同じ段落に当たったときは1回だけ表示する
            for l in lines:
                if l not in hits:
                    print("   " + l)
                    hits.append(l)
        print()
        result.append({"path": path, "url": url, "title": title, "requirement": requirement,
                       "needles": needles, "lines": hits})

    out = OUT / f"maswe-{date.today().isoformat()}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"保存 {out}")


if __name__ == "__main__":
    main()
