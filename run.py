import sys
import os
import uvicorn

# Determine the repository root
repo_root = os.path.dirname(os.path.abspath(__file__))

# Add the 'src/' directory to Python's import path
src_dir = os.path.join(repo_root, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

if __name__ == "__main__":
    # Start the existing FastAPI application
    uvicorn.run("kestrel_returns.api:app", host="127.0.0.1", port=8000, reload=False)
