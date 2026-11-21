"""Run the full pipeline: clean -> KPIs -> charts."""
from src import clean, kpis, charts

if __name__ == "__main__":
    clean.main()
    print("-" * 40)
    kpis.main()
    print("-" * 40)
    charts.main()
