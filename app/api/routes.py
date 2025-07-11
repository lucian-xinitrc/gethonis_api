import core, psycopg2, markdown, os, secrets, requests, json
from core import utils as ut
from typing import List, Dict
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import datetime, timedelta
from .authentication import Authentication
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import StreamingResponse, HTMLResponse

# Router initialiser
router = APIRouter()

# Initialising directory ( the dir were the html files will be)
templates = Jinja2Templates(directory="templates")

# Main Page displayer
@router.get("/")
def custom_docs(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# The route get route that generates the API Key
@router.get("/genToken")
def generatetoken():
    load_dotenv()
    db = Authentication()
    cursor = db.conn.cursor()
    insert_query = """
        INSERT INTO tokens (token, tries)
        VALUES (%s, %s);
        """
    token = "geth-" + secrets.token_urlsafe(16)
    try:
        data = (token, 0)
        cursor.execute(insert_query, data)
        db.conn.commit()
        return {"token": token}
    except Exception as e:
        print("Eroare la inserare în DB:", e)
        return {"error": str(e)}

# The token authorisation path
@router.post("/api/authorisation")
def check(tryIt: ut.Try):
	try:
		conn = Authentication()
		conn.check_auth(tryIt.token)
		if conn.auth == True:
			return {"Status": "Positive"}
	except:
		return {"Status": "Negative"}

@router.post("/api/gethonis")
def response_gethonis(action: ut.Message):
	token = action.headers
	message = action.messages
	if action.stream:
		return ut.streaming(token, message, "text/plain", 1)
	return ut.non_streaming(token, message, "text/plain", 1)

@router.post("/api/post")
def get_post(postc: ut.PostContent):
    token = postc.headers
    type = postc.type
    message = postc.prompt
    return ut.post_returning(token, type, message, 1)

@router.post("/api/checkpost")
def checkpost(check: ut.PostVerify):
    token = check.headers
    id = check.id
    return ut.checkPost(token, id)

@router.post("/api/addpost")
async def addpost(add: ut.PostAdd):
    token = add.headers
    idy = add.id
    prompty = add.prompt

    db = Authentication()
    db.check_auth(token)
    addPostData = db.conn.cursor()

    date_gen = ut.post_returning(token, "", prompty, 1)
    date = next(date_gen)

    addPostData.execute(
        "INSERT INTO public.posts (id, Data) VALUES (%s, %s)",
        (idy, date)
    )

    db.conn.commit()
    addPostData.close()
    return {"status": "ok"}

@router.post("/api/openai")
def response_openai(action: ut.Message):
	token = action.headers
	message = action.messages
	if action.stream:
		return ut.streaming(token, message, "text/plain", 2)
	return ut.non_streaming(token, message, "text/plain", 2)

@router.post("/api/grok")
def response_deepseek(action: ut.Message):
	token = action.headers
	message = action.messages
	if action.stream:
		return ut.streaming(token, message, "text/plain", 3)
	return ut.non_streaming(token, message, "text/plain", 3)
