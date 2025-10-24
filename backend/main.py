from fastapi import FastAPI
from pydantic import BaseModel
from bedrock import create_embeddings, invoke_model

app = FastAPI()

class EmbedRequest(BaseModel):
    text: str

class ChatRequest(BaseModel):
    prompt: str

@app.post("/embed")
def embed(request: EmbedRequest):
    embeddings = create_embeddings(request.text)
    return {"embeddings": embeddings}

@app.post("/chat")
def chat(request: ChatRequest):
    response = invoke_model(request.prompt)
    return {"response": response}
