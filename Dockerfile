FROM python:3.11-slim

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    mecab \
    libmecab-dev \
    mecab-ipadic-utf8 \
    git \
    make \
    curl \
    xz-utils \
    file \
    sudo \
    patch \
    gcc \
    g++ \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN ln -s /etc/mecabrc /usr/local/etc/mecabrc

# mecab-ipadic-neologd のインストール
# ビルド時のメモリ消費を抑えるため --depth 1 を使用
RUN git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git \
    && cd mecab-ipadic-neologd \
    && ./bin/install-mecab-ipadic-neologd -n -y \
    && cd .. \
    && rm -rf mecab-ipadic-neologd

# --- ここから追加：IPADicに必要な定義ファイルのダウンロードとUTF-8変換 ---
RUN TARGET_DIR="/var/lib/mecab/dic/ipadic-utf8" \
    && mkdir -p ${TARGET_DIR} \
    && cd /tmp \
    && for file in pos-id.def rewrite.def left-id.def right-id.def; do \
        wget https://raw.githubusercontent.com/taku910/mecab/master/mecab-ipadic/${file} -O ${file}.euc; \
        iconv -f EUC-JP -t UTF-8 ${file}.euc > ${TARGET_DIR}/${file}; \
        rm ${file}.euc; \
       done
# --- ここまで ---

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY userdic.csv .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]