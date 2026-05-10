import sys
import types


sys.modules.setdefault("requests", types.SimpleNamespace(get=None))
sys.modules.setdefault("PIL", types.SimpleNamespace(Image=types.SimpleNamespace()))
sys.modules.setdefault("tqdm", types.SimpleNamespace(trange=range))
