# Guia de Uso e Documentação: `chat.py`

Guia completo de utilização, comandos, configuração e arquitetura do script [`chat.py`](file:///home/neviim/developer/gemma4/chat.py), desenvolvido para interação com os modelos **Google Gemma 4** (`gemma4:e2b` e `gemma-4-e4b-it-qat-q4_0`) no **Ollama** com interface visual moderna, colorida e estruturada para terminal.

---

## 🎨 Interface Visual (Rich UI)

O script utiliza a biblioteca `rich` para fornecer uma experiência visual limpa, legível e responsiva:
- **Painéis Arredondados e Coloridos:**
  - 🟦 **Ciano:** Caixa destacada para a **Pergunta** enviada (`❓ Pergunta`).
  - 🟪 **Magenta (Itálico):** Caixa dedicada ao **Processo de Pensamento** (`🧠 Processo de Pensamento`) — exibida apenas quando o modo de reflexão está ativo e visível.
  - 🟩 **Verde:** Caixa para a **Resposta Final** (`💬 Resposta (modelo)`), que renderiza Markdown real (negrito, listas, blocos de código e tabelas formatadas).
  - 🟨 **Métricas de Performance:** Rodapé com contagem de tokens, tempo decorrido, taxa de geração em tokens/segundo, modelo ativo e modo de pensamento.
- **Streaming em Tempo Real (*Live Display*):** Os blocos de raciocínio e resposta são atualizados dinamicamente à medida que os tokens chegam do Ollama.

---

## 📐 Tratamento de Notação Matemática e LaTeX no Terminal

### Por que fórmulas apareciam como `$$\text{...}$$` ou `\frac{...}{...}`?
Modelos de linguagem como a família Gemma são pré-treinados com grandes volumes de textos científicos e páginas web que utilizam **LaTeX** (renderizado na web por MathJax ou KaTeX). Por padrão, equações são delimitadas por `$` ou `$$` e palavras/unidades ficam dentro de tags `\text{}`.

No entanto, emuladores de terminal não possuem interpretador nativo de LaTeX, o que fazia com que o terminal exibisse o código cru de forma confusa.

### Como o `chat.py` resolve isso:
1. **System Prompt Especializado:** 
   O script envia uma diretriz nativa ao modelo para que ele priorize notações matemáticas simples e legíveis em linha de comando (como `km/s`, `10 / 2 = 5`, `×`, `÷`).
2. **Filtro de Higienização (`clean_latex`):**
   Caso o modelo ainda produza tags LaTeX residuais, o script intercepta o texto antes da renderização e realiza as seguintes conversões automáticas:

| Sintaxe Original | Resultado no Terminal | Exemplo de Aplicação |
| :--- | :--- | :--- |
| `\text{palavra}` | `palavra` | `\text{km/s}` ➔ `km/s` |
| `\frac{a}{b}` | `(a / b)` | `\frac{299.792.458}{1000}` ➔ `(299.792.458 / 1000)` |
| `\times`, `\cdot` | `×`, `·` | `2 \times 12` ➔ `2 × 12` |
| `\div` | `÷` | `27 \div 2` ➔ `27 ÷ 2` |
| `\approx`, `\pm` | `≈`, `±` | `\approx 300.000` ➔ `≈ 300.000` |
| `\le`, `\ge` | `≤`, `≥` | `x \ge 0` ➔ `x ≥ 0` |
| `$$...$$` ou `$..$` | *texto limpo sem delimitador* | `$$\text{resultado} = 10$$` ➔ `resultado = 10` |

---

## ⚙️ Parâmetros de Linha de Comando (CLI)

```bash
./chat.py [-h] [--model MODEL] [--think {rapido,fast,low,normal,medium,profundo,high,off,desativado}] [--hidethinking] [prompt ...]
```

| Opção | Atalho | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `--model` | `-m` | `gemma4:e2b` | Define o modelo do Ollama (ex: `gemma4:e2b` ou `gemma-4-e4b-it-qat-q4_0`). |
| `--think` | `-t` | `normal` | Nível de raciocínio interno: `rapido`, `normal`, `profundo` ou `off`. |
| `--hidethinking` | — | `False` | Oculta visualmente as etapas de pensamento, exibindo apenas a resposta final. |
| `prompt` | — | *(nenhum)* | Executa uma consulta direta (*one-shot*) e encerra o script sem abrir o chat interativo. |

---

## 🧠 Modos de Raciocínio (*Thinking Modes*)

| Modo | Argumento CLI | Mapeamento Ollama | Comportamento e Casos de Uso |
| :--- | :--- | :--- | :--- |
| **Rápido** | `--think rapido` | `think: "low"` | Reflexão sintética com poucas etapas. Mais ágil mantendo boa lógica. |
| **Normal** | `--think normal` | `think: "medium"` | Raciocínio padrão recomendado para problemas analíticos e código. |
| **Profundo** | `--think profundo` | `think: "high"` | Raciocínio exaustivo e passo a passo minucioso. |
| **Desativado** | `--think off` | `think: false` | Resposta instantânea (~1 a 2 segundos) sem bloco de pensamento. |

---

## 🚀 Exemplos Práticos de Execução

### 1. Consultas Rápidas no Terminal (One-Shot)

```bash
# Resposta instantânea, limpa e organizada (sem pensamento)
./chat.py --think off "Qual é a velocidade da luz no vácuo em km/s? Mostre a conversão dividindo por 1000."

# Pergunta matemática com raciocínio rápido
./chat.py --think rapido "Resolva passo a passo: Se tenho 15 caixas com 8 lápis cada, quantos lápis tenho no total?"

# Pergunta técnica usando o modelo Gemma 4 E4B QAT
./chat.py --model gemma-4-e4b-it-qat-q4_0 --think rapido "Explique o que é Quantization-Aware Training em 2 tópicos."
```

### 2. Iniciar no Modo Chat Interativo

```bash
# Chat interativo padrão (pensamento normal)
./chat.py

# Chat interativo com pensamento rápido
./chat.py --think rapido

# Chat com respostas instantâneas
./chat.py --think off
```

---

## 🧮 Exemplos de Matemática Complexa e Avançada

Para problemas que exigem múltiplas etapas analíticas, substituições algébricas, cálculo diferencial/integral e conferência de sinais, **recomenda-se utilizar `--think normal` ou `--think profundo`**. Nesses modos, o Gemma 4 utiliza sua cadeia interna de reflexão (*Chain-of-Thought*) para validar os passos antes de emitir o resultado final.

### 1. Cálculo Integral: Integração por Partes Repetida

```bash
./chat.py --think normal "Resolva a integral indefinida: ∫ (x^2 * e^x) dx utilizando o método de integração por partes. Mostre o passo a passo completo e a constante de integração C."
```

> **Como o modelo estrutura a resposta:**
> 1. Identifica a fórmula base: $\int u \, dv = uv - \int v \, du$.
> 2. Primeira iteração: $u = x^2 \Rightarrow du = 2x \, dx$ e $dv = e^x \, dx \Rightarrow v = e^x$, obtendo $x^2 e^x - 2 \int x e^x \, dx$.
> 3. Segunda iteração (na integral residual): $u' = x \Rightarrow du' = dx$ e $dv' = e^x \, dx \Rightarrow v' = e^x$, obtendo $x e^x - e^x$.
> 4. Substituição e fatoração de $e^x$:
>    $$\int x^2 e^x \, dx = e^x (x^2 - 2x + 2) + C$$

---

### 2. Equações Diferenciais Ordinárias (EDO com Fator Integrante)

```bash
./chat.py --think normal "Resolva a equação diferencial ordinária de 1ª ordem: dy/dx + 2y = 4x com a condição inicial y(0) = 1. Mostre os passos do fator integrante μ(x), a solução geral e a solução particular."
```

> **Etapas esperadas:**
> - Forma padrão: $y' + P(x)y = Q(x)$ com $P(x) = 2$ e $Q(x) = 4x$.
> - Fator integrante: $\mu(x) = e^{\int 2 \, dx} = e^{2x}$.
> - Integração do lado direito: $\int 4x e^{2x} \, dx = 2x e^{2x} - e^{2x} + C$.
> - Solução geral: $y(x) = 2x - 1 + C e^{-2x}$.
> - Aplicação de $y(0) = 1 \Rightarrow 1 = -1 + C \Rightarrow C = 2$.
> - Solução particular: $y(x) = 2x - 1 + 2e^{-2x}$.

---

### 3. Álgebra Linear: Autovalores e Autovetores (Eigenvalues)

```bash
./chat.py --think rapido "Dada a matriz A = [[4, 1], [2, 3]], determine o polinômio característico, encontre os autovalores λ1 e λ2, e calcule os respectivos autovetores associados."
```

> **Etapas esperadas:**
> - Equação característica: $\det(A - \lambda I) = 0 \Rightarrow (4 - \lambda)(3 - \lambda) - 2 = \lambda^2 - 7\lambda + 10 = 0$.
> - Autovalores: $\lambda_1 = 5$ e $\lambda_2 = 2$.
> - Determinação dos espaços nulos para $(A - \lambda I)v = 0$ e vetores base associados.

---

### 4. Probabilidade e Teorema de Bayes (Epidemiologia / Inferência)

```bash
./chat.py --think normal "Em um teste clínico, uma condição afeta 1% da população (prevalência = 0.01). O exame laboratorial tem sensibilidade de 95% (verdadeiro positivo) e especificidade de 90% (verdadeiro negativo). Se um paciente aleatório obtiver resultado positivo, qual é a probabilidade real de ele ter a condição? Aplique o Teorema de Bayes passo a passo."
```

> **Etapas esperadas:**
> - $P(D) = 0.01$ e $P(\neg D) = 0.99$.
> - $P(+ \mid D) = 0.95$ e $P(+ \mid \neg D) = 1 - 0.90 = 0.10$ (falso positivo).
> - Probabilidade total do teste positivo: $P(+) = (0.95 \times 0.01) + (0.10 \times 0.99) = 0.0095 + 0.099 = 0.1085$.
> - Pós-teste (Bayes): $P(D \mid +) = \frac{0.0095}{0.1085} \approx 8,76\%$.

---

### 5. Otimização Multivariável: Multiplicadores de Lagrange

```bash
./chat.py --think profundo "Encontre os pontos extremos da função f(x, y) = x * y sujeita à restrição x + 2y = 100 utilizando o método dos multiplicadores de Lagrange. Calcule o gradiente, monte o sistema de equações e determine o valor máximo de f."
```

---

### 💡 Dicas de Prompt para Matemática Avançada no Gemma 4

1. **Explicite o método desejado:** Incluir frases como *"resolva utilizando o método de integração por partes"* ou *"pelo método dos coeficientes a determinar"* ajuda o modelo a adotar o caminho analítico exato que você precisa.
2. **Peça a verificação do resultado:** Adicione *"ao final, faça a verificação derivando a solução encontrada"* para incentivar o modelo a conferir se a resposta está matematicamente correta.
3. **Use `--think normal` ou `--think profundo`:** Para problemas longos com múltiplos subcasos, evite o modo `--think off`, pois o processo de reflexão interna previne erros comuns de álgebra e troca de sinais.

---

## 💬 Comandos Disponíveis Durante a Conversa

Dentro do chat, você pode alternar configurações em tempo real digitando diretamente no prompt `Você >`:

| Comando | O que faz |
| :--- | :--- |
| `/think rapido` | Altera imediatamente o raciocínio para o modo rápido (`low`). |
| `/think normal` | Altera imediatamente para o raciocínio padrão completo (`medium`). |
| `/think profundo` | Altera para reflexão analítica detalhada (`high`). |
| `/think off` | Desativa o processo de reflexão para respostas imediatas. |
| `/hide` | Alterna entre exibir ou esconder o painel de pensamento no terminal. |
| `/model <nome>` | Alterna o modelo em execução (ex: `/model gemma-4-e4b-it-qat-q4_0`). |
| `/ajuda` | Reexibe a tabela de comandos disponíveis. |
| `sair` ou `exit` | Encerra o chat. |

---

## 📊 Comparativo dos Modelos Instalados

| Característica | `gemma4:e2b` | `gemma-4-e4b-it-qat-q4_0` |
| :--- | :--- | :--- |
| **Parâmetros** | ~5.1B (+ multimodal) | ~7.46B (+ 478M CLIP) |
| **Quantização** | Q4_K_M | Q4_0 (QAT oficial) |
| **VRAM na GPU** | ~1.8 GB a 3.1 GB | ~3.2 GB |
| **Carga de Hardware** | 100% GPU (GTX 1080 8GB) | 100% GPU (GTX 1080 8GB) |
| **Velocidade Típica** | ~50 a 55 tokens/s | ~43 tokens/s |
| **Multimodalidade** | Texto, Imagem, Áudio | Texto, Imagem, Áudio |
