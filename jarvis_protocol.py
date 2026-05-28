import speech_recognition as sr
import subprocess
import webbrowser
import time
import sys
import os
import keyboard
import threading
import random
import asyncio
import tempfile
import re
import winsound
import ast
import operator
import socket
import edge_tts
import pygame
import psutil
import wikipedia
import speedtest
from colorama import init, Fore, Style
from datetime import datetime

init(autoreset=True)
wikipedia.set_lang('pt')

# ── config ──────────────────────────────────────────────────
VOICE          = "pt-BR-AntonioNeural"
HOTKEY         = "F9"
HOTKEY_TEXT    = "F8"
TRIGGER_PHRASE = "jarvis"
VOICE_RATE     = "+15%"
VOICE_PITCH    = "-15Hz"

# ── spotify config (autoplay) ────────────────────────────────
SPOTIFY_CLIENT_ID     = ""
SPOTIFY_CLIENT_SECRET = ""
SPOTIFY_REDIRECT_URI  = "http://localhost:8888/callback"

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    _sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope="user-modify-playback-state user-read-playback-state"
    )) if SPOTIFY_CLIENT_ID else None
except Exception:
    _sp = None

# ── colors ──────────────────────────────────────────────────
def green(t):  return Fore.GREEN  + str(t) + Style.RESET_ALL
def cyan(t):   return Fore.CYAN   + str(t) + Style.RESET_ALL
def yellow(t): return Fore.YELLOW + str(t) + Style.RESET_ALL
def red(t):    return Fore.RED    + str(t) + Style.RESET_ALL
def white(t):  return Fore.WHITE  + str(t) + Style.RESET_ALL

# ── music ───────────────────────────────────────────────────
MUSICS = [
    "spotify:track:52UWtKlYjZO3dHoRlWuz9S",
    "spotify:track:0TI8TP4FitVPoEHPTySx48",
    "spotify:track:1EHNrwZlxW9Wp07Ohv1Jbw",
    "spotify:track:08mG3Y1vljYA6bvDt4Wqkj",
    "spotify:track:39shmbIHICJ2Wxnk1fPSdz",
]

# ── apps ────────────────────────────────────────────────────
APPS = {
    "netflix":   "https://www.netflix.com",
    "youtube":   "https://www.youtube.com",
    "discord":   "https://discord.com/app",
    "spotify":   "https://open.spotify.com",
    "cloud":     "https://claude.ai",
    "gmail":     "https://mail.google.com",
    "github":    "https://github.com",
    "twitch":    "https://www.twitch.tv",
    "instagram": "https://www.instagram.com",
    "twitter":   "https://twitter.com",
    "whatsapp":  "https://web.whatsapp.com",
}

# ── responses ───────────────────────────────────────────────
RESPONSES = {
    "present": [
        "Estou aqui senhor a sua disposição.",
        "Sempre presente senhor.",
        "Prontamente senhor, o que deseja?",
    ],
    "confirmation": [
        "Claro senhor.",
        "Imediatamente senhor.",
        "Prontamente senhor.",
    ],
    "fallback": [
        "Desculpe senhor, não entendi o que foi solicitado.",
        "Não compreendi senhor, poderia repetir?",
        "Peço desculpas senhor, não captei o comando.",
    ],
    "shutdown": [
        "Encerrando tudo nesse exato momento senhor.",
        "Desligando os sistemas senhor.",
    ],
    "activation": [
        "Ativando todos os processos nesse exato momento senhor.",
        "Sistemas reativados senhor.",
    ],
    "greeting": [
        "Sistemas completamente operacionais. À sua disposição, senhor.",
        "Iniciado com sucesso. O que deseja hoje senhor?",
    ],
    "searching": [
        "Consultando base de dados local e externa senhor.",
        "Buscando informações na rede, um momento.",
    ],
}

def response(key):
    return random.choice(RESPONSES[key])

# ── voice ────────────────────────────────────────────────────
pygame.mixer.init()
voice_lock = threading.Lock()

async def _generate_audio(text):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp.close()
    communicate = edge_tts.Communicate(text, VOICE, rate=VOICE_RATE, pitch=VOICE_PITCH)
    await communicate.save(tmp.name)
    return tmp.name

def speak(text):
    print(cyan(f'  [VOZ]  "{text}"'))
    with voice_lock:
        audio_file = asyncio.run(_generate_audio(text))
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.music.unload()
        try:
            os.unlink(audio_file)
        except:
            pass

