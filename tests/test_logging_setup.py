import logging
from src.logging_setup import setup_logging, DailyRotatingFileHandler
from datetime import datetime
import os
from zoneinfo import ZoneInfo

def test_setup_logging(tmp_path):
    os.chdir(tmp_path)
    setup_logging("DEBUG")
    logger = logging.getLogger()
    assert logger.level == logging.DEBUG
    handlers = logger.handlers
    assert len(handlers) == 2  # file + console
    file_h = next(h for h in handlers if isinstance(h, DailyRotatingFileHandler))
    assert file_h.level == logging.DEBUG
    console_h = next(h for h in handlers if isinstance(h, logging.StreamHandler))
    assert console_h.level == logging.NOTSET  # effective level is root

def test_daily_rotating_handler(tmp_path):
    os.chdir(tmp_path)
    os.makedirs("logs", exist_ok=True)
    handler = DailyRotatingFileHandler()
    record = logging.makeLogRecord({"msg": "test message", "levelname": "INFO", "module": "test"})
    handler.emit(record)
    today = datetime.now().strftime("%Y-%m-%d")
    log_dir = tmp_path / "logs"
    assert log_dir.exists()
    log_file = log_dir / f"{today}.log"
    assert log_file.exists()
    with open(log_file, "r") as f:
        content = f.read()
        assert "INFO - test - test message" in content
    handler.close()

def test_rotation_on_date_change(tmp_path, monkeypatch):
    os.chdir(tmp_path)
    os.makedirs("logs", exist_ok=True)
    class FakeDatetime:
        current = datetime(2025, 12, 1, tzinfo=ZoneInfo("Europe/Athens"))
        @classmethod
        def now(cls, tz):
            return cls.current

    monkeypatch.setattr("src.logging_setup.datetime", FakeDatetime)
    handler = DailyRotatingFileHandler()
    record = logging.makeLogRecord({"msg": "day1", "levelname": "INFO", "module": "test"})
    handler.emit(record)
    FakeDatetime.current = datetime(2025, 12, 2, tzinfo=ZoneInfo("Europe/Athens"))
    record2 = logging.makeLogRecord({"msg": "day2", "levelname": "INFO", "module": "test"})
    handler.emit(record2)
    day1_file = tmp_path / "logs" / "2025-12-01.log"
    day2_file = tmp_path / "logs" / "2025-12-02.log"
    assert day1_file.exists()
    assert day2_file.exists()
    handler.close()