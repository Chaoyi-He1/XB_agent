"""Run the Memristor Crossbar Design Assistant (FastAPI + chat UI).

Server listens on all interfaces (0.0.0.0) so other PCs on the network can open the chat.
Override with env: HOST, PORT (e.g. HOST=0.0.0.0 PORT=8000).
"""

import os
import uvicorn

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=True,
    )
