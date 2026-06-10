# MeCab API Server

MeCabと、標準辞書である IPADic および最新語彙に強い mecab-ipadic-neologd の2つを内包した、汎用的な形態素解析APIサーバです。
クエリパラメータによってリアルタイムに辞書を切り替えることができ、レコメンドシステムやテキストマイニングの検証・比較評価に最適です。

## 特徴

* **FastAPIによる高速な応答**: 非同期処理に対応し、自動でSwagger UI（APIドキュメント）を生成します。
* **ダブル辞書搭載（オンメモリ待機）**: IPADic と NEOlogd の両方を起動時にロード。リクエストごとにオーバヘッドなしで高速に切り替え可能です。
* **完全な形態素解析出力**: MeCabが抽出するすべての機能特徴（品詞詳細、活用型、活用形、原形、読み、発音）を省略せずに構造化したJSONとして返します。
* **エンジニアフレンドリー**: DevContainer構成済みのため、VS Codeで開くだけで開発環境が整います。

## クイックスタート

### 1. 起動方法

Docker Composeを使用してサーバを起動します。
```bash
docker-compose up --build -d
```
※ 辞書のビルドには数分かかります。

### 2. APIドキュメントの確認

ブラウザで以下にアクセスすると、対話形式でAPIをテストできます。
* Swagger UI: http://localhost:8000/docs

### 3. APIリクエスト例

標準辞書 (IPADic) でリクエスト（パラメータ省略時は自動的に IPADic になります）
```bash
curl -X POST http://localhost:8000/parse \
     -H "Content-Type: application/json" \
     -d '{"text": "鬼滅の刃の最新刊を読んだ。"}'
```

NEOlogd に切り替えてリクエスト（URL末尾に ?dic=NEOlogd を付与）
```bash
curl -X POST http://localhost:8000/parse \
     -H "Content-Type: application/json" \
     -d '{"text": "むかしむかしあるところに"}'
```

## パラメータ仕様
POST /parse
|パラメータ名|位置|型|デフォルト値|説明|
|----|----|----|----|----|
|dic|Query (GET)|str|"IPADic"|使用する辞書。"IPADic" または "NEOlogd" を指定可能。|
|text|Body (JSON)|str|なし(必須)|解析したい日本語のテキスト。|


レスポンス
```json
{
  "analysis": [
    {
      "surface": "読ん",
      "pos": "動詞",
      "pos_detail1": "自立",
      "pos_detail2": "*",
      "pos_detail3": "*",
      "conjugated_type": "五段・マ行",
      "conjugated_form": "連用タ接続",
      "base_form": "読む",
      "reading": "ヨン",
      "pronunciation": "ヨン"
    },
    {
      "surface": "だ",
      "pos": "助動詞",
      "pos_detail1": "*",
      "pos_detail2": "*",
      "pos_detail3": "*",
      "conjugated_type": "特殊・タ",
      "conjugated_form": "基本形",
      "base_form": "だ",
      "reading": "ダ",
      "pronunciation": "ダ"
    },
    {
      "surface": "。",
      "pos": "記号",
      "pos_detail1": "句点",
      "pos_detail2": "*",
      "pos_detail3": "*",
      "conjugated_type": "*",
      "conjugated_form": "*",
      "base_form": "。",
      "reading": "。",
      "pronunciation": "。"
    }
  ]
}
```
## プロジェクト構成

```plaintext
.
├── .devcontainer/      # VS Code 開発環境設定
├── Dockerfile          # Debianベースのイメージ定義
├── docker-compose.yml  # 本番・実行用設定
├── main.py             # FastAPI アプリケーション本体
├── requirements.txt    # Python 依存ライブラリ
└── README.md           # 本ファイル
```

## 注意事項

* メモリ消費: mecab-ipadic-neologd のインストールおよび実行には、最低2GB以上のメモリ割り当てを推奨します。
* 設定ファイル: MeCabの動作に mecabrc が必要なため、Dockerfile内で /usr/local/etc/mecabrc へのシンボリックリンクを作成しています。

## ライセンス

このプロジェクトのコード（Dockerfile, docker-compose.yml, main.py等）は**パブリックドメイン**として公開します。
個人・商用問わず、改変や再配布など自由に使用して構いません。クレジット表記も不要です。

### 注意事項

本プロジェクトでインストール・利用している各ソフトウェアのライセンスについては、それぞれの権利者の規定に従ってください。


(Geminiで自動生成)