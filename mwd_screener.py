import pandas as pd
import yfinance as yf
from datetime import datetime
import os
import time


# ============================================================
# CONFIGURATION
# ============================================================

CSV_FILE = "nifty100_symbols.csv"
OUTPUT_FILE = "docs/index.html"


# ============================================================
# FUNCTION: CHECK BULLISH CANDLE
# ============================================================

def is_bullish(open_price, close_price):

    if pd.isna(open_price) or pd.isna(close_price):
        return False

    return close_price > open_price


# ============================================================
# FUNCTION: CALCULATE PERCENTAGE
# ============================================================

def calculate_percentage(open_price, close_price):

    if open_price == 0:
        return 0

    return ((close_price - open_price) / open_price) * 100


# ============================================================
# ANALYZE STOCK
# ============================================================

def analyze_stock(symbol, company):

    yahoo_symbol = symbol + ".NS"

    print(f"Processing: {symbol}")

    try:

        ticker = yf.Ticker(yahoo_symbol)


        # ====================================================
        # DAILY DATA
        # ====================================================

        daily = ticker.history(
            period="1y",
            interval="1d",
            auto_adjust=False
        )


        # ====================================================
        # WEEKLY DATA
        # ====================================================

        weekly = ticker.history(
            period="1y",
            interval="1wk",
            auto_adjust=False
        )


        # ====================================================
        # MONTHLY DATA
        # ====================================================

        monthly = ticker.history(
            period="3y",
            interval="1mo",
            auto_adjust=False
        )


        # ====================================================
        # VALIDATE DATA
        # ====================================================

        if daily.empty:

            print(f"No daily data found for {symbol}")

            return None


        if weekly.empty:

            print(f"No weekly data found for {symbol}")

            return None


        if monthly.empty:

            print(f"No monthly data found for {symbol}")

            return None


        if len(daily) < 5:

            return None


        if len(weekly) < 3:

            return None


        if len(monthly) < 3:

            return None


        # ====================================================
        # DAILY CANDLE
        # LAST AVAILABLE TRADING DAY
        # ====================================================

        daily_candle = daily.iloc[-1]


        # ====================================================
        # WEEKLY CANDLE
        # LAST COMPLETED WEEK
        # ====================================================

        weekly_candle = weekly.iloc[-2]


        # ====================================================
        # MONTHLY CANDLE
        # LAST COMPLETED MONTH
        # ====================================================

        monthly_candle = monthly.iloc[-2]


        # ====================================================
        # DAILY BULLISH
        # ====================================================

        daily_bullish = is_bullish(
            daily_candle["Open"],
            daily_candle["Close"]
        )


        # ====================================================
        # WEEKLY BULLISH
        # ====================================================

        weekly_bullish = is_bullish(
            weekly_candle["Open"],
            weekly_candle["Close"]
        )


        # ====================================================
        # MONTHLY BULLISH
        # ====================================================

        monthly_bullish = is_bullish(
            monthly_candle["Open"],
            monthly_candle["Close"]
        )


        # ====================================================
        # MWD CONDITION
        # ====================================================

        if not (
            monthly_bullish
            and weekly_bullish
            and daily_bullish
        ):

            return None


        # ====================================================
        # LAST TRADING PRICE
        # ====================================================

        last_price = float(
            daily_candle["Close"]
        )


        # ====================================================
        # 52 WEEK HIGH
        # Last 252 trading days
        # ====================================================

        high_52_week = float(
            daily["High"].max()
        )


        # ====================================================
        # REMOVE STOCKS ALREADY AT 52 WEEK HIGH
        # ====================================================

        if last_price >= high_52_week:

            print(
                f"SKIPPED - Already at 52 Week High: "
                f"{symbol}"
            )

            return None


        # ====================================================
        # DISTANCE FROM 52 WEEK HIGH
        # ====================================================

        distance_52w = (
            (
                last_price - high_52_week
            )
            /
            high_52_week
        ) * 100


        # ====================================================
        # MONTHLY RISE PERCENTAGE
        # ====================================================

        monthly_rise_percent = calculate_percentage(

            float(monthly_candle["Open"]),

            float(monthly_candle["Close"])

        )


        # ====================================================
        # RESULT
        # ====================================================

        result = {

            "symbol": symbol,

            "company": company,

            "last_price": round(
                last_price,
                2
            ),

            "high_52_week": round(
                high_52_week,
                2
            ),

            "distance_52w": round(
                distance_52w,
                2
            ),

            "monthly_rise_percent": round(
                monthly_rise_percent,
                2
            ),

            "daily_open": round(
                float(daily_candle["Open"]),
                2
            ),

            "daily_close": round(
                float(daily_candle["Close"]),
                2
            ),

            "weekly_open": round(
                float(weekly_candle["Open"]),
                2
            ),

            "weekly_close": round(
                float(weekly_candle["Close"]),
                2
            ),

            "monthly_open": round(
                float(monthly_candle["Open"]),
                2
            ),

            "monthly_close": round(
                float(monthly_candle["Close"]),
                2
            )

        }


        print(

            f"MATCH: {symbol} | "

            f"Price: {last_price:.2f} | "

            f"52W High: {high_52_week:.2f} | "

            f"Distance: {distance_52w:.2f}% | "

            f"Monthly Rise: {monthly_rise_percent:.2f}%"

        )


        return result


    except Exception as e:

        print(
            f"ERROR processing {symbol}: {str(e)}"
        )

        return None


