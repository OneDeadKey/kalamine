import ctypes
import os
import subprocess
import sys
from pathlib import Path
from shutil import move, rmtree
from stat import S_IREAD, S_IWUSR

import tomli

from .help import create_layout_content
from .layout import KeyboardLayout


class MsklcManager:
    def __init__(
        self,
        layout: "KeyboardLayout",
        msklc_dir: Path,
        working_dir: Path = Path(os.getcwd()),
        verbose: bool = False,
    ) -> None:
        self._layout = layout
        self._msklc_dir = msklc_dir
        self._verbose = verbose
        self._working_dir = working_dir

    # This need the klc file to be created first
    def create_c_files(self):
        """Call kbdutools to generate C files"""
        kbdutools = self._msklc_dir / Path("bin/i386/kbdutool.exe")
        cur = os.getcwd()
        os.chdir(self._working_dir)
        ret = subprocess.run(
            [kbdutools, "-u", "-s", self._layout.meta["name8"] + ".klc"],
            capture_output=not self._verbose,
        )
        os.chdir(cur)
        ret.check_returncode()

    # Check if the driver is already installed
    # as this will cause MSKLC to launch the GUI instead of creating the installer
    def _is_already_installed(self) -> bool:
        sys32 = Path(os.environ["WINDIR"]) / Path("System32")
        dll = sys32 / Path(f'{self._layout.meta["name8"]}.dll')
        return dll.exists()

    def build_msklc_installer(
        self,
    ) -> bool:
        name8 = self._layout.meta["name8"]

        if (self._working_dir / Path(name8)).exists():
            print(
                f"WARN: `{self._working_dir / Path(name8)}` already exists, "
                "assuming installer sits there."
            )
            return True

        if self._is_already_installed():
            print(
                "Error: layout already installed and "
                "installer package not found in the current directory.\n"
                "Either uninstall the layout manually, or put the installer "
                f"folder in the current directory: ({self._working_dir})"
            )
            return False

        # Create a dummy klc file to generate the installer.
        # The file must have a correct name to be reflected in the installer.
        dummy_toml = create_layout_content(
            self._layout.geometry, self._layout.has_altgr, self._layout.has_1dk
        )
        dummy_toml = dummy_toml.replace(
            "custom QWERTY layout", self._layout.meta["description"]
        )
        dummy_toml = dummy_toml.replace("qwerty-custom", self._layout.meta["name"])
        dummy_toml = dummy_toml.replace("custom", self._layout.meta["name8"])
        dummy_toml = dummy_toml.replace("nobody", self._layout.meta["author"])
        dummy_toml = dummy_toml.replace(
            "https://OneDeadKey.github.com/kalamine", self._layout.meta["url"]
        )
        dummy_toml = dummy_toml.replace("0.0.1", self._layout.meta["version"])
        dummy_toml = dummy_toml.replace('"us"', f'"{self._layout.meta["locale"]}"')

        dummy_layout = KeyboardLayout(tomli.loads(dummy_toml))
        dummy_klc = dummy_layout.klc
        klc_file = Path(self._working_dir) / Path(f'{self._layout.meta["name8"]}.klc')
        with klc_file.open("w", encoding="utf-16le", newline="\n") as file:
            file.write(dummy_klc)
        msklc = self._msklc_dir / Path("MSKLC.exe")
        subprocess.run([msklc, klc_file, "-build"], capture_output=not self._verbose)

        # move the installer from "My Documents" to current dir
        if sys.platform == "win32":  # let mypy know this is win32-specific
            CSIDL_PERSONAL = 5  # My Documents
            SHGFP_TYPE_CURRENT = 0  # Get current, not default value
            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(
                None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf
            )
            my_docs = Path(buf.value)
            installer = my_docs / Path(name8)

            if installer.exists():
                move(str(installer), str(self._working_dir / Path(name8)))

        return True

    def build_msklc_dll(
        self,
    ):
        name8 = self._layout.meta["name8"]
        prev = os.getcwd()
        os.chdir(self._working_dir)
        INST_DIR = self._working_dir / Path(name8)
        dll_dirs = ["i386", "amd64", "ia64", "wow64"]
        for dll_dir in dll_dirs:
            full_dir = INST_DIR / Path(dll_dir)
            if not full_dir.exists():
                raise Exception(f"{full_dir} doesn't exist")
            else:
                rmtree(full_dir)
                os.mkdir(full_dir)

        klc_file = self._working_dir / Path(f"{name8}.klc")

        # create correct klc
        with klc_file.open("w", encoding="utf-16le", newline="\n") as file:
            file.write(self._layout.klc)

        self.create_c_files()
        c_file = klc_file.with_suffix(".RC")
        with c_file.open("w", encoding="utf-16le", newline="\n") as file:
            file.write(self._layout.klc_rc)
        c_file = klc_file.with_suffix(".C")
        with c_file.open("w", encoding="utf-16le", newline="\n") as file:
            file.write(self._layout.klc_c)
        c_files = [".C", ".RC", ".H", ".DEF"]

        # Make files read-only to prevent MSKLC from overwriting them.
        for suffix in c_files:
            os.chmod(klc_file.with_suffix(suffix), S_IREAD)

        # build correct DLLs

        kbdutools = self._msklc_dir / Path("bin/i386/kbdutool.exe")
        dll = klc_file.with_suffix(".dll")

        for arch_flag, arch in [
            ("-x", "i386"),
            ("-m", "amd64"),
            ("-i", "ia64"),
            ("-o", "wow64"),
        ]:
            subprocess.run(
                [kbdutools, "-u", arch_flag, klc_file], capture_output=not self._verbose
            ).check_returncode()
            move(dll, INST_DIR / Path(arch))

        # Restore write permission
        for suffix in c_files:
            os.chmod(klc_file.with_suffix(suffix), S_IWUSR)
        os.chdir(prev)
