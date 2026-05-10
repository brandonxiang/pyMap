import importlib.util
import os
import sys
import tempfile
import types
import unittest
from unittest import mock


def load_pymap():
    sys.modules.setdefault("requests", types.SimpleNamespace(get=None))
    sys.modules.setdefault("PIL", types.SimpleNamespace(Image=types.SimpleNamespace()))
    sys.modules.setdefault("tqdm", types.SimpleNamespace(trange=range))
    module_path = os.path.join(os.path.dirname(__file__), "..", "pyMap.py")
    spec = importlib.util.spec_from_file_location("pyMap", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["pyMap"] = module
    spec.loader.exec_module(module)
    return module


class PyMapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pymap = load_pymap()

    def test_latlng2tilenum_converts_coordinates(self):
        self.assertEqual(self.pymap.latlng2tilenum(0, 0, 1), (1, 1))
        self.assertEqual(self.pymap.latlng2tilenum(85.0511, -180, 0), (0, 0))

    def test_getname_uses_known_maptype_or_output_for_custom_url(self):
        self.assertEqual(self.pymap.getname("custom", "gaode"), "gaode")
        self.assertEqual(
            self.pymap.getname("custom", "https://example.com/{z}/{x}/{y}.png"),
            "custom",
        )

    def test_process_latlng_validates_and_delegates_to_tilenum(self):
        with mock.patch.object(self.pymap, "process_tilenum") as process_tilenum:
            self.pymap.process_latlng(
                north="1",
                west="-1",
                south="0",
                east="0",
                zoom="1",
                output="out",
                maptype="gaode",
            )

        process_tilenum.assert_called_once_with(0, 1, 0, 1, 1, "out", "gaode")

    def test_process_latlng_rejects_invalid_bounds(self):
        with self.assertRaises(AssertionError):
            self.pymap.process_latlng(0, 1, 1, 0, 1)

    def test_process_tilenum_downloads_then_mosaics_with_resolved_name(self):
        with (
            mock.patch.object(self.pymap, "download") as download,
            mock.patch.object(self.pymap, "_mosaic") as mosaic,
        ):
            self.pymap.process_tilenum(1, 2, 3, 4, 5, "out", "gaode")

        download.assert_called_once_with(1, 2, 3, 4, 5, "gaode", "gaode")
        mosaic.assert_called_once_with(1, 2, 3, 4, 5, "out", "gaode")

    def test_process_tilenum_rejects_reversed_ranges(self):
        with self.assertRaises(AssertionError):
            self.pymap.process_tilenum(2, 1, 3, 4, 5)

        with self.assertRaises(AssertionError):
            self.pymap.process_tilenum(1, 2, 4, 3, 5)

    def test_download_skips_existing_tiles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                os.makedirs("./tiles/cache/1/2", exist_ok=True)
                with open("./tiles/cache/1/2/3.png", "wb") as tile:
                    tile.write(b"cached")

                with mock.patch.object(self.pymap, "_download") as download:
                    self.pymap.download(2, 2, 3, 4, 1, "cache", "gaode")

                download.assert_called_once_with(2, 4, 1, "cache", "gaode")
            finally:
                os.chdir(old_cwd)

    def test_download_writes_successful_response_chunks(self):
        response = mock.Mock()
        response.status_code = 200
        response.iter_content.return_value = [b"abc", b"", b"def"]

        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                with mock.patch.object(self.pymap.requests, "get", return_value=response):
                    self.pymap._download(1, 2, 3, "cache", "gaode")

                with open("./tiles/cache/3/1/2.png", "rb") as tile:
                    self.assertEqual(tile.read(), b"abcdef")
            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
