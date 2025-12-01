import pytest
from src.services.mt5_service import MT5Manager
from unittest.mock import patch, MagicMock
from collections import namedtuple

@pytest.fixture
def manager():
    return MT5Manager()

def test_initialize_success(manager, mock_mt5):
    account_cfg = {"login": 123, "password": "pass", "server": "server"}
    assert manager.initialize(account_cfg, "/path")
    assert manager._initialized
    mock_mt5.initialize.assert_called_with(path="/path", login=123, password="pass", server="server", timeout=5000)

def test_initialize_failure(manager, mock_mt5):
    mock_mt5.initialize.return_value = False
    account_cfg = {"login": 123, "password": "pass", "server": "server"}
    assert not manager.initialize(account_cfg)
    assert not manager._initialized

def test_shutdown(manager, mock_mt5):
    manager._initialized = True
    manager.shutdown()
    mock_mt5.shutdown.assert_called()
    assert not manager._initialized

def test_place_order_market_buy(manager, mock_mt5):
    manager._initialized = True
    payload = {"symbol": "EURUSD", "volume": 0.01, "order_type": "BUY", "deviation": 5}
    mock_mt5.order_send.return_value = MagicMock(retcode=mock_mt5.TRADE_RETCODE_DONE, order=12345, comment="ok")
    res = manager.place_order(payload)
    assert res["success"]
    assert res["ticket"] == 12345
    assert "details" in res

def test_place_order_market_sell(manager, mock_mt5):
    manager._initialized = True
    payload = {"symbol": "EURUSD", "volume": 0.01, "order_type": "SELL"}
    mock_mt5.order_send.return_value = MagicMock(retcode=mock_mt5.TRADE_RETCODE_DONE, order=12346)
    res = manager.place_order(payload)
    assert res["success"]

def test_place_order_pending_buy_limit(manager, mock_mt5):
    manager._initialized = True
    payload = {"symbol": "EURUSD", "volume": 0.01, "order_type": "BUY_LIMIT", "price": 1.0900}
    mock_mt5.order_send.return_value = MagicMock(retcode=mock_mt5.TRADE_RETCODE_DONE, order=12347)
    res = manager.place_order(payload)
    assert res["success"]

def test_place_order_smart_limit_buy(manager, mock_mt5):
    manager._initialized = True
    payload = {"symbol": "EURUSD", "volume": 0.01, "order_type": "LIMIT", "price": 1.0900}  # below bid
    mock_mt5.order_send.return_value = MagicMock(retcode=mock_mt5.TRADE_RETCODE_DONE, order=12348)
    res = manager.place_order(payload)
    assert res["success"]

def test_place_order_smart_limit_sell(manager, mock_mt5):
    manager._initialized = True
    payload = {"symbol": "EURUSD", "volume": 0.01, "order_type": "LIMIT", "price": 1.1100}  # above ask
    mock_mt5.order_send.return_value = MagicMock(retcode=mock_mt5.TRADE_RETCODE_DONE, order=12349)
    res = manager.place_order(payload)
    assert res["success"]

def test_place_order_smart_limit_too_close(manager, mock_mt5):
    manager._initialized = True
    payload = {"symbol": "EURUSD", "volume": 0.01, "order_type": "LIMIT", "price": 1.0995}
    res = manager.place_order(payload)
    assert not res["success"]
    assert "too close" in res["message"]

def test_place_order_invalid_volume(manager, mock_mt5):
    manager._initialized = True
    payload = {"symbol": "EURUSD", "volume": 0, "order_type": "BUY"}
    res = manager.place_order(payload)
    assert not res["success"]
    assert "Invalid 'volume'" in res["message"]

def test_place_order_sl_too_close(manager, mock_mt5):
    manager._initialized = True
    payload = {"symbol": "EURUSD", "volume": 0.01, "order_type": "BUY", "sl": 1.0999}  # too close to ask 1.1000
    res = manager.place_order(payload)
    assert not res["success"]
    assert "SL too close" in res["message"]

def test_get_open_orders(manager, mock_mt5):
    manager._initialized = True
    Order = namedtuple('Order', ['ticket', 'symbol', 'type', 'price_open', 'volume_initial', 'sl', 'tp', 'time_setup', 'comment'])
    mock_order = Order(123, "EURUSD", 3, 1.1, 0.01, 1.0, 1.2, 1234567890, "test")
    mock_mt5.orders_get.return_value = [mock_order]
    res = manager.get_open_orders("EURUSD")
    assert res["success"]
    assert len(res["orders"]) == 1
    order = res["orders"][0]
    assert order["ticket"] == 123
    assert order["symbol"] == "EURUSD"
    assert "raw" in order

