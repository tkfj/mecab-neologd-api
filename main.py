from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import MeCab

app = FastAPI(title="MeCab Neologd API (Debian Base)")

# Debian系でのNeologd標準パス
DIC_NEOLOGD = "/usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd"

try:
    tagger = MeCab.Tagger(f"-d {DIC_NEOLOGD}")
except Exception as e:
    print(f"Error initializing tagger: {e}")
    tagger = None

class ParseRequest(BaseModel):
    text: str
    wakati: Optional[bool] = False

@app.post("/parse")
async def parse_text(request: ParseRequest):
    if not tagger:
        raise HTTPException(status_code=500, detail="MeCab Tagger not initialized")

    if request.wakati:
        parsed = tagger.parse(request.text).strip()
        return {"tokens": parsed.split(" ")}

    node = tagger.parseToNode(request.text)
    results = []
    while node:
        if node.surface:
            f = node.feature.split(",")
            results.append({
                "surface": node.surface,
                "pos": f[0],
                "base_form": f[6] if len(f) > 6 else node.surface,
                "reading": f[7] if len(f) > 7 else ""
            })
        node = node.next
    return {"analysis": results}
