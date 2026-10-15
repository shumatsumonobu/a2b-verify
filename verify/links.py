"""README で参照している URL の死活とリダイレクト先、リポジトリ内のリンク先を確認する。

リポジトリ内の README.md（直下、verify/、data/）から http(s) の URL を全部読み取って確かめるので、
README にリンクを足せば対象も増える。
相対リンクはファイルの実在を、#見出し へのリンクは見出しの実在を確かめる。
1件でも失敗すれば終了コード 1

使い方: python -I verify/links.py
"""

import json
import pathlib
import re
import sys
import urllib.request
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
READMES = [ROOT / "README.md", ROOT / "verify" / "README.md", ROOT / "data" / "README.md"]
OUT = ROOT / "data"


def readme_urls():
    text = "\n".join(p.read_text(encoding="utf-8") for p in READMES)
    urls = re.findall(r"https?://[^\s)`>]+", text)
    return list(dict.fromkeys(urls))


def check(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (a2b-verify)"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.status, res.geturl()


def slug(heading):
    # GitHub が見出しに付ける ID の規則（小文字にし、記号を消し、空白をハイフンに）を真似たもの
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def anchors(md):
    text = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)
    return {slug(h) for h in re.findall(r"^#{1,6} (.+)$", text, re.M)}


def check_local():
    """README 内の相対リンクについて、ファイルと見出しが実在するかを確かめる。"""
    rows = []
    for readme in READMES:
        text = re.sub(r"```.*?```", "", readme.read_text(encoding="utf-8"), flags=re.S)
        for target in dict.fromkeys(re.findall(r"\]\(([^)\s]+)\)", text)):
            if re.match(r"https?://", target):
                continue
            file_part, _, anchor = target.partition("#")
            dest = (readme.parent / file_part).resolve() if file_part else readme
            ok = dest.exists()
            if ok and anchor:
                ok = dest.suffix == ".md" and anchor in anchors(dest)
            where = f"{readme.relative_to(ROOT).as_posix()} → {target}"
            print(("OK   " if ok else "NG   ") + where)
            rows.append({"readme": readme.relative_to(ROOT).as_posix(), "target": target, "ok": ok})
    return rows


def main():
    OUT.mkdir(exist_ok=True)
    urls = readme_urls()
    print(f"README の URL {len(urls)} 本\n")
    rows = []
    for url in urls:
        try:
            status, final = check(url)
            redirected = final.rstrip("/") != url.rstrip("/")
            print(f"{status}  {url}")
            if redirected:
                print(f"      リダイレクト先 {final}")
            rows.append({"url": url, "status": status, "final": final, "redirected": redirected})
        except Exception as e:
            print(f"ERR  {url}  {e}")
            rows.append({"url": url, "error": str(e)})

    print("\nリポジトリ内のリンク\n")
    local = check_local()

    path = OUT / f"links-{date.today().isoformat()}.json"
    path.write_text(json.dumps({"external": rows, "local": local}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n保存 {path}")

    failed = [r for r in rows if "error" in r] + [r for r in local if not r["ok"]]
    print(f"失敗 {len(failed)} 件")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
