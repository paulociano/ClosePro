// Aguarda o carregamento completo do DOM para garantir que todos os elementos existam
document.addEventListener('DOMContentLoaded', () => {
    
    // Mapeia os elementos da interface para variáveis
    const submitButton = document.getElementById('submit-button');
    const objectionInput = document.getElementById('objection-input');
    const responseArea = document.getElementById('response-area');
    // Nota: O spinner de loading do botão é controlado via innerHTML,
    // então não precisamos de uma variável para o spinner antigo.

    // Adiciona o evento de clique ao botão principal
    submitButton.addEventListener('click', async () => {
        
        const objectionText = objectionInput.value;

        // Validação: não faz a chamada de API se o campo estiver vazio
        if (!objectionText.trim()) {
            alert('Por favor, digite a objeção do cliente antes de continuar.');
            return;
        }

        // --- Inicia o estado de carregamento ---
        submitButton.disabled = true;
        // Atualiza o botão para mostrar um feedback de carregamento
        submitButton.innerHTML = `
            <i class="ph ph-spinner-gap animate-spin"></i>
            <span>Analisando...</span>
        `;
        responseArea.innerHTML = ''; // Limpa a resposta anterior
        

        // Bloco try...catch...finally para lidar com a chamada de API
        try {
            // Faz a requisição para o backend
            const response = await fetch('http://127.0.0.1:5000/api/get-response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                // Envia o texto da objeção no corpo da requisição
                body: JSON.stringify({ objection: objectionText }),
            });

            // Verifica se a resposta da rede foi bem-sucedida
            if (!response.ok) {
                throw new Error('Houve um problema com a resposta do servidor. Tente novamente.');
            }

            // Converte a resposta para JSON
            const data = await response.json();

            // Chama a função que exibe os dados na tela
            displayResponse(data);

        } catch (error) {
            // Em caso de erro, exibe uma mensagem amigável na área de resposta
            responseArea.innerHTML = `<p style="color: red;"><strong>Erro:</strong> ${error.message}</p>`;
        } finally {
            // --- Finaliza o estado de carregamento ---
            // Este bloco é executado sempre, seja com sucesso ou erro.
            // Restaura o botão ao seu estado original
            submitButton.disabled = false;
            submitButton.innerHTML = `
                <i class="ph ph-magic-wand"></i>
                <span>Gerar Roteiro</span>
            `;
        }
    });

    /**
     * Função responsável por renderizar a resposta da API no HTML.
     * @param {object} data - O objeto JSON retornado pelo backend.
     */
    function displayResponse(data) {
        const { tipo_objecao, roteiro, tom_palavras_chave, follow_up } = data;

        // Cria o HTML para cada lista de itens
        const roteiroHtml = roteiro.map(passo => `<li>${passo}</li>`).join('');
        const followUpHtml = follow_up.map(item => `<li>${item}</li>`).join('');

        // Monta a estrutura final com os cards e insere na área de resposta
        responseArea.innerHTML = `
            <div class="response-card">
                <h3><i class="ph ph-shield-check"></i> Tipo de Objeção</h3>
                <p>${tipo_objecao}</p>
            </div>

            <div class="response-card">
                <h3><i class="ph ph-microphone-stage"></i> Roteiro de Contorno Sugerido</h3>
                <ul>${roteiroHtml}</ul>
            </div>

            <div class="response-card">
                <h3><i class="ph ph-key"></i> Tom e Palavras-Chave</h3>
                <p><strong>Tom:</strong> ${tom_palavras_chave.tom}<br>
                <strong>Palavras-Chave:</strong> ${tom_palavras_chave.palavras_chave.join(', ')}</p>
            </div>

            <div class="response-card">
                <h3><i class="ph ph-arrow-circle-right"></i> Sugestões de Follow-up</h3>
                <ul>${followUpHtml}</ul>
            </div>
        `;
    }
});