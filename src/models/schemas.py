from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, Any
from datetime import datetime


OrderType = Literal[
    "BUY",
    "SELL",
    "BUY_LIMIT",
    "SELL_LIMIT",
    "BUY_STOP",
    "SELL_STOP",
    "BUY_STOP_LIMIT",
    "SELL_STOP_LIMIT",
    "LIMIT",   # smart auto-type (server will resolve to buy/sell limit based on ask/bid)
    "MARKET",  # explicit market execution; prefer explicit BUY or SELL instead
]


class BaseResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the operation succeeded.")
    message: Optional[str] = Field(None, description="Optional message or error detail.")


class NewOrderRequest(BaseModel):
    symbol: str = Field(..., example="EURUSD")
    volume: float = Field(..., gt=0, example=0.01)
    order_type: OrderType = Field(..., description="Type of order (BUY/SELL/BUY_LIMIT/.../LIMIT)")
    price: Optional[float] = Field(None, example=1.0850, description="Target price (for pending orders)")
    stop_limit_price: Optional[float] = Field(None, example=1.0840, description="Stop-limit trigger price")
    sl: Optional[float] = Field(None, description="Stop Loss level")
    tp: Optional[float] = Field(None, description="Take Profit level")
    deviation: int = Field(10, description="Max price deviation in points (market orders)")
    comment: Optional[str] = Field(None, description="Client-provided short comment")
    magic: Optional[int] = Field(None, description="Magic number to identify EA/strategy")
    client_id: Optional[str] = Field(None, description="Client correlation id")

    @validator("symbol")
    def symbol_upper(cls, v):
        return v.upper()


class UpdateOrderRequest(BaseModel):
    price: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    stop_limit_price: Optional[float] = None
    volume: Optional[float] = None
    deviation: Optional[int] = None
    comment: Optional[str] = None


class RemoveOrderRequest(BaseModel):
    ticket: int = Field(..., description="Ticket of the pending order to remove")


class ClosePositionRequest(BaseModel):
    ticket: int = Field(..., description="Ticket of the position to close")
    volume: Optional[float] = Field(None, description="Partial close volume, omit for full close")


class OrderEntry(BaseModel):
    ticket: Optional[int]
    symbol: Optional[str]
    type: Optional[int]  # change to int
    price: Optional[float]
    volume: Optional[float]
    sl: Optional[float]
    tp: Optional[float]
    time: Optional[int]
    comment: Optional[str]
    raw: Optional[Any]


class PositionEntry(BaseModel):
    ticket: Optional[int]
    symbol: Optional[str]
    type: Optional[int]  # change to int
    volume: Optional[float]
    price_open: Optional[float]
    sl: Optional[float]
    tp: Optional[float]
    time: Optional[int]
    profit: Optional[float]
    comment: Optional[str]
    raw: Optional[Any]


class OrderResponse(BaseResponse):
    ticket: Optional[int] = Field(None, description="Order or position ticket if available")
    symbol: Optional[str] = None
    order_type: Optional[str] = None
    price: Optional[float] = None
    volume: Optional[float] = None
    time_placed: Optional[datetime] = None
    comment: Optional[str] = None
    details: Optional[Any] = None


class OrderListResponse(BaseResponse):
    orders: list[OrderEntry] = Field(default_factory=list)


class PositionListResponse(BaseResponse):
    positions: list[PositionEntry] = Field(default_factory=list)