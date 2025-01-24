import sqlite3
import csv
import os

def create_database(db_name='address_book.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            firstname TEXT NOT NULL,
            surname TEXT NOT NULL,
            gender TEXT,
            goes_by TEXT,
            phone TEXT,
            mobile_phone TEXT,
            street_address TEXT default'',
            suburb TEXT,
            postcode TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_address(db_name, address_data):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO addresses (title, firstname, surname, gender, goes_by, phone, mobile_phone, street_address, suburb, postcode, email)
        VALUES (:title, :firstname, :surname, :gender, :goes_by, :phone, :mobile_phone, :street_address, :suburb, :postcode, :email)
    ''', {
        'title': address_data.get('title', ''),
        'firstname': address_data.get('firstname', ''),
        'surname': address_data.get('surname', ''),
        'gender': address_data.get('gender', ''),
        'goes_by': address_data.get('goes_by', ''),
        'phone': address_data.get('phone', ''),
        'mobile_phone': address_data.get('mobile_phone', ''),
        'street_address': address_data.get('street_address', ''),
        'suburb': address_data.get('suburb', ''),
        'postcode': address_data.get('postcode', ''),
        'email': address_data.get('email', '')
    })
    conn.commit()
    conn.close()

def edit_address(db_name, address_id, address_data):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    set_clause = ', '.join([f"{key} = :{key}" for key in address_data.keys()])
    address_data['id'] = address_id
    cursor.execute(f'''
        UPDATE addresses
        SET {set_clause}
        WHERE id = :id
    ''', address_data)
    conn.commit()
    conn.close()

def delete_address(db_name, address_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM addresses WHERE id = ?', (address_id,))
    conn.commit()
    conn.close()

def fetch_all_addresses(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM addresses')
    rows = cursor.fetchall()
    conn.close()
    return rows

def main():
    db_name = 'address_book.db'
    if not os.path.exists(db_name):
        create_database(db_name)
    
    # Insert sample addresses
    address1 = {
        'title': 'Mr', 'firstname': 'John', 'surname': 'Doe', 'gender': 'Male', 'goes_by': 'Johnny',
        'phone': '123-456-7890', 'mobile_phone': '098-765-4321', 'street_address': '123 Main St',
        'suburb': 'Anytown', 'postcode': '12345', 'email': 'john.doe@example.com'
    }
    address2 = {
        'title': 'Ms', 'firstname': 'Jane', 'surname': 'Smith', 'gender': 'Female', 'goes_by': 'Janey',
        'phone': '234-567-8901', 'mobile_phone': '987-654-3210', 'street_address': '456 Elm St',
        'suburb': 'Othertown', 'postcode': '67890', 'email': 'jane.smith@example.com'
    }
    insert_address(db_name, address1)
    insert_address(db_name, address2)
    
    # Edit an address
    address1_edit = {
        'email': 'john.doe@newdomain.com'
    }
    edit_address(db_name, 1, address1_edit)
    
    # Delete an address
    delete_address(db_name, 2)
    
    # Fetch and print all addresses
    addresses = fetch_all_addresses(db_name)
    for address in addresses:
        print(address)

def read_csv(file_path, limit=10000):
    entries = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            entries.append({
                'firstname': row[0],
                'surname': row[1],
                'gender': row[2]
            })
    return entries

def insert_multiple_addresses(db_name, addresses):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for address in addresses:
        cursor.execute('''
            INSERT INTO addresses (firstname, surname, gender)
            VALUES (:firstname, :surname, :gender)
        ''', address)
    conn.commit()
    conn.close()

def import_names(file_path, limit=10000):
    entries = read_csv(file_path, limit)
    insert_multiple_addresses(db_name, entries)
    
    

if __name__ == "__main__":
    db_name = 'address_book.db'
    create_database(db_name)
    file_path = '/Users/hherb/AI/datasets/demographics/name_dataset/data/GB.csv'
    import_names(file_path)
    # Fetch and print all addresses to verify
    addresses = fetch_all_addresses(db_name, how_many=10)
    for address in addresses:
        pprint(address)