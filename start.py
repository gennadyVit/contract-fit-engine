import os, sys, glob

pythonpath = os.environ.get('PYTHONPATH', '')
print(f"PYTHONPATH={pythonpath}", flush=True)

antenv_root = next(
    (p[:p.index('/lib/python')] for p in pythonpath.split(':') if 'antenv' in p and '/lib/python' in p),
    None
)
print(f"antenv_root={antenv_root}", flush=True)

if antenv_root:
    bin_dir = f"{antenv_root}/bin"
    print(f"bin_dir contents: {os.listdir(bin_dir) if os.path.exists(bin_dir) else 'MISSING'}", flush=True)

# Search for streamlit binary anywhere under /tmp
hits = glob.glob('/tmp/**/streamlit', recursive=True)
print(f"streamlit binaries found: {hits}", flush=True)

if hits:
    streamlit_bin = hits[0]
    os.execv(streamlit_bin, [
        streamlit_bin, "run", "streamlit/app.py",
        "--server.port", "8000",
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ])
else:
    print("ERROR: no streamlit binary found anywhere", flush=True)
    sys.exit(1)
