// frontend/script.js

document.addEventListener('DOMContentLoaded', () => {
    const submitButton = document.getElementById('submit-button');
    const objectionInput = document.getElementById('objection-input');
    const responseArea = document.getElementById('response-area');
    const loadingSpinner = document.getElementById('loading-spinner');

    submitButton.addEventListener('click', async () => {
        const objectionText = objectionInput.value;

        if (!objectionText.trim()) {
            alert('Por favor, digite uma objeção.');
            return;
        }

        // Mostra o spinner e limpa a área de resposta
        loadingSpinner.classList.remove('hidden');
        responseArea.innerHTML = '';
        
        try {
            // Faz a chamada para o nosso backend
            const response = await fetch('http://127.0.0.1:5000/api/get-response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ objection: objectionText }),
            });

            if (!response.ok) {
                throw new Error('Erro ao se comunicar com o servidor.');
            }

            const data = await response.json();

            // Esconde o spinner
            loadingSpinner.classList.add('hidden');

            // Exibe a resposta formatada na tela
            displayResponse(data);

        } catch (error) {
            loadingSpinner.classList.add('hidden');
            responseArea.innerHTML = `<p style="color: red;">Erro: ${error.message}</p>`;
        }
    });

    function displayResponse(data) {
        const { tipo_objecao, roteiro, tom_palavras_chave, follow_up } = data;

        const roteiroHtml = roteiro.map(passo => `<li>${passo}</li>`).join('');
        const followUpHtml = follow_up.map(item => `<li>${item}</li>`).join('');

        responseArea.innerHTML = `
            <h3>🛡️ Tipo de Objeção: ${tipo_objecao}</h3>
            
            <h4>🎙️ Roteiro de Contorno Sugerido:</h4>
            <ul>${roteiroHtml}</ul>

            <h4>🔑 Tom e Palavras-Chave:</h4>
            <p><strong>Tom:</strong> ${tom_palavras_chave.tom}<br>
            <strong>Palavras-Chave:</strong> ${tom_palavras_chave.palavras_chave.join(', ')}</p>

            <h4>➡️ Sugestões de Follow-up:</h4>
            <ul>${followUpHtml}</ul>
        `;
    }
});