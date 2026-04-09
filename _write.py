import os
import base64

files_b64 = {
'meta_agents/config/loaders.py': '',
'meta_agents/backends/base.py': '',
'meta_agents/models/memory.py': '',
'meta_agents/models/skills.py': '',
'meta_agents/utils/logging.py': '',
}

for path, content_b64 in files_b64.items():
    content = base64.b64decode(content_b64).decode("utf-8")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"Written: {path}")
