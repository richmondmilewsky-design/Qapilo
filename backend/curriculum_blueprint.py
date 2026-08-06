"""Qapilo 200-unit curriculum blueprint.

Pedagogical design only (titles, themes, difficulty tiers). The teaching cards
and quiz questions are generated per lesson in EN/DE/ES by generate_curriculum.py
and stored in curriculum_data.json.

10 tiers x 20 units (u1-u200), 3 lessons per unit (l1-l600). Difficulty rises
every tier (every 20 units). XP per lesson scales with tier so harder lessons
reward more points. Content is strictly educational and never gives personalised
buy/sell advice.
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

# Each unit: (tier, title, subtitle, [3 lesson (title, focus) tuples]).
# The tier value here is for readability; build_units_spec() assigns tier by
# position (20 units per tier).
BLUEPRINT = [
    # ================= Tier 1: Geld verstehen - Money basics (u1-u20) =================
    (1, "Money, Made Simple", "What money is and why we use it", [
        ("What Is Money?", "Money as a tool we trade for things; a simple everyday picture."),
        ("A World Without Money", "Bartering and why swapping goods directly was clumsy and hard."),
        ("Money as an Agreement", "Money works because we all trust it has value."),
    ]),
    (1, "The Story of Money", "How money came to be", [
        ("From Shells to Coins", "Early forms of money used across history."),
        ("Paper and Banknotes", "Why lightweight paper replaced heavy metal coins."),
        ("Money Today", "Cards and phones: money as numbers on a screen."),
    ]),
    (1, "Types of Money", "The forms money takes", [
        ("Cash and Coins", "Physical money you can hold in your hand."),
        ("Digital Money", "Money that lives in bank accounts and apps."),
        ("What Makes Money Work", "Durable, easy to divide and widely accepted."),
    ]),
    (1, "Earning Money", "Where money comes from", [
        ("Work and Wages", "Trading your time and skills for pay."),
        ("Different Incomes", "Salary, hourly pay and self-employment, simply explained."),
        ("Value You Create", "Doing useful things for others is how you earn."),
    ]),
    (1, "Spending Wisely", "Making money go further", [
        ("Needs vs Wants", "Telling essentials apart from nice-to-haves."),
        ("Price and Value", "Cheap is not always good value."),
        ("Everyday Choices", "Small daily decisions add up over time."),
    ]),
    (1, "Saving Money", "Keeping some for later", [
        ("Why Save?", "Setting money aside for future needs and surprises."),
        ("The Piggy-Bank Idea", "Small regular amounts quietly build up."),
        ("Saving vs Spending", "Balancing enjoying now and preparing for later."),
    ]),
    (1, "Why Money Loses Value", "Inflation, simply", [
        ("Prices Slowly Rise", "Most things cost a little more over the years."),
        ("What Is Inflation?", "Money buys a little less as prices climb."),
        ("An Everyday Example", "A loaf of bread over decades shows inflation."),
    ]),
    (1, "Banks Explained", "Where money is kept safe", [
        ("What Is a Bank?", "A safe place that looks after your money."),
        ("How Banks Help", "Keeping money safe and moving it around for you."),
        ("Your Bank Account", "A simple record of money coming in and going out."),
    ]),
    (1, "How Banks Use Money", "The banking cycle, simply", [
        ("Deposits and Loans", "Banks lend out money that people deposit."),
        ("Interest, Simply", "A small fee paid for borrowing or earned for saving."),
        ("Keeping It Balanced", "Why banks always keep some money ready."),
    ]),
    (1, "Everyday Payments", "Moving money around", [
        ("Cash vs Card", "Two common everyday ways to pay."),
        ("Digital Payments", "Phones and apps that pay in an instant."),
        ("Staying Safe", "Simple habits to protect your money when paying."),
    ]),
    (1, "Currencies of the World", "Money across countries", [
        ("Different Money", "Every country has its own currency."),
        ("Exchange Rates, Simply", "Why one currency swaps for another."),
        ("Travelling Money", "Changing money when visiting another country."),
    ]),
    (1, "The Value of Money", "What gives money worth", [
        ("Trust and Value", "Money works because people trust it."),
        ("Supply of Money", "Too much money around can lower its value."),
        ("Rare vs Common", "Scarcity and value, explained simply."),
    ]),
    (1, "Budgeting Basics", "A simple money plan", [
        ("What Is a Budget?", "A plan for money coming in and going out."),
        ("Income and Expenses", "The two sides of any budget."),
        ("A Simple First Budget", "Splitting money into easy buckets."),
    ]),
    (1, "Money Goals", "Giving your money a purpose", [
        ("Short and Long Goals", "Saving for soon versus saving for far away."),
        ("Small Steps", "Breaking a big goal into little amounts."),
        ("Staying Motivated", "Seeing progress keeps you going."),
    ]),
    (1, "Good Money Habits", "Building healthy routines", [
        ("Pay Yourself First", "Saving a little before you spend the rest."),
        ("Track Your Spending", "Knowing where your money actually goes."),
        ("Avoid Waste", "Cutting small leaks in your budget."),
    ]),
    (1, "Understanding Debt", "Borrowing money, simply", [
        ("What Is Debt?", "Money you borrow and must repay later."),
        ("Good vs Bad Debt", "Some debt helps you; some hurts you."),
        ("The Cost of Borrowing", "Interest makes borrowed money cost more."),
    ]),
    (1, "Interest, Made Clear", "The price of money over time", [
        ("Earning Interest", "Money can grow just by sitting in savings."),
        ("Paying Interest", "Borrowing costs extra over time."),
        ("Simple vs Compound", "Compound interest builds on itself."),
    ]),
    (1, "Financial Safety", "Protecting your money", [
        ("Emergency Money", "A small cushion for life's surprises."),
        ("Scams and Fraud", "Spotting tricks that try to steal money."),
        ("Safe Habits", "Simple ways to keep your money secure."),
    ]),
    (1, "Money and Feelings", "The emotional side", [
        ("Money Stress", "Why money worries can feel so big."),
        ("Wants and Impulses", "Pausing before you spend."),
        ("A Healthy Mindset", "A calm, planned view of money."),
    ]),
    (1, "Money Foundations Recap", "Tying it together", [
        ("What You've Learned", "A friendly recap of the money basics."),
        ("Money in Daily Life", "Using these ideas every single day."),
        ("Ready for More", "How these basics lead to personal finance."),
    ]),

    # ============ Tier 2: Persoenliche Finanzen - Personal finance (u21-u40) ============
    (2, "Personal Finance Basics", "Managing your own money", [
        ("Taking Control", "Being in charge of your own money."),
        ("Income In, Money Out", "The everyday flow of personal money."),
        ("Your Financial Picture", "A simple overview of where you stand."),
    ]),
    (2, "Building a Budget", "A plan that works", [
        ("The 50/30/20 Idea", "Splitting money into needs, wants and savings."),
        ("Fixed vs Variable", "Costs that stay the same versus those that change."),
        ("Adjusting Your Budget", "Updating the plan as life changes."),
    ]),
    (2, "Tracking Spending", "Knowing where money goes", [
        ("Why Track?", "You cannot manage what you do not measure."),
        ("Categories", "Grouping spending to see the patterns."),
        ("Finding Leaks", "Spotting small recurring costs."),
    ]),
    (2, "Saving Strategies", "Building your savings", [
        ("Automatic Saving", "Setting money aside without thinking about it."),
        ("Savings Buckets", "Separate savings for separate goals."),
        ("Boosting Savings", "Small ways to save a little more each month."),
    ]),
    (2, "Emergency Funds", "Your safety net", [
        ("Why You Need One", "A cushion for unexpected costs."),
        ("How Much?", "Aiming for a few months of expenses."),
        ("Where to Keep It", "Easy-to-reach, safe savings."),
    ]),
    (2, "Understanding Credit", "Borrowing responsibly", [
        ("What Is Credit?", "The ability to borrow now and repay later."),
        ("Credit Cards, Simply", "How they work and where the risks are."),
        ("Credit Scores", "A number showing how reliably you repay."),
    ]),
    (2, "Managing Debt", "Getting on top of what you owe", [
        ("Listing Your Debts", "Knowing exactly what you owe."),
        ("Paying It Down", "Two common approaches to clearing debt."),
        ("Avoiding New Debt", "Breaking the borrowing cycle."),
    ]),
    (2, "Interest and Loans", "The cost of borrowing", [
        ("How Loans Work", "Principal, interest and repayment."),
        ("APR Explained", "The yearly cost of borrowing as a percent."),
        ("Comparing Loans", "Why the rate and the term both matter."),
    ]),
    (2, "The Power of Compounding", "Money growing on money", [
        ("The Snowball Effect", "Gains that start earning their own gains."),
        ("Time Is Key", "The earlier you start, the bigger it grows."),
        ("Small Amounts Matter", "Tiny regular sums grow large over time."),
    ]),
    (2, "Setting Financial Goals", "Planning your future", [
        ("SMART Goals", "Clear, measurable money targets."),
        ("Prioritizing", "Deciding which goals come first."),
        ("Tracking Progress", "Checking in on your goals over time."),
    ]),
    (2, "Income and Taxes", "Understanding your pay", [
        ("Gross vs Net", "Pay before and after deductions."),
        ("What Are Taxes?", "Money that funds shared public services."),
        ("Reading a Payslip", "Making sense of the numbers on it."),
    ]),
    (2, "Insurance Basics", "Protecting against risk", [
        ("What Is Insurance?", "Paying a little to avoid a big loss."),
        ("Common Types", "Health, home and other everyday cover."),
        ("When It Helps", "Matching cover to real risks."),
    ]),
    (2, "Housing Costs", "Rent, buy and beyond", [
        ("Renting vs Buying", "Weighing flexibility against ownership."),
        ("The True Cost", "Bills, upkeep and hidden costs."),
        ("Housing and Budgets", "Keeping housing affordable."),
    ]),
    (2, "Planning Big Purchases", "Buying smart", [
        ("Save or Borrow?", "Paying now versus paying over time."),
        ("Timing a Purchase", "Planning ahead to pay less."),
        ("Avoiding Regret", "Thinking before a big spend."),
    ]),
    (2, "Retirement, Simply", "Saving for the far future", [
        ("Why Start Early", "Decades of compounding matter most."),
        ("Retirement Accounts", "Special accounts for later life."),
        ("A Little Each Month", "Steady contributions add up."),
    ]),
    (2, "Financial Independence", "Money working for you", [
        ("What It Means", "Having enough to cover your needs."),
        ("The Savings Rate", "How much you keep drives progress."),
        ("Freedom Over Time", "How saving builds real choices."),
    ]),
    (2, "Avoiding Money Mistakes", "Common traps", [
        ("Lifestyle Creep", "Spending more as you earn more."),
        ("Impulse Buying", "The real cost of unplanned spending."),
        ("Ignoring Small Costs", "Little leaks that quietly add up."),
    ]),
    (2, "Money and Relationships", "Sharing finances", [
        ("Talking About Money", "Why open money talk helps."),
        ("Shared Goals", "Planning finances together."),
        ("Splitting Costs", "Fair ways to share expenses."),
    ]),
    (2, "Building Net Worth", "Measuring progress", [
        ("Assets vs Liabilities", "What you own versus what you owe."),
        ("Calculating Net Worth", "A simple snapshot of your wealth."),
        ("Growing It Over Time", "Increasing assets and lowering debt."),
    ]),
    (2, "Personal Finance Recap", "Ready to invest", [
        ("Your Money System", "A recap of budgeting and saving."),
        ("Strong Foundations", "Why finance comes before investing."),
        ("Next: Investing", "How healthy finances make investing possible."),
    ]),

    # ============ Tier 3: Investieren lernen - Learning to invest (u41-u60) ============
    (3, "What Is Investing?", "Putting money to work", [
        ("Growing Your Money", "Using money to try to make more, like planting a seed."),
        ("Saving vs Investing", "Safe and small versus more growth with ups and downs."),
        ("Risk and Reward", "Bigger possible rewards usually mean bigger swings."),
    ]),
    (3, "Why People Invest", "The purpose behind it", [
        ("Beating Inflation", "Growing money faster than prices rise."),
        ("Long-Term Goals", "Funding retirement, homes and more."),
        ("Making Money Work", "Money that earns even while you sleep."),
    ]),
    (3, "Understanding Return", "Measuring gains", [
        ("What Is Return?", "The gain or loss on an investment."),
        ("Percentages Matter", "Why returns use % so any size compares fairly."),
        ("Total Return", "Price change plus income together."),
    ]),
    (3, "Understanding Risk", "The ups and downs", [
        ("What Is Risk?", "The chance an investment loses value."),
        ("Types of Risk", "Market, company and other risks, simply."),
        ("Risk vs Reward", "Balancing safety against growth."),
    ]),
    (3, "Time Horizon", "How long you invest", [
        ("Short vs Long Term", "How your timeline shapes your choices."),
        ("Time and Risk", "Longer horizons can ride out the swings."),
        ("Matching Money to Time", "The right investments for the timeline."),
    ]),
    (3, "The Magic of Compounding", "Growth over time", [
        ("Compounding Returns", "Returns that earn their own returns."),
        ("Time in the Market", "Staying invested beats jumping around."),
        ("Reinvesting", "Putting your gains back to work."),
    ]),
    (3, "Diversification", "Spreading your risk", [
        ("Many Baskets", "Not putting all your eggs in one place."),
        ("Across What?", "Across companies, sectors and asset types."),
        ("Why It Helps", "One loser cannot sink the whole plan."),
    ]),
    (3, "Asset Classes Overview", "The main choices", [
        ("Stocks and Bonds", "Owning versus lending, simply."),
        ("Cash and Property", "Everyday and physical assets."),
        ("Mixing Them", "Blending assets to balance risk."),
    ]),
    (3, "Starting to Invest", "Your first steps", [
        ("What Is a Broker?", "An app or firm that lets you buy and sell."),
        ("Opening an Account", "Setting yourself up to invest, simply."),
        ("Your First Investment", "How a first purchase actually works."),
    ]),
    (3, "Investing Regularly", "Building the habit", [
        ("Dollar-Cost Averaging", "Investing a fixed amount on a schedule."),
        ("Smoothing the Ride", "Buying at many prices over time."),
        ("Discipline Wins", "Automating removes emotion from the decision."),
    ]),
    (3, "Setting an Investment Plan", "Your roadmap", [
        ("Goals and Timeline", "Writing down why and when."),
        ("Your Risk Comfort", "Knowing how much swing you can accept."),
        ("Simple Rules", "A plan you can actually stick to."),
    ]),
    (3, "Understanding Volatility", "Living with swings", [
        ("What Is Volatility?", "How much and how fast prices move."),
        ("Normal Ups and Downs", "Swings are a normal part of investing."),
        ("Staying Calm", "Why patience beats panic."),
    ]),
    (3, "Risk and Emotion", "The human side", [
        ("Fear and Greed", "Two emotions that drive bad choices."),
        ("Panic Selling", "Locking in losses out of fear."),
        ("A Steady Hand", "Sticking to your plan through the noise."),
    ]),
    (3, "Simple vs Complex", "Keeping it easy", [
        ("Keep It Simple", "Simple plans often work best."),
        ("Index Investing", "Owning the whole market cheaply."),
        ("Avoiding Complexity", "Why fancy is not always better."),
    ]),
    (3, "Fees and Costs", "What eats returns", [
        ("Why Fees Matter", "Small fees compound against you."),
        ("Fund Fees", "The yearly % a fund charges to run it."),
        ("Keeping Costs Low", "More return stays with you."),
    ]),
    (3, "Investment Accounts", "Where to invest", [
        ("Taxable vs Sheltered", "Two account types, simply."),
        ("Retirement Accounts", "Special long-term accounts."),
        ("Choosing Wisely", "Matching the account to the goal."),
    ]),
    (3, "Avoiding Investing Mistakes", "Common traps", [
        ("Chasing Hot Tips", "Why hype rarely pays off."),
        ("Timing the Market", "Why it is so hard to get right."),
        ("Overtrading", "Trading too much hurts returns."),
    ]),
    (3, "Investing With Values", "Ethical and green ideas", [
        ("What Is ESG?", "Considering environment and society."),
        ("Values and Returns", "Balancing beliefs and goals."),
        ("Doing Research", "Looking beyond the labels."),
    ]),
    (3, "Measuring Your Progress", "Are you on track?", [
        ("Reviewing Returns", "Checking how you are doing."),
        ("Against Your Goals", "Comparing to your plan, not others."),
        ("When to Adjust", "Small tweaks, not big overhauls."),
    ]),
    (3, "Investing Foundations Recap", "Ready for stocks", [
        ("Core Principles", "A recap of risk, return and time."),
        ("A Simple Investor", "How beginners can start well."),
        ("Next: Stocks", "Diving into shares and companies."),
    ]),

    # ============ Tier 4: Aktien verstehen - Understanding stocks (u61-u80) ============
    (4, "Meet the Stock Market", "Where shares trade", [
        ("What Is a Company?", "A business that sells things to make money."),
        ("A Share Is a Slice", "A share is a tiny slice of a company you can own."),
        ("Why Buy Shares?", "Hoping the company grows and your slice is worth more."),
    ]),
    (4, "Owning a Piece", "Being a shareholder", [
        ("You're an Owner", "Owning shares makes you a part-owner."),
        ("Going Public", "When a company first sells shares to everyone."),
        ("Companies You Know", "Familiar brands are public companies."),
    ]),
    (4, "Stock Exchanges", "The marketplaces", [
        ("What Is an Exchange?", "Where buyers and sellers of shares meet."),
        ("NYSE and Nasdaq", "Two big US marketplaces."),
        ("Ticker Symbols", "Short codes that name each stock."),
    ]),
    (4, "Why Prices Move", "Supply and demand", [
        ("Buyers and Sellers", "More buyers push prices up, more sellers push down."),
        ("Good News, Bad News", "News shifts the balance of buyers and sellers."),
        ("An Everyday Example", "Concert tickets or sneakers showing demand move price."),
    ]),
    (4, "Reading a Stock Quote", "The numbers explained", [
        ("Price and Change", "Last price, daily change and percent change."),
        ("Volume", "How many shares traded; interest and liquidity."),
        ("Market Cap", "Price times shares: the company's total value."),
    ]),
    (4, "Dividends", "Sharing the profits", [
        ("What Are Dividends?", "Cash paid to owners from company profits."),
        ("Dividend Yield", "Annual dividend divided by the share price."),
        ("Not All Pay", "Many companies reinvest profits instead."),
    ]),
    (4, "Capital Gains", "Profit from price", [
        ("Buying Low, Selling High", "Profit from a rising share price."),
        ("Realized vs Unrealized", "On paper versus actually sold."),
        ("Two Ways to Gain", "Price gains plus dividends together."),
    ]),
    (4, "Types of Stocks", "Not all alike", [
        ("Growth vs Value", "Fast expanders versus cheap-looking firms."),
        ("Blue Chips", "Large, stable, well-known companies."),
        ("Small vs Large Caps", "Company size and what it means for risk."),
    ]),
    (4, "Placing Orders", "How trades happen", [
        ("Market Orders", "Buy or sell right now at the best price."),
        ("Limit Orders", "Set the exact price you are willing to accept."),
        ("Stop Orders", "Trigger a trade once a price level is reached."),
    ]),
    (4, "Costs of Trading", "Fees to know", [
        ("Commissions", "Trading fees, and how many apps are now free."),
        ("The Spread", "The small gap between buy and sell price."),
        ("Hidden Costs", "Little costs that quietly add up."),
    ]),
    (4, "Market Indices", "Tracking the market", [
        ("What Is an Index?", "A basket of stocks showing market health."),
        ("S&P 500 and Dow", "500 big US firms versus 30 giants."),
        ("Nasdaq and Others", "Tech-heavy and other global indices."),
    ]),
    (4, "Bulls and Bears", "Market moods", [
        ("Bull Markets", "Rising prices on optimism."),
        ("Bear Markets", "Falling 20%+ on pessimism."),
        ("Market Sentiment", "The overall mood of the crowd."),
    ]),
    (4, "How Companies Grow", "The business behind stocks", [
        ("Selling More", "Growing revenue over time."),
        ("New Products", "Innovation driving growth."),
        ("Expanding Reach", "New markets and new customers."),
    ]),
    (4, "Company Basics", "Understanding a business", [
        ("Revenue and Costs", "Money coming in versus money spent."),
        ("Profit", "What is left after all the costs."),
        ("People and Products", "What a company actually does."),
    ]),
    (4, "Splits and Buybacks", "Company actions", [
        ("Stock Splits", "Slicing shares into smaller pieces."),
        ("Share Buybacks", "Companies buying their own shares."),
        ("Why They Matter", "Effects on price and ownership."),
    ]),
    (4, "IPOs", "Going public", [
        ("What Is an IPO?", "The first sale of shares to the public."),
        ("Why Companies List", "Raising money to grow."),
        ("IPO Risks", "Why new listings can be volatile."),
    ]),
    (4, "Following Your Stocks", "Staying informed", [
        ("Watchlists", "Tracking stocks you are interested in."),
        ("Company News", "How news affects your shares."),
        ("Earnings Dates", "When companies report their results."),
    ]),
    (4, "Long-Term Stock Investing", "Patience with shares", [
        ("Buy and Hold", "Owning good companies for years."),
        ("Riding Out Dips", "Staying calm during downturns."),
        ("Compounding Ownership", "Reinvesting dividends over time."),
    ]),
    (4, "Common Stock Mistakes", "Traps to avoid", [
        ("Falling for Hype", "Chasing the latest hot stock."),
        ("Ignoring Fundamentals", "Buying without understanding."),
        ("Overconcentration", "Too much money in one stock."),
    ]),
    (4, "Stocks Recap", "Ready for funds", [
        ("What You've Learned", "A recap of shares and trading."),
        ("The Stock Investor", "How to approach stocks wisely."),
        ("Next: Funds", "Moving on to ETFs and asset classes."),
    ]),

    # ======== Tier 5: ETFs und Anlageklassen - ETFs & asset classes (u81-u100) ========
    (5, "Funds Explained", "Buying baskets", [
        ("What Is a Fund?", "One pool holding many investments at once."),
        ("Diversification in One", "Instant spread across many holdings."),
        ("Shares of a Fund", "Owning a slice of the whole basket."),
    ]),
    (5, "ETFs", "Funds that trade like stocks", [
        ("What Is an ETF?", "A fund you can buy just like a share."),
        ("How ETFs Work", "Tracking a basket, traded all day long."),
        ("ETF Advantages", "Low cost and easy diversification."),
    ]),
    (5, "Index Funds", "Owning the market", [
        ("What Is an Index Fund?", "A fund that simply tracks an index."),
        ("Passive Investing", "Matching the market, not trying to beat it."),
        ("Low Costs", "Why tracking an index is cheap."),
    ]),
    (5, "Active vs Passive", "Two approaches", [
        ("Active Funds", "Managers picking the investments."),
        ("Passive Funds", "Simply tracking an index."),
        ("The Trade-offs", "Cost, effort and typical results."),
    ]),
    (5, "Choosing an ETF", "What to look at", [
        ("Expense Ratio", "The yearly fee, explained simply."),
        ("What It Holds", "Checking the basket underneath."),
        ("Size and Liquidity", "Bigger, busier ETFs trade more easily."),
    ]),
    (5, "Bonds Explained", "Lending your money", [
        ("What Is a Bond?", "Lending money in return for regular interest."),
        ("Bond Basics", "Face value, coupon and maturity."),
        ("Safer, Steadier", "Why bonds swing less than stocks."),
    ]),
    (5, "How Bonds Work", "Rates and prices", [
        ("Coupon Payments", "The regular interest you receive."),
        ("Rates and Prices", "Why they usually move in opposite directions."),
        ("Bond Risk", "Default risk and interest-rate risk."),
    ]),
    (5, "Government vs Corporate", "Who you lend to", [
        ("Government Bonds", "Lending money to a country."),
        ("Corporate Bonds", "Lending money to a company."),
        ("Risk and Yield", "Higher risk usually means higher interest."),
    ]),
    (5, "Stocks vs Bonds", "Balancing a mix", [
        ("Owning vs Lending", "The core difference between them."),
        ("The Risk Ladder", "From cash to bonds to stocks."),
        ("Mixing Both", "Blending them for balance."),
    ]),
    (5, "Real Estate Investing", "Property as an asset", [
        ("Owning Property", "Buying to rent out or grow in value."),
        ("REITs", "Investing in property without buying buildings."),
        ("Pros and Cons", "Income, cost and being hard to sell fast."),
    ]),
    (5, "Commodities", "Raw materials", [
        ("What Are Commodities?", "Oil, gold, wheat and other raw goods."),
        ("Gold as a Store", "Why gold is often seen as safe."),
        ("Commodity Swings", "Why their prices can be very volatile."),
    ]),
    (5, "Cash and Equivalents", "The safe corner", [
        ("Holding Cash", "Safety and instant access."),
        ("Money Market Funds", "Low-risk, short-term holdings."),
        ("Cash and Inflation", "Why too much cash quietly loses value."),
    ]),
    (5, "Cryptocurrencies", "The new asset class", [
        ("What Is Crypto?", "Digital money recorded on a blockchain."),
        ("Bitcoin and Beyond", "The idea behind cryptocurrencies."),
        ("High Risk", "Extreme volatility and uncertainty."),
    ]),
    (5, "Alternative Investments", "Beyond the basics", [
        ("What Are Alternatives?", "Art, collectibles and other assets."),
        ("Why People Use Them", "Diversification and personal passion."),
        ("The Cautions", "Hard to sell and hard to value."),
    ]),
    (5, "Mutual Funds", "The traditional fund", [
        ("What Is a Mutual Fund?", "A pooled, professionally managed investment."),
        ("ETFs vs Mutual Funds", "Differences in trading and cost."),
        ("Choosing Wisely", "Fees and strategy both matter."),
    ]),
    (5, "Building with Funds", "A simple portfolio", [
        ("A Core Holding", "A broad fund as your foundation."),
        ("Adding Pieces", "Bonds and other assets around it."),
        ("Keeping It Simple", "A few funds can be plenty."),
    ]),
    (5, "Global Investing", "Beyond your home country", [
        ("Home Bias", "Overweighting your own country."),
        ("International Funds", "Investing around the world."),
        ("Currency Effects", "How exchange rates play a part."),
    ]),
    (5, "Sectors and Themes", "Slicing the market", [
        ("The 11 Sectors", "Tech, health, finance and more."),
        ("Sector Funds", "Investing in a single sector."),
        ("Thematic Funds", "Investing around trends and ideas."),
    ]),
    (5, "Diversification in Practice", "Putting it together", [
        ("Across Assets", "Stocks, bonds and beyond."),
        ("Across Regions", "Spreading around the globe."),
        ("Not Too Much", "Over-diversifying can dilute returns."),
    ]),
    (5, "Asset Classes Recap", "Ready for analysis", [
        ("The Full Toolbox", "A recap of the asset classes."),
        ("Choosing Your Mix", "Matching assets to your goals."),
        ("Next: Analysis", "Digging into company numbers."),
    ]),

    # ======== Tier 6: Unternehmen analysieren - Company analysis (u101-u120) ========
    (6, "Fundamental Analysis", "Judging value", [
        ("What It Is", "Studying finances to estimate true worth."),
        ("The Three Statements", "Income statement, balance sheet and cash flow."),
        ("Why It Matters", "Buying good businesses at fair prices."),
    ]),
    (6, "The Income Statement", "The profit story", [
        ("Revenue", "Total sales at the very top."),
        ("Costs and Expenses", "What is spent to run the business."),
        ("Net Income", "The bottom-line profit figure."),
    ]),
    (6, "Earnings and EPS", "Profit per share", [
        ("Revenue vs Profit", "Sales at the top; profit is what is left."),
        ("Net Income", "The bottom-line profit."),
        ("Earnings Per Share", "EPS = net income / shares; profit per share."),
    ]),
    (6, "The Balance Sheet", "Owns and owes", [
        ("Assets", "What the company owns and can use."),
        ("Liabilities", "What the company owes to others."),
        ("Equity", "Assets minus liabilities: the owners' stake."),
    ]),
    (6, "Cash Flow", "Following the money", [
        ("Operating Cash Flow", "Cash generated by the core business."),
        ("Free Cash Flow", "Cash left after investment spending."),
        ("Why Cash Is King", "Profit can be adjusted; cash is harder to fake."),
    ]),
    (6, "The P/E Ratio", "Price versus earnings", [
        ("What P/E Means", "Price / EPS: what you pay per $1 of earnings."),
        ("High vs Low", "Growth hopes versus value or trouble."),
        ("Comparing Fairly", "Compare P/E within the same industry."),
    ]),
    (6, "Valuation Ratios", "More ways to value", [
        ("P/B Ratio", "Price to the book value of assets."),
        ("P/S and PEG", "Price to sales; PEG adjusts P/E for growth."),
        ("Dividend Yield", "Annual dividend / price as an income measure."),
    ]),
    (6, "Growth Metrics", "Measuring expansion", [
        ("Revenue Growth", "How fast sales are rising."),
        ("Earnings Growth", "How fast profit is rising."),
        ("Sustainable Growth", "Growth that can actually last."),
    ]),
    (6, "Profit Margins", "Quality of profit", [
        ("Gross Margin", "Profit after direct costs."),
        ("Operating Margin", "Profit from running the business."),
        ("Net Margin", "Final profit as a percent of sales."),
    ]),
    (6, "Economic Moats", "Durable advantages", [
        ("What Is a Moat?", "A lasting edge over rivals."),
        ("Types of Moats", "Brand, cost, network and more."),
        ("Why Moats Matter", "Protecting long-term profits."),
    ]),
    (6, "Debt and Health", "Spotting fragility", [
        ("Debt Ratios", "Debt-to-equity and why leverage cuts both ways."),
        ("Interest Coverage", "Can profits comfortably cover interest?"),
        ("Red Flags", "Warning signs hiding in the numbers."),
    ]),
    (6, "Return Ratios", "How well capital works", [
        ("Return on Equity", "Profit per dollar of equity."),
        ("Return on Assets", "Profit per dollar of assets."),
        ("Why They Matter", "How efficient the business is."),
    ]),
    (6, "Reading Annual Reports", "The full picture", [
        ("The Annual Report", "A company's yearly story."),
        ("Management Discussion", "Leaders explaining the results."),
        ("Notes and Risks", "The detail behind the numbers."),
    ]),
    (6, "Earnings Season", "When companies report", [
        ("The Reports", "Quarterly results that update the story."),
        ("Guidance", "Management's outlook often moves the price most."),
        ("Surprises", "Beating or missing expectations and the reaction."),
    ]),
    (6, "Qualitative Analysis", "Beyond the numbers", [
        ("Management Quality", "Leaders you can trust."),
        ("Competitive Position", "Standing among rivals."),
        ("Industry Trends", "Tailwinds and headwinds."),
    ]),
    (6, "Valuation Approaches", "Estimating worth", [
        ("Relative Valuation", "Comparing to similar firms."),
        ("Intrinsic Value", "Estimating true worth."),
        ("Margin of Safety", "Buying below your estimate."),
    ]),
    (6, "Comparing Companies", "Peer analysis", [
        ("Same Industry", "Comparing like with like."),
        ("Key Metrics", "Which numbers to line up."),
        ("Drawing Conclusions", "Making sense of the differences."),
    ]),
    (6, "Spotting Value Traps", "Cheap for a reason", [
        ("What Is a Value Trap?", "Cheap but quietly declining."),
        ("Warning Signs", "Falling sales and rising debt."),
        ("Cheap vs Good", "Price alone is not everything."),
    ]),
    (6, "A Research Process", "A repeatable method", [
        ("A Checklist", "Steps to study any company."),
        ("Sources of Data", "Where to find reliable numbers."),
        ("Staying Objective", "Facts over feelings."),
    ]),
    (6, "Analysis Recap", "Ready for portfolios", [
        ("The Analyst's Toolkit", "A recap of company analysis."),
        ("Judging a Business", "Numbers plus judgement."),
        ("Next: Portfolios", "Combining ideas into a plan."),
    ]),

    # ====== Tier 7: Portfolio und Psychologie - Portfolio & psychology (u121-u140) ======
    (7, "Building a Portfolio", "Designing your mix", [
        ("Asset Allocation", "Choosing the split of stocks, bonds and cash."),
        ("Diversify Deeply", "Across sizes, styles and regions."),
        ("Rebalancing", "Trimming winners and topping up laggards."),
    ]),
    (7, "Asset Allocation", "The biggest decision", [
        ("Why It Matters Most", "Allocation drives most of your results."),
        ("Age and Goals", "Matching the mix to your timeline."),
        ("A Simple Split", "Example allocations, explained."),
    ]),
    (7, "Correlation", "How assets move together", [
        ("What Is Correlation?", "Whether assets move in sync."),
        ("Why It Matters", "Low correlation smooths returns."),
        ("Building Balance", "Mixing assets that behave differently."),
    ]),
    (7, "Rebalancing", "Staying on target", [
        ("Why Rebalance?", "Drift slowly changes your risk."),
        ("How Often?", "Time-based versus threshold approaches."),
        ("The Discipline", "Selling high and buying low naturally."),
    ]),
    (7, "Risk Management", "Protecting capital", [
        ("Position Sizing", "How much to put in any single idea."),
        ("Stop-Losses", "Pre-planned exits to cap a loss."),
        ("Risk/Reward", "Weighing potential gain against potential loss."),
    ]),
    (7, "Measuring Risk", "Putting numbers on it", [
        ("Standard Deviation", "How much returns vary."),
        ("Drawdowns", "The size of peak-to-trough falls."),
        ("The Sharpe Idea", "Return earned per unit of risk."),
    ]),
    (7, "Behavioral Finance", "Mastering your mind", [
        ("Common Biases", "Anchoring, confirmation and loss aversion."),
        ("Beating FOMO", "Resisting the fear of missing out."),
        ("Process Over Outcome", "Judging decisions, not luck."),
    ]),
    (7, "Loss Aversion", "Why losses hurt more", [
        ("The Pain of Loss", "Losses feel worse than equal gains."),
        ("Holding Losers", "Refusing to sell a mistake."),
        ("A Clear Head", "Deciding by facts, not by fear."),
    ]),
    (7, "Herd Behavior", "Following the crowd", [
        ("Why We Follow", "The pull of safety in numbers."),
        ("Bubbles", "Crowds pushing prices far too high."),
        ("Independent Thinking", "Deciding for yourself."),
    ]),
    (7, "Overconfidence", "The confidence trap", [
        ("Thinking You Know", "Overrating your own skill."),
        ("Overtrading", "Too much activity hurts returns."),
        ("Staying Humble", "Respecting uncertainty."),
    ]),
    (7, "Emotional Discipline", "Staying steady", [
        ("A Written Plan", "Rules that guide your decisions."),
        ("Ignoring Noise", "Tuning out daily headlines."),
        ("Automating", "Removing emotion from action."),
    ]),
    (7, "Dollar-Cost Averaging", "Investing steadily", [
        ("What Is DCA?", "Investing a fixed amount on a schedule."),
        ("The Timing Myth", "Why consistency usually beats timing."),
        ("Discipline Wins", "Automating removes emotion."),
    ]),
    (7, "Long-Term Compounding", "The eighth wonder", [
        ("Time in Market", "Staying invested beats jumping in and out."),
        ("Reinvestment", "Reinvested returns compound over decades."),
        ("Patience Pays", "Wealth is built slowly and steadily."),
    ]),
    (7, "Portfolio Income", "Living off investments", [
        ("Dividends and Interest", "Cash your portfolio pays you."),
        ("The Withdrawal Idea", "Spending from a portfolio sustainably."),
        ("Income vs Growth", "Balancing steady cash and long-term growth."),
    ]),
    (7, "Tax-Efficient Investing", "Keeping more", [
        ("Capital Gains Tax", "Short-term versus long-term gains."),
        ("Sheltered Accounts", "Sheltering growth from tax."),
        ("Asset Location", "Holding assets in the right account."),
    ]),
    (7, "Reviewing Your Portfolio", "Health checks", [
        ("Regular Reviews", "Checking without overreacting."),
        ("Are You On Track?", "Comparing to your own plan."),
        ("When to Change", "Small tweaks, not overhauls."),
    ]),
    (7, "Handling Market Crashes", "Staying the course", [
        ("Crashes Happen", "Big falls are part of investing."),
        ("Why Not to Panic", "Selling low locks in losses."),
        ("History's Lesson", "Markets have recovered over time."),
    ]),
    (7, "Model Portfolios", "Simple templates", [
        ("The Core Portfolio", "A broad, simple base."),
        ("Adding Satellites", "Small extra positions around the core."),
        ("Keeping It Manageable", "Not too many moving pieces."),
    ]),
    (7, "Life Stages and Investing", "Changing over time", [
        ("Early Years", "More growth, a longer horizon."),
        ("Middle Years", "Balancing growth and safety."),
        ("Later Years", "Protecting what you have built."),
    ]),
    (7, "Portfolio Recap", "Ready for macro", [
        ("Your Portfolio System", "A recap of allocation and discipline."),
        ("The Calm Investor", "Psychology plus process."),
        ("Next: Macro", "How the economy moves markets."),
    ]),

    # ====== Tier 8: Maerkte und Makrooekonomie - Markets & macro (u141-u160) ======
    (8, "The Economy and Markets", "The big backdrop", [
        ("How They Connect", "The economy shapes the markets."),
        ("Leading Indicators", "Signals that hint at what is ahead."),
        ("The Big Picture", "Zooming out from single stocks."),
    ]),
    (8, "Economic Cycles", "Booms and busts", [
        ("Expansion and Recession", "The rhythm of the economy."),
        ("The Four Phases", "Peak, slowdown, trough and recovery."),
        ("Investing Through Cycles", "Staying steady across the phases."),
    ]),
    (8, "GDP and Growth", "Measuring the economy", [
        ("What Is GDP?", "The overall size of an economy."),
        ("Growth and Recession", "Rising versus shrinking output."),
        ("Why It Matters", "Growth affects company profits."),
    ]),
    (8, "Inflation", "Rising prices", [
        ("What Is Inflation?", "Prices climbing across the economy."),
        ("Causes of Inflation", "Demand, supply and the money supply."),
        ("Inflation and Investing", "Protecting your buying power."),
    ]),
    (8, "Interest Rates", "The price of money", [
        ("What Sets Rates", "Central banks and the markets."),
        ("Rates and the Economy", "Cooling or heating up growth."),
        ("Rates and Assets", "How rates move stocks and bonds."),
    ]),
    (8, "Central Banks", "The economy's steering wheel", [
        ("What They Do", "Managing money and interest rates."),
        ("The Fed and Others", "Key central banks around the world."),
        ("Tools They Use", "Rates and the money supply."),
    ]),
    (8, "Monetary Policy", "Managing the money supply", [
        ("Easy vs Tight", "Loosening or tightening money."),
        ("Quantitative Easing", "Central banks buying assets."),
        ("Effects on Markets", "Liquidity and asset prices."),
    ]),
    (8, "Fiscal Policy", "The government's role", [
        ("Spending and Taxes", "How governments steer growth."),
        ("Deficits and Debt", "Spending more than is earned."),
        ("Effects on Markets", "Stimulus and its limits."),
    ]),
    (8, "Employment and Wages", "The jobs picture", [
        ("Unemployment Rate", "How many want work but lack it."),
        ("Wage Growth", "Rising pay and its effects."),
        ("Jobs and Markets", "Why investors watch jobs data."),
    ]),
    (8, "Currencies and Forex", "Money across borders", [
        ("Exchange Rates", "What one currency swaps for."),
        ("What Moves Them", "Rates, trade and confidence."),
        ("Currency and Investing", "Effects on global returns."),
    ]),
    (8, "Global Trade", "The connected world", [
        ("Imports and Exports", "Goods flowing between nations."),
        ("Trade Balances", "Surpluses and deficits."),
        ("Trade and Markets", "How trade shapes economies."),
    ]),
    (8, "Commodities and the Economy", "Raw-material signals", [
        ("Oil and Growth", "Energy prices and the economy."),
        ("Gold and Fear", "A haven in uncertain times."),
        ("Commodities as Signals", "Reading the raw-material story."),
    ]),
    (8, "Bonds and the Yield Curve", "The market's mood", [
        ("The Yield Curve", "Rates across different maturities."),
        ("Normal vs Inverted", "What the shape can signal."),
        ("Why Investors Watch", "A window into expectations."),
    ]),
    (8, "Market Sentiment", "The mood of investors", [
        ("Fear and Greed", "Emotions that move whole markets."),
        ("Sentiment Indicators", "Gauges of the crowd's mood."),
        ("Contrarian Thinking", "Going against the extremes."),
    ]),
    (8, "Bubbles and Crashes", "Market extremes", [
        ("Anatomy of a Bubble", "How prices detach from value."),
        ("Famous Examples", "Historic booms and busts."),
        ("Lessons Learned", "Staying grounded in a mania."),
    ]),
    (8, "Geopolitics and Markets", "World events", [
        ("Politics and Prices", "Elections, policy and markets."),
        ("Global Events", "Conflicts and crises rippling through."),
        ("Staying Focused", "Not overreacting to headlines."),
    ]),
    (8, "Sector Rotation", "Money on the move", [
        ("What Is Rotation?", "Money shifting between sectors."),
        ("Cycles and Sectors", "Which sectors tend to lead when."),
        ("Reading Rotation", "Clues about the economy."),
    ]),
    (8, "Reading Economic Data", "Making sense of numbers", [
        ("Key Reports", "Inflation, jobs and growth data."),
        ("Expectations Matter", "Surprises move the markets."),
        ("Avoiding Overreaction", "Data is noisy in the short term."),
    ]),
    (8, "Long-Term Trends", "Slow-moving forces", [
        ("Demographics", "Populations shaping economies."),
        ("Technology", "Innovation reshaping industries."),
        ("Investing for Trends", "Positioning for the long run."),
    ]),
    (8, "Macro Recap", "Ready for the pros", [
        ("The Macro Lens", "A recap of the big picture."),
        ("Context for Investing", "How macro informs decisions."),
        ("Next: Professional", "Advanced tools and strategies."),
    ]),

    # ==== Tier 9: Professionelles Investieren - Professional investing (u161-u180) ====
    (9, "Professional Investing", "Leveling up", [
        ("Beyond the Basics", "More rigorous approaches."),
        ("Systematic Thinking", "Rules over hunches."),
        ("Managing Complexity", "Keeping discipline as tools grow."),
    ]),
    (9, "Investment Styles", "Different playbooks", [
        ("Value Investing", "Buying below estimated worth."),
        ("Growth Investing", "Paying up for fast expansion."),
        ("Blend Approaches", "Combining the two styles."),
    ]),
    (9, "Factor Investing", "What drives returns", [
        ("What Is a Factor?", "A trait linked to returns."),
        ("Common Factors", "Value, size, quality and momentum."),
        ("Factor Portfolios", "Tilting toward chosen factors."),
    ]),
    (9, "Value and Growth Factors", "Two classic tilts", [
        ("The Value Factor", "Cheap stocks outperforming over time."),
        ("The Growth Factor", "Fast-growing companies."),
        ("Cycles of Leadership", "Why styles take turns leading."),
    ]),
    (9, "Quality and Momentum", "Two more factors", [
        ("The Quality Factor", "Strong, profitable firms."),
        ("The Momentum Factor", "Winners tending to keep winning."),
        ("Combining Factors", "Diversifying across drivers."),
    ]),
    (9, "Smart Beta", "Rules-based investing", [
        ("What Is Smart Beta?", "Indexing with factor tilts."),
        ("How It Works", "Rules instead of a manager."),
        ("Pros and Cons", "Cost, transparency and limits."),
    ]),
    (9, "Options Basics", "Contracts, not shares", [
        ("Calls and Puts", "The right to buy (call) or sell (put)."),
        ("Why They Exist", "Hedging risk and speculating."),
        ("Risk Warning", "Options can expire worthless; risky."),
    ]),
    (9, "Using Options to Hedge", "Managing risk", [
        ("What Is Hedging?", "Reducing downside risk."),
        ("Protective Puts", "Insurance for a holding."),
        ("Covered Calls", "Income from shares you already own."),
    ]),
    (9, "Futures and Derivatives", "Advanced instruments", [
        ("What Are Futures?", "Agreements to trade later."),
        ("Why They Exist", "Hedging and price discovery."),
        ("High Leverage", "Amplified risk and reward."),
    ]),
    (9, "Leverage and Shorting", "High-risk tools", [
        ("Buying on Margin", "Borrowing to invest amplifies both ways."),
        ("Short Selling", "Profiting from a falling price."),
        ("Leverage Risk", "How leverage can wipe out capital."),
    ]),
    (9, "Risk Metrics", "Measuring precisely", [
        ("Beta", "Sensitivity to the overall market."),
        ("Alpha", "Return beyond the benchmark."),
        ("Volatility Measures", "Quantifying the swings."),
    ]),
    (9, "Portfolio Optimization", "Building efficiently", [
        ("The Efficient Frontier", "Best return for a level of risk."),
        ("Diversification Math", "Why mixing genuinely helps."),
        ("Practical Limits", "Where the theory breaks down."),
    ]),
    (9, "Hedging Strategies", "Protecting portfolios", [
        ("Diversification as Defense", "The first line of protection."),
        ("Using Derivatives", "Options and futures to hedge."),
        ("The Cost of Insurance", "Hedging is never free."),
    ]),
    (9, "Quantitative Investing", "Data-driven approaches", [
        ("What Is Quant?", "Rules and data over intuition."),
        ("Backtesting", "Testing ideas on past data."),
        ("Pitfalls", "Overfitting and false patterns."),
    ]),
    (9, "Alternative Strategies", "Beyond long-only", [
        ("Long-Short", "Betting up and down at once."),
        ("Market Neutral", "Removing market direction."),
        ("The Complexity Cost", "Higher fees and higher risk."),
    ]),
    (9, "Income Strategies", "Investing for cash flow", [
        ("Dividend Investing", "Owning steady dividend payers."),
        ("Bond Ladders", "Staggering bond maturities."),
        ("Income and Risk", "Not reaching too far for yield."),
    ]),
    (9, "Tax Optimization", "Advanced efficiency", [
        ("Tax-Loss Harvesting", "Using losses to reduce tax."),
        ("Wash-Sale Rule", "A limit on harvesting losses."),
        ("Long-Term Advantage", "Holding for lower tax."),
    ]),
    (9, "Managing a Larger Portfolio", "Scaling up", [
        ("More Moving Parts", "Complexity grows with size."),
        ("Staying Organized", "Systems and regular reviews."),
        ("Keeping Discipline", "Sticking to the plan at scale."),
    ]),
    (9, "Building an Edge", "Thinking like a pro", [
        ("Sources of Edge", "Information, analysis and behavior."),
        ("A Repeatable Process", "Consistency over luck."),
        ("Continuous Learning", "Improving over time."),
    ]),
    (9, "Professional Recap", "Ready for mastery", [
        ("The Pro Toolkit", "A recap of advanced tools."),
        ("Rigor and Discipline", "What sets professionals apart."),
        ("Next: Mastery", "The most advanced concepts."),
    ]),

    # ================ Tier 10: Investment Mastery (u181-u200) ================
    (10, "Investment Mastery", "The final tier", [
        ("What Mastery Means", "Depth, discipline and judgement."),
        ("Integrating Everything", "Combining all you have learned."),
        ("Lifelong Practice", "Investing as a craft."),
    ]),
    (10, "Discounted Cash Flow", "Valuing the future", [
        ("What Is DCF?", "Valuing future cash in today's terms."),
        ("Present Value", "Why future money is worth less now."),
        ("The Big Assumptions", "Small changes, big effects."),
    ]),
    (10, "Cost of Capital", "The hurdle rate", [
        ("What Is It?", "The return investors require."),
        ("The WACC Idea", "Blending the cost of debt and equity."),
        ("Why It Matters", "Judging whether projects add value."),
    ]),
    (10, "Scenario Analysis", "Planning for many futures", [
        ("Best, Base, Worst", "Mapping possible outcomes."),
        ("Assigning Odds", "Weighing each scenario."),
        ("Deciding Under Uncertainty", "Preparing, not predicting."),
    ]),
    (10, "Monte Carlo Concepts", "Ranges, not points", [
        ("What Is Monte Carlo?", "Simulating many possible outcomes."),
        ("Distributions of Results", "A range of possibilities."),
        ("Using It Wisely", "Insight, not certainty."),
    ]),
    (10, "Advanced Derivatives", "Complex instruments", [
        ("Option Pricing Ideas", "What drives an option's value."),
        ("The Greeks", "The sensitivities of options."),
        ("Structured Products", "Bundled, complex payoffs."),
    ]),
    (10, "Institutional Investing", "How the big players work", [
        ("Pension Funds", "Investing for future retirees."),
        ("Endowments", "Long-horizon institutional money."),
        ("Their Advantages", "Scale, access and horizon."),
    ]),
    (10, "Private Equity", "Investing in private firms", [
        ("What Is PE?", "Owning companies not on exchanges."),
        ("How It Works", "Buying, improving and selling."),
        ("Risks and Illiquidity", "Money locked up for years."),
    ]),
    (10, "Venture Capital", "Funding startups", [
        ("What Is VC?", "Backing young, high-risk firms."),
        ("The Power Law", "A few winners drive the returns."),
        ("High Risk, High Reward", "Most fail; a few soar."),
    ]),
    (10, "Hedge Funds", "Flexible strategies", [
        ("What Is a Hedge Fund?", "Pooled, flexible investment strategies."),
        ("Common Approaches", "Long-short, macro and more."),
        ("Fees and Access", "High costs and limited entry."),
    ]),
    (10, "Alternative Assets Deep Dive", "Beyond stocks and bonds", [
        ("Real Assets", "Property, infrastructure and land."),
        ("Collectibles", "Art, wine and rarities."),
        ("Role in a Portfolio", "Diversification and caution."),
    ]),
    (10, "Global Macro Strategy", "Trading the big picture", [
        ("Top-Down Thinking", "From the economy to positions."),
        ("Cross-Asset Views", "Stocks, bonds and currencies together."),
        ("Managing Big Bets", "Sizing and risk control."),
    ]),
    (10, "Risk Parity and Beyond", "Advanced allocation", [
        ("What Is Risk Parity?", "Balancing by risk, not dollars."),
        ("Leverage in Allocation", "Boosting low-risk assets."),
        ("The Trade-offs", "Complexity and assumptions."),
    ]),
    (10, "Wealth Protection", "Guarding what you build", [
        ("Preserving Capital", "Not losing what you already have."),
        ("Diversifying Risk", "Spreading beyond the markets."),
        ("Estate Basics", "Passing wealth on, simply."),
    ]),
    (10, "Estate and Legacy Planning", "The long view", [
        ("Wills and Trusts", "Directing where your assets go."),
        ("Passing on Wealth", "Planning across generations."),
        ("Giving Back", "Philanthropy and legacy."),
    ]),
    (10, "Your Investment Philosophy", "Your own north star", [
        ("Core Beliefs", "What you believe about markets."),
        ("Your Edge and Limits", "Playing to your strengths."),
        ("Writing It Down", "A philosophy you can follow."),
    ]),
    (10, "A Long-Term Strategy", "The master plan", [
        ("Goals to Strategy", "Turning goals into a plan."),
        ("Rules and Guardrails", "Decisions made in advance."),
        ("Adapting Over Time", "Evolving without drifting."),
    ]),
    (10, "Continuous Improvement", "Getting better forever", [
        ("Reviewing Decisions", "Learning from wins and losses."),
        ("Keeping a Journal", "Recording your reasoning."),
        ("Lifelong Learning", "Markets always keep teaching."),
    ]),
    (10, "Pitfalls at Every Level", "Staying humble", [
        ("Overconfidence", "The expert's biggest risk."),
        ("Needless Complexity", "Simpler often wins."),
        ("Forgetting the Basics", "Fundamentals always matter."),
    ]),
    (10, "The Mastery Recap", "Your investing journey", [
        ("The Complete Investor", "A recap of the whole journey."),
        ("Knowledge Into Action", "Applying it thoughtfully."),
        ("The Journey Continues", "Investing as lifelong learning."),
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
