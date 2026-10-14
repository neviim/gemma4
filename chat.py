#!/usr/bin/env python3
"""
Chat interativo e testes para os modelos Gemma 4 no Ollama com interface rica e colorida.

Suporta:
- Interface gráfica no terminal com Rich (bordas, markdown, cores vibrantes, painéis)
- Streaming em tempo real de raciocínio (Thinking) e resposta
- Modos de pensamento: rápido (low), normal (medium), profundo (high), off (desativado)
- Ocultar/exibir pensamento
- Alternância dinâmica de modelos (gemma4:e2b, gemma-4-e4b-it-qat-q4_0)
- Métricas detalhadas de tokens/s e tempo de inferência
"""

import argparse
import json
import re
import sys
import time
import urllib.request

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.text import Text
    from rich.live import Live
    from rich.table import Table
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

console = Console() if HAS_RICH else None

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"

DEFAULT_SYSTEM_PROMPT = (
    "Você é um assistente respondendo em um terminal de linha de comando (CLI). "
    "Formate equações, unidades e cálculos matemáticos sempre em texto simples legível "
    "(por exemplo: m/s, km/s, 10 / 2 = 5, ×, ÷), sem usar blocos ou tags de código LaTeX "
    "como \\text, \\frac, delimitadores $ ou $$."
)

def clean_latex(text: str) -> str:
    """Converte notações LaTeX comuns em texto simples e legível no terminal."""
    if not text:
        return text
    # \text{palavra} -> palavra
    text = re.sub(r"\\text\{([^}]+)\}", r"\1", text)
    # \frac{a}{b} -> (a / b)
    text = re.sub(r"\\frac\{([^}]+)\}\{([^}]+)\}", r"(\1 / \2)", text)
    # Símbolos matemáticos comuns
    text = text.replace(r"\times", "×").replace(r"\div", "÷")
    text = text.replace(r"\approx", "≈").replace(r"\le", "≤").replace(r"\ge", "≥")
    text = text.replace(r"\cdot", "·").replace(r"\pm", "±")
    # Remove delimitadores de equações LaTeX $$ e $
    text = re.sub(r"\$\$([^\$]+)\$\$", r"\1", text)
    text = re.sub(r"\$([^\$\n]+)\$", r"\1", text)
    return text

THINK_MODES = {
    "rapido": "low",
    "fast": "low",
    "low": "low",
    "normal": "medium",
    "medium": "medium",
    "profundo": "high",
    "high": "high",
    "off": False,
    "desativado": False,
    "none": False
}

def resolve_think_param(mode_str):
    if isinstance(mode_str, bool):
        return mode_str
    mode_lower = str(mode_str).lower().strip()
    return THINK_MODES.get(mode_lower, "medium")

