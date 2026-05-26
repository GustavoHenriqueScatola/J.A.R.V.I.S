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
import edge_tts
import pygame
from colorama import init, Fore, Style

init(autoreset=True)

# ── colors ─────────────────────────────────────────────────
def green(text):  return Fore.GREEN  + str(text) + Style.RESET_ALL
def cyan(text):   return Fore.CYAN   + str(text) + Style.RESET_ALL
def yellow(text): return Fore.YELLOW + str(text) + Style.RESET_ALL
def red(text):    return Fore.RED    + str(text) + Style.RESET_ALL

# ── music ──────────────────────────────────────────────────
MUSICS = [
    "spotify:track:52UWtKlYjZO3dHoRlWuz9S",
    "spotify:track:0TI8TP4FitVPoEHPTySx48",
    "spotify:track:1EHNrwZlxW9Wp07Ohv1Jbw",
    "spotify:track:08mG3Y1vljYA6bvDt4Wqkj"
]

# ── known apps ──────────────────────────────────────────────
APPS = {
    "netflix":    "https://www.netflix.com",
    "youtube":    "https://www.youtube.com",
    "discord":    "https://discord.com/app",
    "spotify":    "https://open.spotify.com",
    "claude":     "https://claude.ai",
    "gmail":      "https://mail.google.com",
    "github":     "https://github.com",
    "twitch":     "https://www.twitch.tv",
    "instagram":  "https://www.instagram.com",
    "twitter":    "https://twitter.com",
    "whatsapp":   "https://web.whatsapp.com",
}

# ── settings ────────────────────────────────────────────────
TRIGGER_PHRASE = "jarvis"
HOTKEY         = "F9"
VOICE          = "pt-BR-AntonioNeural"

# ── random responses ────────────────────────────────────────
RESPONSES = {
    "present": [
        "Estou aqui senhor à sua disposição.",
        "Sempre presente senhor.",
        "Prontamente senhor o que deseja?",
    ],
    "confirmation": [
        "Claro senhor.",
        "Imediatamente senhor.",
        "Prontamente senhor.",
    ],
    "fallback": [
        "Desculpe senhor não entendi o que foi solicitado.",
        "Não compreendi senhor poderia repetir?",
        "Peço desculpas senhor não captei o comando.",
    ],
    "shutdown": [
        "Encerrando tudo nesse exato momento senhor.",
        "Desligando os sistemas senhor.",
    ],
    "activation": [
        "Ativando todos os processos nesse exato momento senhor.",
        "Sistemas reativados senhor.",
    ],
}

def response(key):
    return random.choice(RESPONSES[key])

# ── voice ───────────────────────────────────────────────────
pygame.mixer.init()
voice_lock = threading.Lock()

async def _generate_audio(text):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file.close()
    communicate = edge_tts.Communicate(text, VOICE, rate="+10%", pitch="-15Hz")
    await communicate.save(temp_file.name)
    return temp_file.name

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

# ── boot sound ──────────────────────────────────────────────
def boot_sound():
    for freq, dur in [(440,80),(550,80),(660,80),(880,200),(660,80),(880,300)]:
        winsound.Beep(freq, dur)
        time.sleep(0.03)

# ── banner + animated boot ──────────────────────────────────
BANNER = [
    "     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗",
    "     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝",
    "     ██║███████║██████╔╝██║   ██║██║███████╗",
    "██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║",
    "╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║",
    " ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝",
    "      Just A Rather Very Intelligent System  ",
]

BOOT_STEPS = [
    "Inicializando núcleo de processamento...",
    "Carregando módulos de reconhecimento de voz...",
    "Calibrando sensores de entrada...",
    "Estabelecendo conexão com servidores...",
    "Compilando protocolos de resposta...",
    "Ativando interface neural...",
    "Sistema pronto.",
]

