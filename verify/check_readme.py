"""README の引用が、各スクリプトの出力に原文どおり出ているかを照合する。

nict.py soumu.py masvs.py owasp_api.py maswe.py を順に実行し、その出力と README を突き合わせる。
照合の対象は、README の引用（> で始まる行）と、表の requirement の原文。
PDF から抽出したテキストには改行や空白が入るので、空白を無視して比べる。

使い方: python -I verify/check_readme.py
1件でも見つからなければ終了コード 1
"""

import pathlib
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
SCRIPTS = ["nict.py", "soumu.py", "masvs.py", "owasp_api.py", "maswe.py"]


def normalize(s):
    return re.sub(r"[\s*`]+", "", s)


def run(script):
    res = subprocess.run([sys.executable, "-I", str(ROOT / "verify" / script)],
                         capture_output=True, encoding="utf-8", cwd=ROOT)
    if res.returncode != 0:
        print(f"{script} が失敗した\n{res.stderr}")
        sys.exit(1)
    return res.stdout


def readme_quotes(text):
    # 引用の行頭の箇条書きの記号（原文に合わせた • と、Markdown の -）は原文ではないので外す
    quotes = [re.sub(r"^>\s*(?:[-•]\s*)?", "", l) for l in text.splitlines() if l.startswith(">")]
    # 表のセルにある requirement の原文、列の位置に依らず拾う
    quotes += re.findall(r"\| (The app [^|]+?) \|", text)
    return [q for q in quotes if q.strip()]


def main():
    output = ""
    for script in SCRIPTS:
        print(f"実行 verify/{script}")
        output += run(script)
    flat = normalize(output)

    quotes = readme_quotes(README.read_text(encoding="utf-8"))
    missing = [q for q in quotes if normalize(q) not in flat]

    print()
    for q in quotes:
        print(("なし  " if q in missing else "あり  ") + q[:60])
    print(f"\n出力に見つかった引用 {len(quotes) - len(missing)} / {len(quotes)} 件")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
