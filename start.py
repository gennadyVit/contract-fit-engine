import os, sys

pythonpath = os.environ.get('PYTHONPATH', '')
antenv_root = next(
    (p[:p.index('/lib/python')] for p in pythonpath.split(':') if 'antenv' in p and '/lib/python' in p),
    None
)

if antenv_root:
    streamlit_bin = f"{antenv_root}/bin/streamlit"
    os.execv(streamlit_bin, [
        streamlit_bin, "run", "streamlit/app.py",
        "--server.port", "8000",
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ])
else:
    print(f"ERROR: could not find antenv in PYTHONPATH={pythonpath}", flush=True)
    sys.exit(1)
