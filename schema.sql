-- Box Office Financial Database Schema Documentation
-- This file documents the structure of the SQLite database (enterprise.db) generated from our raw CSV data.

CREATE TABLE IF NOT EXISTS company_data (
    "SN" INTEGER PRIMARY KEY,
    "Movie" TEXT NOT NULL,
    "Worldwide" REAL,
    "India Net" REAL,
    "India Gross" REAL,
    "Overseas" REAL,
    "Budget" REAL,
    "Verdict" TEXT
);

-- ==========================================
-- 🤖 AI AGENT QUERY EXAMPLES
-- ==========================================
-- Below are examples of the raw SQL queries the LangChain SQL Agent 
-- dynamically generates and executes when asking questions about the movie data.

-- Example 1: Finding the top 5 highest-grossing movies worldwide
SELECT Movie, Worldwide 
FROM company_data 
ORDER BY Worldwide DESC 
LIMIT 5;

-- Example 2: Counting how many movies received each verdict (Blockbuster, Flop, etc.)
SELECT Verdict, COUNT(*) as Total_Movies 
FROM company_data 
GROUP BY Verdict 
ORDER BY Total_Movies DESC;

-- Example 3: Finding movies that made more overseas than their total budget
SELECT Movie, Overseas, Budget 
FROM company_data 
WHERE Overseas > Budget;