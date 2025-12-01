import pytest
from src.main import main, _signal_handler, build_app
from unittest.mock import patch, ANY, MagicMock
import sys
import signal


@patch("src.main.uvicorn.run")
@patch("src.main.mt5_manager.initialize", return_value=True)
@patch("src.main.load_config")
@patch("src.main.detect_live_flag", return_value=False)
@patch("src.main.setup_logging")
def test_main_demo(mock_log, mock_detect, mock_load, mock_init, mock_run):
    mock_load.return_value = {
        "accounts": {"demo": [{"login": 1}]},
        "mt5": {},
        "server": {"host": "127.0.0.1", "port": 5100},
    }
    main()
    mock_init.assert_called()
    mock_run.assert_called_with(ANY, host="127.0.0.1", port=5100, log_level="info")


@patch("src.main.uvicorn.run")
@patch("src.main.mt5_manager.initialize", return_value=True)
@patch("src.main.load_config")
@patch("src.main.detect_live_flag", return_value=True)
@patch("src.main.setup_logging")
def test_main_live(mock_log, mock_detect, mock_load, mock_init, mock_run):
    mock_load.return_value = {
        "accounts": {"live": {"login": 1}},
        "mt5": {},
        "server": {},
    }
    main(["--live"])
    mock_detect.assert_called()
    mock_run.assert_called()


@patch("src.main.uvicorn.run")
@patch("src.main.mt5_manager.initialize", return_value=False)
@patch("src.main.load_config")
@patch("src.main.detect_live_flag", return_value=False)
@patch("src.main.setup_logging")
def test_main_init_fail(mock_log, mock_detect, mock_load, mock_init, mock_run):
    mock_load.return_value = {"accounts": {"demo": [{}]}, "mt5": {}}
    with pytest.raises(SystemExit):
        main()
    mock_run.assert_not_called()


def test_signal_handler():
    with patch("src.main.mt5_manager.shutdown") as mock_shut, patch(
        "src.main.sys.exit"
    ) as mock_exit, patch(
        "src.main.logger"
    ) as mock_logger:  # <-- patch the real logger
        _signal_handler(signal.SIGTERM, None)
        mock_shut.assert_called_once()
        mock_exit.assert_called_once_with(0)
        mock_logger.info.assert_called_once_with(
            "Received termination signal (%s). Shutting down.", signal.SIGTERM
        )


@patch("src.main.mt5_manager._initialized", True)
def test_build_app(mock_config):
    app = build_app(mock_config)
    assert app.title == "MT5 Order Manager"
    resp = app.openapi()
    assert "/api/v1/health" in resp["paths"]
    assert "/api/v1/orders/newOrder" in resp["paths"]
