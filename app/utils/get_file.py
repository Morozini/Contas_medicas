from pathlib import Path


def get_latest_file(folder: Path, extension: str):
    files = list(folder.glob(f'*.{extension}'))
    if not files:
        raise FileNotFoundError(f"Nenhum arquivo .{extension} encontrado em {folder}")
    return max(files, key=lambda f: f.stat().st_mtime)