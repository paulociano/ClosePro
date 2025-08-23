# backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import time # Apenas para simular um tempo de resposta

# Inicializa a aplicação Flask
app = Flask(__name__)
# Habilita o CORS para permitir requisições do nosso frontend
CORS(app)

# Define a rota (endpoint) da nossa API
@app.route('/api/get-response', methods=['POST'])
def get_response():
    # 1. Recebe o dado enviado pelo frontend
    data = request.json
    objection_text = data.get('objection', '')

    # Imprime no terminal para sabermos que o backend recebeu a objeção
    print(f"Objeção recebida do frontend: '{objection_text}'")

    # 2. Resposta MOCK (simulando o que a IA vai gerar no futuro)
    #    Nesta fase, a resposta é sempre a mesma, não importa a entrada.
    mock_response = {
        "tipo_objecao": "Preço (Mock)",
        "roteiro": [
            "Passo 1 (Validar): Entendo sua preocupação com o investimento. É um ponto importante. Além do valor, há mais algum detalhe que te preocupa?",
            "Passo 2 (Ressignificar): Quero te mostrar como vemos isso não como um custo, mas como um investimento direto na sua tranquilidade e futuro financeiro. O objetivo é que o valor gerado pague a consultoria múltiplas vezes.",
            "Passo 3 (Prova): Por exemplo, um cliente com um perfil semelhante ao seu conseguiu uma economia fiscal de R$ X já no primeiro ano. Posso te mostrar esse estudo de caso?"
        ],
        "tom_palavras_chave": {
            "tom": "Empático, Consultivo, Confiante",
            "palavras_chave": ["Investimento", "Retorno", "Segurança", "Estudo de Caso"]
        },
        "follow_up": [
            "Enviar o estudo de caso mencionado.",
            "Agendar uma conversa de 15 minutos para detalhar a projeção de retorno."
        ]
    }

    # Simula um pequeno atraso, como se a IA estivesse "pensando"
    time.sleep(1)

    # 3. Envia a resposta de volta para o frontend em formato JSON
    return jsonify(mock_response)

# Roda o servidor quando o script é executado
if __name__ == '__main__':
    # O debug=True faz com que o servidor reinicie automaticamente após cada alteração no código.
    app.run(debug=True, port=5000)