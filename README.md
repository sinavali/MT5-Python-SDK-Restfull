# MT5 REST API – Documentation

## Contribute

You may contribute to this project by actually checking the satibility of the App and send your PRs. i tried too keep the project as a kernel like and let you to have wrappers around it using the socket and rest APIs implemented (maybe adding Auth or paid subscriptions, whatever you like to do) just somewhere in your project mention this repo url.

## Overview

This is a FastAPI-based RESTful service that acts as a bridge to MetaTrader 5 (MT5). It loads configuration from JSON files (`config.dev.json` or `config.live.json`), initializes a single MT5 connection (using the MetaTrader5 Python package), and exposes endpoints for managing orders and positions. The service uses a singleton MT5 manager for thread-safe operations.

Key features:

* Singleton MT5 connection for efficiency and safety.
* Supports demo/live accounts via CLI flag (`--live`).
* Logging to daily rotated files in `./logs` and console.
* Smart order types (e.g., "LIMIT" auto-resolves to BUY_LIMIT or SELL_LIMIT based on market prices).
* Validation for distances (SL/TP min distances, pending order distances from market).
* Graceful shutdown on SIGINT/SIGTERM.
* Real-time WebSocket streaming closed-candle data (multi-timeframe).


**Prerequisites**
- Python 3.13.9 (or compatible).
- Install dependencies: `pip install -r requirements.txt`.
- MT5 terminal installed (path in config).
- Valid MT5 account credentials in config files.
- For live: Replace placeholders in `config.live.json` with real values.

**Running the Service**
```bash
# Demo mode (uses config.dev.json, first demo account)
python src/main.py

# Live mode (uses config.live.json, live account)
python src/main.py --live
```

The server runs on host/port from config (default: 127.0.0.1:5100). Logs at INFO level by default (configurable).

**Running Tests**
After cloning, install requirements and run the full test suite:
```bash
pip install -r requirements.txt
pytest -v tests
```

**Base URL**: `http://<host>:<port>` (e.g., `http://127.0.0.1:5100`).

**API Versioning**: All endpoints under `/api/v1`.

**Authentication**
No built-in authentication; developers can add it via wrappers or middleware (e.g., JWT, API keys).

**Error Handling**
- All responses include `success` (bool) and `message` (str).
- HTTP status: 200 for success/false (to allow details inspection), 4xx/5xx for errors.
- Common errors: 400 (validation), 404 (not found), 500 (internal).
- Details in `details` field (dict) with MT5 error codes if applicable.

Example error:
```json
{
  "success": false,
  "message": "Invalid volume",
  "details": {"mt5_last_error": "..."}
}
```

**General Notes**
- All prices/volumes as floats; tickets as ints.
- Symbols case-insensitive (uppercased internally).
- MT5 must be running or initializable via path.
- Operations are synchronous and locked for safety.
- No rate limiting; add if needed for production.

## Endpoints

### Health Check
**GET /api/v1/health**

Checks service status and MT5 connection.

**Query Params**: None.

**Response** (200 OK)
```json
{
  "status": "ok",
  "mt5_connected": true  // or false
}
```

**cURL Example**
```bash
curl http://127.0.0.1:5100/api/v1/health
```

### Place New Order
**POST /api/v1/orders/newOrder**

Places a market or pending order. Validates inputs, resolves smart types, and sends to MT5.

**Headers**: Content-Type: application/json.

**Body** (NewOrderRequest schema)
- `symbol`: str (required, e.g., "EURUSD") – Trading symbol.
- `volume`: float (required, >0, e.g., 0.01) – Lot size.
- `order_type`: str (required, see Order Types below) – Type like "BUY", "LIMIT".
- `price`: float (optional/required for pending, e.g., 1.0850) – Entry price.
- `stop_limit_price`: float (optional, for STOP_LIMIT types) – Trigger price.
- `sl`: float (optional) – Stop Loss.
- `tp`: float (optional) – Take Profit.
- `deviation`: int (optional, default 10) – Slippage in points for market orders.
- `comment`: str (optional) – Short client comment (truncated to 64 chars).
- `magic`: int (optional) – Strategy identifier.
- `client_id`: str (optional) – Client correlation ID.

