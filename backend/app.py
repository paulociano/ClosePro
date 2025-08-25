# backend/app.py

import os
import json
import filetype
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

# --- Carregamento dos Playbooks e Cases ---
try:
    with open("playbook.txt", "r", encoding="utf-8") as arquivo_playbook:
        playbook_estrategias = arquivo_playbook.read()
    print("Playbook de vendas carregado com sucesso.")
except FileNotFoundError:
    print("Erro Crítico: O arquivo 'playbook.txt' não foi encontrado.")
    playbook_estrategias = "Nenhuma estratégia de playbook foi carregada."

try:
    with open("cases.txt", "r", encoding="utf-8") as arquivo_cases:
        cases_de_sucesso = arquivo_cases.read()
    print("Cases de sucesso carregados com sucesso.")
except FileNotFoundError:
    print("Aviso: O arquivo 'cases.txt' não foi encontrado. A IA não usará exemplos.")
    cases_de_sucesso = "Nenhum case de sucesso disponível."


# --- Inicialização do Servidor Web Flask ---
aplicacao = Flask(__name__)
CORS(aplicacao)

# --- Configuração do Modelo de Inteligência Artificial ---
modelo_ia = genai.GenerativeModel('gemini-1.5-flash')

@aplicacao.route('/api/transcribe-audio', methods=['POST'])
def transcrever_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "Nenhum arquivo de áudio enviado"}), 400

        arquivo_de_audio = request.files['audio']
        bytes_do_audio = arquivo_de_audio.read()
        
        # --- ALTERAÇÃO AQUI ---
        # Usa a nova biblioteca 'filetype' para detetar o tipo do ficheiro
        kind = filetype.guess(bytes_do_audio)
        if kind is None:
            print("Erro: Não foi possível determinar o tipo do ficheiro de áudio.")
            return jsonify({"error": "Tipo de ficheiro de áudio não suportado."}), 400
        
        tipo_mime = kind.mime
        # --- FIM DA ALTERAÇÃO ---
        
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

# --- ROTA 2: GERAÇÃO DE ROTEIRO ---
@aplicacao.route('/api/get-response', methods=['POST'])
def obter_resposta_da_ia():
    try:
        dados_da_requisicao = request.get_json()
        texto_da_objecao = dados_da_requisicao.get('objection', '')
        valor_consultoria = dados_da_requisicao.get('value', '')
        vantagens_percebidas = dados_da_requisicao.get('advantages', '')
        perfil_disc = dados_da_requisicao.get('disc_profile', 'nao_selecionado')

        if not texto_da_objecao.strip():
            return jsonify({"error": "Nenhuma objeção foi fornecida"}), 400

        print(f"Objeção: '{texto_da_objecao}', Perfil DISC: {perfil_disc}")

        prompt_para_ia = f"""
        ### CONTEXTO ###
        Você é um líder da W1 Consultoria Financeira, especialista em treinar consultores financeiros e mestre na metodologia DISC. Sua missão é criar um roteiro completo para contornar uma objeção.

        ### PLAYBOOK DE ESTRATÉGIAS ###
        {playbook_estrategias}

        ### BIBLIOTECA DE CASES DE SUCESSO ###
        {cases_de_sucesso}

        ### DADOS DA NEGOCIAÇÃO ###
        - Objeção do Cliente: "{texto_da_objecao}"
        - Valor da Consultoria: "R$ {valor_consultoria}"
        - Vantagens Percebidas: "{vantagens_percebidas}"
        - Perfil do Cliente (DISC): "{perfil_disc}"

        ### INSTRUÇÕES DE COMUNICAÇÃO (DISC) ###
        - Se o perfil for 'dominancia' (D): Seja direto, rápido e foque nos resultados e no ROI. Use frases curtas e poderosas. Evite detalhes excessivos.
        - Se o perfil for 'influencia' (I): Seja otimista, amigável e foque em como a solução vai melhorar a vida dele e como outros clientes ficaram satisfeitos. Use prova social.
        - Se o perfil for 'estabilidade' (S): Seja calmo, paciente e foque na segurança e na garantia do processo. Apresente um plano passo a passo. Evite pressão.
        - Se o perfil for 'conformidade' (C): Seja preciso, lógico e foque em dados, fatos e evidências. Apresente o processo de forma detalhada e responda a todas as perguntas com exatidão.
        - Se o perfil for 'nao_selecionado', use uma abordagem neutra e equilibrada.
        
        Sempre utilize técnicas como o golden circle, PNL e Rapport para trazer uma resposta bem completa. Nunca deixe para depois para fazer o fechamento.
        Concentre em tentar quebrar as objeções para que a venda seja finalizada no momento da reunião e não 15 minutos ou dias depois.
        Evite perguntas muito fechadas que permitem responder sim ou não.

        ### TAREFA ###
        1.  Use os dados da negociação e o playbook para criar um roteiro.
        2.  Selecione o case de sucesso MAIS RELEVANTE da biblioteca para fortalecer o argumento.
        3.  Crie uma sugestão de ação de follow-up. A PRIMEIRA OPÇÃO deve ser sempre uma LIGAÇÃO ou uma resposta FALADA. Uma mensagem de WhatsApp só deve ser sugerida como último recurso.
        4.  Gere o TEXTO COMPLETO para a mensagem de follow-up (e-mail ou WhatsApp), usando quebras de linha (\\n) para separar parágrafos.
        5.  Gere a resposta no formato JSON com as chaves: "tipo_objecao", "roteiro", "tom_palavras_chave", "follow_up_sugerido" (string com a ação recomendada), e "mensagem_follow_up" (string com o texto completo).

        ### RESTRIÇÃO IMPORTANTE ###
        Sua resposta deve ser APENAS o código JSON, sem nenhum texto ou formatação adicional.
        """

        resposta_ia = modelo_ia.generate_content(prompt_para_ia)
        
        texto_da_resposta = resposta_ia.text
        texto_limpo = texto_da_resposta.strip().replace('```json', '').replace('```', '')
        
        json_da_resposta = json.loads(texto_limpo)
        
        print("Roteiro completo (com case e follow-up) gerado pela IA com sucesso.")
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