import sys
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import MeCab

app = FastAPI(title="MeCab API")

# Debian系でのNeologd標準パス
DIC_NEOLOGD = "/usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd"
DIC_IPADIC = "/var/lib/mecab/dic/ipadic-utf8"

taggers=dict()
try:
    taggers['NEOlogd'] = MeCab.Tagger(f"-d {DIC_NEOLOGD}")
except Exception as e:
    print(f"Error initializing tagger NEOlogd: {e}",file=sys.stderr)
try:
    taggers['IPADic'] = MeCab.Tagger(f"-d {DIC_IPADIC}")
except Exception as e:
    print(f"Error initializing tagger IPADic: {e}",file=sys.stderr)

class ParseRequest(BaseModel):
    text: str

@app.post("/parse")
async def parse_text(
    request: ParseRequest,
    dic: str = Query("IPADic", description="使用する辞書: 'IPADic' または 'NEOlogd'")
):
    if len(taggers)<=0:
        raise HTTPException(status_code=500, detail="MeCab Tagger not initialized")
    tagger = taggers.get(dic)
    if tagger is None:
        raise HTTPException(status_code=400, detail="MeCab Tagger not found")

    node = tagger.parseToNode(request.text)
    results = []
    while node:
        if node.surface:
            f = node.feature.split(",")
            results.append({
                "surface": node.surface,
                "pos": f[0] if len(f) > 0 else "",          # 品詞大分類 (例: 名詞)
                "pos_detail1": f[1] if len(f) > 1 else "",  # 品詞詳細1 (例: 固有名詞)
                "pos_detail2": f[2] if len(f) > 2 else "",  # 品詞詳細2 (例: 一般)
                "pos_detail3": f[3] if len(f) > 3 else "",  # 品詞詳細3 (例: *)
                "conjugated_type": f[4] if len(f) > 4 else "", # 活用型 (例: サ変・スル)
                "conjugated_form": f[5] if len(f) > 5 else "", # 活用形 (例: 基本形)
                "base_form": f[6] if len(f) > 6 else node.surface, # 原形 (例: 健康)
                "reading": f[7] if len(f) > 7 else "",      # 読み (例: ケンコウ)
                "pronunciation": f[8] if len(f) > 8 else "" # 発音 (例: ケンコー)
            })
        node = node.next
    return {"analysis": results}
