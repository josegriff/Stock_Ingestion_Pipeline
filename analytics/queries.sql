-- 1. Daily percentage returns
SELECT
    symbol,
    Date,
    Close,
    LAG(Close) OVER (PARTITION BY symbol ORDER BY Date) AS prev_close,
    (Close - LAG(Close) OVER (PARTITION BY symbol ORDER BY Date))
        / LAG(Close) OVER (PARTITION BY symbol ORDER BY Date) AS daily_return
FROM stock_data
ORDER BY symbol, Date;

-- 2. 30-day rolling volatility (standard deviation of daily returns)
WITH returns AS (
    SELECT
        symbol,
        Date,
        (Close - LAG(Close) OVER (PARTITION BY symbol ORDER BY Date))
            / LAG(Close) OVER (PARTITION BY symbol ORDER BY Date) AS daily_return
    FROM stock_data
)
SELECT
    symbol,
    Date,
    STDDEV(daily_return) OVER (
        PARTITION BY symbol
        ORDER BY Date
        ROWS BETWEEN 30 PRECEDING AND CURRENT ROW
    ) AS rolling_volatility_30d
FROM returns
ORDER BY symbol, Date;

-- 3. 30-day rolling Sharpe ratio
WITH returns AS (
    SELECT
        symbol,
        Date,
        (Close - LAG(Close) OVER (PARTITION BY symbol ORDER BY Date))
            / LAG(Close) OVER (PARTITION BY symbol ORDER BY Date) AS r
    FROM stock_data
),
stats AS (
    SELECT
        symbol,
        Date,
        r,
        AVG(r) OVER (PARTITION BY symbol ORDER BY Date ROWS BETWEEN 30 PRECEDING AND CURRENT ROW) AS mean_r,
        STDDEV(r) OVER (PARTITION BY symbol ORDER BY Date ROWS BETWEEN 30 PRECEDING AND CURRENT ROW) AS vol
    FROM returns
)
SELECT
    symbol,
    Date,
    mean_r / NULLIF(vol, 0) AS sharpe_30d
FROM stats
ORDER BY symbol, Date;

-- 4. Maximum drawdown per symbol
WITH prices AS (
    SELECT
        symbol,
        Date,
        Close,
        MAX(Close) OVER (PARTITION BY symbol ORDER BY Date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS peak
    FROM stock_data
),
drawdowns AS (
    SELECT
        symbol,
        Date,
        (Close - peak) / peak AS drawdown
    FROM prices
)
SELECT
    symbol,
    MIN(drawdown) AS max_drawdown
FROM drawdowns
GROUP BY symbol
ORDER BY max_drawdown;

-- 5. Sorted list of pairwise correlations (highest to lowest)
WITH returns AS (
    SELECT
        symbol,
        Date,
        (Close - LAG(Close) OVER (PARTITION BY symbol ORDER BY Date))
            / LAG(Close) OVER (PARTITION BY symbol ORDER BY Date) AS r
    FROM stock_data
),
pairs AS (
    SELECT
        r1.symbol AS symbol_x,
        r2.symbol AS symbol_y,
        corr(r1.r, r2.r) AS correlation
    FROM returns r1
    JOIN returns r2
        ON r1.Date = r2.Date
    WHERE r1.symbol < r2.symbol   -- avoids duplicates + self-pairs
    GROUP BY symbol_x, symbol_y
)
SELECT *
FROM pairs
ORDER BY correlation DESC;

-- 6. 20-day momentum signal
WITH momentum AS (
    SELECT
        symbol,
        Date,
        Close,
        LAG(Close, 20) OVER (PARTITION BY symbol ORDER BY Date) AS close_20d
    FROM stock_data
)
SELECT
    symbol,
    Date,
    (Close - close_20d) / close_20d AS momentum_20d
FROM momentum
WHERE close_20d IS NOT NULL
ORDER BY symbol, Date;

-- 7. Detect abnormal volume spikes (liquidity shocks)
WITH stats AS (
    SELECT
        symbol,
        Date,
        Volume,
        AVG(Volume) OVER (PARTITION BY symbol ORDER BY Date ROWS BETWEEN 30 PRECEDING AND CURRENT ROW) AS avg_vol,
        STDDEV(Volume) OVER (PARTITION BY symbol ORDER BY Date ROWS BETWEEN 30 PRECEDING AND CURRENT ROW) AS vol_std
    FROM stock_data
)
SELECT
    symbol,
    Date,
    Volume,
    (Volume - avg_vol) / NULLIF(vol_std, 0) AS volume_zscore
FROM stats
WHERE (Volume - avg_vol) / NULLIF(vol_std, 0) > 3
ORDER BY symbol, Date;

-- 8. Best and worst months for each symbol
WITH monthly AS (
    SELECT
        symbol,
        year,
        month,
        FIRST_VALUE(Close) OVER (PARTITION BY symbol, year, month ORDER BY Date) AS open_month,
        LAST_VALUE(Close) OVER (PARTITION BY symbol, year, month ORDER BY Date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS close_month
    FROM stock_data
),
returns AS (
    SELECT
        symbol,
        year,
        month,
        (close_month - open_month) / open_month AS monthly_return
    FROM monthly
    GROUP BY symbol, year, month, open_month, close_month
)
SELECT *
FROM returns
QUALIFY monthly_return = MAX(monthly_return) OVER (PARTITION BY symbol)
    OR monthly_return = MIN(monthly_return) OVER (PARTITION BY symbol)
ORDER BY symbol, monthly_return DESC;