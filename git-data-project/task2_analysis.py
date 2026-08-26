import pandas as pd
import sqlite3
from pathlib import Path
import matplotlib.pyplot as plt

# -----------------------------
# 1. Load CSV and create SQLite
# -----------------------------
BASE_DIR = Path(__file__).parent
csv_path = BASE_DIR / "github_projects.csv"
db_path = BASE_DIR / "github_projects.db"
viz_dir = BASE_DIR / "visualizations"
viz_dir.mkdir(exist_ok=True)

df = pd.read_csv(csv_path)

conn = sqlite3.connect(db_path)
df.to_sql("Repositories", conn, if_exists="replace", index=False)

# -----------------------------
# 2. Filtering & Searching
# -----------------------------
over_10000_stars = pd.read_sql_query("""
    SELECT *
    FROM Repositories
    WHERE stars > 10000;
""", conn)

machine_repositories = pd.read_sql_query("""
    SELECT *
    FROM Repositories
    WHERE name LIKE '%Machine%';
""", conn)

# -----------------------------
# 3. Logical Operators
# -----------------------------
and_query = pd.read_sql_query("""
    SELECT name, language, stars, forks
    FROM Repositories
    WHERE stars > 1000 AND forks > 100;
""", conn)

or_query = pd.read_sql_query("""
    SELECT name, language, stars, forks
    FROM Repositories
    WHERE language = 'Python' OR language = 'Jupyter Notebook';
""", conn)

not_query = pd.read_sql_query("""
    SELECT name, language, stars
    FROM Repositories
    WHERE NOT language = 'Python';
""", conn)

# -----------------------------
# 4. Sorting & Top 10
# -----------------------------
top_10 = pd.read_sql_query("""
    SELECT name, owner, language, stars, forks
    FROM Repositories
    ORDER BY stars DESC
    LIMIT 10;
""", conn)

# -----------------------------
# 5. Aggregate Functions
# -----------------------------
summary = pd.read_sql_query("""
    SELECT
        COUNT(*) AS total_repositories,
        AVG(stars) AS average_stars
    FROM Repositories;
""", conn)

# -----------------------------
# 6. Grouping Analysis
# -----------------------------
language_groups = pd.read_sql_query("""
    SELECT
        language,
        COUNT(*) AS repository_count
    FROM Repositories
    WHERE language IS NOT NULL
      AND language != ''
    GROUP BY language
    HAVING COUNT(*) > 5
    ORDER BY repository_count DESC;
""", conn)

# -----------------------------
# 7. Visualization: Top 10
# -----------------------------
top10_plot = top_10.sort_values("stars", ascending=True)

plt.figure(figsize=(10, 6))
plt.barh(top10_plot["name"], top10_plot["stars"])
plt.xlabel("Stars")
plt.ylabel("Repository")
plt.title("Top 10 Most Popular GitHub Repositories")
plt.tight_layout()
plt.savefig(viz_dir / "popular_repositories.png", dpi=150)
plt.close()

# -----------------------------
# 7. Visualization: Creation Trends
# -----------------------------
dates = pd.read_sql_query("""
    SELECT created_date
    FROM Repositories
    WHERE created_date IS NOT NULL
      AND created_date != '';
""", conn)

dates["created_date"] = pd.to_datetime(dates["created_date"], errors="coerce")
trend = (
    dates.dropna()
         .assign(year=lambda x: x["created_date"].dt.year)
         .groupby("year")
         .size()
)

plt.figure(figsize=(10, 6))
plt.plot(trend.index, trend.values, marker="o")
plt.xlabel("Year")
plt.ylabel("Number of Repositories Created")
plt.title("GitHub Repository Creation Trends Over Time")
plt.tight_layout()
plt.savefig(viz_dir / "creation_trends.png", dpi=150)
plt.close()

# -----------------------------
# 8. Save SQL results
# -----------------------------
results_dir = BASE_DIR / "sql_results"
results_dir.mkdir(exist_ok=True)

results = {
    "over_10000_stars": over_10000_stars,
    "machine_repositories": machine_repositories,
    "and_query": and_query,
    "or_query": or_query,
    "not_query": not_query,
    "top_10": top_10,
    "summary": summary,
    "language_groups": language_groups
}

for filename, result in results.items():
    result.to_csv(results_dir / f"{filename}.csv", index=False)

# -----------------------------
# 8. Print key findings
# -----------------------------
print("Task 2 completed successfully.")
print("\nSummary:")
print(summary.to_string(index=False))

print("\nTop 10 repositories:")
print(top_10.to_string(index=False))

print("\nLanguages with more than 5 repositories:")
print(language_groups.to_string(index=False))

conn.close()
