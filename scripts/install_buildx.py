"""Project-local official Buildx binary, pinned to reviewed release metadata."""
import hashlib
import json
from pathlib import Path
import urllib.request
root=Path(__file__).resolve().parents[1]
metadata=json.loads((root/'notes/runs/buildx-release-metadata.json').read_text())
if metadata['release']!='v0.38.1':raise SystemExit('Review the release before changing this pin')
folder=root/'data/external/docker-buildx'/metadata['release'];folder.mkdir(parents=True,exist_ok=True)
files={}
for asset in metadata['assets']:
 name=asset['name']
 if name not in {'buildx-v0.38.1.linux-amd64','checksums.txt'}:raise ValueError('Unexpected release asset')
 if not asset['browser_download_url'].startswith('https://github.com/docker/buildx/releases/download/v0.38.1/'):
  raise ValueError('Unexpected official asset URL')
 target=folder/name/'content';target.parent.mkdir(exist_ok=True)
 if not target.exists():
  with urllib.request.urlopen(asset['browser_download_url'],timeout=60) as response:content=response.read(asset['size']+1)
  if len(content)!=asset['size']:raise ValueError('Release asset length mismatch')
  target.write_bytes(content)
 digest=hashlib.sha256(target.read_bytes()).hexdigest()
 if 'sha256:'+digest!=asset['digest']:raise ValueError('Official release asset digest mismatch')
 files[name]=(target,digest)
binary,digest=files['buildx-v0.38.1.linux-amd64']
checksums=files['checksums.txt'][0].read_text()
if not any(line.split() in ([digest,'buildx-v0.38.1.linux-amd64'],[digest,'*buildx-v0.38.1.linux-amd64']) for line in checksums.splitlines()):raise ValueError('Official checksums do not confirm binary')
binary.chmod(0o755)
config=root/'data/runtime/docker-client';plugins=config/'cli-plugins';plugins.mkdir(parents=True,exist_ok=True)
link=plugins/'docker-buildx'
if not link.exists():link.symlink_to(binary)
(config/'config.json').write_text(json.dumps({'cliPluginsExtraDirs':[str(plugins)]})+'\n')
print(json.dumps({'release':metadata['release'],'binary_sha256':digest,'docker_config':str(config),'installed_project_local':True}))
