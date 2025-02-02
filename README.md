## *Run the script to generate reports*

### Requirements
- Python 3.7 or higher

### Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

2. Install required packages from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

3. Place input CSV files in the `input` folder:
   - `bills.csv`
   - `legislators.csv`
   - `votes.csv`
   - `vote_results.csv`

4. Clean the `output` folder before running the script.

### Running the Script
Execute the following command:
```bash
python legislator_bill_report.py
```

### Output
The script will generate two CSV files in the `output` folder:
- `legislators-support-oppose-count.csv`
- `bills.csv`
