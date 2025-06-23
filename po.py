

def build_nested_structure(paths):
    structure = {}
    for path in paths:
        CatalogItems = path.split('/')  # разбиваем путь по слэшу
        current_level = structure
        for CatalogItem in CatalogItems:
            if CatalogItem not in current_level:
                current_level[CatalogItem] = {}
            current_level = current_level[CatalogItem]
    paths = [
        'category 1',
        'category 2',
        'category 3/subcategory 1',
        'category 3/subcategory 2',
        'category 4/subcategory 1/subsub 1',
        'category 4/subcategory 1/subsub 2',
        'category 4/subcategory 2',
        'category 4/subcategory 3'
    ]

    import pprint  
    nested_structure = build_nested_structure(paths)

          
            
            
    return pprint.pprint(nested_structure)