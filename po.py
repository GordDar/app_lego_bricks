from flask import render_template, redirect, url_for, request, flash, Request, Blueprint, jsonify, session
from app_lego import db

from app_lego.models import Part, Category
from bs4 import BeautifulSoup



def parse_xml_and_query():
    # Используйте сырую строку для пути
    xml_file_path = r'D:\lego_store\Ekaterina.xml'
    output_lines = []

    with open(xml_file_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()

    soup = BeautifulSoup(xml_content, 'lxml', features='xml') 
    items = soup.find_all('ITEM')

    for item in items:
        item_id_text = item.find('ITEMID').text
        item_type = item.find('ITEMTYPE').text
        color = item.find('COLOR').text
        max_price_text = item.find('MAXPRICE').text
        min_qty_text = item.find('MINQTY').text
        condition = item.find('CONDITION').text
        notify = item.find('NOTIFY').text

        try:
            item_id = int(item_id_text)
            max_price = float(max_price_text)
            min_qty = int(min_qty_text)
        except (ValueError, AttributeError):
            output_lines.append(f"Некорректные данные для ITEMID={item_id_text}")
            continue

        existing_item = Part.query.filter_by(lot_id=item_id).first()

        if existing_item:
            output_lines.append(f"Найден товар: {existing_item}")
        else:
            output_lines.append(f"Товар с ITEMID={item_id} не найден в базе.")

    return '<br>'.join(output_lines)