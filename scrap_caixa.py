import os
import requests
import time

# CONFIGURAÇÃO DE CAMINHOS (funciona localmente e no GitHub Actions)
DIRETORIO_TRABALHO = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_CSV_FINAL = os.path.join(DIRETORIO_TRABALHO, "historico_sorteios.csv")

# Endpoints da API oficial de resultados
URL_ULTIMO = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"
URL_ESPECIFICO = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/{}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def obter_ultimo_concurso_caixa():
    try:
        resposta = requests.get(URL_ULTIMO, headers=HEADERS, timeout=15)
        if resposta.status_code == 200:
            return resposta.json().get("numero")
    except Exception as e:
        print(f"❌ Erro ao consultar último concurso: {e}")
    return None

def obter_dezenas_concurso(numero_concurso):
    try:
        resposta = requests.get(URL_ESPECIFICO.format(numero_concurso), headers=HEADERS, timeout=15)
        if resposta.status_code == 200:
            return resposta.json().get("listaDezenas")
    except Exception as e:
        print(f"❌ Erro ao buscar concurso {numero_concurso}: {e}")
    return None

def atualizar_concursos():
    if not os.path.exists(ARQUIVO_CSV_FINAL):
        print(f"❌ Arquivo não localizado em: {ARQUIVO_CSV_FINAL}")
        return

    with open(ARQUIVO_CSV_FINAL, "r", encoding="utf-8") as f:
        linhas = [l.strip() for l in f.readlines() if l.strip() and ";" in l]
    
    ultimo_gravado = len(linhas)
    print(f"📊 Seu arquivo atual possui {ultimo_gravado} concursos válidos registrados.")

    print("📡 Verificando o último sorteio disponível no servidor da Caixa...")
    ultimo_caixa = obter_ultimo_concurso_caixa()
    
    if not ultimo_caixa:
        print("❌ Não foi possível obter o último concurso do servidor.")
        return
        
    print(f"🎰 Último concurso realizado na Caixa: {ultimo_caixa}")

    if ultimo_gravado >= ultimo_caixa:
        print("✅ Seu arquivo já está totalmente atualizado com o último sorteio.")
        return

    concursos_pendentes = ultimo_caixa - ultimo_gravado
    print(f"🔄 Sincronizando {concursos_pendentes} concurso(s) pendente(s)...")

    with open(ARQUIVO_CSV_FINAL, "a", encoding="utf-8") as f_csv:
        for concurso in range(ultimo_gravado + 1, ultimo_caixa + 1):
            print(f"📥 Baixando Concurso {concurso}...")
            dezenas = obter_dezenas_concurso(concurso)
            
            if dezenas:
                dezenas_ordenadas = sorted([int(d) for d in dezenas])
                linha_formatada = ";".join(map(str, dezenas_ordenadas))
                f_csv.write(linha_formatada + "\n")
                print(f"💾 Gravado com sucesso: {linha_formatada}")
                time.sleep(1)
            else:
                print(f"⚠️ Falha ao obter dados do concurso {concurso}. Processo interrompido.")
                break

    print("✅ Processo de atualização concluído.")

if __name__ == "__main__":
    print("🤖 Execução automatizada iniciada.")
    atualizar_concursos()
