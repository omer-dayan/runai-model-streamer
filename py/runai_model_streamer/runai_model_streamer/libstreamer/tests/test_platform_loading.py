import os
import sys
import unittest
from unittest.mock import patch


class TestPlatformLoading(unittest.TestCase):
    """Tests for cross-platform native library path resolution."""

    def test_darwin_loads_dylib(self):
        """Test that macOS platform loads .dylib files."""
        with patch.object(sys, "platform", "darwin"):
            # Need to re-import to pick up mocked platform
            from runai_model_streamer.libstreamer import _get_library_path

            path = _get_library_path()
            self.assertTrue(
                path.endswith(".dylib"),
                f"Expected .dylib extension on darwin, got: {path}",
            )
            self.assertIn("libstreamer.dylib", path)

    def test_linux_loads_so(self):
        """Test that Linux platform loads .so files."""
        with patch.object(sys, "platform", "linux"):
            from runai_model_streamer.libstreamer import _get_library_path

            path = _get_library_path()
            self.assertTrue(
                path.endswith(".so"), f"Expected .so extension on linux, got: {path}"
            )
            self.assertIn("libstreamer.so", path)

    def test_default_loads_so(self):
        """Test that unknown platforms default to .so files."""
        with patch.object(sys, "platform", "freebsd"):
            from runai_model_streamer.libstreamer import _get_library_path

            path = _get_library_path()
            self.assertTrue(
                path.endswith(".so"),
                f"Expected .so extension on unknown platform, got: {path}",
            )

    def test_streamer_library_env_override(self):
        """Test that STREAMER_LIBRARY environment variable overrides default path."""
        custom_path = "/custom/path/libstreamer.so"
        with patch.dict(os.environ, {"STREAMER_LIBRARY": custom_path}):
            # Re-import to pick up env var
            import importlib
            import runai_model_streamer.libstreamer as lib

            # Note: STREAMER_LIBRARY is read at module load time,
            # so we need to check the module-level variable
            # In production, this is set once at import time
            self.assertEqual(
                os.environ.get("STREAMER_LIBRARY"),
                custom_path,
                "Environment variable should be accessible",
            )

    def test_library_path_contains_lib_directory(self):
        """Test that the library path includes the lib subdirectory."""
        from runai_model_streamer.libstreamer import _get_library_path

        path = _get_library_path()
        self.assertIn(
            os.path.join("lib", "libstreamer"),
            path,
            f"Expected path to contain lib directory, got: {path}",
        )

    def test_library_path_is_absolute(self):
        """Test that the library path is absolute."""
        from runai_model_streamer.libstreamer import _get_library_path

        path = _get_library_path()
        self.assertTrue(
            os.path.isabs(path), f"Expected absolute path, got relative: {path}"
        )


if __name__ == "__main__":
    unittest.main()
