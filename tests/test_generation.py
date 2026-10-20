from types import SimpleNamespace
import pytest
pytest.importorskip('deepagents')
from svh.generation import apply_edits
from svh.browser_runner import allowed_source


def test_source_transfer_ignores_agent_git_and_restricts_paths():
    class Backend:
        def download_files(self,paths):return [SimpleNamespace(error=None,content=b'function actual() { return 1; }')]
    assert apply_edits(Backend(),[{'path':'lib/a.js','old':'return 1','new':'return 2'}])=={'lib/a.js':b'function actual() { return 2; }'}
    for path in ['../lib/a.js','lib/../../runner.js','test/check.js','/workspace/lib/a.js','lib/a.json']:
        with pytest.raises(ValueError):allowed_source({path:b'bad'})
    with pytest.raises(ValueError):apply_edits(Backend(),[{'path':'lib/a.js','old':'missing','new':'changed'}])
    with pytest.raises(ValueError):apply_edits(Backend(),[])