def test_get_open_orders_failure(manager, mock_mt5):
    manager._initialized = True
    mock_mt5.orders_get.return_value = None
    res = manager.get_open_orders()
    assert not res["success"]

def test_get_open_positions(manager, mock_mt5):
    manager._initialized = True
    Position = namedtuple('Position', ['ticket', 'symbol', 'type', 'volume', 'price_open', 'sl', 'tp', 'time', 'profit', 'comment'])
    mock_pos = Position(456, "GBPUSD", 0, 0.02, 1.3, 1.2, 1.4, 1234567890, 10.5, "pos")
    mock_mt5.positions_get.return_value = [mock_pos]
    res = manager.get_open_positions()
    assert res["success"]
    assert len(res["positions"]) == 1
    pos = res["positions"][0]
    assert pos["ticket"] == 456
    assert pos["profit"] == 10.5

def test_modify_order(manager, mock_mt5):
    manager._initialized = True
    Order = namedtuple('Order', ['ticket', 'symbol', 'price_open', 'sl', 'tp'])
    mock_order = Order(123, "EURUSD", 1.1, 1.0, 1.2)
    mock_mt5.orders_get.return_value = [mock_order]
    mock_mt5.order_send.return_value = MagicMock(retcode=mock_mt5.TRADE_RETCODE_DONE)
    update_payload = {"price": 1.11, "sl": 1.01}
    res = manager.modify_order(123, update_payload)
    assert res["success"]
    assert res["ticket"] == 123

def test_modify_order_not_found(manager, mock_mt5):
    manager._initialized = True
    mock_mt5.orders_get.return_value = []
    res = manager.modify_order(999, {})
    assert not res["success"]
    assert "not found" in res["message"]

def test_cancel_order(manager, mock_mt5):
    manager._initialized = True
    Order = namedtuple('Order', ['ticket', 'symbol', 'price_open'])
    mock_order = Order(123, "EURUSD", 1.1)
    mock_mt5.orders_get.return_value = [mock_order]
    mock_mt5.order_send.return_value = MagicMock(retcode=mock_mt5.TRADE_RETCODE_DONE)
    res = manager.cancel_order(123)
    assert res["success"]

def test_cancel_order_not_found(manager, mock_mt5):
    manager._initialized = True
    mock_mt5.orders_get.return_value = []
    res = manager.cancel_order(999)
    assert not res["success"]

def test_close_position_full(manager, mock_mt5):
    manager._initialized = True
    Position = namedtuple('Position', ['ticket', 'symbol', 'type', 'volume'])
    mock_pos = Position(456, "EURUSD", 0, 0.01) # BUY type=0
    mock_mt5.positions_get.return_value = [mock_pos]
    mock_mt5.order_send.return_value = MagicMock(retcode=mock_mt5.TRADE_RETCODE_DONE)
    res = manager.close_position(456)
    assert res["success"]

def test_close_position_partial(manager, mock_mt5):
    manager._initialized = True
    Position = namedtuple('Position', ['ticket', 'symbol', 'type', 'volume'])
    mock_pos = Position(456, "EURUSD", 1, 0.02) # SELL type=1
    mock_mt5.positions_get.return_value = [mock_pos]
    mock_mt5.order_send.return_value = MagicMock(retcode=mock_mt5.TRADE_RETCODE_DONE)
    res = manager.close_position(456, 0.01)
    assert res["success"]

def test_close_position_invalid_volume(manager, mock_mt5):
    manager._initialized = True
    Position = namedtuple('Position', ['ticket', 'symbol', 'type', 'volume'])
    mock_pos = Position(456, "EURUSD", 0, 0.01)
    mock_mt5.positions_get.return_value = [mock_pos]
    res = manager.close_position(456, 0.02)
    assert not res["success"]
    assert "Invalid close volume" in res["message"]

def test_close_position_not_found(manager, mock_mt5):
    manager._initialized = True
    mock_mt5.positions_get.return_value = []
    res = manager.close_position(999)
    assert not res["success"]