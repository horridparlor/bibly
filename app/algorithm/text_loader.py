from PIL import Image, ImageDraw, ImageFont
import kivy

def measure_text_progress(font_size, width, height, words, start_index):
    kivy_data_dir = kivy.kivy_data_dir
    font_path = f"{kivy_data_dir}/fonts/Roboto-Regular.ttf"

    font = ImageFont.truetype(font_path, font_size)

    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    current_width, current_height = 0, 0

    for i, word in enumerate(words[start_index:], start=start_index):
        if '\n' in word:
            current_height += font.getsize(word)[1]
            current_width = 0
            if current_height > height:
                return i
            continue

        word_width, word_height = font.getsize(word + " ")

        if current_width + word_width > width:
            current_height += word_height
            current_width = 0
            if current_height > height:
                return i

        current_width += word_width

    return len(words) - 1


def split_text(text):
    lines = text.split('\n')
    words_with_linebreaks = []
    last_was_space = False

    for line in lines:
        if not len(line.strip()):
            if last_was_space:
                continue
            last_was_space = True
        last_was_space = False
        words_with_linebreaks.extend(line.split())

        if line != lines[-1]:
            words_with_linebreaks.append('\n')

    return words_with_linebreaks