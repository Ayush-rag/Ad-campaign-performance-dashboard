"""Run the whole project from start to finish:

    python main.py

1. Generate the raw ad export        -> data/raw/
2. Clean it                          -> data/processed/
3. Load it into a SQL database       -> data/ad_campaigns.db
4. Run SQL KPI queries + insights    -> outputs/
5. Build the interactive dashboard   -> docs/index.html
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import build_dashboard  # noqa: E402
import clean_data  # noqa: E402
import generate_data  # noqa: E402
import load_database  # noqa: E402
import run_analysis  # noqa: E402

if __name__ == "__main__":
    print("\nAd Campaign Performance Dashboard - pipeline\n" + "-" * 46)
    generate_data.main()
    clean_data.main()
    load_database.main()
    run_analysis.main()
    build_dashboard.main()
    print("\nDone. Open docs/index.html in your browser to see the dashboard.\n")
