"""NICT の A2B 攻撃の注意喚起 PDF を取得し、本文から該当箇所を抜き出す。

README に載せている引用と記載:
  - PDF のページ数と版（更新履歴）
  - LETTICE の説明
  - 情報漏洩事案の原因の一つとして確認された
  - 攻撃の流れ（公開アプリの入手、解析、サーバーごとの攻撃）
  - Android に限らない、認証後の API も対象になる
  - 攻撃対象になっている4種類の脆弱性と、それぞれの定義、識別子が推測しやすい場合の大量漏洩
  - 侵害の確認、脆弱性の点検、暫定的な緩和策の各項目
  - 恒久的な対策の記述と、恒久を含む箇所が1つだけであること
  - 公開アプリが解析されること自体は防げない

使い方: python -I verify/nict.py

注意: PDF は untrusted な取得物なので data/ に置く。スクリプトは verify/ に置いて分離する。
pdftotext は "Unknown character collection 'Adobe-Japan1'" で落ちるため PyMuPDF を使う。
PyMuPDF の既定の抽出は字間を空白として補うため、補わない指定で抽出する。
"""

import pathlib
import re
import sys
import urllib.request
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

PDF_URL = "https://cynex.nict.go.jp/pdf/library/lettice/261013-01.pdf"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data"

# 抜き出す語と、それが支える主張
TARGETS = [
    ("更新履歴", "版と更新日時"),
    ("原因の一つとして", "情報漏洩事案の原因の一つとして確認された"),
    ("Google Play の日本地域", "攻撃の流れ 公開アプリの入手"),
    ("アプリが通信するバックエンドサーバの接続先", "攻撃の流れ 解析で接続先や API の構成を収集"),
    ("個々のバックエンドサーバの構成やAPI の仕様に応じた攻撃", "攻撃の流れ サーバーごとに攻撃を組み立てる"),
    ("iOS アプリやWeb サービス", "対象範囲 Android に限らない"),
    ("利用者アカウントによる認証後", "対象範囲 認証後の API も対象"),
    ("主に以下の4 種類の脆弱性が探索", "攻撃対象になっている4種類の脆弱性"),
    ("SSRF は、外部からのリクエスト", "SSRF の定義"),
    ("RCE は、外部からのリクエスト", "RCE の定義"),
    ("SQL インジェクションは、API など", "SQL インジェクションの定義"),
    ("同様の問題をBOLA", "IDOR の定義と BOLA との関係"),
    ("識別子が容易に推測・列挙", "IDOR 識別子が推測・列挙できる場合の大量漏洩"),
    ("LETTICE はNICT のサイバーセキュリティネクサス", "LETTICE の説明"),
    ("ホストを列挙してください", "侵害の確認 公開ホストの列挙"),
    ("2026 年8 月以降のアクセスログ", "侵害の確認 ログと IoC の照合"),
    ("連番ID などを使ったアクセス", "侵害の確認 通常と異なる API 操作"),
    ("影響の有無と範囲を速やかに調査", "侵害の確認 影響範囲の調査"),
    ("SSRF、RCE、SQL", "4種類の重点点検の推奨"),
    ("認可不備（IDOR/BOLA）", "脆弱性の点検 認可不備"),
    ("認証・セッション管理の不備", "脆弱性の点検 認証・セッション管理"),
    ("固定された認証情報や暗号鍵", "脆弱性の点検 固定された認証情報や暗号鍵の露出"),
    ("SQL インジェクション・NoSQL", "脆弱性の点検 SQL / NoSQL インジェクション"),
    ("SSRF：URL 取得", "脆弱性の点検 SSRF"),
    ("クラウドサービス・ストレージの設定不備", "脆弱性の点検 クラウドの設定不備"),
    ("コード実行・ファイル操作に関する脆弱性", "脆弱性の点検 コード実行・ファイル操作"),
    ("国外からのアクセスや不要なアクセス元", "緩和策 国外や不要なアクセス元からの通信の制限"),
    ("不要な公開API、管理機能、検証環境", "緩和策 不要な公開APIや検証環境の停止"),
    ("API に対するアクセス頻度", "緩和策 監視とレート制限"),
    ("漏洩・悪用が疑われる場合", "緩和策 認証情報の無効化と再発行"),
    ("脆弱性が確認された場合は速やかに修正", "緩和策 修正と一時停止の検討"),
    ("恒久", "恒久的な対策に触れた箇所（README は1か所だけと書いている、ここに出る数で確かめる）"),
    ("アプリ側の制御のみに依存せず", "恒久的な対策の本文"),
    ("解析されること自体を完全に防ぐことは困難", "解析そのものは防げない"),
]


def fetch_pdf(path):
    req = urllib.request.Request(PDF_URL, headers={"User-Agent": "a2b-verify"})
    with urllib.request.urlopen(req, timeout=60) as res:
        path.write_bytes(res.read())
    return path


def extract(pdf_path, txt_path):
    import pymupdf

    doc = pymupdf.open(pdf_path)
    with txt_path.open("w", encoding="utf-8") as f:
        for page in doc:
            # 既定の抽出は、英数字と日本語の間の字間を空白として補う（「4 種類」など）
            # PDF に無い文字を足さないように、補わない指定で抽出する
            f.write(page.get_text(flags=pymupdf.TEXTFLAGS_TEXT | pymupdf.TEXT_INHIBIT_SPACES))
            f.write("\n")
    return txt_path.read_text(encoding="utf-8"), doc.page_count


def unwrap(s):
    """PDF の行の折り返しを外す、英数字どうしが折り返しで分かれた箇所だけ空白を残す。"""
    s = re.sub(r"[ \t]*\n[ \t]*", "\n", s)
    s = re.sub(r"(?<=[A-Za-z0-9])\n(?=[A-Za-z0-9])", " ", s)
    return s.replace("\n", "")


def main():
    OUT.mkdir(exist_ok=True)
    stamp = date.today().isoformat()
    pdf_path = OUT / f"nict-a2b-{stamp}.pdf"
    txt_path = OUT / f"nict-a2b-{stamp}.txt"

    print(f"取得 {PDF_URL}")
    fetch_pdf(pdf_path)
    text, pages = extract(pdf_path, txt_path)
    print(f"抽出 {txt_path}  {pages} ページ  {len(text)} 文字\n")

    for needle, claim in TARGETS:
        print(f"--- {claim} ---")
        found = False
        # 空白と改行を無視して探す、行の折り返しや抽出のしかたで空白の位置が変わっても当たるように
        pattern = r"\s*".join(re.escape(c) for c in needle if not c.isspace())
        for m in re.finditer(pattern, text):
            s, e = max(0, m.start() - 110), min(len(text), m.end() + 110)
            print("   ..." + unwrap(text[s:e]) + "...")
            found = True
        if not found:
            print("   該当なし（PDF が改訂された可能性あり）")
        print()


if __name__ == "__main__":
    main()
