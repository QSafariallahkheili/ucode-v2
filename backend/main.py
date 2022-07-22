from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from db import get_table_names

app = FastAPI()
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def root():
    table_names = get_table_names()
    if table_names:
        result = []
        for table in table_names:
            d = dict()
            d['id'] = table_names.index(table)
            d['name'] = table[0]
            result.append(d)
        subjects = json.dumps(result)
        return json.loads(subjects)
    else:
        return "json.loads(subjects)"
