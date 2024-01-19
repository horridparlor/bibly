from kivy.storage.jsonstore import JsonStore
def load_data():
    store = JsonStore('save.json')
    if store.exists('data'):
        return store.get('data')['value']
    else:
        return {"books": {}, "fontSize": 12}

def save_data(data):
    store = JsonStore('save.json')
    store.put('data', value=data)

def get_book_progress(book_name):
    data = load_data()
    return data['books'].get(book_name, 0)

def set_book_progress(book_name, progress):
    data = load_data()
    data['books'][book_name] = progress
    save_data(data)

def get_font_size():
    data = load_data()
    return data['fontSize']

def set_font_size(font_size):
    data = load_data()
    data['fontSize'] = font_size
    save_data(data)
