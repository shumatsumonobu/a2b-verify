# verify

[README](../README.md) の引用を一次情報から取り直し、照合するスクリプトの置き場  
引用を自分で確かめたい人と、README を書き直す人が使う

## 実行

[README の検証手順](../README.md#検証手順)で仮想環境を作って有効にしたあと、リポジトリの直下で実行する

```
python -I verify/links.py
python -I verify/check_readme.py
```

[check_readme.py](check_readme.py) が残りのスクリプトを順に実行するので、個別に走らせる必要は無い  
1本ずつ出力を見たいときは `python -I verify/nict.py` のように直接実行する

## スクリプト

| スクリプト | 取得先 | 画面に出るもの |
|---|---|---|
| [links.py](links.py) | README にある全 URL と、リポジトリ内のリンク | 各 URL の status とリダイレクト先、リンク先のファイルと見出しがあるか |
| [nict.py](nict.py) | NICT の注意喚起の PDF | ページ数と文字数、`TARGETS` の文字列の前後110文字 |
| [soumu.py](soumu.py) | 総務省の注意喚起のページ | ページの日付と、A2B攻撃に触れた行 |
| [masvs.py](masvs.py) | GitHub の OWASP/masvs の `controls/` | コントロールの総数、`KEYWORDS` を含む行、認可の強制をサーバー側に置くコントロール |
| [owasp_api.py](owasp_api.py) | API Security Top 10 の API1:2023 のページ | How To Prevent の項目 |
| [maswe.py](maswe.py) | GitHub の OWASP/maswe の MASWE-0004 0005 0061 0063 | requirement と、`TARGETS` を含む行 |
| [check_readme.py](check_readme.py) | なし（links.py 以外のスクリプトを実行して、その出力を使う） | README の引用ごとに、出力に見つかったかどうか |

取得したファイルは [data/](../data/README.md) に日付つきで保存される

## README の記載との対応

| README の節 | 確かめるスクリプト |
|---|---|
| [概要](../README.md#概要) の総務省の注意喚起の日付 | [soumu.py](soumu.py) |
| [概要](../README.md#概要) の LETTICE の説明 | [nict.py](nict.py) |
| [概要](../README.md#概要) の攻撃の流れの図と、原因の一つとして確認された、の原文 | [nict.py](nict.py) |
| [調査対象](../README.md#調査対象) の PDF のページ数と版 | [nict.py](nict.py) |
| [点検表](../README.md#点検表) の確かめ方 | 各行の出典の節と同じスクリプト |
| [点検表](../README.md#点検表) の試し方の参考（OWASP WSTG） | [links.py](links.py)（ページが開けるかだけを確かめる、中身は引用していない） |
| [対象範囲](../README.md#対象範囲) | [nict.py](nict.py) |
| [狙われる脆弱性](../README.md#狙われる脆弱性) | [nict.py](nict.py) |
| [侵害の確認](../README.md#侵害の確認) | [nict.py](nict.py) |
| [脆弱性の点検](../README.md#脆弱性の点検) | [nict.py](nict.py) |
| [暫定的な緩和策](../README.md#暫定的な緩和策) | [nict.py](nict.py) |
| [恒久対策](../README.md#恒久対策) の NICT の記述 | [nict.py](nict.py) |
| [恒久対策](../README.md#恒久対策) の MASVS | [masvs.py](masvs.py) |
| [恒久対策](../README.md#恒久対策) の API Security Top 10 | [owasp_api.py](owasp_api.py) |
| [アプリ側の対策](../README.md#アプリ側の対策) の MASWE | [maswe.py](maswe.py) |
| [アプリ側の対策](../README.md#アプリ側の対策) の MASVS-AUTH-1 | [masvs.py](masvs.py) |
| [解析への対策](../README.md#解析への対策) | [nict.py](nict.py) |
| [考察](../README.md#考察) | なし（筆者の見解、各項目の根拠は調査結果の節へのリンクで示している） |
| README の全リンク | [links.py](links.py) |

## 検索文字列

- [masvs.py](masvs.py) は `KEYWORDS`、[nict.py](nict.py) と [soumu.py](soumu.py) と [maswe.py](maswe.py) は `TARGETS` に並べてある ── 増やせば当たる範囲が広がる
- README に引用を足したら、その文字列を `TARGETS` に足し、[check_readme.py](check_readme.py) で照合する
- サーバー側の認可について書いてあるかの最終判断は目視なので、出力を見て各自で判断してほしい

## 留意事項

- [check_readme.py](check_readme.py) で なし が出たら、一次情報が改訂された可能性がある ── その引用を確かめるスクリプトを単体で実行し、出力を見て README を直す
- NICT の PDF は `pdftotext` では `Unknown character collection 'Adobe-Japan1'` で落ちる ── [PyMuPDF](https://github.com/pymupdf/PyMuPDF) なら通る（実測1回）
- PyMuPDF の既定の抽出は、英数字と日本語の間の字間を空白として補う（4 種類、Android アプリなど）── PDF に無い文字を足さないよう、[nict.py](nict.py) は補わない指定（`TEXT_INHIBIT_SPACES`）で抽出し、行の折り返しは外して表示する
- PDF から抽出したテキストには行の折り返しが入るので、[nict.py](nict.py) の検索と [check_readme.py](check_readme.py) の照合は、空白と改行を無視する
- MASVS と MASWE は GitHub から認証なしで取得する ── 続けて実行して 403 が出たらレート制限なので時間を置く
- [links.py](links.py) の見出しの判定は、GitHub が見出しに付ける ID の規則を真似たもの
- Windows のコンソールは cp932 なので、各スクリプトは先頭で標準出力を UTF-8 にしている
