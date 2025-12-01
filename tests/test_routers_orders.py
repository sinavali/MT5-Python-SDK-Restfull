from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch


@patch("src.routers.orders.mt5_manager.place_order")
def test_new_order_success(mock_place, client):
    mock_place.return_value = {
        "success": True,
        "message": "ok",
        "ticket": 123,
        "details": {},
    }
    payload = {
        "symbol": "EURUSD",
        "volume": 0.01,
        "order_type": "BUY",
        "price": None,
        "sl": None,
        "tp": None,
        "deviation": 10,
        "comment": None,
        "magic": None,
        "client_id": None,
    }
    resp = client.post("/api/v1/orders/newOrder", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"]
    assert data["ticket"] == 123


@patch("src.routers.orders.mt5_manager.place_order")
def test_new_order_failure(mock_place, client):
    mock_place.return_value = {"success": False, "message": "error", "details": {}}
    payload = {"symbol": "EURUSD", "volume": 0.01, "order_type": "BUY"}
    resp = client.post("/api/v1/orders/newOrder", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert not data["success"]


@patch("src.routers.orders.mt5_manager.get_open_orders")
def test_get_open_orders_success(mock_get, client):
    mock_get.return_value = {
        "success": True,
        "message": "ok",
        "orders": [
            {
                "ticket": 123,
                "symbol": "EURUSD",
                "type": 3,
                "price": 1.1,
                "volume": 0.01,
                "sl": 1.0,
                "tp": 1.2,
                "time": 1234567890,        # <-- this is what your current OrderEntry model requires
                "comment": "test",
                "raw": {}
            }
        ]
    }

    resp = client.get("/api/v1/orders/getOpenOrders?symbol=EURUSD")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"]
    assert len(data["orders"]) == 1
    assert data["orders"][0]["ticket"] == 123


@patch("src.routers.orders.mt5_manager.get_open_orders")
def test_get_open_orders_failure(mock_get, client):
    mock_get.return_value = {"success": False, "message": "error"}
    resp = client.get("/api/v1/orders/getOpenOrders")
    assert resp.status_code == 200
    data = resp.json()
    assert not data["success"]
    assert data["orders"] == []


@patch("src.routers.orders.mt5_manager.get_open_positions")
def test_get_open_positions_success(mock_get, client):
    mock_get.return_value = {
        "success": True,
        "message": "ok",
        "positions": [
            {
                "ticket": 456,
                "symbol": "GBPUSD",
                "type": 0,
                "volume": 0.02,
                "price_open": 1.3,
                "sl": 1.2,
                "tp": 1.4,
                "time": 123,
                "profit": 10.5,
                "comment": "pos",
                "raw": {},
            }
        ],
    }
    resp = client.get("/api/v1/orders/getOpenPositions")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"]
    assert len(data["positions"]) == 1


@patch("src.routers.orders.mt5_manager.get_open_positions")
def test_get_open_positions_failure(mock_get, client):
    mock_get.return_value = {"success": False, "message": "error"}
    resp = client.get("/api/v1/orders/getOpenPositions")
    assert resp.status_code == 200
    data = resp.json()
    assert not data["success"]
    assert data["positions"] == []


@patch("src.routers.orders.mt5_manager.cancel_order")
def test_remove_order_success(mock_cancel, client):
    mock_cancel.return_value = {
        "success": True,
        "message": "canceled",
        "ticket": 123,
        "details": {},
    }
    payload = {"ticket": 123}
    resp = client.post("/api/v1/orders/removeOrder", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"]


@patch("src.routers.orders.mt5_manager.cancel_order")
def test_remove_order_failure(mock_cancel, client):
    mock_cancel.return_value = {"success": False, "message": "not found", "details": {}}
    payload = {"ticket": 999}
    resp = client.post("/api/v1/orders/removeOrder", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert not data["success"]


@patch("src.routers.orders.mt5_manager.close_position")
def test_close_position_success(mock_close, client):
    mock_close.return_value = {
        "success": True,
        "message": "closed",
        "ticket": 456,
        "details": {},
    }
    payload = {"ticket": 456, "volume": 0.01}
    resp = client.post("/api/v1/orders/closePosition", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"]


@patch("src.routers.orders.mt5_manager.close_position")
def test_close_position_failure(mock_close, client):
    mock_close.return_value = {"success": False, "message": "error", "details": {}}
    payload = {"ticket": 456}
    resp = client.post("/api/v1/orders/closePosition", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert not data["success"]


@patch("src.routers.orders.mt5_manager.modify_order")
def test_update_order_success(mock_modify, client):
    mock_modify.return_value = {
        "success": True,
        "message": "modified",
        "ticket": 123,
        "details": {},
    }
    payload = {"price": 1.11, "sl": 1.01, "tp": 1.21}
    resp = client.post("/api/v1/orders/updateOrder?ticket=123", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"]


@patch("src.routers.orders.mt5_manager.modify_order")
def test_update_order_failure(mock_modify, client):
    mock_modify.return_value = {"success": False, "message": "error", "details": {}}
    payload = {}
    resp = client.post("/api/v1/orders/updateOrder?ticket=999", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert not data["success"]
