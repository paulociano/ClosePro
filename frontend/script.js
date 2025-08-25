document.addEventListener('DOMContentLoaded', () => {
    // Mapeamento dos elementos da interface para variáveis
    const submitButton = document.getElementById('submit-button');
    const objectionInput = document.getElementById('objection-input');
    const valueInput = document.getElementById('value-input');
    const advantagesInput = document.getElementById('advantages-input');
    const discProfileSelect = document.getElementById('disc-profile-select');
    const responseArea = document.getElementById('response-area');
    const recordButton = document.getElementById('record-button');
    const recordingIndicator = document.getElementById('recording-indicator');
    const clearButton = document.getElementById('clear-button');

    // Variáveis para controlar o estado da gravação
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    // --- LÓGICA DO BOTÃO LIMPAR ---
    clearButton.addEventListener('click', () => {
        objectionInput.value = '';
        valueInput.value = '';
        advantagesInput.value = '';
        discProfileSelect.value = 'nao_selecionado';
        responseArea.innerHTML = '';
        objectionInput.focus();
    });

    // --- LÓGICA DE GRAVAÇÃO DE ÁUDIO ---
    recordButton.addEventListener('click', async () => {
        if (!isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();
                isRecording = true;

                recordButton.innerHTML = `<i class="ph ph-stop"></i>`;
                recordButton.title = "Parar Gravação";
                recordingIndicator.classList.remove('hidden');
                objectionInput.value = "";
                objectionInput.disabled = true;

                mediaRecorder.addEventListener('dataavailable', evento => {
                    audioChunks.push(evento.data);
                });

                mediaRecorder.addEventListener('stop', () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    transcribeAudio(audioBlob);
                    audioChunks = [];
                    stream.getTracks().forEach(track => track.stop());
                });

            } catch (erro) {
                console.error("Erro ao acessar o microfone:", erro);
                alert("Não foi possível acessar o microfone. Verifique as permissões do navegador.");
            }
        } else {
            mediaRecorder.stop();
            isRecording = false;
            
            recordButton.innerHTML = `<i class="ph ph-microphone"></i>`;
            recordButton.title = "Gravar Áudio";
            recordingIndicator.classList.add('hidden');
            objectionInput.disabled = false;
        }
    });

    async function transcribeAudio(audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');

        objectionInput.placeholder = "Transcrevendo áudio, por favor aguarde...";
        recordButton.disabled = true;
        submitButton.disabled = true;

        try {
            const resposta = await fetch('https://closepro.onrender.com/api/transcribe-audio', {
                method: 'POST',
                body: formData,
            });

            if (!resposta.ok) {
                throw new Error('Falha ao transcrever o áudio.');
            }

            const resultado = await resposta.json();
            objectionInput.value = resultado.transcription;

        } catch (erro) {
            console.error("Erro na transcrição:", erro);
            alert("Ocorreu um erro ao transcrever o áudio.");
        } finally {
            objectionInput.placeholder = "Digite a objeção aqui ou use o gravador de voz...";
            recordButton.disabled = false;
            submitButton.disabled = false;
        }
    }

    // --- LÓGICA DE GERAÇÃO DE ROTEIRO (A PARTIR DO TEXTO) ---
    submitButton.addEventListener('click', async () => {
        const textoDaObjecao = objectionInput.value;
        const valorDaConsultoria = valueInput.value;
        const vantagensPercebidas = advantagesInput.value;
        const perfilDisc = discProfileSelect.value;

        if (!textoDaObjecao.trim()) {
            alert('Por favor, preencha pelo menos a objeção do cliente.');
            return;
        }

        submitButton.disabled = true;
        submitButton.innerHTML = `<i class="ph ph-spinner-gap animate-spin"></i><span>Analisando...</span>`;
        responseArea.innerHTML = '';

        try {
            const resposta = await fetch('https://closepro.onrender.com/api/get-response', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    objection: textoDaObjecao,
                    value: valorDaConsultoria,
                    advantages: vantagensPercebidas,
                    disc_profile: perfilDisc
                }),
            });

            if (!resposta.ok) {
                const erroTexto = await resposta.text();
                throw new Error(`Houve um problema com a resposta do servidor: ${erroTexto}`);
            }

            const dados = await resposta.json();
            displayResponse(dados);

        } catch (erro) {
            responseArea.innerHTML = `<p style="color: #ff4d4d;"><strong>Erro:</strong> ${erro.message}</p>`;
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = `<i class="ph ph-magic-wand"></i><span>Gerar Roteiro</span>`;
        }
    });

    /**
     * Renderiza a resposta da IA na tela em formato de cards.
     * @param {object} dados - O objeto JSON retornado pelo backend.
     */
    function displayResponse(dados) {
        try {
            const { 
                tipo_objecao = "Não classificada", 
                roteiro = ["Não foi possível gerar um roteiro."], 
                tom_palavras_chave = { tom: "N/A", palavras_chave: [] }, 
                follow_up_sugerido = "Nenhuma sugestão de follow-up.",
                mensagem_follow_up = "Não foi possível gerar a mensagem de follow-up."
            } = dados || {};

            const roteiroArray = Array.isArray(roteiro) ? roteiro : [roteiro];
            const palavrasChaveArray = Array.isArray(tom_palavras_chave.palavras_chave) ? tom_palavras_chave.palavras_chave : [];

            const roteiroHtml = roteiroArray.map(passo => `<li>${passo}</li>`).join('');
            const mensagemFollowUpHtml = mensagem_follow_up.replace(/\n/g, '<br>');

            responseArea.innerHTML = `
                <div class="response-card">
                    <h3><i class="ph ph-shield-check"></i> Tipo de Objeção</h3>
                    <p>${tipo_objecao}</p>
                </div>
                <div class="response-card">
                    <h3>
                        <i class="ph ph-microphone-stage"></i> Roteiro de Contorno Sugerido
                        <button class="copy-button" data-copy-target="roteiro" title="Copiar Roteiro"><i class="ph ph-copy"></i> Copiar</button>
                    </h3>
                    <ul>${roteiroHtml}</ul>
                </div>
                <div class="response-card">
                    <h3><i class="ph ph-key"></i> Tom e Palavras-Chave</h3>
                    <p><strong>Tom:</strong> ${tom_palavras_chave.tom}<br>
                    <strong>Palavras-Chave:</strong> ${palavrasChaveArray.join(', ') || 'N/A'}</p>
                </div>
                <div class="response-card">
                    <h3><i class="ph ph-arrow-circle-right"></i> Ação de Follow-up Sugerida</h3>
                    <p>${follow_up_sugerido}</p>
                </div>
                <div class="response-card">
                    <h3>
                        <i class="ph ph-envelope"></i> Mensagem de Follow-up Pronta
                        <button class="copy-button" data-copy-target="followup" title="Copiar Mensagem"><i class="ph ph-copy"></i> Copiar</button>
                    </h3>
                    <p class="follow-up-message">${mensagemFollowUpHtml}</p>
                </div>
            `;
            
            document.querySelectorAll('.copy-button').forEach(button => {
                button.addEventListener('click', () => {
                    let textoParaCopiar = "";
                    const target = button.dataset.copyTarget;

                    if (target === 'roteiro') {
                        textoParaCopiar = roteiroArray.join('\n');
                    } else if (target === 'followup') {
                        textoParaCopiar = mensagem_follow_up;
                    }

                    navigator.clipboard.writeText(textoParaCopiar).then(() => {
                        const originalText = button.innerHTML;
                        button.innerHTML = '<i class="ph ph-check"></i> Copiado!';
                        setTimeout(() => { button.innerHTML = originalText; }, 2000);
                    });
                });
            });

        } catch (erro) {
            console.error("Erro ao exibir a resposta:", erro);
            responseArea.innerHTML = `<p style="color: #ff4d4d;"><strong>Erro:</strong> Não foi possível processar a estrutura da resposta recebida.</p>`;
        }
    }
});
