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

RESULTS = []


# ============================================================
# FUNCTION: CHECK BULLISH CANDLE
# ============================================================

def is_bullish(open_price, close_price):

    if pd.isna(open_price) or pd.isna(close_price):
        return False

    return close_price > open_price


# ============================================================
# FUNCTION: GET STOCK DATA
# ============================================================

def analyze_stock(symbol, company):

    yahoo_symbol = symbol + ".NS"

    print(f"Processing: {symbol}")

    try:

        ticker = yf.Ticker(yahoo_symbol)

        # ----------------------------------------------------
        # DAILY DATA
        # ----------------------------------------------------

        daily = ticker.history(
            period="3mo",
            interval="1d",
            auto_adjust=False
        )


        # ----------------------------------------------------
        # WEEKLY DATA
        # ----------------------------------------------------

        weekly = ticker.history(
            period="1y",
            interval="1wk",
            auto_adjust=False
        )


        # ----------------------------------------------------
        # MONTHLY DATA
        # ----------------------------------------------------

        monthly = ticker.history(
            period="3y",
            interval="1mo",
            auto_adjust=False
        )


        # Validate data

        if daily.empty:
            print(f"No daily data for {symbol}")
            return None

        if weekly.empty:
            print(f"No weekly data for {symbol}")
            return None

        if monthly.empty:
            print(f"No monthly data for {symbol}")
            return None


        # ====================================================
        # IMPORTANT:
        # USE LAST COMPLETED CANDLE
        # ====================================================

        # Daily:
        # Latest row is normally latest trading day
        daily_candle = daily.iloc[-1]


        # Weekly:
        # Use previous completed week
        if len(weekly) < 2:
            return None

        weekly_candle = weekly.iloc[-2]


        # Monthly:
        # Use previous completed month
        if len(monthly) < 2:
            return None

        monthly_candle = monthly.iloc[-2]


        # ====================================================
        # CHECK DAILY BULLISH
        # ====================================================

        daily_bullish = is_bullish(
            daily_candle["Open"],
            daily_candle["Close"]
        )


        # ====================================================
        # CHECK WEEKLY BULLISH
        # ====================================================

        weekly_bullish = is_bullish(
            weekly_candle["Open"],
            weekly_candle["Close"]
        )


        # ====================================================
        # CHECK MONTHLY BULLISH
        # ====================================================

        monthly_bullish = is_bullish(
            monthly_candle["Open"],
            monthly_candle["Close"]
        )


        # ====================================================
        # MWD LOGIC
        # ====================================================

        if (
            monthly_bullish
            and weekly_bullish
            and daily_bullish
        ):


            last_price = daily_candle["Close"]


            result = {

                "symbol": symbol,

                "company": company,

                "last_price": round(float(last_price), 2),

                "daily_open": round(
                    float(daily_candle["Open"]), 2
                ),

                "daily_close": round(
                    float(daily_candle["Close"]), 2
                ),

                "weekly_open": round(
                    float(weekly_candle["Open"]), 2
                ),

                "weekly_close": round(
                    float(weekly_candle["Close"]), 2
                ),

                "monthly_open": round(
                    float(monthly_candle["Open"]), 2
                ),

                "monthly_close": round(
                    float(monthly_candle["Close"]), 2
                )

            }


            print(
                f"MATCH FOUND: {symbol} | "
                f"Price: {last_price}"
            )


            return result


        return None


    except Exception as e:

        print(
            f"Error processing {symbol}: {str(e)}"
        )

        return None


# ============================================================
# READ CSV
# ============================================================

def load_symbols():

    try:

        df = pd.read_csv(CSV_FILE)

        df.columns = df.columns.str.strip().str.lower()


        if "symbol" not in df.columns:

            raise Exception(
                "CSV must contain column: symbol"
            )


        if "company" not in df.columns:

            df["company"] = df["symbol"]


        return df


    except Exception as e:

        print(f"Error reading CSV: {e}")

        raise


# ============================================================
# CREATE HTML
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

<title>Nifty 100 MWD Screener</title>


<style>


body {{

    font-family: Arial, sans-serif;

    background: #f4f6f9;

    margin: 0;

    padding: 20px;

}}


.container {{

    max-width: 1200px;

    margin: auto;

}}


