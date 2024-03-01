import ctypes
import os
import subprocess
import sys
import winreg
from pathlib import Path
from shutil import move, rmtree
from stat import S_IREAD, S_IWUSR

from progress.bar import ChargingBar

from .help import dummy_layout
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
        self._progress = ChargingBar(
            f"Creating MSKLC driver for `{layout.meta['name']}`", max=14
        )

    def create_c_files(self):
        """Call kbdutool on the KLC descriptor to generate C files."""

        kbdutool = self._msklc_dir / Path("bin/i386/kbdutool.exe")
        cur = os.getcwd()
        os.chdir(self._working_dir)
        ret = subprocess.run(
            [kbdutool, "-u", "-s", f"{self._layout.meta['name8']}.klc"],
            capture_output=not self._verbose,
        )
        os.chdir(cur)
        ret.check_returncode()

    def _is_already_installed(self) -> bool:
        """Check if the keyboard driver is already installed,
        which would cause MSKLC to launch the GUI instead of creating the installer."""

        # check if the DLL is present
        sys32 = Path(os.environ["WINDIR"]) / Path("System32")
        sysWow = Path(os.environ["WINDIR"]) / Path("SysWOW64")
        dll_name = f'{self._layout.meta["name8"]}.dll'
        dll_exists = (sys32 / dll_name).exists() or (sysWow / Path(dll_name)).exists()

        if dll_exists:
            print(f"Error: {dll_name} is already installed")
            return True

        if sys.platform != "win32":  # let mypy know this is win32-specific
            return False
        # check if the registry still has it
        # that can happen after a botch uninstall of the driver
        kbd_layouts_handle = winreg.OpenKeyEx(
            winreg.HKEY_LOCAL_MACHINE,
            "SYSTEM\\CurrentControlSet\\Control\\Keyboard Layouts",
        )
        # [0] is the number of sub keys
        for i in range(0, winreg.QueryInfoKey(kbd_layouts_handle)[0]):
            sub_key = winreg.EnumKey(kbd_layouts_handle, i)
            sub_handle = winreg.OpenKey(kbd_layouts_handle, sub_key)
            layout_file = winreg.QueryValueEx(sub_handle, "Layout File")[0]
            if layout_file == dll_name:
                print(
                    f"Error: The registry still have reference to `{dll_name}` in"
                    f"`HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Keyboard Layouts\\{sub_key}`"
                )
                return True
        return False

    def _create_dummy_layout(self) -> str:
        return dummy_layout(
            self._layout.geometry,
            self._layout.has_altgr,
            self._layout.has_1dk,
            self._layout.meta,
        ).klc

    def build_msklc_installer(self) -> bool:
        def installer_exists(installer: Path) -> bool:
            return (
                installer.exists()
                and installer.is_dir()
                and (installer / Path("setup.exe")).exists()
                and (installer / Path("amd64")).exists()
                and (installer / Path("i386")).exists()
                and (installer / Path("ia64")).exists()
                and (installer / Path("wow64")).exists()
            )

        name8 = self._layout.meta["name8"]
        installer_dir = self._working_dir / Path(name8)
        if installer_exists(installer_dir):
            self._progress.next(4)
            return True

        if self._is_already_installed():
            self._progress.finish()
            print(
                "Error: layout already installed and "
                "installer package not found in the current directory.\n"
                "Either uninstall the layout manually, or put the installer "
                f"folder in the current directory: ({self._working_dir})"
            )
            return False
        self._progress.message = "Creating installer package"
        self._progress.next()
        # Create a dummy klc file to generate the installer.
        # The file must have a correct name to be reflected in the installer.
        dummy_klc = self._create_dummy_layout()
        klc_file = Path(self._working_dir) / Path(f"{name8}.klc")
        with klc_file.open("w", encoding="utf-16le", newline="\r\n") as file:
            file.write(dummy_klc)

        self._progress.next()
        msklc = self._msklc_dir / Path("MSKLC.exe")
        result = subprocess.run(
            [msklc, klc_file, "-build"], capture_output=not self._verbose, text=True
        )

        self._progress.next()
        # move the installer from "My Documents" to current dir
        if sys.platform != "win32":  # let mypy know this is win32-specific
            return False

        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(
            None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf
        )
        my_docs = Path(buf.value)
        installer = my_docs / Path(name8)

        self._progress.next()
        if not installer_exists(installer):
            self._progress.finish()
            print(f"MSKLC Exit code: {result.returncode}")
            print(result.stdout)
            print(result.stderr)
            print("Error: installer was not created.")
            return False

        move(str(installer), str(self._working_dir / Path(name8)))
        return True

    def build_msklc_dll(self) -> bool:
        self._progress.next()
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

        self._progress.next()
        # create correct klc
        klc_file = self._working_dir / Path(f"{name8}.klc")
        with klc_file.open("w", encoding="utf-16le", newline="\r\n") as file:
            try:
                file.write(self._layout.klc)
            except ValueError as err:
                print(f"ERROR: {err}")
                return False

        self._progress.next()
        self.create_c_files()

        self._progress.next()
        rc_file = klc_file.with_suffix(".RC")
        with rc_file.open("w", encoding="utf-16le", newline="\r\n") as file:
            file.write(self._layout.klc_rc)

        self._progress.next()
        c_file = klc_file.with_suffix(".C")
        with c_file.open("w", encoding="utf-16le", newline="\r\n") as file:
            file.write(self._layout.klc_c)

        c_files = [".C", ".RC", ".H", ".DEF"]

        self._progress.next()
        # Make files read-only to prevent MSKLC from overwriting them.
        for suffix in c_files:
            os.chmod(klc_file.with_suffix(suffix), S_IREAD)

        # build correct DLLs

        kbdutool = self._msklc_dir / Path("bin/i386/kbdutool.exe")
        dll = klc_file.with_suffix(".dll")
        self._progress.message = "Creating driver DLLs"
        for arch_flag, arch in [
            ("-x", "i386"),
            ("-m", "amd64"),
            ("-i", "ia64"),
            ("-o", "wow64"),
        ]:
            self._progress.next()
            result = subprocess.run(
                [kbdutool, "-u", arch_flag, klc_file],
                text=True,
                capture_output=not self._verbose,
            )
            if result.returncode == 0:
                move(str(dll), str(INST_DIR / Path(arch)))
            else:
                # Restore write permission
                for suffix in c_files:
                    os.chmod(klc_file.with_suffix(suffix), S_IWUSR)
                self._progress.finish()
                print(f"Error while creating DLL for arch {arch}:")
                print(result.stdout)
                print(result.stderr)
                return False

        # Restore write permission
        for suffix in c_files:
            os.chmod(klc_file.with_suffix(suffix), S_IWUSR)
        os.chdir(prev)
        self._progress.finish()
        return True
