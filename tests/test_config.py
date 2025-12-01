import pytest
from src.config import load_config, detect_live_flag
from pathlib import Path
import json

def test_detect_live_flag():
    assert detect_live_flag(["--live"]) is True
    assert detect_live_flag(["-l"]) is True
    assert detect_live_flag([]) is False
    assert detect_live_flag(["other"]) is False

# tests/test_config.py
def test_load_config(tmp_path, monkeypatch):
    config_content = {
        "accounts": {"demo": [], "live": {}},
        "mt5": {"path": "C:/fake/terminal64.exe"},
        "server": {"host": "0.0.0.0", "port": 9999},
        "log_level": "INFO",
        "auth": {"enabled": False, "api_keys": []}
    }

    # Write the config files directly into the temp folder
    (tmp_path / "config.dev.json").write_text(json.dumps(config_content))
    (tmp_path / "config.live.json").write_text(json.dumps(config_content))

    # Make src.config.__file__ point to a fake file inside tmp_path
    fake_config_py = tmp_path / "src" / "config.py"
    fake_config_py.parent.mkdir()
    fake_config_py.touch()
    monkeypatch.setattr("src.config.__file__", str(fake_config_py))

    # Now load_config will resolve Path(__file__).parent.parent → tmp_path
    cfg_dev = load_config(use_live=False)
    cfg_live = load_config(use_live=True)

    assert cfg_dev["server"]["port"] == 9999
    assert cfg_live["server"]["port"] == 9999
    assert "accounts" in cfg_dev
    assert "mt5" in cfg_dev

    # Invalid config
    (tmp_path / "config.dev.json").write_text('{"no_accounts": {}}')
    with pytest.raises(KeyError):
        load_config(use_live=False)

    # File not found
    (tmp_path / "config.dev.json").unlink()
    with pytest.raises(FileNotFoundError):
        load_config(use_live=False)