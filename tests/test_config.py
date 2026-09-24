import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

from config import Settings


class SettingsTests(unittest.TestCase):
    def test_defaults_match_current_demo_behavior(self):
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings(_env_file=None)

        self.assertEqual(settings.host, "127.0.0.1")
        self.assertEqual(settings.port, 0)
        self.assertEqual(settings.model_default, "multilingual")
        self.assertIsNone(settings.device)
        self.assertFalse(settings.preload)

    def test_reads_dotenv_values_and_uses_auto_device_when_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text(
                "# 中文注释\n"
                "LAYA_DEMO_HOST=127.0.0.2\n"
                "LAYA_DEMO_PORT=6410\n"
                "LAYA_DEMO_MODEL_DEFAULT=multilingual\n"
                "LAYA_DEMO_DEVICE=\n"
                "LAYA_DEMO_PRELOAD=true\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {}, clear=True):
                settings = Settings(_env_file=env_file)

        self.assertEqual(settings.host, "127.0.0.2")
        self.assertEqual(settings.port, 6410)
        self.assertEqual(settings.model_default, "multilingual")
        self.assertIsNone(settings.device)
        self.assertTrue(settings.preload)

    def test_process_environment_overrides_dotenv(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text("LAYA_DEMO_PORT=6410\n", encoding="utf-8")
            with patch.dict(
                os.environ, {"LAYA_DEMO_PORT": "6420"}, clear=True
            ):
                settings = Settings(_env_file=env_file)

        self.assertEqual(settings.port, 6420)

    def test_accepts_port_boundaries(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(Settings(_env_file=None, port=0).port, 0)
            self.assertEqual(Settings(_env_file=None, port=65535).port, 65535)

    def test_rejects_port_outside_range(self):
        with patch.dict(os.environ, {}, clear=True):
            for port in (-1, 65536):
                with self.subTest(port=port):
                    with self.assertRaises(ValidationError):
                        Settings(_env_file=None, port=port)


if __name__ == "__main__":
    unittest.main()
