import os
import subprocess
import sys

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import MeCab

app = FastAPI(title="MeCab API")

# Debian系でのNeologd標準パス
SYSDIC_NEOLOGD = "/usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd"
SYSDIC_IPADIC = "/var/lib/mecab/dic/ipadic-utf8"
USERDIC_NEOLOGD = "userdic-neologd.dic"
USERDIC_IPADIC = "userdic-ipadic.dic"
USERDICCSV = "userdic.csv"

env = os.environ.copy()
env["LANG"] = "C.UTF-8"
env["LC_ALL"] = "C.UTF-8"

def build_user_dic(user_csv:str, user_dic:str, system_dic:str):
    if not os.path.exists(user_dic) or os.path.getmtime(user_csv) > os.path.getmtime(user_dic):
        print("ユーザー辞書を再ビルド中...")
        subprocess.run([
            "/usr/lib/mecab/mecab-dict-index", 
            "-d", system_dic, 
            "-u", user_dic, 
            "-f", "utf-8", 
            "-t", "utf-8", 
            user_csv
        ], check=True, stdout=sys.stdout, stderr=sys.stderr, env=env)
taggers=dict()
try:
    build_user_dic(USERDICCSV, USERDIC_NEOLOGD, SYSDIC_NEOLOGD)
    taggers['NEOlogd'] = MeCab.Tagger(f"-d {SYSDIC_NEOLOGD} -u {USERDIC_NEOLOGD}")
except Exception as e:
    print(f"Error initializing tagger NEOlogd: {e}",file=sys.stderr)
try:
    build_user_dic(USERDICCSV, USERDIC_IPADIC, SYSDIC_IPADIC)
    taggers['IPADic'] = MeCab.Tagger(f"-d {SYSDIC_IPADIC} -u {USERDIC_IPADIC}")
except Exception as e:
    print(f"Error initializing tagger IPADic: {e}",file=sys.stderr)

class ParseRequest(BaseModel):
    text: str

class ParseRequests(BaseModel):
    texts: List[str]

@app.post("/parse")
async def parse_one(
    request: ParseRequest,
    dic: str = Query("IPADic", description="使用する辞書: 'IPADic' または 'NEOlogd'")
):
    return {"analysis": await parse_impl([request.text], dic)[0]}


@app.post("/parseAll")
async def parse_all(
    request: ParseRequests,
    dic: str = Query("IPADic", description="使用する辞書: 'IPADic' または 'NEOlogd'")
):
    return {"analysis": await parse_impl(request.texts, dic)}

async def parse_impl(
    texts: List[str],
    dic: str = Query("IPADic", description="使用する辞書: 'IPADic' または 'NEOlogd'")
):
    if len(taggers)<=0:
        raise HTTPException(status_code=500, detail="MeCab Tagger not initialized")
    tagger = taggers.get(dic)
    if tagger is None:
        raise HTTPException(status_code=422, detail="MeCab Tagger not found")

    results = []
    for text in texts:
        node = tagger.parseToNode(text)
        results_one = []
        while node:
            if node.surface:
                f = node.feature.split(",")
                results_one.append({
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
        results.append(results_one)
    return results
