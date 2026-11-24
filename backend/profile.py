"""Preferências temporárias por UID e validação segura de imagens de perfil."""

from collections import OrderedDict
from dataclasses import dataclass, replace
from io import BytesIO
from pathlib import PurePath
import threading
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError

TEMAS = ("Automático", "Claro", "Escuro")
MAX_UPLOAD = 2 * 1024 * 1024


@dataclass(frozen=True, repr=False)
class Preferencias:
    tema: str = "Automático"
    nome: str = ""
    avatar: bytes | None = None


def validar_nome(nome):
    if not isinstance(nome, str) or any(ord(c) < 32 or ord(c) == 127 for c in nome):
        raise ValueError("Informe um nome de 1 a 80 caracteres, sem caracteres de controle.")
    nome = nome.strip()
    if not nome or len(nome) > 80:
        raise ValueError("Informe um nome de 1 a 80 caracteres, sem caracteres de controle.")
    return nome


def preparar_avatar(conteudo, nome_arquivo):
    """Recorte central 256², sem animação, EXIF ou conteúdo original embutido."""
    if not isinstance(conteudo, bytes) or not 0 < len(conteudo) <= MAX_UPLOAD:
        raise ValueError("A foto deve ter no máximo 2 MB.")
    sufixo = PurePath(nome_arquivo.replace("\\", "/")).suffix.lower()
    formatos = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".webp": "WEBP"}
    if sufixo not in formatos:
        raise ValueError("Escolha uma foto PNG, JPG ou WEBP.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(conteudo)) as original:
                if (original.format != formatos[sufixo] or getattr(original, "is_animated", False)
                        or max(original.size) > 4096 or original.width * original.height > 8_000_000):
                    raise ValueError("Formato ou dimensões da foto não permitidos.")
                original.verify()
            with Image.open(BytesIO(conteudo)) as original:
                imagem = ImageOps.exif_transpose(original).convert("RGB")
                imagem = ImageOps.fit(imagem, (256, 256), method=Image.Resampling.LANCZOS)
                saida = BytesIO()
                imagem.save(saida, format="WEBP", quality=85, method=6)
                resultado = saida.getvalue()
                if len(resultado) > 128 * 1024:
                    raise ValueError("A foto não pôde ser preparada.")
                return resultado
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError,
            Image.DecompressionBombWarning, SyntaxError):
        raise ValueError("O conteúdo do arquivo não é uma foto válida.") from None


class PreferenciasLocais:
    """Somente memória do processo, limitada e isolada por identidade verificada."""
    def __init__(self, capacidade=256):
        self._dados = OrderedDict()
        self._lock = threading.RLock()
        self.capacidade = capacidade

    def obter(self, uid):
        with self._lock:
            valor = self._dados.get(uid, Preferencias())
            if uid in self._dados:
                self._dados.move_to_end(uid)
            return valor

    def _gravar(self, uid, **campos):
        if not isinstance(uid, str) or not uid:
            raise PermissionError("Identidade necessária.")
        with self._lock:
            valor = replace(self.obter(uid), **campos)
            self._dados[uid] = valor
            self._dados.move_to_end(uid)
            while len(self._dados) > self.capacidade:
                self._dados.popitem(last=False)
            return valor

    def tema(self, uid, tema):
        if tema not in TEMAS:
            raise ValueError("Tema inválido.")
        return self._gravar(uid, tema=tema)

    def previa(self, uid, nome, avatar):
        nome = validar_nome(nome)
        if avatar is not None:
            # Só aceita a versão preparada; nenhuma referência arbitrária externa.
            avatar = preparar_avatar(avatar, "avatar.webp")
        return self._gravar(uid, nome=nome, avatar=avatar)


preferencias = PreferenciasLocais()
