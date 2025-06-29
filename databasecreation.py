import csv
from datetime import datetime
from app_lego import app, db
from app_lego.models import CatalogItem

# Функция для преобразования строк в булевы значения
def str_to_bool(s):
    return s.strip().lower() in ['true', '1', 'yes']

with app.app_context():
    # Открываем CSV файл
    with open('database.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Обработка заголовков: убираем пробелы и делаем их нижним регистром
        rows = []
        for row in reader:
            row = {k.strip(): v for k, v in row.items()}
            rows.append(row)
        
        for row in rows:
            # Создаем объект CatalogItem
            item = CatalogItem(
                lot_id=row['Lot ID'].strip(),
                color=row['Color'].strip(),
                category=row['Category'].strip(),  # предполагается, что category - это id (число)
                condition=row.get('Condition', '').strip(),
                sub_condition=row.get('Sub-Condition', '').strip(),
                description=row.get('Description', '').strip(),
                remarks=row.get('Remarks', '').strip(),
                price=float(row['Price'].replace('$', '').strip()) if row['Price'] else None,
                quantity=int(row['Quantity']) if row['Quantity'] else None,
                bulk=str_to_bool(row.get('Bulk', 'False')),
                sale=str_to_bool(row.get('Sale', 'False')),
                url=row.get('URL', '').strip(),
                item_no=row.get('Item No', '').strip(),
                tier_qty_1=int(row['Tier Qty 1']) if row['Tier Qty 1'] else None,
                tier_price_1=float(row['Tier Price 1'].replace('$', '').strip()) if row['Tier Price 1'] else None,
                tier_qty_2=int(row['Tier Qty 2']) if row['Tier Qty 2'] else None,
                tier_price_2=float(row['Tier Price 2'].replace('$', '').strip()) if row['Tier Price 2'] else None,
                tier_qty_3=int(row['Tier Qty 3']) if row['Tier Qty 3'] else None,
                tier_price_3=float(row['Tier Price 3'].replace('$', '').strip()) if row['Tier Price 3'] else None,
                reserved_for=row.get('Reserved For', '').strip(),
                stockroom=row.get('Stockroom', '').strip(),
                retain=str_to_bool(row.get('Retain', 'False')),
                super_lot_id=row.get('Super Lot ID', '').strip(),
                super_lot_qty=int(row['Super Lot Qty']) if row['Super Lot Qty'] else None,
                weight=float(row['Weight']) if row['Weight'] else None,
                extended_description=row.get('Extended Description', '').strip(),
                
    
                date_added=datetime.strptime(row['Date Added'], '%m/%d/%Y') if row.get('Date Added') else None,
                date_last_sold=datetime.strptime(row['Date Last Sold'], '%Y-%m-%d') if row.get('Date Last Sold') else None,
                
                currency=row.get('Currency', '').strip()
            )
            db.session.add(item)
    db.session.commit()