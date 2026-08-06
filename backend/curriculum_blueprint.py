"""Qapilo 50-unit curriculum blueprint.

Pedagogical design only (titles, themes, difficulty tiers). The teaching cards
and quiz questions are generated per lesson in EN/DE/ES by generate_curriculum.py
and stored in curriculum_data.json.

5 tiers x 10 units. Difficulty rises every tier (every 10 units). XP per lesson
scales with tier so harder lessons reward more points.
"""

TIER_META = {
    1: {"color": "#10B981", "xp": 10,
        "difficulty": ("Absolute beginner with ZERO finance knowledge. Money basics, its history and "
                       "everyday value. Warm everyday analogies, very short simple sentences, no jargon. "
                       "Easy, intuitive, encouraging questions.")},
    2: {"color": "#F59E0B", "xp": 12,
        "difficulty": ("Beginner. Personal finance: budgeting, saving, debt, interest, emergency funds and "
                       "goals. Friendly and concrete with simple everyday examples. Questions test basic "
                       "understanding.")},
    3: {"color": "#3B82F6", "xp": 14,
        "difficulty": ("Beginner+ learning to invest: return, risk, time horizon, plans and diversification. "
                       "Simple concrete examples and small numbers. Questions apply the ideas.")},
    4: {"color": "#8B5CF6", "xp": 16,
        "difficulty": ("Intermediate. Stocks and companies: shares, exchanges, dividends and business basics. "
                       "Clear concrete examples. Questions require applying concepts.")},
    5: {"color": "#EC4899", "xp": 18,
        "difficulty": ("Intermediate. Funds and asset classes: indexes, ETFs, bonds, real estate, commodities "
                       "and crypto. Concrete examples with small numbers. Applied questions.")},
    6: {"color": "#14B8A6", "xp": 20,
        "difficulty": ("Upper-intermediate. Company analysis: statements, cash flow, ratios, moats and "
                       "valuation. Use real ratios and numeric examples. Questions involve calculation or "
                       "judgement.")},
    7: {"color": "#6366F1", "xp": 22,
        "difficulty": ("Advanced. Portfolio construction and investor psychology: allocation, rebalancing, "
                       "volatility, correlation and behavioural biases. Precise and concise. Nuanced questions.")},
    8: {"color": "#F97316", "xp": 24,
        "difficulty": ("Advanced. Macroeconomics and markets: cycles, central banks, rates, currencies, bonds "
                       "and inflation. Concrete and precise. Questions test cause-and-effect reasoning.")},
    9: {"color": "#06B6D4", "xp": 27,
        "difficulty": ("Professional-level. Factor investing, value/growth/quality/momentum, options and futures "
                       "basics, risk metrics and optimization. Rigorous yet clear. Challenging questions.")},
    10: {"color": "#A855F7", "xp": 30,
        "difficulty": ("Expert but still educational. DCF, cost of capital, scenario and Monte-Carlo concepts, "
                       "derivatives, institutional investing, PE/VC/hedge funds, wealth protection and strategy. "
                       "Precise, well-explained, demanding questions.")},
}

ICONS = ["trending-up", "bank", "chart-line", "swap-vertical", "cash", "shield",
         "list", "cursor", "chart-bar", "receipt", "calculator", "globe", "grid", "clock"]

