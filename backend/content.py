"""Static curriculum content for TradeQuest — Duolingo-style stock learning."""

UNITS = [
    {
        "id": "u1",
        "title": "Stock Market Basics",
        "subtitle": "What stocks are and why they exist",
        "color": "#10B981",
        "lessons": [
            {
                "id": "l1", "title": "What Is a Stock?", "icon": "trending-up", "xp": 20,
                "cards": [
                    {"heading": "A share of ownership", "body": "A stock is a tiny slice of ownership in a company. Buy one share and you literally own a piece of that business."},
                    {"heading": "Why companies sell stock", "body": "Companies sell shares to raise money for growth — building factories, hiring people, or launching products — without taking on debt."},
                    {"heading": "You are a shareholder", "body": "As a shareholder you may gain if the company grows in value, and sometimes receive a share of profits called a dividend."},
                ],
                "questions": [
                    {"q": "What does owning a stock represent?", "options": ["A loan to the company", "A slice of ownership in the company", "A guaranteed monthly salary", "A government bond"], "answer": 1, "explain": "A stock is partial ownership of a company."},
                    {"q": "Why do companies issue stock?", "options": ["To raise money for growth", "To pay taxes", "To avoid making products", "To reduce their value"], "answer": 0, "explain": "Issuing shares raises capital without borrowing."},
                    {"q": "A person who owns shares is called a…", "options": ["Lender", "Shareholder", "Customer", "Auditor"], "answer": 1, "explain": "Owners of shares are shareholders."},
                ],
            },
            {
                "id": "l2", "title": "Stock Exchanges", "icon": "bank", "xp": 20,
                "cards": [
                    {"heading": "The marketplace", "body": "A stock exchange is a marketplace where buyers and sellers trade shares. The NYSE and Nasdaq are two of the largest."},
                    {"heading": "Matching orders", "body": "Exchanges match buy and sell orders and publish the latest price everyone can see, keeping trading fair and transparent."},
                    {"heading": "Ticker symbols", "body": "Each company gets a short ticker symbol — AAPL for Apple, TSLA for Tesla — used to look up and trade the stock quickly."},
                ],
                "questions": [
                    {"q": "What is a stock exchange?", "options": ["A bank vault", "A marketplace for trading shares", "A type of tax", "A company's warehouse"], "answer": 1, "explain": "Exchanges are marketplaces matching buyers and sellers."},
                    {"q": "AAPL is the ticker symbol for…", "options": ["Amazon", "Apple", "Alphabet", "AMD"], "answer": 1, "explain": "AAPL represents Apple Inc."},
                    {"q": "Which is a major US stock exchange?", "options": ["Nasdaq", "FIFA", "NASA", "IKEA"], "answer": 0, "explain": "Nasdaq is a major exchange, along with the NYSE."},
                ],
            },
            {
                "id": "l3", "title": "Bulls vs Bears", "icon": "chart-line", "xp": 25,
                "cards": [
                    {"heading": "Bull market", "body": "A bull market is when prices are rising and optimism is high. Think of a bull thrusting its horns upward."},
                    {"heading": "Bear market", "body": "A bear market is a prolonged drop of 20% or more, with pessimism. Picture a bear swiping its paw downward."},
                    {"heading": "Sentiment moves markets", "body": "Prices reflect how hopeful or fearful investors feel about the future, not just today's facts."},
                ],
                "questions": [
                    {"q": "A rising, optimistic market is called…", "options": ["Bear market", "Bull market", "Flat market", "Dead market"], "answer": 1, "explain": "Bulls charge upward — rising prices."},
                    {"q": "A bear market usually means prices…", "options": ["Rise sharply", "Stay exactly flat", "Fall significantly", "Get deleted"], "answer": 2, "explain": "Bear markets are extended declines of 20%+."},
                    {"q": "Market sentiment refers to…", "options": ["Investor mood and outlook", "The building's temperature", "Company payroll", "Tax rates"], "answer": 0, "explain": "Sentiment is the collective mood of investors."},
                ],
            },
        ],
    },
    {
        "id": "u2",
        "title": "How Stocks Work",
        "subtitle": "Prices, dividends and returns",
        "color": "#F59E0B",
        "lessons": [
            {
                "id": "l4", "title": "What Moves Prices", "icon": "swap-vertical", "xp": 25,
                "cards": [
                    {"heading": "Supply and demand", "body": "If more people want to buy a stock than sell it, the price rises. If more want to sell, it falls."},
                    {"heading": "News and earnings", "body": "Strong profits, new products, or good news attract buyers. Bad news or weak earnings push prices down."},
                    {"heading": "The whole market", "body": "Interest rates, the economy, and global events can move nearly all stocks at once."},
                ],
                "questions": [
                    {"q": "If demand for a stock exceeds supply, the price tends to…", "options": ["Fall", "Rise", "Freeze", "Disappear"], "answer": 1, "explain": "More buyers than sellers pushes prices up."},
                    {"q": "Which often boosts a stock price?", "options": ["Strong earnings report", "A product recall", "A lawsuit loss", "Falling sales"], "answer": 0, "explain": "Good earnings attract buyers."},
                    {"q": "What can move almost all stocks at once?", "options": ["One customer's opinion", "Interest rate changes", "A single tweet with no reach", "The company logo"], "answer": 1, "explain": "Macro factors like rates affect the whole market."},
                ],
            },
            {
                "id": "l5", "title": "Dividends", "icon": "cash", "xp": 25,
                "cards": [
                    {"heading": "Sharing the profit", "body": "A dividend is a cash payment some companies send shareholders from their profits, often every quarter."},
                    {"heading": "Dividend yield", "body": "Yield = annual dividend ÷ share price. A $2 dividend on a $100 stock is a 2% yield."},
                    {"heading": "Not everyone pays", "body": "Fast-growing companies often reinvest profits instead of paying dividends, aiming for bigger future growth."},
                ],
                "questions": [
                    {"q": "A dividend is…", "options": ["A penalty fee", "A share of profits paid to owners", "A type of loan", "A trading tax"], "answer": 1, "explain": "Dividends distribute profits to shareholders."},
                    {"q": "A $4 annual dividend on a $100 stock is a yield of…", "options": ["0.4%", "4%", "40%", "14%"], "answer": 1, "explain": "4 ÷ 100 = 4%."},
                    {"q": "Growth companies often…", "options": ["Reinvest profits instead of paying dividends", "Always pay huge dividends", "Never make profit", "Pay dividends daily"], "answer": 0, "explain": "They reinvest to fuel growth."},
                ],
            },
            {
                "id": "l6", "title": "Risk & Return", "icon": "shield", "xp": 30,
                "cards": [
                    {"heading": "The trade-off", "body": "Higher potential returns usually come with higher risk. Safer assets tend to grow more slowly."},
                    {"heading": "Volatility", "body": "Volatility is how much a price swings up and down. High volatility means bigger, faster moves."},
                    {"heading": "Time horizon", "body": "The longer you can stay invested, the more short-term swings tend to smooth out."},
                ],
                "questions": [
                    {"q": "Higher potential return usually means…", "options": ["Lower risk", "Higher risk", "No risk", "Guaranteed profit"], "answer": 1, "explain": "Risk and reward move together."},
                    {"q": "Volatility measures…", "options": ["Company age", "Price swing size", "Number of employees", "Dividend dates"], "answer": 1, "explain": "Volatility is the size of price swings."},
                    {"q": "A longer time horizon tends to…", "options": ["Amplify daily swings forever", "Smooth out short-term swings", "Guarantee losses", "Remove all risk"], "answer": 1, "explain": "Time helps smooth volatility."},
                ],
            },
        ],
    },
    {
        "id": "u3",
        "title": "Reading the Market",
        "subtitle": "Indexes, orders and charts",
        "color": "#10B981",
        "lessons": [
            {
                "id": "l7", "title": "Market Indexes", "icon": "list", "xp": 30,
                "cards": [
                    {"heading": "A market scoreboard", "body": "An index tracks a group of stocks to show how a market is doing overall — like a scoreboard."},
                    {"heading": "Famous indexes", "body": "The S&P 500 tracks 500 large US companies. The Nasdaq-100 is tech-heavy. The Dow tracks 30 big names."},
                    {"heading": "Why they matter", "body": "Indexes are benchmarks. Investors compare their returns against them to see if they're beating the market."},
                ],
                "questions": [
                    {"q": "A stock index is best described as…", "options": ["A single company", "A scoreboard for a group of stocks", "A bank account", "A tax form"], "answer": 1, "explain": "Indexes summarize a group of stocks."},
                    {"q": "The S&P 500 tracks roughly…", "options": ["5 companies", "50 companies", "500 large US companies", "5000 companies"], "answer": 2, "explain": "It tracks 500 large US firms."},
                    {"q": "Investors use indexes as…", "options": ["Benchmarks to compare returns", "Cooking recipes", "Legal contracts", "Passwords"], "answer": 0, "explain": "Indexes are performance benchmarks."},
                ],
            },
            {
                "id": "l8", "title": "Order Types", "icon": "cursor", "xp": 30,
                "cards": [
                    {"heading": "Market order", "body": "A market order buys or sells immediately at the best available price. Fast, but the exact price isn't guaranteed."},
                    {"heading": "Limit order", "body": "A limit order only executes at your chosen price or better. You control price, but it may not fill."},
                    {"heading": "Stop order", "body": "A stop order triggers a trade once a price level is hit — often used to limit losses."},
                ],
                "questions": [
                    {"q": "A market order prioritizes…", "options": ["Exact price", "Speed of execution", "Avoiding trades", "Dividends"], "answer": 1, "explain": "Market orders fill fast at the best available price."},
                    {"q": "A limit order lets you…", "options": ["Set the price you'll accept", "Skip the exchange", "Guarantee a fill", "Avoid all fees"], "answer": 0, "explain": "Limit orders control the execution price."},
                    {"q": "A stop order is often used to…", "options": ["Limit potential losses", "Pay dividends", "Register a company", "Increase volatility"], "answer": 0, "explain": "Stops help cap losses."},
                ],
            },
            {
                "id": "l9", "title": "Reading a Chart", "icon": "chart-bar", "xp": 35,
                "cards": [
                    {"heading": "Price over time", "body": "A chart plots price on the vertical axis and time across the bottom, showing the story of a stock's moves."},
                    {"heading": "Trends", "body": "An uptrend makes higher highs and higher lows. A downtrend makes lower highs and lower lows."},
                    {"heading": "Volume", "body": "Volume shows how many shares traded. Big moves on high volume are seen as more meaningful."},
                ],
                "questions": [
                    {"q": "On a standard chart, time is shown on the…", "options": ["Vertical axis", "Horizontal axis", "Company logo", "Ticker"], "answer": 1, "explain": "Time runs along the horizontal axis."},
                    {"q": "An uptrend is a series of…", "options": ["Lower highs and lower lows", "Higher highs and higher lows", "Flat lines only", "Random dots"], "answer": 1, "explain": "Uptrends climb with higher highs and lows."},
                    {"q": "Trading volume measures…", "options": ["Shares traded", "Company age", "Dividend size", "CEO salary"], "answer": 0, "explain": "Volume is the number of shares traded."},
                ],
            },
        ],
    },
    {
        "id": "u4",
        "title": "Fundamental Analysis",
        "subtitle": "Judging a company's value",
        "color": "#F59E0B",
        "lessons": [
            {
                "id": "l10", "title": "Earnings & Revenue", "icon": "receipt", "xp": 35,
                "cards": [
                    {"heading": "Revenue vs profit", "body": "Revenue is total money coming in. Profit (earnings) is what's left after all costs are paid."},
                    {"heading": "Earnings season", "body": "Every quarter companies report results. Beating expectations often lifts the stock; missing can sink it."},
                    {"heading": "EPS", "body": "Earnings per share (EPS) is profit divided by number of shares — a quick read on profitability per share."},
                ],
                "questions": [
                    {"q": "Profit is revenue minus…", "options": ["Nothing", "All costs and expenses", "Dividends only", "The stock price"], "answer": 1, "explain": "Profit is what remains after costs."},
                    {"q": "EPS stands for…", "options": ["Extra Profit Sum", "Earnings Per Share", "Equity Price Scale", "Exchange Priority System"], "answer": 1, "explain": "EPS = Earnings Per Share."},
                    {"q": "Beating earnings expectations often…", "options": ["Lifts the stock", "Delists the company", "Cancels dividends", "Has no effect ever"], "answer": 0, "explain": "Beats tend to push prices up."},
                ],
            },
            {
                "id": "l11", "title": "The P/E Ratio", "icon": "calculator", "xp": 35,
                "cards": [
                    {"heading": "Price to earnings", "body": "The P/E ratio = share price ÷ earnings per share. It shows how much investors pay for $1 of earnings."},
                    {"heading": "High vs low", "body": "A high P/E can mean high growth expectations — or an overpriced stock. Low P/E may signal value or trouble."},
                    {"heading": "Compare fairly", "body": "P/E is most useful when comparing similar companies in the same industry."},
                ],
                "questions": [
                    {"q": "The P/E ratio compares price to…", "options": ["Revenue", "Earnings per share", "Dividends", "Volume"], "answer": 1, "explain": "P/E = price ÷ EPS."},
                    {"q": "A very high P/E often reflects…", "options": ["High growth expectations", "Zero interest", "A guaranteed crash", "No earnings ever"], "answer": 0, "explain": "High P/E implies growth expectations."},
                    {"q": "P/E is most meaningful when…", "options": ["Comparing similar companies", "Comparing a bank to a bakery", "Ignoring the industry", "Used on random numbers"], "answer": 0, "explain": "Compare within the same industry."},
                ],
            },
            {
                "id": "l12", "title": "Market Cap", "icon": "globe", "xp": 40,
                "cards": [
                    {"heading": "Company size", "body": "Market capitalization = share price × total shares. It's the market's price tag for the whole company."},
                    {"heading": "Size buckets", "body": "Large-cap (huge, stable), mid-cap (growing), and small-cap (smaller, riskier, higher growth potential)."},
                    {"heading": "Price ≠ size", "body": "A $500 stock isn't automatically 'bigger' than a $10 stock — it depends on how many shares exist."},
                ],
                "questions": [
                    {"q": "Market cap equals share price times…", "options": ["Total shares outstanding", "The P/E ratio", "Revenue", "Dividend yield"], "answer": 0, "explain": "Market cap = price × shares."},
                    {"q": "Large-cap companies are generally…", "options": ["Tiny and risky", "Huge and more stable", "Always unprofitable", "Private only"], "answer": 1, "explain": "Large-caps are big and relatively stable."},
                    {"q": "A higher share price alone means the company is bigger. True or false?", "options": ["True", "False"], "answer": 1, "explain": "Size depends on shares outstanding too."},
                ],
            },
        ],
    },
    {
        "id": "u5",
        "title": "Smart Investing",
        "subtitle": "Strategies that stand the test of time",
        "color": "#10B981",
        "lessons": [
            {
                "id": "l13", "title": "Diversification", "icon": "grid", "xp": 40,
                "cards": [
                    {"heading": "Don't put all eggs in one basket", "body": "Spreading money across many stocks and sectors reduces the damage if any single one falls."},
                    {"heading": "Funds make it easy", "body": "Index funds and ETFs bundle hundreds of stocks in one purchase — instant diversification."},
                    {"heading": "Lower risk, steadier ride", "body": "Diversification won't remove all risk, but it smooths returns and protects against single-company disasters."},
                ],
                "questions": [
                    {"q": "Diversification means…", "options": ["Buying one stock only", "Spreading investments across many", "Timing the market daily", "Avoiding all stocks"], "answer": 1, "explain": "Spread risk across many holdings."},
                    {"q": "An easy way to diversify is to buy…", "options": ["An index fund or ETF", "A single share", "Only your employer's stock", "Lottery tickets"], "answer": 0, "explain": "ETFs bundle many stocks at once."},
                    {"q": "Diversification mainly reduces…", "options": ["Single-company risk", "Your age", "Trading hours", "Ticker length"], "answer": 0, "explain": "It cushions single-company blowups."},
                ],
            },
            {
                "id": "l14", "title": "Dollar-Cost Averaging", "icon": "clock", "xp": 40,
                "cards": [
                    {"heading": "Invest on a schedule", "body": "Dollar-cost averaging means investing a fixed amount regularly, no matter the price."},
                    {"heading": "Smooths out timing", "body": "You buy more shares when prices are low and fewer when high, averaging your cost over time."},
                    {"heading": "Beats guessing", "body": "It removes the stress of trying to perfectly time the market, which even pros rarely do well."},
                ],
                "questions": [
                    {"q": "Dollar-cost averaging invests…", "options": ["A fixed amount on a schedule", "Everything at once at the top", "Only when scared", "Never"], "answer": 0, "explain": "Fixed amounts at regular intervals."},
                    {"q": "When prices are low, a fixed amount buys…", "options": ["Fewer shares", "More shares", "No shares", "Only bonds"], "answer": 1, "explain": "Lower prices buy more shares."},
                    {"q": "A key benefit is…", "options": ["Removing market-timing stress", "Guaranteeing profit", "Avoiding all taxes", "Doubling money monthly"], "answer": 0, "explain": "It avoids the need to time the market."},
                ],
            },
            {
                "id": "l15", "title": "Long-Term Mindset", "icon": "trophy", "xp": 50,
                "cards": [
                    {"heading": "Compounding is magic", "body": "Reinvested gains earn their own gains. Over decades this snowball can grow surprisingly large."},
                    {"heading": "Stay the course", "body": "Panic-selling in downturns locks in losses. History shows markets have trended upward over long periods."},
                    {"heading": "Time in the market", "body": "'Time in the market beats timing the market.' Consistency usually wins over clever guessing."},
                ],
                "questions": [
                    {"q": "Compounding means…", "options": ["Gains earning their own gains", "Losing money slowly", "Paying more tax", "Selling everything"], "answer": 0, "explain": "Reinvested gains compound over time."},
                    {"q": "Panic-selling in a downturn tends to…", "options": ["Lock in losses", "Guarantee gains", "Pause the market", "Raise dividends"], "answer": 0, "explain": "Selling low locks in losses."},
                    {"q": "The saying goes: time in the market beats…", "options": ["Timing the market", "Saving money", "Reading charts", "Diversifying"], "answer": 0, "explain": "Consistency beats trying to time tops and bottoms."},
                ],
            },
        ],
    },
]

