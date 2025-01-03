import csv
import sqlite3
import re

def clean_price(price_str):
    # Remove '₹' symbol and convert to float
    try:
        # Remove '₹' and any whitespace, then convert to float
        return float(re.sub(r'[₹\s,]', '', price_str))
    except:
        return 0.0

def import_medicines():
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    
    # Read the CSV file and insert data
    with open('A_Z_medicines_dataset_of_India.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        # Prepare insert statement
        insert_query = '''
        INSERT OR REPLACE INTO medicines 
        (id, name, price, is_banned, manufacturer_name, type, 
         pack_size_label, short_composition1, short_composition2, stock)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        for row in csv_reader:
            try:
                # Clean and prepare the data
                medicine_id = int(row['id'])
                name = row['name'].strip()
                price = clean_price(row['price(₹)'])
                is_banned = 1 if row['is_banned'].lower() in ['true', '1', 'yes'] else 0
                manufacturer = row['manufacturer_name'].strip()
                med_type = row['type'].strip()
                pack_size = row['pack_size_label'].strip()
                comp1 = row['short_composition1'].strip() if row['short_composition1'] else None
                comp2 = row['short_composition2'].strip() if row['short_composition2'] else None
                
                # Default stock value
                stock = 100
                
                # Insert the data
                cursor.execute(insert_query, (
                    medicine_id, name, price, is_banned, manufacturer,
                    med_type, pack_size, comp1, comp2, stock
                ))
                
            except Exception as e:
                print(f"Error processing row {row.get('id', 'unknown')}: {str(e)}")
                continue
    
    # Commit the changes and close the connection
    conn.commit()
    
    # Print summary
    cursor.execute("SELECT COUNT(*) FROM medicines")
    total_medicines = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM medicines WHERE is_banned = 1")
    banned_medicines = cursor.fetchone()[0]
    
    print(f"\nImport Summary:")
    print(f"Total medicines imported: {total_medicines}")
    print(f"Banned medicines: {banned_medicines}")
    
    conn.close()

if __name__ == "__main__":
    try:
        import_medicines()
        print("\nMedicine data import completed successfully!")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
