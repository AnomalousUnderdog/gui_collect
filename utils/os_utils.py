import os
import platform
import subprocess
from pathlib import Path


def open_file_browser(path):
    if isinstance(path, str):
        path = Path(path)
    elif not isinstance(path, Path):
        raise TypeError(f'Argument must either be str or pathlib.Path, not {type(path).__name__}')

    if not path.exists():
        print(f'Trying to open path in {get_file_browser_name()}, but the path does not exist: "{path}"')
        return

    abs_path = str(path.resolve())

    if platform.system() == "Windows":
        abs_path = abs_path.replace('/', '\\') # Windows File Explorer doesn't like forward slashes

        # Attempt to get the full path since that is what Python recommends
        # (https://docs.python.org/3/library/subprocess.html#popen-constructor)
        explorer_path = os.path.join(os.getenv('WINDIR'), 'explorer.exe')

        if not os.path.isfile(explorer_path):
            explorer_path = 'explorer'

        if path.is_file():
            subprocess.Popen(f'{explorer_path} /select,"{abs_path}"')
        else:
            subprocess.Popen(f'{explorer_path} /root,"{abs_path}"')

    elif platform.system() == "Darwin": # macOS
        if path.is_file():
            # -R means reveal the file instead of opening it
            subprocess.Popen(["open", "-R", abs_path])
        else:
            subprocess.Popen(["open", abs_path])

    elif platform.system() == "Linux":
        # Note: xdg-open only works as expected if given a folder.
        # If given a path to a file, xdg-open will open that file with the associated program (like opening Notepad if given the path to a txt file, in Windows).
        # So we use dbus-send instead, if path is a file.
        try:
            fallback_to_xdg_open = False
            if path.is_file():
                # ridiculously long arg is from https://askubuntu.com/a/1424380
                dbus_send_command = f'dbus-send --print-reply --dest=org.freedesktop.FileManager1 /org/freedesktop/FileManager1 org.freedesktop.FileManager1.ShowItems array:string:"file://{abs_path}" string:""';
                subprocess.run(dbus_send_command, shell=True)
        except OSError as e:
            print(f"dbus-send failed: {repr(e)}")
            fallback_to_xdg_open = True
        try:
            if not path.is_file() or fallback_to_xdg_open:
                subprocess.Popen(["xdg-open", abs_path])
        except OSError as e:
            print(f"Can't open File Browser to open path: \"{abs_path}\" xdg-open failed: {repr(e)}")
    else:
        print(f"Unrecognized operating system for opening a path in File Browser: {platform.system()}")

def get_file_browser_name():
    if platform.system() == "Windows":
        return "File Explorer"
    elif platform.system() == "Darwin": # macOS
        return "Finder"
    else: # Linux
        return "File Browser"

