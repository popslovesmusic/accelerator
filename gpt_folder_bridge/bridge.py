from pathlib import Path
from fastapi import FastAPI, HTTPException, Header

ROOT = Path(r"D:\projects\acellorator").resolve()
API_KEY = "change-this-long-random-key"

app = FastAPI(title="Local GPT Folder Bridge - Read Only")


def check_auth(authorization: str | None):
    expected = f"Bearer {API_KEY}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


def safe_path(relative_path: str) -> Path:
    target = (ROOT / relative_path).resolve()

    if not str(target).startswith(str(ROOT)):
        raise HTTPException(status_code=403, detail="Path escapes allowed folder")

    return target


@app.get("/health")
def health(authorization: str | None = Header(default=None)):
    check_auth(authorization)
    return {
        "status": "ok",
        "mode": "read_only",
        "root": str(ROOT),
    }


@app.get("/list")
def list_files(path: str = ".", authorization: str | None = Header(default=None)):
    check_auth(authorization)
    folder = safe_path(path)

    if not folder.exists():
        raise HTTPException(status_code=404, detail="Folder not found")

    if not folder.is_dir():
        raise HTTPException(status_code=400, detail="Path is not a folder")

    return {
        "path": str(folder.relative_to(ROOT)),
        "items": [
            {
                "name": item.name,
                "type": "folder" if item.is_dir() else "file",
            }
            for item in folder.iterdir()
        ],
    }


@app.get("/read")
def read_file(path: str, authorization: str | None = Header(default=None)):
    check_auth(authorization)
    file_path = safe_path(path)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Path is not a file")

    return {
        "path": str(file_path.relative_to(ROOT)),
        "content": file_path.read_text(encoding="utf-8", errors="replace"),
    }