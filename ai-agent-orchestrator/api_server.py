#!/usr/bin/env python3
"""
Servidor da API para n8n + Ollama
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import uvicorn

app = FastAPI(title="n8n + Ollama API")

# CORS para n8n
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5678"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str
    model: str = "llama2"

@app.get("/")
def root():
    return {"message": "n8n + Ollama API funcionando"}

@app.post("/chat")
def chat(request: ChatRequest):
    """Chat com Ollama"""
    try:
        payload = {
            "model": request.model,
            "prompt": request.prompt,
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "response": data.get("response", ""),
            "model": request.model
        }
        
    except Exception as e:
        return {
            "response": f"Erro: {str(e)}",
            "model": request.model
        }

import subprocess
import sys

if __name__ == "__main__":
    # Inicia o n8n em segundo plano
    try:
        # Caminho padrão para instalação global do n8n via npm no Windows
        n8n_cmd_path = r"C:\Users\Felipe\AppData\Roaming\npm\n8n.cmd"
        n8n_process = subprocess.Popen([n8n_cmd_path, "start"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("n8n iniciado em segundo plano.")
    except Exception as e:
        print(f"Erro ao iniciar o n8n: {e}", file=sys.stderr)
    # Inicia o servidor FastAPI normalmente
    uvicorn.run(app, host="0.0.0.0", port=8000)
