"""Run on Windows: python build.py [--video path.mp4]."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from media import encrypt


def main():
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video', type=Path, default=root / 'bad-apple.mp4')
    args = parser.parse_args()
    if sys.platform != 'win32':
        parser.error('Gere o .exe no Windows; o PyInstaller não faz compilação cruzada.')
    if not args.video.is_file():
        parser.error('Adicione bad-apple.mp4 ou informe --video caminho.mp4.')
    with tempfile.TemporaryDirectory(prefix='pcdiagnostic-build-') as directory:
        work = Path(directory)
        key = AESGCM.generate_key(bit_length=256)
        (work / 'media.bin').write_bytes(encrypt(args.video.read_bytes(), key))
        (work / 'media_key.py').write_text(f'KEY = {key!r}\n', encoding='utf-8')
        subprocess.run([
            sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
            '--onefile', '--windowed', '--name', 'PcDiagnostic',
            '--distpath', str(root / 'dist'), '--workpath', str(work / 'work'),
            '--specpath', str(work), '--paths', str(work),
            '--hidden-import', 'media_key',
            '--add-data', str(work / 'media.bin') + os.pathsep + '.',
            str(root / 'app.py'),
        ], cwd=root, check=True)
    print('Pronto:', root / 'dist' / 'PcDiagnostic.exe')


if __name__ == '__main__':
    main()
