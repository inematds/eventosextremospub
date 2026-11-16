"""Regressões: indisponibilidade da fonte não pode virar ausência de boletim."""
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("fontes", Path(__file__).with_name("fontes_youtube.py"))
fontes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fontes)


class FontesTest(unittest.TestCase):
    def test_boletim_entre_muitos_conteudos_restritos(self):
        entries = [{"id": str(i), "title": "Membros | Sul (15/11/2026)"} for i in range(15)]
        entries += [
            {"id": "bom", "title": "Brasil | Chuva (15/11/2026)"},
            {"id": "fechado", "title": "Brasil | Chuva (15/11/2026)", "availability": "subscriber_only"},
            {"id": "enso", "title": "Enso | El Niño (15/11/2026)"},
        ]
        self.assertEqual(list(fontes.candidates("dia", {"entries": entries})),
                         [("bom", "15/11/2026", "Brasil | Chuva (15/11/2026)")])

    def test_erro_http_preservado_e_consulta_inconclusiva(self):
        with tempfile.TemporaryDirectory() as d:
            result = subprocess.CompletedProcess([], 1, "", "HTTP Error 429: Too Many Requests")
            with patch.object(fontes.subprocess, "run", return_value=result), patch.object(
                fontes.sys, "argv", ["fontes", "dia", d]
            ), patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(fontes.main(), 4)
            self.assertIn("429", (Path(d) / "youtube-erros.log").read_text())

    def test_consulta_valida_sem_boletim_nao_e_erro(self):
        with tempfile.TemporaryDirectory() as d:
            result = subprocess.CompletedProcess([], 0, json.dumps({"entries": [
                {"id": "outro", "title": "Enso | El Niño (15/11/2026)"}
            ]}), "")
            with patch.object(fontes.subprocess, "run", return_value=result), patch.object(
                fontes.sys, "argv", ["fontes", "dia", d]
            ):
                self.assertEqual(fontes.main(), 0)

    def test_previsao_sem_metadados_nao_e_video_ausente(self):
        with tempfile.TemporaryDirectory() as d:
            listing = subprocess.CompletedProcess([], 0, json.dumps({"entries": [
                {"id": "publico", "title": "Previsão"}
            ]}), "")
            failed = subprocess.CompletedProcess([], 1, "", "Sign in to confirm")
            with patch.object(fontes.subprocess, "run", side_effect=[listing, failed]), patch.object(
                fontes.sys, "argv", ["fontes", "previsao", d]
            ):
                self.assertEqual(fontes.main(), 4)

    def test_previsao_parcial_preserva_falha_do_video_mais_novo(self):
        with tempfile.TemporaryDirectory() as d:
            listing = subprocess.CompletedProcess([], 0, json.dumps({"entries": [
                {"id": "novo", "title": "Previsão nova"},
                {"id": "velho", "title": "Previsão antiga"},
            ]}), "")
            failed = subprocess.CompletedProcess([], 1, "", "HTTP 429")
            old = subprocess.CompletedProcess([], 0, json.dumps({
                "upload_date": "20261113", "title": "Previsão antiga", "availability": "public"
            }), "")
            with patch.object(fontes.subprocess, "run", side_effect=[listing, failed, old]), patch.object(
                fontes.sys, "argv", ["fontes", "previsao", d]
            ), patch("sys.stdout", new_callable=io.StringIO) as output:
                self.assertEqual(fontes.main(), 4)
                self.assertIn("velho|20261113", output.getvalue())


if __name__ == "__main__":
    unittest.main()
