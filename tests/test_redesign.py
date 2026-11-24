"""Contrato do perfil, avatar, temas, navegação e autorização do redesign."""
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from PIL import Image
from streamlit.testing.v1 import AppTest
from backend.profile import PreferenciasLocais, preparar_avatar, validar_nome, MAX_UPLOAD
from backend.session_store import SessoesServidor
from ui.components import usuario_html


def imagem(formato="PNG", tamanho=(400, 240)):
    saida = BytesIO()
    Image.new("RGB", tamanho, "#19b775").save(saida, format=formato)
    return saida.getvalue()


class TestAvatar(unittest.TestCase):
    def test_formatos_permitidos_normalizados(self):
        for formato, ext in (("PNG", "png"), ("JPEG", "jpg"), ("WEBP", "webp")):
            with self.subTest(formato=formato):
                foto = preparar_avatar(imagem(formato), "foto." + ext)
                with Image.open(BytesIO(foto)) as avatar:
                    self.assertEqual(avatar.format, "WEBP")
                    self.assertEqual(avatar.size, (256, 256))

    def test_rejeita_extensao_disfarcada(self):
        with self.assertRaises(ValueError):
            preparar_avatar(imagem("PNG"), "foto.jpg")

    def test_rejeita_svg_e_codigo(self):
        for dados, nome in ((b'<svg onload="alert(1)"></svg>', "foto.png"), (b"codigo", "foto.webp"), (imagem(), "foto.svg")):
            with self.subTest(tipo=nome.rsplit(".", 1)[-1]), self.assertRaises(ValueError):
                preparar_avatar(dados, nome)

    def test_limite_bytes(self):
        with self.assertRaises(ValueError):
            preparar_avatar(b"x" * (MAX_UPLOAD + 1), "foto.png")
        with self.assertRaises(ValueError):
            preparar_avatar(b"", "foto.png")

    def test_limite_dimensoes(self):
        with self.assertRaises(ValueError):
            preparar_avatar(imagem(tamanho=(4097, 1)), "foto.png")

    def test_rejeita_animacao(self):
        saida = BytesIO()
        Image.new("RGB", (20, 20), "red").save(saida, format="WEBP", save_all=True,
            append_images=[Image.new("RGB", (20, 20), "blue")], duration=100, loop=0)
        with self.assertRaises(ValueError):
            preparar_avatar(saida.getvalue(), "foto.webp")

    def test_remove_metadados(self):
        origem = BytesIO()
        exif = Image.Exif()
        exif[270] = "METADADO_PRIVADO_SIMULADO"
        Image.new("RGB", (40, 60), "red").save(origem, format="JPEG", exif=exif)
        foto = preparar_avatar(origem.getvalue(), "foto.jpg")
        self.assertNotIn(b"METADADO_PRIVADO_SIMULADO", foto)
        with Image.open(BytesIO(foto)) as avatar:
            self.assertFalse(avatar.getexif())


