from sc_companion.config import load_config, save_brain_default

def test_defaults_when_no_file(tmp_path, monkeypatch):
    monkeypatch.setenv("MINIMAX_API_KEY", "mm-test")
    monkeypatch.setenv("DEEPGRAM_API_KEY", "dg-test")
    cfg = load_config(tmp_path / "missing.toml")
    assert cfg.hotkey.key == "home"
    assert cfg.brain.model == "MiniMax-M2.7"
    assert cfg.brain.history_turns == 12
    assert cfg.overlay.opacity == 0.85
    assert cfg.secrets.minimax_api_key == "mm-test"
    assert cfg.secrets.deepgram_api_key == "dg-test"

def test_overrides_from_toml(tmp_path, monkeypatch):
    monkeypatch.setenv("MINIMAX_API_KEY", "")
    monkeypatch.setenv("DEEPGRAM_API_KEY", "")
    p = tmp_path / "c.toml"
    p.write_text(
        '[hotkey]\nkey = "f8"\n'
        '[brain]\nhistory_turns = 12\n'
        '[overlay]\nposition = "top-left"\n'
    )
    cfg = load_config(p)
    assert cfg.hotkey.key == "f8"
    assert cfg.brain.history_turns == 12
    assert cfg.overlay.position == "top-left"
    assert cfg.brain.model == "MiniMax-M2.7"


def test_save_brain_default_creates_file_when_missing(tmp_path):
    p = tmp_path / "config.toml"
    save_brain_default("minimax", path=p)
    assert p.read_text(encoding="utf-8") == '[brain]\ndefault = "minimax"\n'


def test_save_brain_default_creates_parent_dir(tmp_path):
    p = tmp_path / "nested" / "deep" / "config.toml"
    save_brain_default("openai", path=p)
    assert load_config(p).brain.default == "openai"


def test_save_brain_default_replaces_existing_default(tmp_path):
    p = tmp_path / "config.toml"
    p.write_text(
        '[brain]\n'
        'default = "openai"\n'
        'history_turns = 8\n'
        '[overlay]\nposition = "top-left"\n',
        encoding="utf-8",
    )
    save_brain_default("minimax", path=p)
    cfg = load_config(p)
    assert cfg.brain.default == "minimax"
    # Other keys preserved
    assert cfg.brain.history_turns == 8
    assert cfg.overlay.position == "top-left"


def test_save_brain_default_appends_when_section_missing(tmp_path):
    p = tmp_path / "config.toml"
    p.write_text(
        '[hotkey]\nkey = "f8"\n[overlay]\nopacity = 0.5\n',
        encoding="utf-8",
    )
    save_brain_default("openai_web", path=p)
    cfg = load_config(p)
    assert cfg.brain.default == "openai_web"
    assert cfg.hotkey.key == "f8"
    assert cfg.overlay.opacity == 0.5


def test_save_brain_default_inserts_when_section_empty(tmp_path):
    p = tmp_path / "config.toml"
    p.write_text(
        '[brain]\n[overlay]\nposition = "top-left"\n',
        encoding="utf-8",
    )
    save_brain_default("minimax", path=p)
    cfg = load_config(p)
    assert cfg.brain.default == "minimax"
    assert cfg.overlay.position == "top-left"


def test_save_brain_default_preserves_comments(tmp_path):
    p = tmp_path / "config.toml"
    original = (
        '# my custom config\n'
        '[brain]\n'
        '# brain settings\n'
        'default = "openai"\n'
        'history_turns = 4\n'
    )
    p.write_text(original, encoding="utf-8")
    save_brain_default("minimax", path=p)
    text = p.read_text(encoding="utf-8")
    assert '# my custom config' in text
    assert '# brain settings' in text
    assert 'default = "minimax"' in text
    assert 'history_turns = 4' in text
