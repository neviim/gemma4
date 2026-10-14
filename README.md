# Google Gemma 4 no Ollama (E4B-it QAT & E2B)

Este repositório contém a configuração e o script interativo para executar localmente os modelos **Gemma 4** (`gemma4:e2b` e `gemma-4-e4b-it-qat-q4_0`) com controle sobre os modos de pensamento (*thinking*), interface rica em cores e suporte a formatação matemática limpa.

> 📖 Para ver o manual completo com todos os detalhes e tabelas de conversão, consulte o [docs/DOCUMENTACAO_CHAT.md](docs/DOCUMENTACAO_CHAT.md).

---

## 🎨 Interface e Recursos do `chat.py`

O script [`chat.py`](file:///home/neviim/developer/gemma4/chat.py) oferece:
- **Painéis Coloridos (Rich):** Caixas separadas para a Pergunta (ciano), Processo de Pensamento (magenta itálico) e Resposta (verde com Markdown renderizado).
- **Sem Códigos Estranhos de LaTeX:** Fórmulas matemáticas e unidades são limpas automaticamente, evitando códigos como `$$\text{...}$$` ou `\frac{}{}` no terminal.
- **Métricas em Tempo Real:** Tokens gerados, tempo total e velocidade (tokens/s).

---

## 🚀 Como Usar o `chat.py`

### 1. Iniciar no Modo Chat Interativo

- **Pensamento Rápido (`low`):**
  ```bash
  ./chat.py --think rapido
  ```

- **Pensamento Normal (`medium`):**
  ```bash
  ./chat.py --think normal
  ```

- **Sem Pensamento / Resposta Imediata (`off`):**
  ```bash
  ./chat.py --think off
  ```

- **Ocultar Pensamento Visualmente:**
  ```bash
  ./chat.py --hidethinking
  ```

- **Escolher o Modelo (padrão: `gemma4:e2b`):**
  ```bash
  ./chat.py --model gemma-4-e4b-it-qat-q4_0 --think rapido
  ```

---

### 2. Comandos Durante a Conversa

Dentro do chat, você não precisa reiniciar o script para mudar as configurações:
- `/think rapido` → Alterna para pensamento mais conciso e rápido
- `/think normal` → Alterna para o raciocínio padrão completo
- `/think profundo` → Alterna para o modo de reflexão mais analítico
- `/think off` → Desativa o pensamento para respostas imediatas
- `/hide` → Alterna entre exibir ou esconder o painel de pensamento
- `/model <nome>` → Alterna entre modelos (ex: `/model gemma4:e2b` ou `/model gemma-4-e4b-it-qat-q4_0`)
- `sair` ou `exit` → Encerra o chat

---

### 3. Perguntas Diretas via Linha de Comando (One-Shot)

```bash
# Resposta instantânea e limpa
./chat.py --think off "Qual é a velocidade da luz no vácuo em km/s? Mostre a conversão dividindo por 1000."

# Pergunta com raciocínio rápido
./chat.py --think rapido "Resolva: quanto é 15% de 80?"

# Pergunta técnica com o Gemma 4 E4B QAT
./chat.py --model gemma-4-e4b-it-qat-q4_0 --think rapido "O que é QAT?"
```

---

### 4. Exemplos de Matemática Complexa e Avançada

Para problemas que exigem cálculo simbólico, álgebra linear ou equações diferenciais, utilize `--think normal` ou `--think profundo`:

```bash
# Cálculo Integral por Partes
./chat.py --think normal "Resolva a integral indefinida: ∫ (x^2 * e^x) dx por partes com passo a passo completo."

# Equação Diferencial Ordinária (EDO com fator integrante)
./chat.py --think normal "Resolva a EDO: dy/dx + 2y = 4x com y(0) = 1. Mostre o fator integrante e a solução."

# Álgebra Linear (Autovalores e Autovetores)
./chat.py --think rapido "Encontre os autovalores e autovetores da matriz [[4, 1], [2, 3]]."

# Probabilidade e Teorema de Bayes
./chat.py --think normal "Calcule a probabilidade posterior via Teorema de Bayes para teste clínico com prevalência 1%, sensibilidade 95% e especificidade 90%."
```

---

## 📊 Modelos Disponíveis no Ambiente

| Modelo | Identificador | Quantização | VRAM GPU (GTX 1080) | Velocidade |
| :--- | :--- | :--- | :--- | :--- |
| **Gemma 4 E2B** | `gemma4:e2b` | Q4_K_M | ~1.8 GB a 3.1 GB | ~50 a 55 tokens/s |
| **Gemma 4 E4B QAT** | `gemma-4-e4b-it-qat-q4_0` | Q4_0 | ~3.2 GB | ~43 tokens/s |
