import subprocess
import requests
import sys
import os

def executar_testes():
    print("Executando todos os testes do projeto...")
    resultado = subprocess.run([sys.executable, "-m", "pytest", "--maxfail=5", "--disable-warnings"], capture_output=True, text=True)
    print("Saída dos testes:\n", resultado.stdout)
    if resultado.stderr:
        print("Erros:\n", resultado.stderr)
    return resultado.stdout + resultado.stderr, resultado.returncode

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
    # Busca instrução do tipo: Altere o arquivo X na linha Y para ... ou patch unified diff
    padrao1 = r"Altere o arquivo ([^ ]+) na linha (\d+) para:(.*)"
    padrao2 = r"Patch para ([^\n]+):\n([\s\S]+)"
    padrao_diff = r"diff --git a/(.+?) b/(.+?)\n([\s\S]+)"
    match1 = re.search(padrao1, sugestao, re.DOTALL)
    match2 = re.search(padrao2, sugestao, re.DOTALL)
    match_diff = re.search(padrao_diff, sugestao, re.DOTALL)
    if match1:
        arquivo = match1.group(1).strip()
        linha = int(match1.group(2))
        novo_conteudo = match1.group(3).strip()
        print(f"Alterando {arquivo} na linha {linha}...")
        # Faz backup
        if os.path.exists(arquivo):
            os.rename(arquivo, arquivo + ".bak")
        with open(arquivo + ".bak", "r", encoding="utf-8") as f:
            linhas = f.readlines()
        if linha <= len(linhas):
            linhas[linha-1] = novo_conteudo + "\n"
            with open(arquivo, "w", encoding="utf-8") as f:
                f.writelines(linhas)
            print(f"Alteração aplicada em {arquivo}.")
        else:
            print(f"Linha {linha} não existe em {arquivo}.")
    elif match2:
        arquivo = match2.group(1).strip()
        patch = match2.group(2).strip()
        print(f"Aplicando patch em {arquivo}...")
        # Aplica patch simples (substituição de bloco)
        with open(arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()
        padrao_patch = r"### PATCH START[\s\S]+### PATCH END"
        conteudo_novo = re.sub(padrao_patch, patch, conteudo)
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(conteudo_novo)
        print(f"Patch aplicado em {arquivo}.")
    elif match_diff:
        print("Patch unified diff detectado. Aplicando...")
        diff_text = match_diff.group(0)
        # Salva diff em arquivo temporário
        with open("temp_patch.diff", "w", encoding="utf-8") as f:
            f.write(diff_text)
        # Aplica patch usando git
        resultado = subprocess.run(["git", "apply", "temp_patch.diff"], capture_output=True, text=True)
        if resultado.returncode == 0:
            print("Patch aplicado com sucesso.")
        else:
            print("Falha ao aplicar patch:", resultado.stderr)
        os.remove("temp_patch.diff")
    else:
        print("Sugestão não reconhecida para aplicação automática. Revise sugestao_ollama.txt.")

def commit_alteracoes():
    print("Fazendo commit das alterações...")
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Auto-aprimoramento pelo AI agent"])
    print("Commit realizado.")

def ciclo_auto_aprimoramento():
    # Rollback automático em caso de falha
    stdout, returncode = executar_testes()
    falha = ("FAILED" in stdout or "error" in stdout.lower() or returncode != 0)
    if falha:
        print("Falha detectada nos testes. Acionando Ollama para correção...")
        sugestao = solicitar_sugestao_ollama(stdout)
        if sugestao:
            aplicar_sugestao(sugestao)
            print("Sugestão aplicada. Reexecutando testes...")
            stdout2, returncode2 = executar_testes()
            if "FAILED" not in stdout2 and "error" not in stdout2.lower() and returncode2 == 0:
                print("Testes passaram após sugestão. Realizando commit.")
                commit_alteracoes()
            else:
                print("Testes ainda falham após sugestão. Sugestão salva para revisão manual.")
                print("Realizando rollback das alterações...")
                # Restaura arquivos .bak
                for file in os.listdir():
                    if file.endswith(".bak"):
                        original = file[:-4]
                        os.replace(file, original)
                        print(f"Arquivo restaurado: {original}")
        else:
            print("Não foi possível obter sugestão do Ollama. Verifique conectividade ou logs.")
    else:
        print("Todos os testes passaram. Solicitando sugestões de melhorias ao Ollama...")
        prompt_melhoria = "Sugira melhorias, refatorações ou otimizações para o código deste projeto."
        sugestao_melhoria = solicitar_sugestao_ollama(prompt_melhoria)
        if sugestao_melhoria:
            with open("sugestao_melhoria_ollama.txt", "w", encoding="utf-8") as f:
                f.write(sugestao_melhoria)
            print("Sugestão de melhoria salva em sugestao_melhoria_ollama.txt.")
            # Tenta aplicar sugestão automaticamente se vier em formato reconhecível
            print("Tentando aplicar sugestão de melhoria automaticamente...")
            aplicar_sugestao(sugestao_melhoria)
            # Reexecuta testes para validar melhoria
            stdout3, returncode3 = executar_testes()
            if "FAILED" not in stdout3 and "error" not in stdout3.lower() and returncode3 == 0:
                print("Melhoria aplicada com sucesso. Realizando commit.")
                commit_alteracoes()
            else:
                print("Melhoria não pôde ser aplicada automaticamente ou causou falha. Sugestão salva para revisão manual.")
                print("Realizando rollback das alterações...")
                for file in os.listdir():
                    if file.endswith(".bak"):
                        original = file[:-4]
                        os.replace(file, original)
                        print(f"Arquivo restaurado: {original}")
        else:
            print("Ollama não respondeu sugestões de melhoria.")

if __name__ == "__main__":
    ciclo_auto_aprimoramento()
