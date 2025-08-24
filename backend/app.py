# backend/app.py

import os
import json
import magic
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

# --- Configuração Inicial da Aplicação ---
load_dotenv()

try:
    chave_de_api = os.getenv("GOOGLE_API_KEY")
    if not chave_de_api:
        raise ValueError("A chave de API do Google não foi encontrada. Verifique seu arquivo .env")
    genai.configure(api_key=chave_de_api)
except ValueError as erro:
    print(f"Erro Crítico na Configuração: {erro}")
    exit()

# --- Carregamento do Playbook de Vendas ---
try:
    with open("playbook.txt", "r", encoding="utf-8") as arquivo_playbook:
        playbook_estrategias = arquivo_playbook.read()
    print("Playbook de vendas carregado com sucesso.")
except FileNotFoundError:
    print("Erro Crítico: O arquivo 'playbook.txt' não foi encontrado.")
    playbook_estrategias = "Nenhuma estratégia de playbook foi carregada."

# --- Inicialização do Servidor Web Flask ---
aplicacao = Flask(__name__)
CORS(aplicacao)

# --- Configuração do Modelo de Inteligência Artificial ---
modelo_ia = genai.GenerativeModel('gemini-1.5-flash')

# --- ROTA 1: TRANSCRIÇÃO DE ÁUDIO ---
@aplicacao.route('/api/transcribe-audio', methods=['POST'])
def transcrever_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "Nenhum arquivo de áudio enviado"}), 400

        arquivo_de_audio = request.files['audio']
        bytes_do_audio = arquivo_de_audio.read()
        tipo_mime = magic.from_buffer(bytes_do_audio, mime=True)
        
        print(f"Arquivo de áudio recebido. Tipo: {tipo_mime}. Tamanho: {len(bytes_do_audio)} bytes.")
        print("Enviando para a IA para transcrição...")

        arquivo_gemini = genai.upload_file(path=bytes_do_audio, mime_type=tipo_mime)

        resposta_ia = modelo_ia.generate_content([
            "Transcreva o seguinte áudio em português do Brasil.", 
            arquivo_gemini
        ])

        texto_transcrito = resposta_ia.text.strip()
        print(f"Texto transcrito: '{texto_transcrito}'")

        genai.delete_file(arquivo_gemini.name)
        return jsonify({"transcription": texto_transcrito})

    except Exception as erro:
        print(f"Ocorreu um erro na transcrição: {erro}")
        return jsonify({"error": "Não foi possível processar o arquivo de áudio."}), 500

# --- ROTA 2: GERAÇÃO DE ROTEIRO A PARTIR DE TEXTO ---
@aplicacao.route('/api/get-response', methods=['POST'])
def obter_resposta_da_ia():
    try:
        dados_da_requisicao = request.get_json()
        texto_da_objecao = dados_da_requisicao.get('objection', '')
        valor_consultoria = dados_da_requisicao.get('value', '')
        vantagens_percebidas = dados_da_requisicao.get('advantages', '')

        if not texto_da_objecao.strip():
            return jsonify({"error": "Nenhuma objeção foi fornecida"}), 400

        print(f"Objeção recebida: '{texto_da_objecao}'")
        print(f"Valor: R$ {valor_consultoria} | Vantagens: {vantagens_percebidas}")

        prompt_para_ia = f"""
        ### CONTEXTO ###
        Você é um líder da W1 Consultoria Financeira, especialista em treinar consultores financeiros. Sua missão é criar um roteiro eficaz para contornar uma objeção de fechamento de proposta de consultoria.

        ### PLAYBOOK DE ESTRATÉGIAS ###
        {playbook_estrategias}

        ### DADOS ESPECÍFICOS DA NEGOCIAÇÃO ###
        - Objeção do Cliente: "{texto_da_objecao}"
        - Valor da Consultoria: "R$ {valor_consultoria}"
        - Vantagens que o cliente já percebeu ou que foram apresentadas: "{vantagens_percebidas}"

        ### TAREFA ###
        Use TODOS os dados da negociação para criar uma resposta altamente personalizada.
        - Se a objeção for sobre PREÇO, use o 'Valor da Consultoria' e as 'Vantagens' para construir um argumento de ROI (Retorno sobre Investimento) forte e específico. Transforme o valor de um 'custo' para um 'investimento' que se paga.
        - Se a objeção for outra, use as 'Vantagens' para reforçar o valor e relembrar o cliente do que ele está buscando.
        - Gere a resposta no formato JSON com as chaves: "tipo_objecao", "roteiro", "tom_palavras_chave", "follow_up".

        ### RESTRIÇÃO IMPORTANTE ###
        Sua resposta deve ser APENAS o código JSON, sem nenhum texto ou formatação adicional.
        """

        resposta_ia = modelo_ia.generate_content(prompt_para_ia)
        
        texto_da_resposta = resposta_ia.text
        texto_limpo = texto_da_resposta.strip().replace('```json', '').replace('```', '')
        
        json_da_resposta = json.loads(texto_limpo)
        
        print("Roteiro personalizado gerado pela IA com sucesso.")
        return jsonify(json_da_resposta)

    except json.JSONDecodeError:
        print(f"Erro de Formato: A IA retornou um texto que não é um JSON válido. Resposta: {resposta_ia.text}")
        return jsonify({"error": "A resposta da IA não pôde ser processada."}), 500
    except Exception as erro:
        print(f"Ocorreu um erro inesperado: {erro}")
        return jsonify({"error": "Ocorreu um erro interno no servidor."}), 500

# --- Execução da Aplicação ---
if __name__ == '__main__':
    aplicacao.run(debug=True, port=5000)
