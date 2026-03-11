"""Helper script to mirror the Receita Federal CNPJ open data site.

Usage (in workspace root):

    python download_rfb_data.py [--dest DIR]

This will execute the equivalent of:

    wget --mirror --no-parent https://dadosabertos.rfb.gov.br/CNPJ/ -P <DIR>

The mirror contains enormes volume de arquivos (mais de 40 GB comprimidos,
~550 GB descompactados), portanto certifique-se de ter espaço e banda.

O comando requer que o utilitário **wget** esteja disponível no PATH. No
Windows pode ser instalado via Chocolatey, WSL, Git Bash etc. Alternativamente
use PowerShell/Invoke-WebRequest manual.

O script apenas invoca o processo e imprime status; não faz parsing dos dados.
"""

import argparse
import subprocess
import sys


def mirror_cnpj(dest_dir=None):
    """Run wget mirror command.

    :param dest_dir: optional base directory where the mirror will be created.
    :return: exit code of wget
    """
    cmd = ["wget", "--mirror", "--no-parent", "https://dadosabertos.rfb.gov.br/CNPJ/"]
    if dest_dir:
        cmd.extend(["-P", dest_dir])
    try:
        print("Executing:", " ".join(cmd))
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        print("wget command not found. Please install wget before running this script.")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Mirror Receita Federal CNPJ open data site using wget.")
    parser.add_argument("--dest", "-d", help="Destination directory for the mirror")
    args = parser.parse_args()

    code = mirror_cnpj(args.dest)
    sys.exit(code)


if __name__ == "__main__":
    main()