# Each unit: (title, subtitle, [3 lesson (title, focus) tuples])
BLUEPRINT = [
    # ---------------- Tier 1: Money & Investing Foundations (u1-u10) ----------------
    (1, "Money, Made Simple", "What money is and how it grows", [
        ("What Is Money?", "Money as a tool we trade for things; a simple everyday picture."),
        ("Saving vs Spending", "Keeping some money for later versus using it now, with a piggy-bank analogy."),
        ("Why Money Shrinks", "Inflation explained simply: things slowly cost more, so saved cash buys less."),
    ]),
    (1, "What Is Investing?", "Putting money to work", [
        ("Growing Your Money", "Investing means using money to try to make more, like planting a seed."),
        ("Saving vs Investing", "Saving is safe and small; investing can grow more but can go up and down."),
        ("Risk and Reward", "Bigger possible rewards usually come with bigger ups and downs."),
    ]),
    (1, "Meet the Stock Market", "Where people buy pieces of companies", [
        ("What Is a Company?", "A business that sells things to make money, using a lemonade-stand analogy."),
        ("A Share Is a Slice", "A share is a tiny slice of a company you can own."),
        ("Why Buy Shares?", "People buy shares hoping the company grows and their slice becomes worth more."),
    ]),
    (1, "Owning a Piece", "What it means to be a part-owner", [
        ("You're an Owner", "Owning shares makes you a part-owner called a shareholder."),
        ("Going Public", "When a private company sells shares to everyone for the first time, in plain words."),
        ("Companies You Know", "Familiar brands are public companies anyone can own a slice of."),
    ]),
    (1, "Why Prices Move", "The simple reason prices change", [
        ("Buyers and Sellers", "Prices rise when more people want to buy, fall when more want to sell."),
        ("Good News, Bad News", "Good news attracts buyers; bad news makes people sell."),
        ("An Everyday Example", "A relatable example (concert tickets / sneakers) showing demand moving price."),
    ]),
    (1, "Growing Money Over Time", "Patience and compounding, simply", [
        ("The Snowball Effect", "Compounding: your gains start earning their own gains, like a rolling snowball."),
        ("Starting Small", "Even tiny amounts invested regularly can grow big over many years."),
        ("Time Is Your Friend", "The earlier you start, the more time your money has to grow."),
    ]),
    (1, "Risk and Staying Safe", "Handling ups and downs", [
        ("Don't Risk It All", "Never invest money you need soon; only spare money you can leave alone."),
        ("Many Baskets", "Spreading money across things so one bad pick can't hurt you much."),
        ("Ups and Downs Are Normal", "Prices wobble; staying calm beats panicking."),
    ]),
    (1, "How to Buy Stocks", "Your first practical steps", [
        ("What Is a Broker?", "A broker or app lets you buy and sell shares easily."),
        ("Opening an Account", "The simple idea of setting up an investing account."),
        ("Your First Share", "How buying a single share actually works, step by step, simply."),
    ]),
    (1, "Good Money Habits", "Habits that build wealth", [
        ("Invest Regularly", "Adding a little money on a schedule builds a habit and smooths ups and downs."),
        ("Think Long Term", "Wealth usually grows over years, not days."),
        ("Avoid Panic", "Selling in fear often locks in losses; a calm plan wins."),
    ]),
    (1, "Everyday Market Words", "The starter vocabulary", [
        ("Ticker and Portfolio", "A ticker is a short code; a portfolio is all your investments together."),
        ("Dividends Are Gifts", "Some companies share profits with owners as small cash payments."),
        ("Quick Recap", "A friendly recap tying together the foundations you've learned."),
    ]),

    # ---------------- Tier 2: Stock Market Essentials (u11-u20) ----------------
    (2, "Stock Market Basics", "What stocks are and why they exist", [
        ("What Is a Stock?", "A stock is partial ownership of a company; shareholders can gain from growth."),
        ("Stock Exchanges", "Marketplaces like the NYSE and Nasdaq match buyers and sellers; ticker symbols."),
        ("Bulls vs Bears", "Bull markets rise on optimism; bear markets fall 20%+ on pessimism; sentiment."),
    ]),
    (2, "How Stocks Work", "Prices, dividends and returns", [
        ("What Moves Prices", "Supply and demand, news and earnings, and market-wide forces move prices."),
        ("Dividends", "Cash paid from profits; dividend yield = annual dividend / price; not all pay."),
        ("Capital Gains", "Profit from selling higher than you bought; the other way stocks make money."),
    ]),
    (2, "Returns and Growth", "Measuring how you do", [
        ("Total Return", "Total return combines price change plus dividends."),
        ("Percentages Matter", "Why returns are measured in % so amounts of any size compare fairly."),
        ("Reinvesting", "Reinvesting dividends and gains speeds up compounding."),
    ]),
    (2, "Types of Stocks", "Not all stocks are alike", [
        ("Growth vs Value", "Growth stocks reinvest for fast expansion; value stocks look cheap vs worth."),
        ("Blue Chips", "Large, stable, well-known companies with long track records."),
        ("Small vs Large Caps", "Company size (market cap) and what it means for risk and growth."),
    ]),
    (2, "Market Indices", "Tracking the whole market", [
        ("What Is an Index?", "An index tracks a basket of stocks to show how a market is doing."),
        ("S&P 500 and Dow", "The S&P 500 tracks 500 big US firms; the Dow tracks 30; what they signal."),
        ("Nasdaq and Others", "The Nasdaq is tech-heavy; other global indices exist too."),
    ]),
    (2, "Placing Orders", "How trades actually happen", [
        ("Market Orders", "A market order buys/sells right now at the best available price."),
        ("Limit Orders", "A limit order sets the exact price you're willing to accept."),
        ("Stop Orders", "Stop orders trigger a trade once a price level is reached, to limit loss."),
    ]),
    (2, "Reading a Stock Quote", "Understanding the numbers", [
        ("Price and Change", "Last price, daily change and percent change explained."),
        ("Volume", "Volume is how many shares traded; it shows interest and liquidity."),
        ("Market Cap", "Market cap = price x shares; the company's total market value."),
    ]),
    (2, "Costs and Fees", "What eating into returns", [
        ("Commissions", "Trading fees and how many apps are now commission-free."),
        ("Spreads", "The small gap between buy and sell price."),
        ("Fund Fees", "Expense ratios: the yearly % a fund charges to run it."),
    ]),
    (2, "Emotions and Markets", "The human side", [
        ("Fear and Greed", "Two emotions that drive many bad investing decisions."),
        ("Herd Behavior", "Following the crowd can lead into bubbles and crashes."),
        ("A Simple Plan Wins", "Having rules protects you from emotional mistakes."),
    ]),
    (2, "Putting It Together", "Your essentials checkpoint", [
        ("Building Blocks", "Recap of shares, prices, dividends and orders."),
        ("A Balanced View", "Weighing risk and reward before any buy."),
        ("Next Steps", "How the essentials set you up for reading the market."),
    ]),

    # ---------------- Tier 3: Reading the Market (u21-u30) ----------------
    (3, "Reading Charts", "Seeing price stories", [
        ("Line vs Candlestick", "Line charts show the path; candlesticks show open/high/low/close."),
        ("Timeframes", "Daily, weekly and intraday charts show different pictures."),
        ("Spotting Trends", "Uptrends, downtrends and sideways ranges."),
    ]),
    (3, "Candlesticks", "Decoding candles", [
        ("Body and Wick", "The body is open-to-close; wicks are the highs and lows."),
        ("Green and Red", "Green closes up, red closes down; what a long body means."),
        ("Common Patterns", "Doji and hammer as simple sentiment clues."),
    ]),
    (3, "Support and Resistance", "Price floors and ceilings", [
        ("Support", "A price floor where buyers tend to step in."),
        ("Resistance", "A price ceiling where sellers tend to appear."),
        ("Breakouts", "When price pushes through a level with force."),
    ]),
    (3, "Moving Averages", "Smoothing the noise", [
        ("What They Are", "An average price over a period that smooths the line."),
        ("50 and 200 Day", "Popular averages traders watch for trend."),
        ("Crossovers", "Golden cross and death cross signals."),
    ]),
    (3, "Momentum and Volume", "Strength behind moves", [
        ("Volume Confirms", "Rising price on rising volume is stronger."),
        ("RSI Basics", "A 0-100 gauge hinting overbought/oversold."),
        ("Momentum Idea", "Trends in motion often continue for a while."),
    ]),
    (3, "Volatility", "Handling turbulence", [
        ("What Is Volatility?", "How much and how fast a price swings."),
        ("The VIX", "A 'fear gauge' for expected market swings."),
        ("Staying Steady", "Why volatility is the price of long-term returns."),
    ]),
    (3, "Sectors and Industries", "Grouping the market", [
        ("The 11 Sectors", "Tech, health, finance and more; how the market is grouped."),
        ("Sector Rotation", "Money shifting between sectors as the economy changes."),
        ("Examples", "Placing familiar companies into their sectors."),
    ]),
    (3, "Stocks vs Bonds", "Two core assets", [
        ("What Is a Bond?", "Lending money for interest; safer, steadier than stocks."),
        ("The Risk Ladder", "From cash to bonds to stocks, risk and reward rise."),
        ("Mixing Both", "Blending stocks and bonds to balance a portfolio."),
    ]),
    (3, "ETFs and Funds", "Buying baskets", [
        ("What Is an ETF?", "One fund holding many stocks, traded like a share."),
        ("Index Funds", "Funds that simply track an index cheaply."),
        ("Active vs Passive", "Managers picking stocks vs just tracking the market."),
    ]),
    (3, "Diversification", "Not all eggs in one basket", [
        ("Why Diversify", "Spreading risk so one loser can't sink you."),
        ("Across What?", "Across companies, sectors, and asset types."),
        ("Too Much?", "Over-diversifying can dilute returns."),
    ]),

    # ---------------- Tier 4: Fundamental Analysis (u31-u40) ----------------
    (4, "Fundamental Analysis", "Judging a company's value", [
        ("What It Is", "Studying a business's finances to estimate its true worth."),
        ("The Statements", "Income statement, balance sheet and cash flow overview."),
        ("Why It Matters", "Buying good businesses at fair prices beats guessing."),
    ]),
    (4, "Earnings and EPS", "The profit picture", [
        ("Revenue vs Profit", "Sales at the top; profit is what's left after costs."),
        ("Net Income", "The bottom-line profit figure."),
        ("Earnings Per Share", "EPS = net income / shares; profit per share owned."),
    ]),
    (4, "The P/E Ratio", "Price versus earnings", [
        ("What P/E Means", "Price / EPS: what you pay per $1 of earnings."),
        ("High vs Low", "High P/E signals growth hopes; low can signal value or trouble."),
        ("Comparing Fairly", "Compare P/E within the same industry."),
    ]),
    (4, "Valuation Ratios", "More ways to value", [
        ("P/B Ratio", "Price to book value of assets."),
        ("P/S and PEG", "Price to sales; PEG adjusts P/E for growth."),
        ("Dividend Yield", "Annual dividend / price as an income measure."),
    ]),
    (4, "The Balance Sheet", "What a company owns and owes", [
        ("Assets", "What the company owns and can use."),
        ("Liabilities", "What the company owes to others."),
        ("Equity", "Assets minus liabilities: owners' stake."),
    ]),
    (4, "Cash Flow", "Following the money", [
        ("Operating Cash Flow", "Cash generated by the core business."),
        ("Free Cash Flow", "Cash left after investments; fuel for growth and dividends."),
        ("Why Cash Is King", "Profit can be adjusted; cash is harder to fake."),
    ]),
    (4, "Growth and Margins", "Quality of a business", [
        ("Revenue Growth", "How fast sales are rising year over year."),
        ("Profit Margins", "What portion of sales becomes profit."),
        ("Economic Moats", "Durable advantages that protect profits."),
    ]),
    (4, "Debt and Health", "Spotting fragility", [
        ("Debt Ratios", "Debt-to-equity and why leverage cuts both ways."),
        ("Interest Coverage", "Can profits comfortably cover interest?"),
        ("Red Flags", "Warning signs in the numbers."),
    ]),
    (4, "The Economy", "The big backdrop", [
        ("Interest Rates", "How rates affect borrowing, spending and stock values."),
        ("Inflation", "Rising prices and their market impact."),
        ("GDP and Cycles", "Growth and recession phases of the economy."),
    ]),
    (4, "Earnings Season", "When companies report", [
        ("The Reports", "Quarterly results that update the story."),
        ("Guidance", "Management's outlook often moves the price most."),
        ("Surprises", "Beating or missing expectations and the reaction."),
    ]),

    # ---------------- Tier 5: Professional Investing (u41-u50) ----------------
    (5, "Building a Portfolio", "Designing your mix", [
        ("Asset Allocation", "Choosing the split between stocks, bonds and cash."),
        ("Diversify Deeply", "Across geographies, sizes and styles."),
        ("Rebalancing", "Trimming winners and topping up laggards to stay on target."),
    ]),
    (5, "Risk Management", "Protecting capital", [
        ("Position Sizing", "How much to put in any single idea."),
        ("Stop-Losses", "Pre-planned exits to cap a loss."),
        ("Risk/Reward", "Weighing potential gain against potential loss."),
    ]),
    (5, "Dollar-Cost Averaging", "Investing on autopilot", [
        ("What Is DCA?", "Investing a fixed amount on a schedule regardless of price."),
        ("The Timing Myth", "Why timing the market rarely beats consistency."),
        ("Discipline Wins", "Automating removes emotion from the decision."),
    ]),
    (5, "Long-Term Compounding", "The eighth wonder", [
        ("Time in Market", "Staying invested beats jumping in and out."),
        ("Reinvestment", "Reinvested returns compound powerfully over decades."),
        ("Patience Pays", "Real wealth is built slowly and steadily."),
    ]),
    (5, "Options Basics", "Contracts, not shares", [
        ("Calls and Puts", "The right to buy (call) or sell (put) at a set price."),
        ("Why They Exist", "Hedging risk and speculating with leverage."),
        ("Risk Warning", "Options can expire worthless; advanced and risky."),
    ]),
    (5, "Leverage and Shorting", "Advanced, high-risk tools", [
        ("Buying on Margin", "Borrowing to invest amplifies gains and losses."),
        ("Short Selling", "Profiting from a falling price and its dangers."),
        ("Leverage Risk", "Why leverage can wipe an account out fast."),
    ]),
    (5, "Behavioral Finance", "Mastering your mind", [
        ("Common Biases", "Anchoring, confirmation and loss aversion."),
        ("Beating FOMO", "Resisting the fear of missing out."),
        ("Process Over Outcome", "Judging decisions by process, not luck."),
    ]),
    (5, "Global Macro", "The world stage", [
        ("Currencies", "How exchange rates affect investments."),
        ("Commodities", "Oil, gold and their market roles."),
        ("Geopolitics", "How world events ripple through markets."),
    ]),
    (5, "Taxes and Accounts", "Keeping more of your gains", [
        ("Capital Gains Tax", "Short vs long-term gains and why holding can pay off."),
        ("Tax-Advantaged Accounts", "Retirement and tax-sheltered accounts in principle."),
        ("Wash Sales", "A rule limiting loss harvesting."),
    ]),
    (5, "Your Investing Strategy", "Putting it all together", [
        ("Write Your Plan", "Goals, timeline and rules on paper."),
        ("Review and Adjust", "Checking progress without over-tinkering."),
        ("Lifelong Investing", "Growing as an investor for decades."),
    ]),
]


