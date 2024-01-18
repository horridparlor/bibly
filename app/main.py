from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from algorithm.text_loader import measure_text_progress, split_text
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
from kivy.properties import StringProperty, NumericProperty

class BookItem(BoxLayout):
    book_name = StringProperty('')
    page_number = NumericProperty(0)
    reading_progress = NumericProperty(0)

class HomeScreen(Screen):
    availableBooks = [
        {'name': 'Book 1', 'page': 100, 'progress': 30},
        {'name': 'Book 2', 'page': 200, 'progress': 60},
        # Add more books as needed
    ]

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.load_books(), 0)

    def load_books(self):
        data = [
            {'book_name': book['name'], 'page_number': book['page'], 'reading_progress': book['progress']}
            for book in self.availableBooks
        ]
        print(data)
        print(self.ids)

class ReaderScreen(Screen):
    window_margin_width = 40
    window_scale_height = 0.76
    font_size = 32

    def __init__(self, **kwargs):
        super(ReaderScreen, self).__init__(**kwargs)

    def on_enter(self, *args):
        Clock.schedule_once(lambda dt: self.load_text(), 0)

    def load_text(self):
        with open('./data/mystory.txt', 'r') as file:
            self.full_text = split_text(file.read())
            self.text_end = len(self.full_text) - 1

        self.reset_page()
        self.current_start = 0
        self.update_text()

    def update_text(self):
        self.ids.text_label.font_size = self.font_size
        self.update_page_end()
        self.ids.text_label.text = " ".join(self.full_text[self.page_start:self.page_end])
        self.ids.page_label.text = f'Page {self.page_number + 1}'

    def update_page_end(self):
        self.page_end = measure_text_progress(self.font_size,
              int (Window.size[0] - self.window_margin_width),
              int(self.window_scale_height * Window.size[1]), self.full_text, self.page_start)

    def next_page(self, flipped = True):
        if self.page_end >= self.text_end:
            return False
        if len(self.page_starts) <= self.page_number:
            self.page_starts.append(0)
        self.page_starts[self.page_number] = self.page_start
        self.page_start = self.page_end
        self.page_number += 1
        self.update_text()
        if flipped:
            self.page_flipped()
        return True

    def next_page_10(self):
        for i in range(10):
            if not self.next_page():
                break

    def prev_page(self, flipped = True):
        if self.page_start == 0:
            return False
        self.page_start = self.page_starts[self.page_number - 1]
        self.page_number -= 1
        if flipped:
            self.page_flipped()
        return True

    def page_flipped(self):
        self.current_start = self.page_start
        self.update_text()

    def prev_page_10(self):
        for i in range(10):
            if not self.prev_page():
                break

    def increase_font(self):
        if self.font_size > 128:
            return
        self.font_size += 8
        self.font_updated()

    def decrease_font(self):
        if self.font_size <= 16:
            return
        self.font_size -= 8
        self.font_updated()

    def font_updated(self):
        self.reset_page()
        while self.page_start < self.current_start and self.page_end < self.current_start and self.next_page(False):
            self.update_page_end()
        self.update_text()

    def reset_page(self):
        self.page_start = 0
        self.page_end = 0
        self.page_starts = []
        self.page_number = 0

screenManager = ScreenManager()
screenManager.add_widget(HomeScreen(name='home'))
screenManager.add_widget(ReaderScreen(name='reader'))

class BiblyApp(App):
    def build(self):
        return screenManager

if __name__ == '__main__':
    BiblyApp().run()
