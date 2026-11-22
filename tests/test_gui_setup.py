import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from icp.gui import setup


class SetupTests(unittest.TestCase):
    def test_install_command_uses_the_distribution_package_manager(self):
        with mock.patch("shutil.which", side_effect=lambda name: "/usr/bin/dnf" if name == "dnf" else None):
            self.assertEqual(setup.install_command(["wine", "mingw"]), "sudo dnf install wine mingw64-gcc-c++")
        with mock.patch("shutil.which", side_effect=lambda name: "/usr/bin/apt" if name == "apt" else None):
            self.assertEqual(setup.install_command(["cmake"]), "sudo apt install cmake")
        self.assertEqual(setup.install_command([]), "")

    def test_missing_tools_lists_what_is_not_installed(self):
        with mock.patch("shutil.which", side_effect=lambda name: None if name in ("cmake",) else "/usr/bin/" + name):
            self.assertEqual(setup.missing_tools(), ["cmake"])

    def test_icloud_folder_needs_all_three_libraries(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            for dll in setup.REQUIRED_DLLS[:2]:
                (folder / dll).write_bytes(b"x")
            self.assertFalse(setup.is_icloud_dir(folder))
            (folder / setup.REQUIRED_DLLS[2]).write_bytes(b"x")
            self.assertTrue(setup.is_icloud_dir(folder))

    def test_wine_paths_use_the_z_drive(self):
        self.assertEqual(setup.wine_path(Path("/home/a/icloud")), "Z:\\home\\a\\icloud")

    def test_installer_refuses_an_unreviewed_checkout(self):
        reports = []
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {"XDG_DATA_HOME": tmp}):
            source = Path(tmp) / "source"
            source.mkdir()
            for dll in setup.REQUIRED_DLLS:
                (source / dll).write_bytes(b"x")
            installer = setup.Installer(str(source), lambda kind, text: reports.append((kind, text)))
            (setup.tool_dir() / ".git").mkdir(parents=True)

            def fake_run(cmd, **kwargs):
                return mock.Mock(stdout="0" * 40 + "\n", returncode=0)

            with mock.patch.object(installer, "_run_cmd"), mock.patch("subprocess.run", fake_run):
                installer._run()
        self.assertEqual(reports[-1][0], "error")
        self.assertIn("reviewed version", reports[-1][1])
        self.assertNotIn(("step", "build"), reports)



class DesktopIntegrationTests(unittest.TestCase):
    def test_appimage_is_copied_and_added_to_the_menu(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "download.AppImage"
            image.write_bytes(b"\x7fELF")
            icon = Path(tmp) / "icon.svg"
            icon.write_text("<svg/>")
            env = {"APPIMAGE": str(image), "XDG_DATA_HOME": str(Path(tmp) / "share"), "HOME": tmp}
            with mock.patch.dict(os.environ, env), mock.patch("pathlib.Path.home", return_value=Path(tmp)):
                target = Path(setup.integrate(icon))
                entry = setup.desktop_entry().read_text()
                self.assertTrue(target.is_file() and os.access(target, os.X_OK))
                self.assertIn(f'Exec="{target}"', entry)
                self.assertTrue(setup.is_integrated())
                setup.unintegrate()
                self.assertFalse(setup.is_integrated())


if __name__ == "__main__":
    unittest.main()