def build_units_spec():
    """Return a list of unit specs with ids, tier, color, xp and lesson ids/icons."""
    units = []
    lesson_counter = 1
    for i, (_tier, title, subtitle, lessons) in enumerate(BLUEPRINT, start=1):
        tier = (i - 1) // 20 + 1  # 10 tiers of 20 units each (u1-u200)
        meta = TIER_META[tier]
        lspecs = []
        for j, (ltitle, focus) in enumerate(lessons):
            lspecs.append({
                "id": f"l{lesson_counter}",
                "icon": ICONS[(lesson_counter - 1) % len(ICONS)],
                "title": ltitle,
                "focus": focus,
            })
            lesson_counter += 1
        units.append({
            "id": f"u{i}",
            "tier": tier,
            "color": meta["color"],
            "xp": meta["xp"],
            "difficulty": meta["difficulty"],
            "title": title,
            "subtitle": subtitle,
            "lessons": lspecs,
        })
    return units


UNITS_SPEC = build_units_spec()

if __name__ == "__main__":
    print(f"Units: {len(UNITS_SPEC)}  Lessons: {sum(len(u['lessons']) for u in UNITS_SPEC)}")
    for u in UNITS_SPEC[:3]:
        print(u["id"], u["tier"], u["title"], [l["id"] for l in u["lessons"]])
