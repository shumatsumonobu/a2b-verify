# data

[verify/](../verify/README.md) のスクリプトが取得したファイルの置き場  
この README 以外はリポジトリに含めない ── スクリプトを実行すると、その日に取得したものが手元に保存される

## 取得物の索引

`YYYY-MM-DD` は実行した日付、同じ日に実行し直すと上書きされる  
日付ごとにファイルが分かれるので、日を変えて取り直せば、一次情報が改訂されたかを比べられる

| ファイル | 作るスクリプト | 中身 |
|---|---|---|
| `links-YYYY-MM-DD.json` | [links.py](../verify/links.py) | README にある各 URL の status、最終的な URL、リダイレクトの有無と、リポジトリ内のリンクの確認結果 |
| `nict-a2b-YYYY-MM-DD.pdf` | [nict.py](../verify/nict.py) | NICT の注意喚起の PDF そのもの |
| `nict-a2b-YYYY-MM-DD.txt` | [nict.py](../verify/nict.py) | PDF から PyMuPDF で抽出した全文（字間を空白で補わない指定、行の折り返しはそのまま） |
| `soumu-YYYY-MM-DD.html` | [soumu.py](../verify/soumu.py) | 総務省の注意喚起のページの HTML そのもの |
| `masvs-YYYY-MM-DD.json` | [masvs.py](../verify/masvs.py) | コントロールの総数、`KEYWORDS` に当たった行、認可の強制をサーバー側に置くコントロール |
| `owasp-api1-YYYY-MM-DD.html` | [owasp_api.py](../verify/owasp_api.py) | API1:2023 のページの HTML そのもの |
| `maswe-YYYY-MM-DD.json` | [maswe.py](../verify/maswe.py) | 各弱点の URL、タイトル、requirement、`TARGETS` に当たった行 |

[check_readme.py](../verify/check_readme.py) はファイルを保存しない

## 扱い

- PDF と HTML は外部のサイトから取得したもの ── この中で Python を起動しない、スクリプトは `verify/` から `python -I` で実行する
- このリポジトリの作者が取得したものを公開しないのは、各自が取り直した結果で確かめるため
