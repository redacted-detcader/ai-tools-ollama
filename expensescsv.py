python -m 'import pandas as pd; df = pd.read_csv(\'politicians_finances.csv\'); anomalies = df[df['Expenses'] > df['Income']]; anomalies.to_csv(\'anomalies.csv\')'
