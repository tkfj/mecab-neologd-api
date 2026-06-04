# MeCab Neologd API Server

MeCabと最新語彙に強い辞書 `mecab-ipadic-neologd` を組み合わせた、汎用的な形態素解析APIサーバです。
Debianベースの軽量な構成で、DockerおよびDevContainer環境ですぐに開発・運用が可能です。

## 特徴

- **FastAPIによる高速な応答**: 非同期処理に対応し、自動でSwagger UI（APIドキュメント）を生成します。
- **最新語彙に対応**: `mecab-ipadic-neologd` を標準搭載し、新語や固有名詞の解析に強いです。
- **柔軟な解析オプション**: 詳細な品詞解析と、シンプルな分かち書き（Wakati）モードを選択可能です。
- **エンジニアフレンドリー**: DevContainer構成済みのため、VS Codeで開くだけで開発環境が整います。

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

形態素解析 (詳細)
```bash
curl -X POST http://localhost:8000/parse \
     -H "Content-Type: application/json" \
     -d '{"text": "鬼滅の刃の最新刊を読んだ。"}'
```
分かち書きモード
```bash
curl -X POST http://localhost:8000/parse \
     -H "Content-Type: application/json" \
     -d '{"text": "むかしむかしあるところに", "wakati": true}'
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