.header {{

    background: linear-gradient(
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

}}


.stats {{

    display: flex;

    gap: 20px;

    margin-top: 20px;

    flex-wrap: wrap;

}}


.card {{

    background: white;

    padding: 20px;

    border-radius: 10px;

    box-shadow:
    0 2px 10px rgba(0,0,0,0.08);

    min-width: 180px;

}}


.card h3 {{

    margin: 0;

    color: #555;

}}


.card h2 {{

    margin-top: 10px;

}}


table {{

    width: 100%;

    border-collapse: collapse;

    background: white;

    box-shadow:
    0 2px 10px rgba(0,0,0,0.08);

}}


th {{

    background: #1f4e78;

    color: white;

    padding: 14px;

    text-align: left;

}}


td {{

    padding: 12px;

    border-bottom:
    1px solid #ddd;

}}


tr:hover {{

    background: #f1f5f9;

}}


.bullish {{

    color: green;

    font-weight: bold;

}}


.price {{

    font-weight: bold;

    font-size: 16px;

}}


.search-box {{

    width: 100%;

    padding: 12px;

    margin-bottom: 15px;

    border-radius: 8px;

    border: 1px solid #ccc;

    font-size: 16px;

}}


.footer {{

    text-align: center;

    margin-top: 30px;

    color: #777;

}}


@media(max-width:768px) {{

    table {{

        font-size: 12px;

    }}

}}


</style>


</head>


<body>


<div class="container">


<div class="header">


<h1>📈 NIFTY 100 MWD SCREENER</h1>


<p>

Monthly + Weekly + Daily
All Bullish Stocks

</p>


<div class="stats">


<div class="card">

<h3>Total Matches</h3>

<h2>{total_stocks}</h2>

</div>


<div class="card">

<h3>Last Updated</h3>

<h2>{current_time}</h2>

</div>


</div>


</div>


<input

type="text"

id="searchInput"

class="search-box"

placeholder="Search Stock..."

onkeyup="searchTable()"

/>


<table id="stockTable">


<thead>

<tr>

<th>#</th>

<th>Symbol</th>

<th>Company</th>

<th>Last Price</th>

<th>Daily</th>

<th>Weekly</th>

<th>Monthly</th>

</tr>

</thead>


<tbody>

"""


    if results:

        for index, stock in enumerate(results, start=1):


            html += f"""

<tr>

<td>{index}</td>

<td>

<b>{stock["symbol"]}</b>

</td>


<td>

{stock["company"]}

</td>


<td class="price">

₹ {stock["last_price"]:,.2f}

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

<td colspan="7"
style="text-align:center;padding:30px">

No stocks found matching
Monthly + Weekly + Daily Bullish condition.

</td>

</tr>

"""


    html += """

</tbody>

</table>


<div class="footer">

<p>

Data Source: Yahoo Finance |

This screener is for educational purposes only.

</p>

</div>


</div>


<script>


function searchTable() {


    var input =
    document.getElementById(
        "searchInput"
    );


    var filter =
    input.value.toUpperCase();


    var table =
    document.getElementById(
        "stockTable"
    );


    var tr =
    table.getElementsByTagName(
        "tr"
    );


    for (
        var i = 1;
        i < tr.length;
        i++
    ) {


        var td =
        tr[i].getElementsByTagName(
            "td"
        );


        if (td.length > 0) {


            var text =
            tr[i].innerText;


            if (
                text.toUpperCase()
                .indexOf(filter)
                > -1
            ) {


                tr[i].style.display = "";


            } else {


                tr[i].style.display = "none";


            }

        }

    }

}


</script>


</body>

</html>

"""


    return html


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)

    print("NIFTY 100 MWD SCREENER")

    print("=" * 60)


    df = load_symbols()


    print(
        f"Total Stocks Loaded: {len(df)}"
    )


    results = []


    for index, row in df.iterrows():

        symbol = str(row["symbol"]).strip()

        company = str(row["company"]).strip()


        result = analyze_stock(
            symbol,
            company
        )


        if result:

            results.append(result)


        # Avoid Yahoo Finance rate limit

        time.sleep(0.3)


    # ========================================================
    # SORT BY SYMBOL
    # ========================================================

    results = sorted(
        results,
        key=lambda x: x["symbol"]
    )


    # ========================================================
    # CREATE DOCS DIRECTORY
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


    print("=" * 60)

    print(
        f"TOTAL MATCHES: {len(results)}"
    )

    print(
        f"HTML GENERATED: {OUTPUT_FILE}"
    )

    print("=" * 60)


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    main()