class TestPreferencias(unittest.TestCase):
    def setUp(self):
        self.prefs = PreferenciasLocais(capacidade=2)

    def test_tres_temas_validos(self):
        for tema in ("Claro", "Escuro", "Automático"):
            self.assertEqual(self.prefs.tema("a", tema).tema, tema)
        with self.assertRaises(ValueError):
            self.prefs.tema("a", "outro")

    def test_isolamento_por_uid(self):
        self.prefs.tema("a", "Escuro")
        self.assertEqual(self.prefs.obter("b").tema, "Automático")

    def test_previa_substituicao_e_remocao(self):
        foto = preparar_avatar(imagem(), "foto.png")
        self.prefs.previa("a", "Ana", foto)
        self.assertIsNotNone(self.prefs.obter("a").avatar)
        anterior = self.prefs.obter("a").avatar
        azul = BytesIO()
        Image.new("RGB", (50,50), "blue").save(azul,format="WEBP")
        self.prefs.previa("a", "Ana", azul.getvalue())
        self.assertNotEqual(anterior, self.prefs.obter("a").avatar)
        self.prefs.previa("a", "Ana", None)
        self.assertIsNone(self.prefs.obter("a").avatar)
        self.assertEqual(self.prefs.obter("b").nome, "")

    def test_nome_e_identidade_obrigatorios(self):
        for nome in ("", "  ", "a" * 81, "Ana\n", "A\x00B", None):
            with self.subTest(caso=type(nome).__name__), self.assertRaises(ValueError):
                validar_nome(nome)
        self.assertEqual(validar_nome("  Ana Silva  "), "Ana Silva")
        with self.assertRaises(PermissionError):
            self.prefs.tema("", "Claro")

    def test_memoria_limitada(self):
        for uid in ("a", "b", "c"):
            self.prefs.tema(uid, "Escuro")
        self.assertEqual(self.prefs.obter("a").tema, "Automático")

    def test_reinicio_perde_previa_honestamente(self):
        self.prefs.previa("a", "Ana", None)
        self.assertEqual(PreferenciasLocais().obter("a").nome, "")

    def test_html_escapa_nome(self):
        html = usuario_html('<img src=x onerror="alert(1)">')
        self.assertNotIn('<img src=x', html)
        self.assertIn("&lt;img", html)


class TestIdentidade(unittest.TestCase):
    def setUp(self):
        self.store = SessoesServidor()
        self.cliente = MagicMock()
        self.cliente.auth.get_session.return_value = SimpleNamespace(access_token="SIMULADO")
        self.cliente.auth.get_user.return_value.user = SimpleNamespace(id="uid-a", email="a@exemplo.invalid", user_metadata={"preferred_name":"Ana"})
        self.cliente.rpc.return_value.execute.return_value.data = True
        self.sid = self.store.criar(self.cliente)

    def test_retorna_so_identidade_verificada(self):
        self.assertEqual(self.store.identidade(self.sid), {"id":"uid-a", "email":"a@exemplo.invalid", "nome":"Ana"})
        self.cliente.table.assert_not_called()

    def test_dono_negado_impede_perfil(self):
        self.cliente.rpc.return_value.execute.return_value.data = False
        with self.assertRaises(PermissionError):
            self.store.identidade(self.sid)
        self.assertFalse(self.store.existe(self.sid))

    def test_logout_impede_identidade(self):
        self.store.revogar(self.sid)
        with self.assertRaises(PermissionError):
            self.store.identidade(self.sid)


