"""Encerra somente o Chrome descartável iniciado pelo teste, de forma graciosa."""
import json
from pathlib import Path
import subprocess
import time
from websockets.sync.client import connect


def aguardar_devtools(perfil, timeout=15):
    arquivo = Path(perfil) / "DevToolsActivePort"
    limite = time.monotonic() + timeout
    while time.monotonic() < limite:
        try:
            linhas = arquivo.read_text().splitlines()
            int(linhas[0])
            if len(linhas) >= 2:
                return linhas
        except (OSError, ValueError, IndexError):
            pass
        time.sleep(.05)
    raise TimeoutError("Chrome de teste não disponibilizou DevTools")


def encerrar_browser(browser, perfil):
    arquivo = Path(perfil) / "DevToolsActivePort"
    try:
        linhas = aguardar_devtools(perfil, timeout=2)
        with connect(f"ws://127.0.0.1:{int(linhas[0])}{linhas[1]}", proxy=None, open_timeout=2, close_timeout=1) as cdp:
            cdp.send(json.dumps({"id": 1, "method": "Browser.close"}))
        browser.wait(timeout=10)
    except (OSError, ValueError, TimeoutError, subprocess.TimeoutExpired):
        if browser.poll() is None:
            browser.terminate()
            browser.wait(timeout=10)
    # Dá aos subprocessos de cache tempo para soltar os arquivos no Windows.
    time.sleep(0.4)