# ============================================================
# READ CSV
# ============================================================

def load_symbols():

    try:

        df = pd.read_csv(CSV_FILE)

        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
        )


        if "symbol" not in df.columns:

            raise Exception(

                "CSV must contain "
                "'symbol' column"

            )


        if "company" not in df.columns:

            df["company"] = df["symbol"]


        # Remove blank rows

        df = df.dropna(
            subset=["symbol"]
        )


        return df


    except Exception as e:

        print(
            f"ERROR reading CSV: {e}"
        )

        raise


# ============================================================
# GENERATE HTML
# ============================================================

def generate_html(results):


    current_time = datetime.now().strftime(
        "%d-%b-%Y %I:%M %p"
    )


    total_stocks = len(results)


    html = f"""

<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">


<title>
Nifty 100 MWD Screener
</title>


<style>


* {{

    box-sizing: border-box;

}}


body {{

    font-family: Arial, sans-serif;

    background: #f4f6f9;

    margin: 0;

    padding: 20px;

}}


.container {{

    max-width: 1400px;

    margin: auto;

}}


.header {{

    background:
    linear-gradient(
        135deg,
        #1f4e78,
        #2e75b6
    );

    color: white;

    padding: 30px;

    border-radius: 12px;

    margin-bottom: 25px;

}}


.header h1 {{

    margin: 0;

    font-size: 30px;

}}


.header p {{

    margin-top: 10px;

    font-size: 16px;

}}


.stats {{

    display: flex;

    gap: 20px;

    margin-top: 20px;

    flex-wrap: wrap;

}}


.card {{

    background: white;

    color: #333;

    padding: 18px;

    border-radius: 10px;

    min-width: 200px;

    box-shadow:
    0 2px 10px
    rgba(0,0,0,0.15);

}}


.card h3 {{

    margin: 0;

    font-size: 14px;

    color: #666;

}}


.card h2 {{

    margin: 10px 0 0 0;

    color: #1f4e78;

}}


.filters {{

    background: white;

    padding: 20px;

    border-radius: 10px;

    margin-bottom: 20px;

    box-shadow:
    0 2px 10px
    rgba(0,0,0,0.08);

    display: flex;

    gap: 20px;

    flex-wrap: wrap;

    align-items: center;

}}


.filter-group {{

    display: flex;

    flex-direction: column;

}}


.filter-group label {{

    font-weight: bold;

    margin-bottom: 7px;

    color: #444;

}}


.filter-group input {{

    padding: 10px;

    width: 200px;

    border-radius: 6px;

    border: 1px solid #ccc;

    font-size: 15px;

}}


.search-box {{

    padding: 10px;

    width: 250px;

    border-radius: 6px;

    border: 1px solid #ccc;

    font-size: 15px;

}}


.filter-button {{

    background: #1f4e78;

    color: white;

    border: none;

    padding: 11px 25px;

    border-radius: 6px;

    cursor: pointer;

    font-size: 15px;

    margin-top: 22px;

}}


.filter-button:hover {{

    background: #163a5c;

}}


.reset-button {{

    background: #777;

    color: white;

    border: none;

    padding: 11px 25px;

    border-radius: 6px;

    cursor: pointer;

    font-size: 15px;

    margin-top: 22px;

}}


.table-container {{

    overflow-x: auto;

    background: white;

    border-radius: 10px;

    box-shadow:
    0 2px 10px
    rgba(0,0,0,0.08);

}}


table {{

    width: 100%;

    border-collapse: collapse;

    min-width: 1000px;

}}


th {{

    background: #1f4e78;

    color: white;

    padding: 14px;

    text-align: left;

    position: sticky;

    top: 0;

}}


td {{

    padding: 12px;

    border-bottom:
    1px solid #e5e5e5;

}}


tr:hover {{

    background: #f5f9fc;

}}


.bullish {{

    color: #138a36;

    font-weight: bold;

}}


.price {{

    font-weight: bold;

    font-size: 15px;

}}


.distance {{

    color: #d97706;

    font-weight: bold;

}}


.rise {{

    color: #138a36;

    font-weight: bold;

}}


.no-data {{

    text-align: center;

    padding: 30px;

    font-size: 16px;

    color: #777;

}}


.result-info {{

    margin: 15px 0;

    font-weight: bold;

    color: #1f4e78;

}}


.footer {{

    text-align: center;

    margin-top: 30px;

    color: #777;

    font-size: 13px;

}}


@media(max-width:768px) {{

    body {{

        padding: 10px;

    }}

    .header {{

        padding: 20px;

    }}

    .header h1 {{

        font-size: 22px;

    }}

    .filter-group input {{

        width: 100%;

    }}

}}


</style>


</head>


<body>


<div class="container">


<!-- ================================================= -->
<!-- HEADER -->
<!-- ================================================= -->


<div class="header">


<h1>
📈 NIFTY 100 MWD SCREENER
</h1>


<p>

Monthly + Weekly + Daily
Bullish Stocks

</p>


<p>

Only stocks below their
52 Week High are included.

</p>


<div class="stats">


<div class="card">

<h3>Total MWD Matches</h3>

<h2>{total_stocks}</h2>

</div>


<div class="card">

<h3>Last Updated</h3>

<h2>{current_time}</h2>

</div>


</div>


</div>


<!-- ================================================= -->
<!-- FILTERS -->
<!-- ================================================= -->


<div class="filters">


<div class="filter-group">


<label>

Distance from 52 Week High (%)

</label>


<input

type="number"

id="distanceFilter"

value="-10"

step="0.1"

/>


</div>


<div class="filter-group">


<label>

Monthly Rise Above (%)

</label>


<input

type="number"

id="monthlyRiseFilter"

value="2"

step="0.1"

/>


</div>


<div class="filter-group">


<label>

Search Stock

</label>


<input

type="text"

id="searchInput"

placeholder="Symbol or Company"

/>


</div>


<button

class="filter-button"

onclick="applyFilters()"

>

Apply Filters

</button>


<button

class="reset-button"

onclick="resetFilters()"

>

Reset

</button>


</div>


<div
id="resultInfo"
class="result-info">

</div>


<!-- ================================================= -->
<!-- TABLE -->
<!-- ================================================= -->


<div class="table-container">


<table id="stockTable">


<thead>


<tr>


<th>#</th>

<th>Symbol</th>

<th>Company</th>

<th>Last Price</th>

<th>52 Week High</th>

<th>Distance from 52W High</th>

<th>Monthly Rise %</th>

<th>Daily</th>

<th>Weekly</th>

<th>Monthly</th>


</tr>


</thead>


<tbody>

"""


    if results:


        for index, stock in enumerate(
            results,
            start=1
        ):


            html += f"""

<tr

data-distance="{stock["distance_52w"]}"

data-monthly-rise="{stock["monthly_rise_percent"]}"

>


<td>{index}</td>


<td>

<b>

{stock["symbol"]}

</b>

</td>


<td>

{stock["company"]}

</td>


<td class="price">

₹ {stock["last_price"]:,.2f}

</td>


<td>

₹ {stock["high_52_week"]:,.2f}

</td>


<td class="distance">

{stock["distance_52w"]:.2f}%

</td>


<td class="rise">

+{stock["monthly_rise_percent"]:.2f}%

</td>


<td class="bullish">

BULLISH

</td>


<td class="bullish">

BULLISH

</td>


<td class="bullish">

BULLISH

</td>


</tr>

"""


    else:


        html += """

<tr>

<td
colspan="10"
class="no-data">

No stocks found matching
Monthly + Weekly + Daily
Bullish condition.

</td>

</tr>

"""


    html += """

</tbody>


</table>


</div>


<div class="footer">


<p>

MWD Logic:
Monthly Bullish +
Weekly Bullish +
Daily Bullish

</p>


<p>

Stocks already at
52 Week High are excluded.

</p>


<p>

Data Source: Yahoo Finance

</p>


<p>

For educational purposes only.
Not investment advice.

</p>


</div>


</div>


<!-- ================================================= -->
<!-- JAVASCRIPT -->
<!-- ================================================= -->


<script>


function applyFilters() {


    var distanceFilter = parseFloat(

        document.getElementById(
            "distanceFilter"
        ).value

    );


    var monthlyRiseFilter = parseFloat(

        document.getElementById(
            "monthlyRiseFilter"
        ).value

    );


    var searchText =

        document.getElementById(
            "searchInput"
        ).value
        .toUpperCase();


    var table =

        document.getElementById(
            "stockTable"
        );


    var rows =

        table
        .getElementsByTagName(
            "tbody"
        )[0]
        .getElementsByTagName(
            "tr"
        );


    var visibleCount = 0;


    for (

        var i = 0;

        i < rows.length;

        i++

    ) {


        var row = rows[i];


        var distance = parseFloat(

            row.getAttribute(
                "data-distance"
            )

        );


        var monthlyRise = parseFloat(

            row.getAttribute(
                "data-monthly-rise"
            )

        );


        var rowText =

            row.innerText
            .toUpperCase();


        var distanceMatch =

            distance >= distanceFilter;


        var monthlyRiseMatch =

            monthlyRise >= monthlyRiseFilter;


        var searchMatch =

            rowText.indexOf(
                searchText
            ) > -1;


        if (

            distanceMatch

            &&

            monthlyRiseMatch

            &&

            searchMatch

        ) {


            row.style.display = "";

            visibleCount++;


        }

        else {


            row.style.display = "none";


        }


    }


    document.getElementById(
        "resultInfo"
    ).innerHTML =

        "Stocks matching filters: "

        +

        visibleCount;


}


function resetFilters() {


    document.getElementById(
        "distanceFilter"
    ).value = -10;


    document.getElementById(
        "monthlyRiseFilter"
    ).value = 2;


    document.getElementById(
        "searchInput"
    ).value = "";


    applyFilters();


}


document.addEventListener(

    "DOMContentLoaded",

    function() {

        applyFilters();

    }

);


document.getElementById(
    "searchInput"
).addEventListener(

    "keyup",

    function() {

        applyFilters();

    }

);


</script>


</body>


</html>

"""


    return html


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():


    print("=" * 70)

    print(
        "NIFTY 100 MWD + 52 WEEK HIGH SCREENER"
    )

    print("=" * 70)


    # Load CSV

    df = load_symbols()


    print(
        f"Total Stocks Loaded: {len(df)}"
    )


    results = []


    # ========================================================
    # PROCESS STOCKS
    # ========================================================

    for index, row in df.iterrows():


        symbol = str(
            row["symbol"]
        ).strip()


        company = str(
            row["company"]
        ).strip()


        result = analyze_stock(

            symbol,

            company

        )


        if result:

            results.append(result)


        # Avoid Yahoo Finance rate limiting

        time.sleep(0.4)


    # ========================================================
    # SORT RESULTS
    # Priority:
    # 1. Nearest to 52 Week High
    # ========================================================

    results = sorted(

        results,

        key=lambda x: x["distance_52w"],

        reverse=True

    )


    # ========================================================
    # CREATE DOCS FOLDER
    # ========================================================

    os.makedirs(

        "docs",

        exist_ok=True

    )


    # ========================================================
    # GENERATE HTML
    # ========================================================

    html = generate_html(results)


    with open(

        OUTPUT_FILE,

        "w",

        encoding="utf-8"

    ) as f:


        f.write(html)


    # ========================================================
    # SUMMARY
    # ========================================================

    print()

    print("=" * 70)

    print(
        f"TOTAL MWD MATCHES BELOW 52W HIGH: "
        f"{len(results)}"
    )

    print()

    print(
        f"HTML GENERATED: "
        f"{OUTPUT_FILE}"
    )

    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()