Validations:
- Volume >0.
- For pending: price required.
- SL/TP distances >= min_stop_distance (10 points default).
- For LIMIT: auto-resolves (see Order Types).
- Rejects if symbol not available/selectable.

**Response** (OrderResponse schema, 200 OK)
- `success`: bool.
- `message`: str.
- `ticket`: int (optional) – MT5 ticket.
- `symbol`: str.
- `order_type`: str.
- `price`: float (optional).
- `volume`: float.
- `time_placed`: datetime (optional, UTC).
- `comment`: str (optional).
- `details`: dict – Raw MT5 result.

Example Body:
```json
{
  "symbol": "EURUSD",
  "volume": 0.05,
  "order_type": "BUY_LIMIT",
  "price": 1.08500,
  "sl": 1.08000,
  "tp": 1.09500,
  "deviation": 10,
  "comment": "strategy-v1",
  "magic": 12345,
  "client_id": "client-abc"
}
```

Success Response Example:
```json
{
  "success": true,
  "message": "Order placed",
  "ticket": 123456789,
  "symbol": "EURUSD",
  "order_type": "BUY_LIMIT",
  "price": 1.085,
  "volume": 0.05,
  "comment": "strategy-v1",
  "details": {"retcode": 10009, ...}
}
```

**cURL Example**
```bash
curl -X POST http://127.0.0.1:5100/api/v1/orders/newOrder \
  -H "Content-Type: application/json" \
  -d '{"symbol": "EURUSD", "volume": 0.05, "order_type": "BUY_LIMIT", "price": 1.08500, "sl": 1.08000, "tp": 1.09500}'
```

### List Open Pending Orders
**GET /api/v1/orders/getOpenOrders**

Retrieves all open pending orders, optionally filtered by symbol.

**Query Params**
- `symbol`: str (optional) – Filter by symbol (e.g., "EURUSD").

**Response** (OrderListResponse schema, 200 OK)
- `success`: bool.
- `message`: str.
- `orders`: list[OrderEntry] – List of orders.
  - Each OrderEntry: dict with `ticket` (int), `symbol` (str), `type` (str), `price` (float), `volume` (float), `sl` (float), `tp` (float), `time` (int, UNIX), `comment` (str), `raw` (dict – full MT5 data).

Example Response:
```json
{
  "success": true,
  "message": "Open orders retrieved",
  "orders": [
    {
      "ticket": 123456789,
      "symbol": "EURUSD",
      "type": "BUY_LIMIT",
      "price": 1.08500,
      "volume": 0.05,
      "sl": 1.08000,
      "tp": 1.09500,
      "time": 1733086412,
      "comment": "strategy-v1",
      "raw": {...}
    }
  ]
}
```

**cURL Example**
```bash
curl http://127.0.0.1:5100/api/v1/orders/getOpenOrders?symbol=EURUSD
```

### List Open Positions
**GET /api/v1/orders/getOpenPositions**

Retrieves all open positions, optionally filtered by symbol.

**Query Params**
- `symbol`: str (optional).

**Response** (PositionListResponse schema, 200 OK)
- `success`: bool.
- `message`: str.
- `positions`: list[PositionEntry] – List of positions.
  - Each PositionEntry: dict with `ticket` (int), `symbol` (str), `type` (str), `volume` (float), `price_open` (float), `sl` (float), `tp` (float), `time` (int), `profit` (float), `comment` (str), `raw` (dict).

Example Response:
```json
{
  "success": true,
  "message": "Open positions retrieved",
  "positions": [
    {
      "ticket": 987654321,
      "symbol": "EURUSD",
      "type": "BUY",
      "volume": 0.05,
      "price_open": 1.08765,
      "sl": 1.08000,
      "tp": 1.09500,
      "time": 1733086412,
      "profit": 23.45,
      "comment": "strategy-v1",
      "raw": {...}
    }
  ]
}
```

