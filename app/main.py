import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from algorithm.text_loader import measure_text_progress, split_text
from algorithm.saving import set_font_size, get_font_size, set_book_progress, get_book_progress
from kivy.core.window import Window
from kivy.uix.label import Label
from plyer import filechooser
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform

class ClickableLabel(ButtonBehavior, Label):
    pass


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)

        self.scroll_view = ScrollView()
        self.add_widget(self.scroll_view)

        self.grid_layout = GridLayout(cols=3, spacing=10, size_hint_y=None)
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))

        self.scroll_view.add_widget(self.grid_layout)
        self.load_texts()
        self.has_permission = False

    def load_texts(self):
        self.grid_layout.clear_widgets()
        for filename in os.listdir('books/'):
            if filename.endswith('.txt'):
                with open(os.path.join('books/', filename), 'r') as file:
                    text_content = file.read()
                word_count = len(text_content.split())

                book_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)

                btn = Button(text=f'{os.path.splitext(filename)[0]} - {word_count} words')
                btn.bind(on_press=self.open_reader)

                delete_btn = Button(text='X', size_hint_x=None, width=60, background_color=(1, 0, 0, 1))
                delete_btn.bind(on_press=lambda btn, filename=filename: self.delete_book(filename))

                book_layout.add_widget(btn)
                book_layout.add_widget(delete_btn)

                self.grid_layout.add_widget(book_layout)

        self.add_text_button = Button(text='Add New Text', size_hint_y=None, height=80, background_color=(0, 1, 0.5, 1))
        self.add_text_button.bind(on_press=self.show_upload_modal)
        self.grid_layout.add_widget(self.add_text_button)

    def open_reader(self, instance):
        self.manager.current = 'reader'
        self.manager.get_screen('reader').load_text(instance.text.split(' - ')[0])

    def show_upload_modal(self, instance):
        modal = UploadModal(self)
        modal.open()

    def delete_book(self, filename):
        os.remove(os.path.join('books/', filename))
        self.load_texts()


