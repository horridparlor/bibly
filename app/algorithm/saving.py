import json
def load_data():
    try:
        with open('save.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"books": {}, "fontSize": 12}

def save_data(data):
    with open('save.json', 'w') as file:
        json.dump(data, file, indent=4)

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
