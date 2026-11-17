"""set_key.py writes the key into .env without ever printing it. No real key is used."""

import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import set_key

FAKE = "test-key-" + "x" * 30


class SetKeyTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.folder = Path(directory.name)
        self.env = self.folder / ".env"
        self.template = self.folder / ".env.example"

    def read(self):
        return self.env.read_text(encoding="utf-8")

    def test_replaces_an_existing_line_and_keeps_everything_else(self):
        self.env.write_text("A=1\nLLM_API_KEY=old\nB=2\n", encoding="utf-8")
        set_key.set_key(self.env, FAKE)
        self.assertEqual(self.read(), f"A=1\nLLM_API_KEY={FAKE}\nB=2\n")

    def test_activates_a_commented_line_in_place(self):
        self.env.write_text("A=1\n# LLM_API_KEY=\nB=2\n", encoding="utf-8")
        set_key.set_key(self.env, FAKE)
        self.assertEqual(self.read(), f"A=1\nLLM_API_KEY={FAKE}\nB=2\n")

    def test_appends_when_there_is_no_line_at_all(self):
        self.env.write_text("A=1", encoding="utf-8")
        set_key.set_key(self.env, FAKE)
        self.assertEqual(self.read(), f"A=1\nLLM_API_KEY={FAKE}\n")

    def test_creates_the_file_from_the_template(self):
        self.template.write_text("A=1\n# LLM_API_KEY=\n", encoding="utf-8")
        set_key.set_key(self.env, FAKE, self.template)
        self.assertEqual(self.read(), f"A=1\nLLM_API_KEY={FAKE}\n")
        self.assertEqual(self.template.read_text(encoding="utf-8"), "A=1\n# LLM_API_KEY=\n")

    def test_creates_the_file_without_a_template(self):
        set_key.set_key(self.env, FAKE)
        self.assertEqual(self.read(), f"LLM_API_KEY={FAKE}\n")

    def test_keeps_windows_line_endings(self):
        self.env.write_bytes(b"A=1\r\nLLM_API_KEY=\r\n")
        set_key.set_key(self.env, FAKE)
        self.assertEqual(self.env.read_bytes(), f"A=1\r\nLLM_API_KEY={FAKE}\r\n".encode())

    def test_leaves_no_temporary_file_behind(self):
        set_key.set_key(self.env, FAKE)
        self.assertEqual(os.listdir(self.folder), [".env"])

    def test_a_byte_order_mark_is_not_carried_over(self):
        self.env.write_bytes(b"\xef\xbb\xbfA=1\nLLM_API_KEY=\n")
        set_key.set_key(self.env, FAKE)
        self.assertEqual(self.env.read_bytes(), f"A=1\nLLM_API_KEY={FAKE}\n".encode())

    def test_clean_strips_quotes_and_refuses_junk(self):
        self.assertEqual(set_key.clean(f'  "{FAKE}"\n'), FAKE)
        for bad in ("", "   ", "short", "two words " + "x" * 30):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                set_key.clean(bad)

    def test_the_provider_is_read_back_like_the_engine_defaults_it(self):
        self.env.write_text("DAALE_LIVE_PROVIDER=Generic\n", encoding="utf-8")
        self.assertEqual(set_key.configured_provider(self.env), "generic")
        self.assertEqual(set_key.configured_provider(self.folder / "missing"), "openrouter")

    def run_main(self, tty=True, typed=FAKE):
        stdin = mock.Mock()
        stdin.isatty.return_value = tty
        output = io.StringIO()
        with mock.patch.object(set_key, "ROOT", self.folder), \
                mock.patch("set_key.sys.stdin", stdin), \
                mock.patch("set_key.getpass.getpass", return_value=typed) as ask, \
                contextlib.redirect_stdout(output):
            code = set_key.main()
        return code, output.getvalue(), ask

    def test_main_saves_the_key_and_never_prints_it(self):
        code, output, _ = self.run_main()
        self.assertEqual(code, 0)
        self.assertNotIn(FAKE, output)
        self.assertIn(f"LLM_API_KEY={FAKE}", self.read())

    def test_main_refuses_when_the_input_cannot_be_hidden(self):
        code, _, ask = self.run_main(tty=False)
        self.assertEqual(code, 2)
        ask.assert_not_called()
        self.assertFalse(self.env.exists())

    def test_main_does_not_save_a_bad_entry(self):
        code, output, _ = self.run_main(typed="short")
        self.assertEqual(code, 1)
        self.assertIn("Not saved", output)
        self.assertFalse(self.env.exists())


if __name__ == "__main__":
    unittest.main()