class ReaderScreen(Screen):
    window_margin_width = 40
    window_scale_height = 0.72

    def __init__(self, **kwargs):
        super(ReaderScreen, self).__init__(**kwargs)
        self.current_page = 0
        self.font_size = get_font_size()
        self.bookname = ''
        self.page_start = 0

        main_layout = BoxLayout(orientation='vertical')

        nav_layout = BoxLayout(size_hint_y=None, height=70)
        prev_page_10_button = Button(text='<<', size_hint_x=1.2, background_color=(0.1, 0.1, 0.1, 1), opacity=0.2)
        prev_page_10_button.bind(on_press=self.prev_page_10)
        nav_layout.add_widget(prev_page_10_button)

        self.page_label = ClickableLabel(opacity=0.2)
        self.page_label.bind(on_press=self.return_home)
        nav_layout.add_widget(self.page_label)

        next_page_10_button = Button(text='>>', size_hint_x=1.2, background_color=(0.1, 0.1, 0.1, 1), opacity=0.1)
        next_page_10_button.bind(on_press=self.next_page_10)
        nav_layout.add_widget(next_page_10_button)

        main_layout.add_widget(nav_layout)

        content_layout = BoxLayout(orientation='vertical', spacing=10)

        self.text_label = Label(size_hint=(1, 1))
        self.text_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value - 40, None)))
        content_layout.add_widget(self.text_label)

        font_nav_layout = BoxLayout(size_hint_y=None, height=70, opacity=0.2)
        prev_page_button = Button(text='<')
        prev_page_button.bind(on_press=self.prev_page)
        font_nav_layout.add_widget(prev_page_button)

        invisible_prev_button = Button(size_hint=(None, None), size=(100,
            self.window_scale_height * Window.size[0]),
            opacity=1, background_color=(0, 0, 0, 1))
        invisible_prev_button.bind(on_press=self.prev_page)
        invisible_prev_button.y = prev_page_button.top
        invisible_prev_button.pos_hint = {'left': 1, 'y': 0}
        self.add_widget(invisible_prev_button)

        decrease_font_button = Button(text='A-', size_hint_x=0.5, background_color=(0.1, 0.1, 0.1, 1))
        decrease_font_button.bind(on_press=self.decrease_font)
        font_nav_layout.add_widget(decrease_font_button)

        increase_font_button = Button(text='A+', size_hint_x=0.5, background_color=(0.1, 0.1, 0.1, 1))
        increase_font_button.bind(on_press=self.increase_font)
        font_nav_layout.add_widget(increase_font_button)

        next_page_button = Button(text='>')
        next_page_button.bind(on_press=self.next_page)
        font_nav_layout.add_widget(next_page_button)
        content_layout.add_widget(font_nav_layout)

        invisible_next_button = Button(size_hint=(None, None), size=(100,
            self.window_scale_height * Window.size[0]),
            opacity=1, background_color=(0, 0, 0, 1))
        invisible_next_button.bind(on_press=self.next_page)
        invisible_next_button.y = next_page_button.top
        invisible_next_button.pos_hint = {'right': 1, 'y': 0}
        self.add_widget(invisible_next_button)

        main_layout.add_widget(content_layout)
        self.add_widget(main_layout)

    def load_text(self, filename):
        self.bookname = filename
        with open(f"./books/{filename}.txt", 'r') as file:
            self.full_text = split_text(file.read())
            self.text_end = len(self.full_text) - 1

        self.reset_page()
        self.find_bookmark()

    def find_bookmark(self):
        bookmark = get_book_progress(self.bookname)
        while self.page_end < bookmark:
            self.next_page(False)
        self.page_flipped()

    def return_home(self, *args):
        self.manager.current = 'home'

    def update_text(self):
        set_font_size(self.font_size)
        self.text_label.font_size = self.font_size
        self.update_page_end()
        self.text_label.text = " ".join(self.full_text[self.page_start:self.page_end])
        self.page_label.text = f'Page {self.page_number + 1}'

    def update_page_end(self):
        self.page_end = measure_text_progress(self.font_size,
              int (Window.size[0] - self.window_margin_width),
              int(self.window_scale_height * Window.size[1]), self.full_text, self.page_start)
        set_book_progress(self.bookname, self.page_end)

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

    def next_page_10(self, *args):
        for i in range(10):
            if not self.next_page(False):
                break
        self.page_flipped()

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

    def prev_page_10(self, *args):
        for i in range(10):
            if not self.prev_page(False):
                break
        self.page_flipped()

    def increase_font(self, *args):
        if self.font_size > 128:
            return
        self.font_size += 8
        self.font_updated()

    def decrease_font(self, *args):
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

    def go_back(self, instance):
        self.manager.current = 'home'


class UploadModal(ModalView):
    def __init__(self, home_screen, **kwargs):
        super(UploadModal, self).__init__(**kwargs)
        self.home_screen = home_screen
        self.layout = BoxLayout(orientation='vertical')

        top_row = BoxLayout(orientation='horizontal', size_hint=(1, None), height=64)

        self.file_label = Label(text='No file selected', halign='left', size_hint=(1, 1))
        top_row.add_widget(self.file_label)

        close_button = Button(text='X', size_hint=(None, None), size=(64, 64))
        close_button.bind(on_press=self.dismiss_modal)
        top_row.add_widget(close_button)

        self.layout.add_widget(top_row)

        open_button = Button(text='Open', size_hint=(1, 0.1))
        open_button.bind(on_press=self.open_filechooser)
        self.layout.add_widget(open_button)

        upload_button = Button(text='Upload', size_hint=(1, 0.1))
        upload_button.bind(on_press=self.upload_file)
        self.layout.add_widget(upload_button)
        self.add_widget(self.layout)

        self.selected_file = None

    def dismiss_modal(self, instance):
        self.dismiss()

    def open_filechooser(self, instance):
        self.selected_file = filechooser.open_file(filters=['*.txt'])
        if self.selected_file:
            filename = os.path.basename(self.selected_file[0])
            self.file_label.text = filename
    def upload_file(self, instance):
        if self.selected_file:
            try:
                filename = os.path.basename(self.selected_file[0])
                os.makedirs('books/', exist_ok=True)
                with open(self.selected_file[0], 'r') as file:
                    content = file.read()
                with open(f'books/{filename}', 'w') as file:
                    file.write(content)
                self.home_screen.load_texts()
                self.dismiss()
            except Exception as e:
                print(f'Error: {e}')


class BookApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(ReaderScreen(name='reader'))
        return sm

if __name__ == '__main__':
    BookApp().run()
