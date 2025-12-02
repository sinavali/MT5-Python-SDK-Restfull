const websocket_result_model = [
    {
        symbol: "EURUSD",
        live: {
            ask: 1.0, // live ask price
            bid: 1.0 // live bid price
        },
        timeframes: {
            m1: [ // one minute candles
                {}, // the lastest closed candle
                {}, // this goes on as much as asked in the subscription payload
            ],
            m15: [ // 15 minute candles
                {}, // the lastest closed candle
                {}, // this goes on as much as asked in the subscription payload
            ],
            h1: [ // hourly candles
                {}, // the lastest closed candle
                {}, // this goes on as much as asked in the subscription payload
            ]
        }
    },
    {
        symbol: "GBPUSD",
        live: {
            ask: 1.0, // live ask price
            bid: 1.0 // live bid price
        },
        timeframes: {
            m1: [ // one minute candles
                {}, // the lastest closed candle
                {}, // this goes on as much as asked in the subscription payload
            ],
            m30: [ // 30 minute candles
                {}, // the lastest closed candle
                {}, // this goes on as much as asked in the subscription payload
            ],
            h4: [ // 4 hour candles
                {}, // the lastest closed candle
                {}, // this goes on as much as asked in the subscription payload
            ]
        }
    }
]


const subscription_model_1 = [
    {
        symbol: "EURUSD",
        live: false, // default is true, if false the current prices wont be added
        timeframes: [ // the timeframes that client needs and how many candle from position 1 (1 included)
            ["m1", 1, true], // first value is the timeframe, second value is the count of candles, the third value is if the user want the timeframe key gets filled everytime in the websocket result (true) or filled only new candle is closed (false), default is false
            ["m15"], // default is 1
            ["h1", 50, false]
        ]
    },
    {
        symbol: "GBPUSD",
        timeframes: [ // the timeframes that client needs and how many candle from position 1 (1 included)
            ["m1", 1],
            ["m30"], // default is 1
            ["h4", 50]
        ]
    },
]