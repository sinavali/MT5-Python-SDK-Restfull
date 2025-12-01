import pytest
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import build_app
from src.config import load_config
from src.services.mt5_service import MT5Manager

@pytest.fixture
def mock_config():
    return {
        "accounts": {
            "demo": [{"login": 123, "password": "pass", "server": "server"}]
        },
        "mt5": {"path": "/fake/path"},
        "server": {"host": "127.0.0.1", "port": 8000},
        "log_level": "INFO",
        "auth": {"enabled": False, "api_keys": []}
    }

@pytest.fixture
def mock_mt5():
    with patch("src.services.mt5_service.mt5") as mock:
        mock.initialize.return_value = True
        mock.last_error.return_value = None
        mock.symbol_info.return_value = MagicMock(point=0.0001, visible=True)
        mock.symbol_select.return_value = True
        mock.symbol_info_tick.return_value = MagicMock(ask=1.1000, bid=1.0990)
        mock.TRADE_RETCODE_DONE = 10009
        mock.ORDER_TYPE_BUY = 0
        mock.ORDER_TYPE_SELL = 1
        mock.ORDER_TYPE_BUY_LIMIT = 2
        mock.ORDER_TYPE_SELL_LIMIT = 3
        mock.TRADE_ACTION_DEAL = 0
        mock.TRADE_ACTION_PENDING = 1
        mock.TRADE_ACTION_MODIFY = 5
        mock.TRADE_ACTION_REMOVE = 6
        mock.ORDER_FILLING_RETURN = 2
        mock.ORDER_TIME_GTC = 0
        yield mock

@pytest.fixture
def app(mock_config):
    return build_app(mock_config)

@pytest.fixture
def client(app):
    from fastapi.testclient import TestClient
    return TestClient(app)