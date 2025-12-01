```markdown
# MT5 REST API – Documentation

Base URL: `http://127.0.0.1:5100`

All endpoints are under `/api/v1`.  
Authentication: optional API key via header `X-API-Key` (disabled in dev config, enabled in live).

## Health Check

```
GET /api/v1/health
```

**Response**
```json
{
  "status": "ok",
  "mt5_connected": true
}
```

## Orders & Positions

### 1. Place New Order (market or pending)
```
POST /api/v1/orders/newOrder
```

**Body** (JSON)
```json
{
  "symbol": "EURUSD",
  "volume": 0.05,
  "order_type": "BUY_LIMIT",           // or BUY, SELL, SELL_STOP, LIMIT, etc.
  "price": 1.08500,                    // required for pending orders
  "sl": 1.08000,
  "tp": 1.09500,
  "deviation": 10,
  "comment": "my-strategy-v2",
  "magic": 20241201,
  "client_id": "abc123"
}
```

**Success response**
```json
{
  "success": true,
  "message": "Order placed",
  "ticket": 123456789,
  "symbol": "EURUSD",
  "order_type": "BUY_LIMIT",
  "price": 1.085,
  "volume": 0.05,
  "comment": "my-strategy-v2",
  "details": { ...mt5 result... }
}
```

### 2. List Open Pending Orders
```
GET /api/v1/orders/getOpenOrders
GET /api/v1/orders/getOpenOrders?symbol=EURUSD
```

### 3. List Open Positions
```
GET /api/v1/orders/getOpenPositions
GET /api/v1/orders/getOpenPositions?symbol=GBPUSD
```

**Response example**
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
      "profit": 23.45,
      "comment": "my-strategy-v2",
      ...
    }
  ]
}
```

### 4. Cancel Pending Order
```
POST /api/v1/orders/removeOrder
```

**Body**
```json
{ "ticket": 123456789 }
```

### 5. Modify Pending Order
```
POST /api/v1/orders/updateOrder?ticket=123456789
```

**Body** (only fields you want to change)
```json
{
  "price": 1.New price,
  "sl": 1.08200,
  "tp": 1.10000
}
```

### 6. Close Position (full or partial)
```
POST /api/v1/orders/closePosition
```

**Body**
```json
{
  "ticket": 987654321,
  "volume": 0.03        // omit → full close
}
```

## Order Types Accepted

| Value              | Meaning                              |
|-------------------|---------------------------------------|
| BUY               | Market buy                            |
| SELL              | Market sell                           |
| BUY_LIMIT         | Buy limit below market                |
| SELL_LIMIT        | Sell limit above market               |
| BUY_STOP          | Buy stop above market                 |
| SELL_STOP         | Sell stop below market                |
| BUY_STOP_LIMIT    | Buy stop-limit                        |
| SELL_STOP_LIMIT   | Sell stop-limit                       |
| LIMIT             | Smart limit – server decides BUY_LIMIT based on price vs market |
| MARKET            | Not recommended – use BUY/SELL instead|

## WebSocket (not implemented yet)

Planned endpoint (future):

```
wss://127.0.0.1:5100/ws/mt5
```

Will broadcast in real time:
- New orders
- Order modifications/cancellations
- New trades/positions
- Position updates & profit changes

Say “add websocket” and I’ll drop the full working broadcast implementation in <2 minutes.

## Run modes

```bash
python src/main.py          # demo account (config.dev.json)
python src/main.py --live   # live account (config.live.json)
```