**cURL Example**
```bash
curl http://127.0.0.1:5100/api/v1/orders/getOpenPositions?symbol=GBPUSD
```

### Cancel Pending Order
**POST /api/v1/orders/removeOrder**

Cancels a pending order by ticket.

**Headers**: Content-Type: application/json.

**Body** (RemoveOrderRequest schema)
- `ticket`: int (required) – Order ticket.

**Response** (OrderResponse schema, 200 OK)
- As above, without symbol/order_type/etc.

Example Body:
```json
{"ticket": 123456789}
```

**cURL Example**
```bash
curl -X POST http://127.0.0.1:5100/api/v1/orders/removeOrder \
  -H "Content-Type: application/json" \
  -d '{"ticket": 123456789}'
```

### Modify Pending Order
**POST /api/v1/orders/updateOrder**

Modifies a pending order. Ticket in query; updates in body.

**Query Params**
- `ticket`: int (required) – Order ticket.

**Headers**: Content-Type: application/json.

**Body** (UpdateOrderRequest schema)
- `price`: float (optional).
- `sl`: float (optional).
- `tp`: float (optional).
- `stop_limit_price`: float (optional).
- `volume`: float (optional).
- `deviation`: int (optional).
- `comment`: str (optional).

Only provided fields are updated.

**Response** (OrderResponse schema, 200 OK)

Example Body:
```json
{"price": 1.08600, "sl": 1.08100}
```

**cURL Example**
```bash
curl -X POST http://127.0.0.1:5100/api/v1/orders/updateOrder?ticket=123456789 \
  -H "Content-Type: application/json" \
  -d '{"price": 1.08600, "sl": 1.08100}'
```

### Close Position
**POST /api/v1/orders/closePosition**

Closes a position fully or partially.

**Headers**: Content-Type: application/json.

**Body** (ClosePositionRequest schema)
- `ticket`: int (required) – Position ticket.
- `volume`: float (optional) – Partial volume; omit for full.

Validations: Volume <= current; >0.

**Response** (OrderResponse schema, 200 OK)

Example Body:
```json
{"ticket": 987654321, "volume": 0.03}
```

**cURL Example**
```bash
curl -X POST http://127.0.0.1:5100/api/v1/orders/closePosition \
  -H "Content-Type: application/json" \
  -d '{"ticket": 987654321, "volume": 0.03}'
```

## Order Types

Supported `order_type` values (case-insensitive):

| Value            | Description                                                                 | Requirements                  |
|------------------|-----------------------------------------------------------------------------|-------------------------------|
| BUY             | Market buy at current ask.                                                  | None                          |
| SELL            | Market sell at current bid.                                                 | None                          |
| BUY_LIMIT       | Pending buy below market (price < bid - min_distance).                      | price                         |
| SELL_LIMIT      | Pending sell above market (price > ask + min_distance).                     | price                         |
| BUY_STOP        | Pending buy above market.                                                   | price                         |
| SELL_STOP       | Pending sell below market.                                                  | price                         |
| BUY_STOP_LIMIT  | Buy stop-limit (trigger at stop_limit_price, then limit at price).          | price, stop_limit_price       |
| SELL_STOP_LIMIT | Sell stop-limit.                                                            | price, stop_limit_price       |
| LIMIT           | Smart: Auto BUY_LIMIT if price below market; SELL_LIMIT if above. Rejects if too close (inside spread + min_distance=2 points). | price                         |
| MARKET          | Not supported; use BUY/SELL instead.                                        | N/A                           |

- Min distances configurable in MT5Manager (MIN_DISTANCE_POINTS=2, MIN_STOP_DISTANCE_POINTS=10).
- Points converted to price via symbol info.
- For market: deviation applies.
- All use GTC expiration, RETURN/IOC filling.

# WebSocket Streaming

The service includes a real-time WebSocket endpoint that streams MT5 market data based on per-client subscription models.
Each client can subscribe to multiple symbols, optionally including:

* Live bid/ask ticks.
* One or more timeframes.
* A configurable count of candles per timeframe.
* A per-timeframe `always_send` flag to receive updates every second even if no new candle closed.

**Endpoint**

```
ws://<host>:<port>/ws
```

## Subscription Format

Send a JSON message after connecting. The server accepts two formats:

### 1. Direct subscription list (recommended)

```json
[
  {
    "symbol": "EURUSD",
    "live": true,
    "timeframes": [
      ["m1", 2, false],
      ["h1", 1, true]
    ]
  },
  {
    "symbol": "GBPUSD",
    "live": false,
    "timeframes": [
      ["m5", 10, false]
    ]
  }
]
```

### 2. Action-based (optional)

```json
{
  "action": "subscribe",
  "data": [
    { "symbol": "EURUSD", "live": true, "timeframes": [["m1",1,true]] }
  ]
}
```

Both forms produce the same result.

### Timeframe Format

Each timeframe entry is a 3-element array:

```
["M1", count, always_send]
```

* `M1`, `H1`, `D1` etc.
* `count` = number of closed candles to retrieve every time data updates.
* `always_send`:

  * true → send candles every second regardless of new candle.
  * false → send only when a new candle timestamp appears.

### Available Timeframes

```
M1, M2, M3, M4, M5, M6, M10, M12,
M15, M20, M30,
H1, H2, H3, H4, H6, H8, H12,
D1, W1, MN1
```

## What You Receive

The server pushes a list of symbol payloads every second:

Example push:

```json
[
  {
    "symbol": "EURUSD",
    "live": { "ask": 1.08654, "bid": 1.08643 },
    "timeframes": {
      "m1": [
        {
          "time": 1733086400,
          "open": 1.08610,
          "high": 1.08680,
          "low": 1.08600,
          "close": 1.08650,
          "tick_volume": 123
        }
      ],
      "h1": []
    }
  }
]
```

Notes:

* Timeframe keys are always lowercase (`"m1"`, `"h1"`).
* If no new candle is available and `always_send` is false, the timeframe will be an empty list.
* If MT5 is not connected or symbol not available, lists return empty.
* Live prices return `ask`/`bid` or `null` if market is closed.

## Server-side Behavior

* A global `candle_watcher()` runs every 1 second.
* For each connected client:

  * The subscription model is validated and stored.
  * Each symbol/timeframe pair has its own last-sent timestamp to avoid resending duplicate candles.
  * Live ticks are fetched only if requested (`live: true`).
* Disconnected clients are automatically cleaned up.

## Example Client (JavaScript)

```js
const ws = new WebSocket("ws://127.0.0.1:5100/ws");

ws.onopen = () => {
  ws.send(JSON.stringify([
    { symbol: "EURUSD", live: true, timeframes: [["m1", 2, false]] }
  ]));
};

ws.onmessage = (ev) => {
  const data = JSON.parse(ev.data);
  console.log("Incoming:", data);
};
```

## Logging & Monitoring

- Daily rotated logs in `./logs/YYYY-MM-DD.log` (Europe/Athens TZ).
- Console output.
- Level from config (`log_level`: "DEBUG", "INFO", etc.).
- Includes timestamps, levels, modules.

## Configuration Details

- `accounts`: dict with `live` (dict: login, password, server) and `demo` (list of dicts).
- `mt5.path`: str – Terminal executable.
- `server`: dict with `host`, `port`.
- `log_level`: str.
- `auth`: dict with `enabled` (bool), `api_keys` (list[str]).

No merging; full config per mode.

## Troubleshooting

- MT5 init fails: Check path, credentials, MT5 running.
- Symbol not found: Ensure selected in MT5.
- Connection issues: Increase timeout in init.
- Auth errors: Check config, header.
- Run with DEBUG log for details.
- Shutdown: CTRL+C graceful (closes MT5).
- WebSocket returns empty lists: Symbol not available or market closed.
- If you receive `{"error":"Invalid JSON"}`, check the payload formatting.
- If nothing is received: ensure subscription was accepted (`{"status":"subscribed"}`).