def boot_animation():
    os.system("cls")
    print()
    for line in BANNER:
        print(cyan(f"  {line}"))
        time.sleep(0.07)
    print()
    for step in BOOT_STEPS:
        n = random.randint(70, 99)
        bar = "█" * (n // 5) + "░" * (20 - n // 5)
        print(green(f"  [BOOT] {step}"))
        print(green(f"         [{bar}] {n}%"))
        time.sleep(random.uniform(0.15, 0.4))
    print()
    threading.Thread(target=boot_sound, daemon=True).start()
    time.sleep(0.8)

# ── hacker visual effect ────────────────────────────────────
HACKER_MESSAGES = [
    "Escaneando rede local...",
    "Monitorando processos do sistema...",
    "Analisando tráfego de dados...",
    "Verificando integridade dos arquivos...",
    "Compilando módulos de segurança...",
    "Sincronizando protocolo neural...",
    "Lendo memória volátil...",
    "Decifrando pacotes criptografados...",
    "Estabelecendo conexão segura...",
    "Atualizando banco de dados interno...",
    "Calibrando sensores de voz...",
    "Processando algoritmo adaptativo...",
    "Checando assinaturas digitais...",
    "Otimizando performance do núcleo...",
    "Rastreando anomalias no sistema...",
]

def fake_ip():
    return f"{random.randint(10,192)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

def fake_hex():
    return "0x" + "".join(random.choices("0123456789ABCDEF", k=8))

def progress_bar():
    n = random.randint(30, 95)
    return f"[{'█'*(n//5)}{'░'*(20-n//5)}] {n}%"

listening = True

def hacker_effect():
    while True:
        if listening:
            kind = random.randint(1, 4)
            if kind == 1:
                print(green(f"  [SYS]  {random.choice(HACKER_MESSAGES)}"))
            elif kind == 2:
                print(green(f"  [NET]  Conexão com {fake_ip()} — latência {random.randint(1,99)}ms"))
            elif kind == 3:
                print(green(f"  [MEM]  Endereço {fake_hex()} → {random.randint(1,999)} KB alocados"))
            elif kind == 4:
                print(green(f"  [LOAD] {progress_bar()}"))
        time.sleep(random.uniform(1.5, 3.5))

# ── F9 toggle ───────────────────────────────────────────────
def toggle_listening():
    global listening
    listening = not listening
    if listening:
        print(green("\n[F9] 🟢 JARVIS LIGADO\n"))
        speak_thread("Olá novamente senhor.")
    else:
        print(red("\n[F9] 🔴 JARVIS DESLIGADO\n"))
        speak_thread("Até mais senhor.")

keyboard.add_hotkey(HOTKEY, toggle_listening)

# ── actions ────────────────────────────────────────────────
def play_random_music():
    os.startfile(random.choice(MUSICS))

def open_vscode():
    subprocess.Popen(["code"], shell=True)

def open_claude():
    webbrowser.open("https://claude.ai")

# ── calculator ──────────────────────────────────────────────
def calculate(text):
    text = (text
        .replace("mais", "+")
        .replace("menos", "-")
        .replace("vezes", "*")
        .replace("dividido por", "/")
        .replace("dividido", "/"))
    numbers = re.sub(r"[^0-9+\-*/.\s]", "", text).strip()
    try:
        return eval(numbers)
    except:
        return None

# ── process commands ────────────────────────────────────────
def process_command(text):
    global listening
    print(yellow(f"  [CMD]  '{text}'"))
    command_text = text.replace("jarvis", "").strip()

    # alone
    if command_text == "":
        speak_thread(response("present"))

    # time
    elif any(p in command_text for p in ["que horas", "horas são", "hora"]):
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M")
        speak_thread(f"Agora são {current_time} senhor.")

    # are you there → open everything
    elif any(p in command_text for p in ["tá aí", "ta aí", "tá ai", "ta ai"]):
        speak_thread(response("confirmation"))
        time.sleep(2)
        play_random_music()
        open_vscode()
        open_claude()

    # shutdown
    elif any(p in command_text for p in ["encerre todos", "encerrar todos", "encerre os processos", "encerrar processos"]):
        speak(response("shutdown"))
        listening = False
        print(red("\n[F9] 🔴 JARVIS DESLIGADO\n"))

    # activate
    elif any(p in command_text for p in ["ative todos", "ativar todos", "ative os processos", "ativar processos"]):
        speak_thread(response("activation"))
        listening = True
        print(green("\n[F9] 🟢 JARVIS LIGADO\n"))

    # google search
    elif any(p in command_text for p in ["pesquisa", "pesquisar"]):
        query = command_text.replace("pesquisa", "").replace("pesquisar", "").strip()
        if query:
            speak_thread(response("confirmation"))
            webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
        else:
            speak_thread(response("fallback"))

    # play specific song on spotify
    elif any(p in command_text for p in ["toca ", "tocar "]):
        query = command_text.replace("toca", "").replace("tocar", "").strip()
        if query:
            speak_thread(response("confirmation"))
            webbrowser.open(f"https://open.spotify.com/search/{query.replace(' ', '%20')}")
        else:
            speak_thread(response("fallback"))

    # calculator
    elif any(p in command_text for p in ["quanto é", "quanto e", "calcule", "calcular"]):
        result = calculate(command_text)
        if result is not None:
            speak_thread(f"O resultado é {result},senhor.")
        else:
            speak_thread("Não consegui calcular isso senhor.")

    # open app
    elif any(p in command_text for p in ["abre", "abrir"]):
        name = command_text.replace("abre", "").replace("abrir", "").strip()
        found = False
        for app, url in APPS.items():
            if app in name:
                speak_thread(response("confirmation"))
                webbrowser.open(url)
                found = True
                break
        if not found:
            speak_thread(response("fallback"))

    # projects
    elif any(p in command_text for p in ["projetos", "projeto"]):
        speak_thread("O senhor está atualmente trabalhando na armadura, Mark 45.")

    # fallback
    else:
        speak_thread(response("fallback"))

# ── initialization ──────────────────────────────────────────
boot_animation()
threading.Thread(target=hacker_effect, daemon=True).start()

recognizer = sr.Recognizer()
print(green(f'🟢 J.A.R.V.I.S. LIGADO — aperte {HOTKEY} pra ligar/desligar'))
speak_thread("Olá senhor, o que tem em mente hoje?")

with sr.Microphone() as source:
    recognizer.adjust_for_ambient_noise(source, duration=1)
    while True:
        try:
            if not listening:
                time.sleep(0.5)
                continue
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            text = recognizer.recognize_google(audio, language="pt-BR").lower()
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