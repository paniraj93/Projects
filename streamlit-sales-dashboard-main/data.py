import pymongo
import pandas as pd
from datetime import datetime

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["store"]
collection = db["data"]

# Form the full file path
excel_file_path = 'supermarkt_sales.xlsx'

# Load data from Excel into a pandas DataFrame, skipping the first 3 rows and the first column
df = pd.read_excel(excel_file_path, skiprows=3, usecols=lambda x: x != 'Unnamed: 0')

# Convert 'Time' column to string format
df['Time'] = df['Time'].apply(lambda x: x.strftime('%H:%M:%S'))

# Check column names
print(df.columns)

# Convert DataFrame to list of dictionaries
data = df.to_dict(orient='records')

# Insert data into MongoDB
collection.insert_many(data)

# Confirm insertion
print("Data inserted successfully.")
