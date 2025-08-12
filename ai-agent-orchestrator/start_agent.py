#!/usr/bin/env python3
"""
Start Agent - Inicia todos os serviços automaticamente
"""
import subprocess
import time
import requests
import sys
import os
from pathlib import Path

def check_service(url, service_name, timeout=10):
    """Verifica se um serviço está rodando"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def start_ollama():
    """Inicia o Ollama"""
    print("🤖 Iniciando Ollama...")
    
    try:
        # Verificar se já está rodando
        if check_service("http://localhost:11434/api/tags", "Ollama"):
            print("✅ Ollama já está rodando!")
            return True
        
        # Tentar iniciar o Ollama
        print("   Iniciando serviço Ollama...")
        subprocess.Popen(["ollama", "serve"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Aguardar inicialização
        for i in range(30):
            if check_service("http://localhost:11434/api/tags", "Ollama"):
                print("✅ Ollama iniciado com sucesso!")
                return True
            time.sleep(1)
            print(f"   Aguardando... {i+1}/30")
        
        print("❌ Falha ao iniciar Ollama")
        return False
        
    except Exception as e:
        print(f"❌ Erro ao iniciar Ollama: {e}")
        return False

def start_n8n():
    """Verifica se o n8n está rodando"""
    print("🔧 Verificando n8n...")
    
    if check_service("http://localhost:5678", "n8n"):
        print("✅ n8n já está rodando!")
        return True
    else:
        print("⚠️  n8n não está rodando na porta 5678")
        print("   Inicie manualmente com: n8n start")
        return False

def start_api_server():
    """Inicia o servidor da API"""
    print("🚀 Iniciando servidor da API...")
    
    try:
        # Verificar se já está rodando
        if check_service("http://localhost:8000", "API"):
            print("✅ API já está rodando!")
            return True
        
        # Iniciar servidor em background
        subprocess.Popen([sys.executable, "api_server.py"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Aguardar inicialização
        for i in range(15):
            if check_service("http://localhost:8000", "API"):
                print("✅ API iniciada com sucesso!")
                return True
            time.sleep(1)
            print(f"   Aguardando... {i+1}/15")
        
        print("❌ Falha ao iniciar API")
        return False
        
    except Exception as e:
        print(f"❌ Erro ao iniciar API: {e}")
        return False

def create_api_server():
    """Cria o servidor da API se não existir"""
    if not Path("api_server.py").exists():
        print("📝 Criando servidor da API...")
        
        api_code = '''#!/usr/bin/env python3
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        with open("api_server.py", "w", encoding="utf-8") as f:
            f.write(api_code)
        
        print("✅ Servidor da API criado!")

def main():
    """Função principal"""
    print("🚀 START AGENT - Iniciando todos os serviços...")
    print("=" * 50)
    
    # Criar servidor da API se necessário
    create_api_server()
    
    # Iniciar serviços
    ollama_ok = start_ollama()
    n8n_ok = start_n8n()
    api_ok = start_api_server()
    
    print("\n" + "=" * 50)
    print("📊 STATUS DOS SERVIÇOS:")
    print(f"   🤖 Ollama: {'✅' if ollama_ok else '❌'}")
    print(f"   🔧 n8n: {'✅' if n8n_ok else '❌'}")
    print(f"   🚀 API: {'✅' if api_ok else '❌'}")
    
    if ollama_ok and n8n_ok and api_ok:
        print("\n🎉 TODOS OS SERVIÇOS ESTÃO FUNCIONANDO!")
        print("\n🔗 URLs:")
        print("   • n8n: http://localhost:5678")
        print("   • Ollama: http://localhost:11434")
        print("   • API: http://localhost:8000")
        print("\n📖 Para usar no n8n:")
        print("   • URL: http://localhost:8000/chat")
        print("   • Method: POST")
        print("   • Body: {\"prompt\": \"sua pergunta\"}")
        
    else:
        print("\n⚠️  Alguns serviços falharam. Verifique os logs acima.")
    
    print("\n🔄 Para parar tudo, use: Ctrl+C")

if __name__ == "__main__":
    try:
        main()
        print("\n⏸️  Pressione Ctrl+C para parar os serviços...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Parando todos os serviços...")
        sys.exit(0)