def generate_stream_rich(prompt: str, model: str, think_mode: str, show_thinking: bool = True):
    think_param = resolve_think_param(think_mode)
    
    payload = {
        "model": model,
        "prompt": prompt,
        "system": DEFAULT_SYSTEM_PROMPT,
        "stream": True,
        "think": think_param,
        "options": {
            "temperature": 1.0,
            "top_p": 0.95,
            "top_k": 64
        }
    }

    req = urllib.request.Request(
        OLLAMA_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    console.print(Panel(prompt, title="[bold cyan]❓ Pergunta[/bold cyan]", border_style="cyan"))

    start_time = time.time()
    total_eval_tokens = 0
    eval_duration_ns = 0

    try:
        response = urllib.request.urlopen(req)
    except Exception as e:
        console.print(Panel(f"[bold red]Erro ao conectar com Ollama:[/bold red] {e}", border_style="red"))
        return

    thinking_text = ""
    response_text = ""

    # Live display para thinking e response
    live_thinking = None
    live_response = None

    try:
        for line in response:
            if not line:
                continue
            chunk = json.loads(line.decode("utf-8"))

            # Streaming de Pensamento
            th = chunk.get("thinking", "")
            if th:
                thinking_text += th
                if show_thinking:
                    if live_thinking is None:
                        live_thinking = Live(console=console, refresh_per_second=15)
                        live_thinking.start()
                    live_thinking.update(
                        Panel(
                            Text(clean_latex(thinking_text), style="dim italic"),
                            title="[bold magenta]🧠 Processo de Pensamento[/bold magenta]",
                            border_style="magenta"
                        )
                    )

            # Streaming de Resposta
            rs = chunk.get("response", "")
            if rs:
                # Se o pensamento estava ativo na tela, finaliza o painel dele antes de abrir o da resposta
                if live_thinking is not None:
                    live_thinking.stop()
                    live_thinking = None

                response_text += rs
                if live_response is None:
                    live_response = Live(console=console, refresh_per_second=15)
                    live_response.start()
                live_response.update(
                    Panel(
                        Markdown(clean_latex(response_text)),
                        title=f"[bold green]💬 Resposta ({model})[/bold green]",
                        border_style="green"
                    )
                )

            if chunk.get("done", False):
                total_eval_tokens = chunk.get("eval_count", 0)
                eval_duration_ns = chunk.get("eval_duration", 0)

    finally:
        if live_thinking is not None:
            live_thinking.stop()
        if live_response is not None:
            live_response.stop()

    elapsed = time.time() - start_time

    # Exibe barra de métricas organizadas
    if eval_duration_ns > 0:
        tps = total_eval_tokens / (eval_duration_ns / 1e9)
        stats = (
            f"[bold yellow]⚡ {total_eval_tokens} tokens[/bold yellow] em "
            f"[bold cyan]{elapsed:.2f}s[/bold cyan] "
            f"([bold green]{tps:.1f} tokens/s[/bold green]) • "
            f"Modelo: [bold white]{model}[/bold white] • "
            f"Modo: [bold magenta]{think_mode}[/bold magenta]"
        )
    else:
        stats = (
            f"[bold yellow]⚡ Concluído[/bold yellow] em "
            f"[bold cyan]{elapsed:.2f}s[/bold cyan] • "
            f"Modelo: [bold white]{model}[/bold white] • "
            f"Modo: [bold magenta]{think_mode}[/bold magenta]"
        )
    
    console.print(stats)
    console.print()

def generate_stream_fallback(prompt: str, model: str, think_mode: str, show_thinking: bool = True):
    """Fallback caso rich não esteja presente."""
    think_param = resolve_think_param(think_mode)
    payload = {
        "model": model,
        "prompt": prompt,
        "system": DEFAULT_SYSTEM_PROMPT,
        "stream": True,
        "think": think_param,
        "options": {"temperature": 1.0, "top_p": 0.95, "top_k": 64}
    }
    req = urllib.request.Request(
        OLLAMA_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    print(f"\n\033[1;36m>> Pergunta:\033[0m {prompt}\n")
    start = time.time()
    is_thinking = False
    started_resp = False
    eval_tokens = 0
    eval_ns = 0

    try:
        with urllib.request.urlopen(req) as resp:
            for line in resp:
                if not line:
                    continue
                chunk = json.loads(line.decode("utf-8"))
                th = chunk.get("thinking", "")
                if th and show_thinking:
                    if not is_thinking:
                        is_thinking = True
                        print("\033[1;35m🧠 [Pensando...]\033[0m\033[90m")
                    sys.stdout.write(th)
                    sys.stdout.flush()

                rs = chunk.get("response", "")
                if rs:
                    if is_thinking and show_thinking:
                        print("\033[0m\n\033[1;32m💬 [Resposta]:\033[0m\n")
                        is_thinking = False
                    elif not started_resp:
                        print("\033[1;32m💬 [Resposta]:\033[0m\n")
                    started_resp = True
                    sys.stdout.write(rs)
                    sys.stdout.flush()

                if chunk.get("done", False):
                    eval_tokens = chunk.get("eval_count", 0)
                    eval_ns = chunk.get("eval_duration", 0)

        elapsed = time.time() - start
        print("\033[0m")
        if eval_ns > 0:
            tps = eval_tokens / (eval_ns / 1e9)
            print(f"\033[90m⚡ {eval_tokens} tokens em {elapsed:.2f}s (~{tps:.1f} t/s) | Modelo: {model} | Modo: {think_mode}\033[0m\n")
    except Exception as e:
        print(f"\033[31mErro: {e}\033[0m")

def generate_stream(prompt: str, model: str, think_mode: str, show_thinking: bool = True):
    if HAS_RICH:
        generate_stream_rich(prompt, model, think_mode, show_thinking)
    else:
        generate_stream_fallback(prompt, model, think_mode, show_thinking)

def show_interactive_banner(model: str, think_mode: str):
    if HAS_RICH:
        grid = Table.grid(padding=(0, 2))
        grid.add_column(style="bold cyan")
        grid.add_column(style="white")
        grid.add_row("/think rapido", "Pensamento conciso e rápido (low)")
        grid.add_row("/think normal", "Pensamento estruturado completo (medium)")
        grid.add_row("/think profundo", "Pensamento analítico profundo (high)")
        grid.add_row("/think off", "Sem reflexão prévia (resposta imediata)")
        grid.add_row("/model <nome>", "Alterna o modelo (ex: gemma-4-e4b-it-qat-q4_0)")
        grid.add_row("/hide", "Alterna visibilidade do pensamento")
        grid.add_row("sair / exit", "Encerra a sessão")

        console.print(
            Panel(
                grid,
                title=f"[bold green]🤖 Chat Gemma 4 (Ollama)[/bold green] • [yellow]Modelo: {model}[/yellow] • [magenta]Pensamento: {think_mode}[/magenta]",
                border_style="green"
            )
        )
    else:
        print(f"\n=== Chat Gemma 4 | Modelo: {model} | Modo: {think_mode} ===")
        print("Comandos: /think [rapido|normal|profundo|off] | /model <nome> | /hide | sair\n")

def main():
    parser = argparse.ArgumentParser(
        description="Chat interativo com os modelos Gemma 4 no Ollama com interface rica e organizada."
    )
    parser.add_argument(
        "--model", "-m",
        default="gemma4:e2b",
        help="Modelo a ser utilizado (padrão: gemma4:e2b ou gemma-4-e4b-it-qat-q4_0)"
    )
    parser.add_argument(
        "--think", "-t",
        default="normal",
        choices=["rapido", "fast", "low", "normal", "medium", "profundo", "high", "off", "desativado"],
        help="Modo de pensamento: 'rapido' (low), 'normal' (medium), 'profundo' (high), ou 'off' (sem pensamento)"
    )
    parser.add_argument(
        "--hidethinking",
        action="store_true",
        help="Oculta o texto do processo de pensamento, exibindo apenas a resposta final"
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Prompt único direto (se omitido, inicia o chat interativo)"
    )

    args = parser.parse_args()

    current_model = args.model
    current_think = args.think
    show_thinking = not args.hidethinking

    # Se um prompt foi passado diretamente na linha de comando
    if args.prompt:
        question = " ".join(args.prompt)
        generate_stream(question, current_model, current_think, show_thinking)
        return

    # Modo chat interativo
    show_interactive_banner(current_model, current_think)

    while True:
        try:
            if HAS_RICH:
                prompt = console.input("[bold cyan]Você >[/bold cyan] ").strip()
            else:
                prompt = input("Você > ").strip()

            if not prompt:
                continue

            if prompt.lower() in ["sair", "exit", "quit"]:
                if HAS_RICH:
                    console.print("[bold cyan]Até logo![/bold cyan]")
                else:
                    print("Até logo!")
                break

            # Comandos em tempo de execução
            if prompt.startswith("/think"):
                parts = prompt.split()
                if len(parts) > 1:
                    target_mode = parts[1].lower()
                    if target_mode in THINK_MODES:
                        current_think = target_mode
                        msg = f"✓ Modo de pensamento alterado para: {current_think}"
                    else:
                        msg = "Modos válidos: rapido, normal, profundo, off"
                else:
                    msg = f"Modo atual: {current_think}"
                
                if HAS_RICH:
                    console.print(f"[bold yellow]{msg}[/bold yellow]\n")
                else:
                    print(f"{msg}\n")
                continue

            if prompt.startswith("/model"):
                parts = prompt.split()
                if len(parts) > 1:
                    current_model = parts[1]
                    msg = f"✓ Modelo alterado para: {current_model}"
                else:
                    msg = f"Modelo atual: {current_model}"
                
                if HAS_RICH:
                    console.print(f"[bold green]{msg}[/bold green]\n")
                else:
                    print(f"{msg}\n")
                continue

            if prompt.lower() == "/hide":
                show_thinking = not show_thinking
                status_str = "visível" if show_thinking else "oculto"
                msg = f"✓ Processo de pensamento agora está: {status_str}"
                if HAS_RICH:
                    console.print(f"[bold magenta]{msg}[/bold magenta]\n")
                else:
                    print(f"{msg}\n")
                continue

            if prompt.lower() in ["/ajuda", "/help"]:
                show_interactive_banner(current_model, current_think)
                continue

            generate_stream(prompt, current_model, current_think, show_thinking)

        except (KeyboardInterrupt, EOFError):
            if HAS_RICH:
                console.print("\n[bold cyan]Encerrando chat...[/bold cyan]")
            else:
                print("\nEncerrando chat...")
            break

if __name__ == "__main__":
    main()