class TestPainelRedesign(unittest.TestCase):
    def setUp(self):
        self.prefs = PreferenciasLocais()
        self.store = SessoesServidor()
        self.cliente = MagicMock()
        self.cliente.auth.get_session.return_value = SimpleNamespace(access_token="SIMULADO")
        self.cliente.auth.get_user.return_value.user = SimpleNamespace(id="uid-qa", email="qa@example.invalid", user_metadata={})
        self.cliente.rpc.return_value.execute.return_value.data = True
        self.sid = self.store.criar(self.cliente)
        self.ctx = SimpleNamespace(headers={"x-botwhats-session":self.sid})
        for p in (patch("backend.session.st.context", self.ctx), patch("backend.session_runtime.sessoes", self.store),
                  patch("ui.pages.preferencias", self.prefs), patch("backend.auth.criar_cliente_supabase", side_effect=AssertionError("Remoto proibido"))):
            p.start()
            self.addCleanup(p.stop)
        self.app = self.nova()

    def nova(self):
        return AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=10)

    def test_todas_paginas_nos_dois_temas(self):
        self.app.run()
        for tema in ("Claro", "Escuro"):
            self.app.selectbox[0].set_value(tema).run()
            for pagina in self.app.radio[0].options:
                self.app.radio[0].set_value(pagina).run()
                self.assertFalse(self.app.exception)
                self.assertEqual(self.app.selectbox[0].value, tema)

    def test_tema_persiste_apos_f5(self):
        self.app.run().selectbox[0].set_value("Escuro").run()
        self.assertEqual(self.nova().run().selectbox[0].value, "Escuro")

    def test_outro_uid_nao_herda_tema_ou_nome(self):
        self.prefs.tema("uid-qa", "Escuro")
        self.prefs.previa("uid-qa", "Ana", None)
        outro = MagicMock()
        outro.auth.get_session.return_value = SimpleNamespace(access_token="SIMULADO")
        outro.auth.get_user.return_value.user = SimpleNamespace(id="uid-b",email="b@example.invalid",user_metadata={})
        outro.rpc.return_value.execute.return_value.data = True
        self.ctx.headers["x-botwhats-session"] = self.store.criar(outro)
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.selectbox[0].value, "Automático")
        self.assertEqual(self.prefs.obter("uid-b").nome, "")

    def test_perfil_email_nao_editavel_e_salvar_desabilitado(self):
        self.app.run().radio[0].set_value("Meu Perfil").run()
        email = next(e for e in self.app.text_input if e.label == "E-mail da conta autenticada")
        self.assertTrue(email.disabled)
        self.assertEqual(email.value, "qa@example.invalid")
        self.assertTrue(next(b for b in self.app.button if b.label == "Salvar alterações").disabled)

    def test_nome_previa_e_feedback_honesto(self):
        self.app.run().radio[0].set_value("Meu Perfil").run()
        next(e for e in self.app.text_input if e.label == "Nome de preferência").input("Ana")
        next(b for b in self.app.button if b.label == "Aplicar prévia local").click().run()
        self.assertEqual(self.prefs.obter("uid-qa").nome, "Ana")
        self.assertTrue(any("não foram salvos" in e.value for e in self.app.info))
        self.app.run()
        self.assertTrue(any("não foram salvos" in e.value for e in self.app.info))
        self.cliente.table.assert_not_called()

    def test_sem_permissao_nao_exibe_perfil(self):
        self.cliente.rpc.return_value.execute.return_value.data = False
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.radio), 0)

    def test_regra_continua_simulada(self):
        self.app.run().radio[0].set_value("Regras de Conversa").run()
        self.app.text_input[0].input("Olá")
        self.app.text_area[0].input("Bem-vindo")
        next(b for b in self.app.button if b.label == "Salvar Regra").click().run()
        self.assertTrue(any("Nenhuma regra foi gravada" in e.value for e in self.app.info))

    def test_qr_permanece_demonstrativo(self):
        self.app.run()
        next(b for b in self.app.button if b.label == "Gerar QR Code para Conectar").click().run()
        self.assertTrue(any("Nenhum QR Code foi gerado" in e.value for e in self.app.info))


def contraste(a, b):
    def luminancia(c):
        rgb = [int(c[i:i+2], 16)/255 for i in (1, 3, 5)]
        rgb = [x/12.92 if x <= .04045 else ((x+.055)/1.055)**2.4 for x in rgb]
        return sum(x*y for x,y in zip(rgb,(.2126,.7152,.0722)))
    x,y=sorted((luminancia(a),luminancia(b)))
    return (y+.05)/(x+.05)


class TestContraste(unittest.TestCase):
    def test_textos_e_botoes_aa(self):
        for fg, bg in (("#172925","#ffffff"),("#586e65","#f5f8f6"),("#b1c9be","#1d302d"),
                       ("#ffffff","#08794d"),("#062d2c","#5bdba3"),("#b7cec5","#062d2c")):
            with self.subTest(fg=fg,bg=bg):
                self.assertGreaterEqual(contraste(fg,bg),4.5)


class TestConfiguracaoASGI(unittest.TestCase):
    def test_configuracao_efetiva_mantem_protecoes(self):
        from backend.runtime_config import configurar_streamlit
        from streamlit import config
        configurar_streamlit("http://127.0.0.1:8501")
        self.assertIs(config.get_option("server.enableXsrfProtection"), True)
        self.assertIs(config.get_option("server.enableAgentApi"), False)
        self.assertEqual(config.get_option("server.corsAllowedOrigins"), ["http://127.0.0.1:8501"])
        self.assertEqual(config.get_option("client.toolbarMode"), "minimal")


if __name__ == "__main__":
    unittest.main()
