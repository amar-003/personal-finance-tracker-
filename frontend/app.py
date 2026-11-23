"""Launch the custom browser dashboard and its local API."""

import uvicorn


if __name__ == "__main__":
    uvicorn.run("backend.src.main:app", host="127.0.0.1", port=8000)
