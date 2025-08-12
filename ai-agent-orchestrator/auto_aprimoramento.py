import subprocess
import requests
import sys
import os

def executar_testes():
    print("Executando testes...")
    resultado = subprocess.run([sys.executable, "-m", "pytest"], capture_output=True, text=True)
    print(resultado.stdout)
    return resultado.stdout, resultado.returncode

def solicitar_sugestao_ollama(erro):
    print("Solicitando sugestão ao Ollama...")
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama2",
        "prompt": f"Corrija o seguinte erro nos testes: {erro}"
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        sugestao = data.get("response", "")
        print("Sugestão recebida:", sugestao)
        return sugestao
    except Exception as e:
        print("Erro ao solicitar ao Ollama:", e)
        return None

def aplicar_sugestao(sugestao):
    print("Aplicando sugestão automaticamente...")
    import re
    # Salva sugestão para histórico
    with open("sugestao_ollama.txt", "w", encoding="utf-8") as f:
        f.write(sugestao)
    # Busca instrução do tipo: Altere o arquivo X na linha Y para ...
    padrao = r"Altere o arquivo ([^ ]+) na linha (\d+) para:(.*)"
    match = re.search(padrao, sugestao, re.DOTALL)
    if match:
        arquivo = match.group(1).strip()
        linha = int(match.group(2))
        novo_conteudo = match.group(3).strip()
        print(f"Alterando {arquivo} na linha {linha}...")
        # Faz backup
        if os.path.exists(arquivo):
            os.rename(arquivo, arquivo + ".bak")
        # Aplica alteração
        with open(arquivo + ".bak", "r", encoding="utf-8") as f:
            linhas = f.readlines()
        if linha <= len(linhas):
            linhas[linha-1] = novo_conteudo + "\n"
            with open(arquivo, "w", encoding="utf-8") as f:
                f.writelines(linhas)
            print(f"Alteração aplicada em {arquivo}.")
        else:
            print(f"Linha {linha} não existe em {arquivo}.")
    else:
        print("Sugestão não reconhecida para aplicação automática. Revise sugestao_ollama.txt.")

def commit_alteracoes():
    print("Fazendo commit das alterações...")
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Auto-aprimoramento pelo AI agent"])
    print("Commit realizado.")

def ciclo_auto_aprimoramento():
    stdout, returncode = executar_testes()
    if "FAILED" in stdout or returncode != 0:
        sugestao = solicitar_sugestao_ollama(stdout)
        if sugestao:
            aplicar_sugestao(sugestao)
            print("Execute a sugestão manualmente ou adapte o script para aplicar automaticamente.")
            stdout2, returncode2 = executar_testes()
            if "FAILED" not in stdout2 and returncode2 == 0:
                commit_alteracoes()
            else:
                print("Testes ainda falham após sugestão.")
        else:
            print("Não foi possível obter sugestão do Ollama.")
    else:
        print("Todos os testes passaram. Nenhuma ação necessária.")

if __name__ == "__main__":
    ciclo_auto_aprimoramento()
