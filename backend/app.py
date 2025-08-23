import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

# --- Configuração Inicial ---

# Carrega as variáveis de ambiente do arquivo .env (que contém nossa chave de API)
# Isso permite manter a chave secreta e fora do código fonte.
load_dotenv()

# Configura a API do Google Generative AI com a chave obtida do arquivo .env
# O bloco try-except garante que a aplicação avise caso a chave não seja encontrada.
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("A chave de API do Google não foi encontrada. Verifique seu arquivo .env")
    genai.configure(api_key=api_key)
except ValueError as e:
    print(f"Erro Crítico: {e}")
    exit() # Encerra a aplicação se a chave não estiver configurada

# --- Inicialização da Aplicação Flask ---

# Cria a instância principal da aplicação web
app = Flask(__name__)
# Habilita o CORS (Cross-Origin Resource Sharing) para permitir que o frontend
# (rodando em um endereço diferente) possa fazer requisições para este backend.
CORS(app)

# --- Configuração do Modelo de Inteligência Artificial ---

# Seleciona e inicializa o modelo do Gemini que será utilizado.
# 'gemini-1.5-flash' é uma excelente escolha por ser rápido e ter um bom custo-benefício.
model = genai.GenerativeModel('gemini-1.5-flash')

# --- Definição da Rota (Endpoint) da API ---

# Define o endpoint '/api/get-response' que aceitará requisições do tipo POST.
# É para este endereço que o nosso frontend enviará a objeção do cliente.
@app.route('/api/get-response', methods=['POST'])
def get_response():
    """
    Recebe uma objeção de cliente, envia para a IA do Gemini e retorna
    uma resposta estruturada em formato JSON.
    """
    try:
        # 1. Recebe e valida os dados enviados pelo frontend
        data = request.get_json()
        objection_text = data.get('objection', '')

        # Se o texto da objeção estiver vazio, retorna um erro para o cliente.
        if not objection_text.strip():
            return jsonify({"error": "Nenhuma objeção foi fornecida"}), 400

        print(f"Objeção recebida do frontend: '{objection_text}'")
        print("Enviando para a IA do Gemini para análise...")

        # 2. Constrói o Prompt para o Gemini (Engenharia de Prompt)
        # Esta é a parte mais importante. As instruções abaixo guiam a IA para
        # gerar a resposta no formato e com a qualidade que desejamos.
        
        # No futuro, este playbook pode ser lido de um arquivo externo (ex: .txt ou .json)
        # para facilitar atualizações sem alterar o código.
        playbook_exemplo = """
        - Objeção de Preço: O foco deve ser em VALOR e RETORNO, não em CUSTO. Use analogias de investimento. Apresente o ROI (retorno sobre o investimento) com exemplos concretos.
        - Objeção de Timing ("Preciso de um tempo", "Vou pensar"): O objetivo é descobrir o receio por trás da procrastinação. Crie um senso de urgência mostrando o "custo da inação" (quanto o cliente perde por não agir agora).
        - Objeção de Confiança ("Não sei se funciona para mim"): Use prova social (cases de sucesso, depoimentos de clientes com perfis similares). Ofereça uma pequena entrega de valor para demonstrar capacidade, como uma mini-análise gratuita.
        - Objeção de Decisão em Conjunto ("Preciso falar com meu sócio/cônjuge"): Valide a importância da outra pessoa e se posicione como um aliado para ajudar a "vender a ideia" para o outro decisor. Sugira uma breve reunião a três.
        """

        prompt = f"""
        ### CONTEXTO ###
        Você é um coach de vendas sênior, especialista em treinar consultores financeiros de alta performance. Sua missão é criar um roteiro claro e eficaz para contornar uma objeção de cliente.

        ### PLAYBOOK DE ESTRATÉGIAS ###
        Use as seguintes estratégias como base para sua resposta:
        {playbook_exemplo}

        ### OBJEÇÃO DO CLIENTE ###
        A objeção que o consultor recebeu foi a seguinte: "{objection_text}"

        ### TAREFA ###
        Gere uma resposta estritamente no formato JSON. O objeto JSON deve conter exatamente as seguintes chaves e tipos de dados:
        1. "tipo_objecao": (string) Uma classificação da objeção (ex: "Preço", "Timing com toque de Confiança").
        2. "roteiro": (lista de strings) Um passo a passo com 3 a 4 etapas claras para o consultor seguir.
        3. "tom_palavras_chave": (objeto) Um objeto contendo duas chaves: "tom" (string descrevendo o tom de voz ideal) e "palavras_chave" (uma lista de strings com palavras recomendadas).
        4. "follow_up": (lista de strings) Duas sugestões de próximos passos ou ações de acompanhamento.

        ### RESTRIÇÃO IMPORTANTE ###
        Sua resposta deve ser APENAS o código JSON, sem nenhum texto, explicação ou formatação adicional como "```json" antes ou "```" depois.
        """

        # 3. Envia o prompt para a API do Gemini e aguarda a resposta
        response_ia = model.generate_content(prompt)
        
        # 4. Processa e formata a resposta da IA
        # A resposta da IA vem em um formato de texto. Precisamos garantir que é um JSON válido.
        response_text = response_ia.text.strip()
        
        # Converte a string de texto (que deve ser um JSON) em um dicionário Python
        response_json = json.loads(response_text)
        
        print("Resposta gerada pela IA e processada com sucesso.")
        
        # 5. Envia a resposta final para o frontend
        return jsonify(response_json)

    except json.JSONDecodeError:
        print(f"Erro: A IA retornou um formato que não é um JSON válido. Resposta recebida: {response_ia.text}")
        return jsonify({"error": "A resposta da IA não pôde ser processada. Tente uma formulação diferente para a objeção."}), 500
    except Exception as e:
        # Captura qualquer outro erro que possa ocorrer durante o processo
        print(f"Ocorreu um erro inesperado no servidor: {e}")
        return jsonify({"error": "Ocorreu um erro interno no servidor. Por favor, tente novamente mais tarde."}), 500

# --- Execução da Aplicação ---

# Este bloco verifica se o script está sendo executado diretamente (e não importado)
# e inicia o servidor de desenvolvimento do Flask.
if __name__ == '__main__':
    # 'debug=True' faz com que o servidor reinicie automaticamente a cada alteração no código
    # e fornece mais detalhes sobre erros.
    app.run(debug=True, port=5000)