# Flatten lessons for quick lookup
LESSON_MAP = {}
LESSON_ORDER = []
for _u in UNITS:
    for _l in _u["lessons"]:
        LESSON_MAP[_l["id"]] = {**_l, "unit_id": _u["id"], "unit_title": _u["title"], "unit_color": _u["color"]}
        LESSON_ORDER.append(_l["id"])


BADGES = [
    {"id": "first_step", "name": "First Step", "desc": "Complete your first lesson", "icon": "flag"},
    {"id": "streak_3", "name": "On Fire", "desc": "Reach a 3-day streak", "icon": "flame"},
    {"id": "streak_7", "name": "Unstoppable", "desc": "Reach a 7-day streak", "icon": "flame"},
    {"id": "perfectionist", "name": "Perfectionist", "desc": "Ace a lesson with a perfect score", "icon": "star"},
    {"id": "half_way", "name": "Halfway There", "desc": "Complete 8 lessons", "icon": "medal"},
    {"id": "graduate", "name": "Market Graduate", "desc": "Complete all lessons", "icon": "trophy"},
    {"id": "level_5", "name": "Rising Investor", "desc": "Reach level 5", "icon": "trending-up"},
    {"id": "xp_500", "name": "XP Hunter", "desc": "Earn 500 total XP", "icon": "bolt"},
]
BADGE_MAP = {b["id"]: b for b in BADGES}
