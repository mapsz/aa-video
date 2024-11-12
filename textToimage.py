from PIL import Image, ImageDraw, ImageFont
import textwrap
from datetime import datetime

# Параметры изображения
bubble_width, bubble_height = 500, 450  # ширина и высота бабла
background_color = (0, 0, 0, 0)  # прозрачный фон (RGBA)
bubble_color = (200, 200, 255, 255)  # цвет "бабла" (голубой, полный альфа-канал)
text_color = (0, 0, 0)  # цвет текста (черный)
outline_color = (0, 0, 0)  # цвет обводки
outline_width = 5  # ширина обводки

# Текст и дополнительные элементы
author = "dontbeahater_dear"  # только имя автора
likes = "3904"  # количество лайков
date = datetime.now().strftime("%d %B %Y")  # текущая дата в формате "день месяц год"
text = "My ex told me if i ever got a cat, he’d do his best to run it over with his car because he hates cats. \n\nThat was after i told him i loved cats and wanted go volunteer in a shelter."  # текст для отображения

# Создаем пустое изображение с прозрачным фоном, которое будет соответствовать размеру бабла
image = Image.new("RGBA", (bubble_width, bubble_height), background_color)
draw = ImageDraw.Draw(image)

# Задаем шрифт и размер текста
try:
    font = ImageFont.truetype("arial.ttf", 20)  # шрифт Arial, размер 20
    bold_font = ImageFont.truetype("arial.ttf", 22, encoding="unic")  # жирный шрифт для автора
except IOError:
    font = ImageFont.load_default()  # стандартный шрифт, если Arial не найден
    bold_font = font  # если Arial не найден, используем обычный шрифт

# Определяем ширину бабла
padding = 20  # отступы внутри бабла
max_text_width = bubble_width - 2 * padding

# Разбиваем основной текст на строки, чтобы каждая строка помещалась по ширине бабла
wrapped_text = textwrap.fill(text, width=50)

# Определяем размеры текста с переносом строк
text_lines = wrapped_text.splitlines()
line_height = draw.textbbox((0, 0), "hg", font=font)[3]  # высота строки
text_height = line_height * len(text_lines)

# Определяем шрифт и размеры для лайков и даты
likes_font = ImageFont.truetype("arial.ttf", 16) if font else ImageFont.load_default()
date_font = ImageFont.truetype("arial.ttf", 16) if font else ImageFont.load_default()

# Рассчитываем размеры лайков и даты
likes_text = f"{likes} "
likes_bbox = draw.textbbox((0, 0), likes_text, font=likes_font)
likes_width, likes_height = likes_bbox[2] - likes_bbox[0], likes_bbox[3] - likes_bbox[1]

date_bbox = draw.textbbox((0, 0), date, font=date_font)
date_width, date_height = date_bbox[2] - date_bbox[0], date_bbox[3] - date_bbox[1]

# Рассчитываем размеры автора
author_bbox = draw.textbbox((0, 0), author, font=bold_font)
author_width, author_height = author_bbox[2] - author_bbox[0], author_bbox[3] - author_bbox[1]

# Высота бабла с учетом текста, лайков, даты и автора
bubble_content_height = text_height + likes_height + date_height + author_height + padding * 4  # добавляем пространство между элементами

# Координаты бабла
bubble_x = (bubble_width - max_text_width) // 2
bubble_y = (bubble_height - bubble_content_height) // 2  # вертикальная позиция внутри бабла

# Рисуем обводку для бабла с хвостиком (увеличиваем размер на ширину обводки)
outline_bbox = (bubble_x - outline_width, bubble_y - outline_width,
                bubble_x + max_text_width + outline_width, bubble_y + bubble_content_height + outline_width)

# Рисуем закруглённый прямоугольник для обводки
draw.rounded_rectangle(outline_bbox, radius=25, fill=outline_color)

# Рисуем хвостик обводки
outline_tail = [
    (bubble_x + max_text_width - 40, bubble_y + bubble_content_height + outline_width),  # левый край хвостика
    (bubble_x + max_text_width - 60, bubble_y + bubble_content_height + 30 + outline_width),  # низ хвостика
    (bubble_x + max_text_width - 20, bubble_y + bubble_content_height + outline_width)  # правый край хвостика
]
draw.polygon(outline_tail, fill=outline_color)

# Рисуем сам бабл (внутри обводки)
draw.rounded_rectangle(
    (bubble_x, bubble_y, bubble_x + max_text_width, bubble_y + bubble_content_height),
    radius=20,
    fill=bubble_color
)

# Рисуем хвостик бабла
tail = [
    (bubble_x + max_text_width - 40, bubble_y + bubble_content_height),  # левый край хвостика
    (bubble_x + max_text_width - 60, bubble_y + bubble_content_height + 30),  # низ хвостика
    (bubble_x + max_text_width - 20, bubble_y + bubble_content_height)  # правый край хвостика
]
draw.polygon(tail, fill=bubble_color)

# Определяем место для размещения элементов (автора, лайков, даты)
bubble_content_y = bubble_y + padding  # Начальная позиция для текста внутри бабла

# Рисуем автора (слева, жирным шрифтом)
author_x = bubble_x + padding  # автор слева
draw.text((author_x, bubble_content_y), author, fill=text_color, font=bold_font)
bubble_content_y += author_height + padding  # Отступ после автора

# Рисуем основной текст
for line in text_lines:
    text_x = bubble_x + padding
    draw.text((text_x, bubble_content_y), line, fill=text_color, font=font)
    bubble_content_y += line_height  # переносим курсор на следующую строку

# Добавляем отступ перед лайками и датой
bubble_content_y += padding

# Вставляем изображение сердечка
heart_image = Image.open("heart.png")  # путь к вашему изображению сердечка (например, heart.png)

# Преобразуем изображение в RGBA (если оно не в этом формате)
heart_image = heart_image.convert("RGBA")

# Масштабируем сердечко до нужного размера
heart_size = 20  # размер сердечка
heart_image = heart_image.resize((heart_size, heart_size))

# Определяем координаты для вставки сердечка
heart_x = bubble_x + padding  # сдвигаем сердечко на отступ от левого края
heart_y = bubble_content_y  # позиция сердечка сразу после текста

# Вставляем сердечко на изображение с альфа-каналом как маской
image.paste(heart_image, (heart_x, heart_y), heart_image.split()[3])  # используем альфа-канал как маску

# Позиции для лайков и даты
likes_x = heart_x + heart_size + 5
date_x = bubble_x + max_text_width - padding - date_width

# Рисуем лайки и дату на одной строке внутри бабла
draw.text((likes_x, bubble_content_y), likes_text, fill=text_color, font=likes_font)
draw.text((date_x, bubble_content_y), date, fill=text_color, font=date_font)

# Сохраняем изображение с прозрачным фоном, соответствующее размеру бабла
image.save("comic_bubble_with_heart_image.png")

# Показываем изображение (необязательно)
image.show()