def speak_thread(text):
    threading.Thread(target=speak, args=(text,), daemon=True).start()

# ── boot sounds ─────────────────────────────────────────────
def boot_sound():
    for freq, dur in [(440,80),(550,80),(660,80),(880,200),(660,80),(880,300)]:
        winsound.Beep(freq, dur)
        time.sleep(0.03)

def processing_sound(stop):
    freqs = [200,250,300,350,400,500,600,700]
    while not stop.is_set():
        winsound.Beep(random.choice(freqs), 40)
        time.sleep(random.uniform(0.04, 0.15))

# ── banner + boot ────────────────────────────────────────────
BANNER = [
    "     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗",
    "     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝",
    "     ██║███████║██████╔╝██║   ██║██║███████╗",
    "██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║",
    "╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║",
    " ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝",
    "    Just  A  Rather  Very  Intelligent  System",
]

BOOT_STEPS = [
    "Inicializando nucleo de processamento...",
    "Carregando modulos de reconhecimento de voz...",
    "Calibrando sensores de entrada...",
    "Estabelecendo conexao com servidores...",
    "Compilando protocolos de resposta...",
    "Ativando interface neural...",
    "Sistema pronto.",
]

# FIX 3 — barra mais larga no boot
def boot_animation():
    os.system("cls")
    print()
    for line in BANNER:
        print(cyan(f"  {line}"))
        time.sleep(0.07)
    print()
    stop_proc = threading.Event()
    threading.Thread(target=processing_sound, args=(stop_proc,), daemon=True).start()
    for step in BOOT_STEPS:
        n   = random.randint(70, 99)
        bar = "█" * (n * 40 // 100) + "░" * (40 - n * 40 // 100)
        print(green(f"  [BOOT] {step}"))
        print(green(f"         [{bar}] {n}%"))
        time.sleep(random.uniform(0.15, 0.4))
    stop_proc.set()
    print()
    threading.Thread(target=boot_sound, daemon=True).start()
    time.sleep(0.8)

# ── hacker visual ────────────────────────────────────────────
HACKER_MESSAGES = [
    "Escaneando rede local...",
    "Monitorando processos do sistema...",
    "Analisando trafego de dados...",
    "Verificando integridade dos arquivos...",
    "Compilando modulos de seguranca...",
    "Sincronizando protocolo neural...",
    "Lendo memoria volatil...",
    "Decifrando pacotes criptografados...",
    "Estabelecendo conexao segura...",
    "Atualizando banco de dados interno...",
    "Calibrando sensores de voz...",
    "Processando algoritmo adaptativo...",
    "Checando assinaturas digitais...",
    "Otimizando performance do nucleo...",
    "Rastreando anomalias no sistema...",
]

ALERT_MESSAGES = [
    "!!! INTRUSAO DETECTADA — RASTREANDO ORIGEM !!!",
    "!!! FIREWALL SOB ATAQUE — BLOQUEANDO !!!",
    "!!! ACESSO NAO AUTORIZADO — PROTOCOLO ATIVO !!!",
    "!!! MONITORAMENTO TOTAL — TODOS OS SISTEMAS !!!",
    "!!! CRIPTOGRAFIA AES-256 — ATIVADA !!!",
    "!!! VARREDURA DE AMEACAS — 100% !!!",
    "!!! MODO EMERGENCIA — STARK PROTOCOL !!!",
    "!!! RASTREANDO ATIVIDADE SUSPEITA !!!",
    "!!! TODOS OS ACESSOS EXTERNOS BLOQUEADOS !!!",
    "!!! SISTEMA EM ALERTA MAXIMO !!!",
]

def fake_ip():
    return f"{random.randint(10,192)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

def fake_hex():
    return "0x" + "".join(random.choices("0123456789ABCDEF", k=8))

# FIX 3 — barra mais larga no hacker visual
def progress_bar():
    n      = random.randint(30, 95)
    filled = n * 40 // 100
    return f"[{'█'*filled}{'░'*(40-filled)}] {n}%"

listening        = True
text_mode        = False
hacker_pause     = False
alert_mode       = False
stop_alert_event = threading.Event()
stop_alert_event.set()

# ── alert mode ───────────────────────────────────────────────
def alert_beep(stop):
    while not stop.is_set():
        for freq in range(500, 1501, 60):
            if stop.is_set(): return
            winsound.Beep(freq, 18)
        for freq in range(1500, 499, -60):
            if stop.is_set(): return
            winsound.Beep(freq, 18)

def _alert_bar_animated(label, color_fn=red, delay=0.022):
    sys.stdout.write(color_fn(f"  {label}  ["))
    sys.stdout.flush()
    for _ in range(20):
        sys.stdout.write(color_fn("█"))
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(color_fn("]  ATIVO\n"))
    sys.stdout.flush()

# ── painel de emergência ─────────────────────────────────────
def _emergency_panel():
    W   = 56
    now = datetime.now().strftime("%H:%M:%S")
    ip  = fake_ip()

    def s(text, color_fn=red, delay=0.006):
        for ch in text:
            sys.stdout.write(color_fn(ch))
            sys.stdout.flush()
            time.sleep(delay)

    def row(content, color_fn=red, W=W):
        # garante que content nunca ultrapasse W-2 chars
        content = content[: W - 2]
        pad = W - 2 - len(content)
        lp  = pad // 2
        rp  = pad - lp
        s(f"  ║ {' ' * lp}{content}{' ' * rp} ║\n", color_fn)

    def divider(l="╠", m="═", r="╣", color_fn=red):
        s(f"  {l}{m * W}{r}\n", color_fn, delay=0.003)

    print()

    s("  ╔", red, delay=0.003)
    for _ in range(W):
        s("═", red, delay=0.003)
    s("╗\n", red)
    winsound.Beep(900, 80)

    row("", red)
    row("S . T . A . R . K   S E C U R I T Y", red)
    row("PROTOCOLO DE EMERGENCIA — NIVEL MAXIMO", yellow)
    row("", red)
    divider()

    row(f"HORA   : {now}   AMEACA : DETECTADA", yellow)
    row(f"ORIGEM : {ip}   NIVEL  : CRITICO", yellow)
    row("ACESSO : NAO AUTORIZADO   STATUS : ALERTA", yellow)
    row("", red)
    divider(l="╠", m="─", r="╣")

    s(f"  ║  ", red)
    s("ATIVANDO PROTOCOLOS DE DEFESA...\n", yellow, delay=0.025)
    winsound.Beep(700, 60)

    protocols = [
        ("FIREWALL  STARK     ", 0.018),
        ("CRIPTOGRAFIA AES-256", 0.016),
        ("RASTREAMENTO TOTAL  ", 0.020),
        ("BLOQUEIO  EXTERNO   ", 0.014),
        ("VARREDURA DE AMEACAS", 0.017),
    ]
    for label, spd in protocols:
        s(f"  ║  {label}  [", red)
        for _ in range(20):
            s("█", red)
            time.sleep(spd)
        s("]  ATIVO\n", red)
        winsound.Beep(random.choice([600, 800, 1000]), 40)

    row("", red)
    divider()
    row("", red)
    row("TODOS OS SISTEMAS EM ALERTA MAXIMO", red)
    row("MONITORANDO TODAS AS CONEXOES ATIVAS", yellow)
    row("", red)

    s("  ╚", red, delay=0.003)
    for _ in range(W):
        s("═", red, delay=0.003)
    s("╝\n\n", red)
    winsound.Beep(1200, 150)

# FIX 4 — hacker_pause antes do painel
def activate_alert():
    global alert_mode, stop_alert_event, hacker_pause
    alert_mode   = True
    hacker_pause = True
    time.sleep(0.3)
    stop_alert_event = threading.Event()
    _emergency_panel()
    hacker_pause = False
    threading.Thread(target=alert_beep, args=(stop_alert_event,), daemon=True).start()
    speak_thread("Protocolo de emergencia ativado senhor. "
                 "Todos os sistemas em alerta maximo. Monitorando.")

def deactivate_alert():
    global alert_mode, stop_alert_event
    alert_mode = False
    stop_alert_event.set()
    print()
    print(green("  ╔══════════════════════════════════════════════════════╗"))
    print(green("  ║       MODO DE SEGURANCA DESATIVADO — SISTEMA OK      ║"))
    print(green("  ╚══════════════════════════════════════════════════════╝"))
    print()
    speak_thread("Modo de seguranca desativado senhor. Retornando ao estado normal.")

def hacker_effect():
    while True:
        if listening and not hacker_pause and not text_mode:
            if alert_mode:
                print(red(f"  [!!!]  {random.choice(ALERT_MESSAGES)}"))
                time.sleep(random.uniform(0.3, 0.7))
            else:
                kind = random.randint(1, 4)
                if kind == 1:
                    print(green(f"  [SYS]  {random.choice(HACKER_MESSAGES)}"))
                elif kind == 2:
                    print(green(f"  [NET]  Conexao com {fake_ip()} — latencia {random.randint(1,99)}ms"))
                elif kind == 3:
                    print(green(f"  [MEM]  Endereco {fake_hex()} -> {random.randint(1,999)} KB alocados"))
                elif kind == 4:
                    print(green(f"  [LOAD] {progress_bar()}"))
                time.sleep(random.uniform(1.5, 3.5))
        else:
            time.sleep(0.5)

# ── F9 toggle ────────────────────────────────────────────────
def toggle_listening():
    global listening
    listening = not listening
    if listening:
        print(green("\n[F9] JARVIS LIGADO\n"))
        speak_thread("Ola novamente, Senhor.")
    else:
        print(red("\n[F9] JARVIS DESLIGADO\n"))
        speak_thread("Ate mais, senhor.")

keyboard.add_hotkey(HOTKEY, toggle_listening)

# ── internet speed com barra real ────────────────────────────
def get_internet_speed():
    global hacker_pause

    hacker_pause = True
    time.sleep(0.25)

    done_dl = threading.Event()
    done_ul = threading.Event()
    dl_bits = [0]
    ul_bits = [0]

    # FIX 3 — barra mais larga no speedtest
    def _draw_bar(label, color_fn, pct, value_str=""):
        filled = min(pct, 100) * 40 // 100
        bar    = "█" * filled + "░" * (40 - filled)
        suffix = f"  {value_str}" if value_str else f"  {pct}%"
        sys.stdout.write(f"\r  {color_fn(f'{label}  [{bar}]{suffix}')}")
        sys.stdout.flush()

    print(cyan("\n  ╔══════════════════════════════════════════╗"))
    print(cyan("  ║   DIAGNOSTICO DE REDE — S.T.A.R.K PROTOCOL   ║"))
    print(cyan("  ╠══════════════════════════════════════════╣"))
    print(cyan("  ║  Selecionando servidor mais proximo...    ║"))

    try:
        st = speedtest.Speedtest(secure=True)
        st.get_best_server()
    except Exception as e:
        print(red(f"\n  [ERR] Speedtest: {e}\n"))
        hacker_pause = False
        return None, None

    srv  = st.results.server
    host = srv.get("host", "desconhecido")[:30]
    print(cyan(f"  ║  Servidor : {host:<29}║"))
    print(cyan("  ╠══════════════════════════════════════════╣"))

    def run_download():
        dl_bits[0] = st.download()
        done_dl.set()

    threading.Thread(target=run_download, daemon=True).start()
    est_dl = 18
    t0 = time.time()
    print()
    while not done_dl.is_set():
        pct = min(int((time.time() - t0) / est_dl * 98), 98)
        _draw_bar("↓ DOWNLOAD", cyan, pct)
        time.sleep(0.12)
    dl_mbps = round(dl_bits[0] / 1_000_000, 2)
    _draw_bar("↓ DOWNLOAD", cyan, 100, f"  {dl_mbps} Mbps")
    print()

    def run_upload():
        ul_bits[0] = st.upload()
        done_ul.set()

    threading.Thread(target=run_upload, daemon=True).start()
    est_ul = 18
    t0 = time.time()
    print()
    while not done_ul.is_set():
        pct = min(int((time.time() - t0) / est_ul * 98), 98)
        _draw_bar("↑ UPLOAD  ", yellow, pct)
        time.sleep(0.12)
    ul_mbps = round(ul_bits[0] / 1_000_000, 2)
    _draw_bar("↑ UPLOAD  ", yellow, 100, f"  {ul_mbps} Mbps")
    print()

    print(cyan("  ╠══════════════════════════════════════════╣"))
    print(cyan("  ║  ") + yellow(f"Download : {dl_mbps} Mbps".ljust(41)) + cyan("║"))
    print(cyan("  ║  ") + yellow(f"Upload   : {ul_mbps} Mbps".ljust(41)) + cyan("║"))
    print(cyan("  ╚══════════════════════════════════════════╝\n"))

    hacker_pause = False
    return dl_mbps, ul_mbps

# ── system status ────────────────────────────────────────────
def status_report():
    now = datetime.now().strftime("%H:%M")
    try:
        cpu      = psutil.cpu_percent(interval=1)
        ram      = psutil.virtual_memory().percent
        bat      = psutil.sensors_battery()
        bat_str  = f"{int(bat.percent)}%" if bat else "N/A"
        charging = " carregando" if bat and bat.power_plugged else ""

        speak("Medindo a velocidade da sua conexao senhor. Um momento.")
        dl, ul = get_internet_speed()

        if dl is not None:
            net_spoken = (f"download a {dl} megabits por segundo "
                          f"e upload a {ul} megabits por segundo")
        else:
            net_spoken = "indisponivel no momento"

        print(cyan("\n  ╔══════════════════════════════════════╗"))
        print(cyan("  ║   STATUS DO SISTEMA J.A.R.V.I.S      ║"))
        print(cyan("  ╠══════════════════════════════════════╣"))
        print(cyan("  ║  Hora:     ") + yellow(now.ljust(26))                    + cyan("║"))
        print(cyan("  ║  CPU:      ") + yellow(f"{cpu}%".ljust(26))              + cyan("║"))
        print(cyan("  ║  RAM:      ") + yellow(f"{ram}%".ljust(26))              + cyan("║"))
        print(cyan("  ║  Bateria:  ") + yellow(f"{bat_str}{charging}".ljust(26)) + cyan("║"))
        print(cyan("  ╚══════════════════════════════════════╝\n"))

        bat_spoken = f"{int(bat.percent)} porcento" if bat else "nao disponivel"
        plug = ", carregando" if bat and bat.power_plugged else ""
        speak(f"Relatorio completo senhor. Sao {now}. "
              f"CPU em {cpu} porcento. Memoria em {ram} porcento. "
              f"Bateria em {bat_spoken}{plug}. "
              f"Velocidade de internet: {net_spoken}.")
    except Exception as e:
        speak("Erro ao verificar o status do sistema senhor.")
        print(red(f"  [ERR]  {e}"))

# FIX 1 — wikipedia com suporte a palavras compostas
def wikipedia_speak(query):
    speak_thread(response("searching"))
    try:
        page = None
        try:
            page = wikipedia.page(query, auto_suggest=True)
        except wikipedia.DisambiguationError as e:
            page = wikipedia.page(e.options[0], auto_suggest=False)
        except Exception:
            hits = wikipedia.search(query, results=5)
            if hits:
                try:
                    page = wikipedia.page(hits[0], auto_suggest=False)
                except wikipedia.DisambiguationError as e:
                    page = wikipedia.page(e.options[0], auto_suggest=False)

        if page:
            clean   = re.sub(r'\([^)]*\)', '', page.summary).strip()
            phrases = [s.strip() for s in clean.split('. ') if s.strip()]
            result  = '. '.join(phrases[:3]).strip()[:500]
            speak(result)
        else:
            speak(f"Nao encontrei informacoes sobre {query} senhor.")
    except Exception as e:
        speak("Nao consegui acessar a Wikipedia no momento senhor.")
        print(red(f"  [ERR] Wikipedia: {e}"))

# ── calculator ───────────────────────────────────────────────
_OPS = {
    ast.Add:  operator.add,
    ast.Sub:  operator.sub,
    ast.Mult: operator.mul,
    ast.Div:  operator.truediv,
    ast.USub: operator.neg,
}

_NUM_WORDS = {
    "zero":"0","um":"1","uma":"1","dois":"2","duas":"2",
    "tres":"3","três":"3","quatro":"4","cinco":"5","seis":"6",
    "sete":"7","oito":"8","nove":"9","dez":"10","onze":"11",
    "doze":"12","treze":"13","quatorze":"14","catorze":"14",
    "quinze":"15","dezesseis":"16","dezessete":"17","dezoito":"18",
    "dezenove":"19","vinte":"20","trinta":"30","quarenta":"40",
    "cinquenta":"50","sessenta":"60","setenta":"70","oitenta":"80",
    "noventa":"90","cem":"100","cento":"100","duzentos":"200",
    "trezentos":"300","quatrocentos":"400","quinhentos":"500","mil":"1000",
}

def _words_to_numbers(text):
    for word, digit in _NUM_WORDS.items():
        text = re.sub(rf'\b{word}\b', digit, text)
    return text

def _eval_node(node):
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    elif isinstance(node, ast.UnaryOp):
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("Operacao nao suportada")

def safe_calculate(text):
    text = _words_to_numbers(text)
    text = (text
        .replace("mais",             "+")
        .replace("menos",            "-")
        .replace("vezes",            "*")
        .replace("multiplicado por", "*")
        .replace("dividido por",     "/")
        .replace("dividido",         "/"))
    expr = re.sub(r"[^0-9+\-*/\.\s()]", "", text).strip()
    expr = re.sub(r'\s+', ' ', expr).strip()
    try:
        result = _eval_node(ast.parse(expr, mode='eval').body)
        return int(result) if isinstance(result, float) and result.is_integer() else round(result, 4)
    except:
        return None

# ── spotify play ─────────────────────────────────────────────
def spotify_play(query):
    if _sp:
        try:
            results = _sp.search(q=query, type='track', limit=1)
            items   = results['tracks']['items']
            if items:
                track = items[0]
                _sp.start_playback(uris=[track['uri']])
                speak_thread(f"Tocando {track['name']}, de {track['artists'][0]['name']}, senhor.")
                return
            else:
                speak_thread("Nao encontrei essa musica no Spotify senhor.")
                return
        except Exception as e:
            print(red(f"  [ERR] Spotify API: {e}"))
    speak_thread(response("confirmation"))
    webbrowser.open(f"https://open.spotify.com/search/{query.replace(' ', '%20')}")

# ── text mode — Iron Man HUD ─────────────────────────────────
_HUD_WIDTH = 54

def _stream(text, color_fn=cyan, delay=0.012):
    for ch in text:
        sys.stdout.write(color_fn(ch))
        sys.stdout.flush()
        time.sleep(delay)

def _hud_beep():
    for freq in [800, 1200, 600, 1000]:
        winsound.Beep(freq, 35)

def _hud_scan_beep():
    for freq in [400, 600, 900, 1200, 900, 600]:
        winsound.Beep(freq, 25)
        time.sleep(0.02)

def _hud_row(content, W=_HUD_WIDTH, fill=" "):
    pad = W - len(content)
    return "║" + fill[:1] + content + fill[:1] * (pad - 1) + "║"

def _hud_divider(left="╠", mid="═", right="╣", W=_HUD_WIDTH):
    return left + mid * W + right

def _hud_tag(label, value="", W=_HUD_WIDTH):
    inner = f"◆ {label:<18}{value}"
    pad   = W - len(inner)
    return "║" + inner + " " * max(pad, 1) + "║"

def build_text_field_animation():
    global hacker_pause
    hacker_pause = True
    time.sleep(0.18)

    W   = _HUD_WIDTH
    now = datetime.now().strftime("%H:%M:%S")

    print()

    sys.stdout.write(cyan("  ╔"))
    sys.stdout.flush()
    for _ in range(W):
        sys.stdout.write(cyan("═"))
        sys.stdout.flush()
        time.sleep(0.006)
    sys.stdout.write(cyan("╗\n"))
    threading.Thread(target=_hud_scan_beep, daemon=True).start()

    time.sleep(0.05)
    title = "◢  STARK  TACTICAL  INTERFACE  ◣"
    _stream(f"  {_hud_row(title.center(W - 2))}\n", delay=0.008)

    sub = f"JARVIS v2.0   |   {now}   |   CANAL SEGURO"
    _stream(f"  {_hud_row(sub.center(W - 2))}\n", color_fn=yellow, delay=0.007)

    time.sleep(0.04)
    _stream(f"  {_hud_divider()}\n", delay=0.005)

    time.sleep(0.03)
    _stream(f"  {_hud_tag('MODO',        'ENTRADA TEXTUAL')}\n",   color_fn=cyan,   delay=0.007)
    _stream(f"  {_hud_tag('PROTOCOLO',   'AES-256  ▸  ATIVO')}\n", color_fn=green,  delay=0.007)
    _stream(f"  {_hud_tag('CONFIRMACAO', 'ENTER')}\n",              color_fn=cyan,   delay=0.007)
    _stream(f"  {_hud_tag('ENCERRAR',    'sair')}\n",               color_fn=yellow, delay=0.007)

    label_div = "─── AGUARDANDO ENTRADA ───"
    pad_div   = W - len(label_div)
    lp = pad_div // 2
    rp = pad_div - lp
    time.sleep(0.04)
    _stream(f"  ╠{'─' * lp}{label_div}{'─' * rp}╣\n", delay=0.005)
    threading.Thread(target=_hud_beep, daemon=True).start()

    time.sleep(0.05)
    sys.stdout.write(cyan("  ║ "))
    for i in range(W - 2):
        ch = "▓" if i % 3 != 2 else "░"
        sys.stdout.write(cyan(ch))
        sys.stdout.flush()
        time.sleep(0.003)
    sys.stdout.write(cyan(" ║\n"))

    time.sleep(0.08)
    sys.stdout.write(cyan("  ║ "))
    sys.stdout.write(green("▶▶ "))
    sys.stdout.flush()

    time.sleep(0.06)
    foot = "STARK  INDUSTRIES  //  JARVIS  NEURAL  ENGINE"
    _stream(f"\n  {_hud_row(foot.center(W - 2))}\n", color_fn=yellow, delay=0.006)
    sys.stdout.write(cyan("  ╚"))
    for _ in range(W):
        sys.stdout.write(cyan("═"))
        sys.stdout.flush()
        time.sleep(0.004)
    sys.stdout.write(cyan("╝\n\n"))
    sys.stdout.flush()
    threading.Thread(target=_hud_beep, daemon=True).start()

    hacker_pause = False

# FIX 2 — text_mode_loop passa from_text=True
def text_mode_loop():
    global text_mode

    print(yellow("\n  [TEXT] Inicializando interface tatica..."))
    time.sleep(0.4)
    build_text_field_animation()
    speak_thread("Interface tatica ativa senhor. Pode digitar seus comandos.")

    while text_mode:
        try:
            sys.stdout.write(cyan("  ║ ▶▶ "))
            sys.stdout.flush()
            raw  = input()
            text = raw.strip().lower()

            if not text:
                continue

            if text in ("sair", "fechar", "exit", "quit"):
                _stream(f"  {_hud_divider('╠','─','╣')}\n", delay=0.004)
                _stream(f"  {_hud_row('◆  INTERFACE ENCERRADA  ◆'.center(_HUD_WIDTH - 2))}\n", color_fn=yellow, delay=0.008)
                _stream(f"  {_hud_divider('╚','═','╝')}\n\n", delay=0.004)
                speak_thread("Interface tatica encerrada senhor.")
                text_mode = False
                break

            if TRIGGER_PHRASE not in text:
                text = f"{TRIGGER_PHRASE} {text}"

            process_command(text, from_text=True)
            time.sleep(0.1)

        except (EOFError, KeyboardInterrupt):
            text_mode = False
            break

# ── F8 toggle text mode ──────────────────────────────────────
def toggle_text_mode():
    global text_mode
    if text_mode:
        text_mode = False
        print(yellow(f"\n[{HOTKEY_TEXT}] Interface tatica desativada.\n"))
    else:
        text_mode = True
        print(cyan(f"\n[{HOTKEY_TEXT}] INICIANDO INTERFACE TATICA\n"))
        threading.Thread(target=text_mode_loop, daemon=True).start()

keyboard.add_hotkey(HOTKEY_TEXT, toggle_text_mode)

# ── actions ──────────────────────────────────────────────────
def play_random_music():
    os.startfile(random.choice(MUSICS))

def open_vscode():
    subprocess.Popen(["code"], shell=True)

def open_claude():
    webbrowser.open("https://claude.ai")

# FIX 2 — process_command sem print duplicado na voz
def process_command(text, from_text=False):
    global listening, alert_mode
    if from_text:
        print(yellow(f"  [CMD]  '{text}'"))
    ct = text.replace(TRIGGER_PHRASE, "").strip()

    if ct == "":
        speak_thread(response("present"))

    elif any(p in ct for p in ["status", "relatorio", "relatório"]):
        threading.Thread(target=status_report, daemon=True).start()

    elif any(p in ct for p in ["que horas", "horas sao", "horas são", "hora"]):
        speak_thread(f"Agora sao {datetime.now().strftime('%H:%M')} senhor.")

    elif any(p in ct for p in ["ta ai", "tá aí", "ta aí", "tá ai"]):
        speak_thread(response("confirmation"))
        time.sleep(2)
        play_random_music()
        open_vscode()
        open_claude()

    elif any(p in ct for p in ["emergencia", "emergência", "modo seguranca", "modo segurança", "a casa caiu"]):
        activate_alert()

    elif any(p in ct for p in ["desativar modo", "alarme falso", "cancelar alerta", "modo normal"]):
        deactivate_alert()

    elif any(p in ct for p in ["encerre todos", "encerrar todos", "encerre os processos", "encerrar processos"]):
        speak(response("shutdown"))
        listening = False
        print(red(f"\n[{HOTKEY}] JARVIS DESLIGADO\n"))

    elif any(p in ct for p in ["ative todos", "ativar todos", "ative os processos", "ativar processos"]):
        speak_thread(response("activation"))
        listening = True
        print(green(f"\n[{HOTKEY}] JARVIS LIGADO\n"))

    elif any(p in ct for p in ["apresente-se", "apresente se", "quem e voce", "quem é você", "se apresente"]):
        speak_thread("Eu sou JARVIS. "
                     "Desenvolvido para auxiliar o senhor em todas as suas necessidades digitais. "
                     "Posso abrir aplicativos, pesquisar na internet, verificar sistemas e muito mais. "
                     "Completamente a sua disposicao senhor.")

    elif any(p in ct for p in ["pesquisa", "pesquisar"]):
        query = ct.replace("pesquisa","").replace("pesquisar","").strip()
        if query:
            speak_thread(response("confirmation"))
            webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
        else:
            speak_thread(response("fallback"))

    # FIX 1 — adicionado "me fale sobre" e outros variantes
    elif any(p in ct for p in ["me fala sobre", "me fale sobre", "pesquise sobre",
                                "fala sobre", "fale sobre",
                                "quem foi", "quem e", "quem é",
                                "o que e", "o que é", "o que foi"]):
        query = ct
        for p in ["me fala sobre", "me fale sobre", "pesquise sobre",
                  "fala sobre", "fale sobre",
                  "quem foi", "quem e", "quem é",
                  "o que e", "o que é", "o que foi"]:
            query = query.replace(p, "").strip()
        if query:
            threading.Thread(target=wikipedia_speak, args=(query,), daemon=True).start()
        else:
            speak_thread(response("fallback"))

    elif any(p in ct for p in ["toca ", "tocar "]):
        query = ct.replace("toca","").replace("tocar","").strip()
        if query:
            spotify_play(query)
        else:
            speak_thread(response("fallback"))

    elif any(p in ct for p in ["quanto e", "quanto é", "calcule", "calcular"]):
        result = safe_calculate(ct)
        if result is not None:
            speak_thread(f"O resultado é {result} senhor.")
        else:
            speak_thread("Nao consegui calcular isso senhor.")

    elif any(p in ct for p in ["abre", "abrir"]):
        name  = ct.replace("abre","").replace("abrir","").strip()
        found = False
        for app, url in APPS.items():
            if app in name:
                speak_thread(response("confirmation"))
                webbrowser.open(url)
                found = True
                break
        if not found:
            speak_thread(response("fallback"))

    elif any(p in ct for p in ["projetos", "projeto"]):
        speak_thread("O senhor está atualmente trabalhando na armadura, Mark 45.")

    else:
        speak_thread(response("fallback"))

# ── main ─────────────────────────────────────────────────────
boot_animation()
threading.Thread(target=hacker_effect, daemon=True).start()

recognizer = sr.Recognizer()
print(green(f'JARVIS LIGADO — {HOTKEY} ligar/desligar voz  |  {HOTKEY_TEXT} interface tatica'))
speak_thread(response("greeting"))

with sr.Microphone() as source:
    recognizer.adjust_for_ambient_noise(source, duration=1)
    while True:
        try:
            if not listening or text_mode:
                time.sleep(0.5)
                continue
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            text  = recognizer.recognize_google(audio, language="pt-BR").lower()
            print(yellow(f'   Ouvi: "{text}"'))
            if TRIGGER_PHRASE in text:
                process_command(text)
        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(red(f"❌ Erro de conexão: {e}"))
        except KeyboardInterrupt:
            print(red("\n👋 J.A.R.V.I.S. encerrado."))
            sys.exit()