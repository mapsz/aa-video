from PIL import Image, ImageDraw, ImageFont
from modules import make_dir
from datetime import datetime
import os

class TextToImage:
    def __init__():
        pass

    def text_to_lines_by_width(text, font, max_width):
        # Create an image and a drawing object to measure the text
        image = Image.new("RGB", (max_width, 100), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            # Check how the line will look with the added word
            test_line = current_line + ((" " if current_line else "") + word)

            # Calculate the bounding box for the text
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]  # Get the width of the bounding box

            # If the length of the line with the added word exceeds the max width, start a new line
            if width > max_width:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line

        # Add the last line if it's not empty
        if current_line:
            lines.append(current_line)

        return lines

    def get_font_height(font):
        # Create an image and a drawing object to measure the text
        image = Image.new("RGB", (500, 100), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        return draw.textbbox((0, 0), "hg", font=font)[3]

    def get_text_width(text, font):
        image = Image.new("RGB", (500, 100), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]

class ComicBubble:
    def __init__(self,
        author_font_path = "arial.ttf",
        text_font_path = "arial.ttf",
        author_font_size=18,
        text_font_size=16,
        image_width=500,
        bubble_color=(200, 200, 255, 255),
        text_color=(0, 0, 0),
        outline_color=(0, 0, 0),
        outline_width=4,
        padding=14,
        tail_height = 60,
    ):
        self.image_width = image_width
        self.bubble_color = bubble_color
        self.text_color = text_color
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.author_font_path = author_font_path
        self.text_font_path = text_font_path
        self.author_font_size = author_font_size
        self.text_font_size = text_font_size
        self.padding = padding
        self.tail_height = tail_height
        self.text_width = int(image_width - (padding * 2))
        self.author_font = ImageFont.truetype(author_font_path, size=author_font_size)
        self.text_font = ImageFont.truetype(text_font_path, size=text_font_size)

    def calculate_image_height(self, author_lines, text_lines):
        author_line_height = TextToImage.get_font_height(self.author_font)
        text_line_height = TextToImage.get_font_height(self.text_font)

        author_height = len(author_lines) * author_line_height
        text_height = len(text_lines) * text_line_height

        height = \
            self.padding + \
            author_height + \
            self.padding + \
            text_height + \
            self.padding + \
            text_line_height + \
            self.padding + \
            self.tail_height

        return height

    def generate(self, filepath, author, text, score, date):
        # Split By Lines
        author_lines = TextToImage.text_to_lines_by_width(author, self.author_font, self.text_width)
        text_lines = TextToImage.text_to_lines_by_width(text, self.text_font, self.text_width)

        image_height = self.calculate_image_height(author_lines, text_lines)

        # Draw image
        image = Image.new("RGBA", (self.image_width, image_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw border
        draw.rounded_rectangle((0, 0, self.image_width, image_height - self.tail_height), radius=25, fill=self.outline_color)

        # Draw bubble
        draw.rounded_rectangle(
            (
                self.outline_width,
                self.outline_width,
                self.image_width - self.outline_width,
                image_height - self.outline_width - self.tail_height
            ),
            radius=20,
            fill=self.bubble_color
        )

        #Draw Tail
        if self.tail_height > 0:
            outline_tail = [
                (self.image_width - (self.image_width * 0.19), image_height - self.tail_height),  # левый край хвостика
                (self.image_width - (self.image_width * 0.25), image_height),  # низ хвостика
                (self.image_width - (self.image_width * 0.1), image_height - self.tail_height)  # правый край хвостика
            ]
            draw.polygon(outline_tail, fill=self.outline_color)

            outline_tail = [
                (
                    self.image_width - (self.image_width * 0.19) + self.outline_width + (self.outline_width / 2),
                    image_height - self.tail_height - self.outline_width
                ),
                (
                    self.image_width - (self.image_width * 0.25) + self.outline_width + (self.outline_width / 2),
                    image_height - self.outline_width - (self.outline_width)
                ),
                (
                    self.image_width - (self.image_width * 0.1),
                    image_height - self.tail_height - self.outline_width
                ),
            ]
            draw.polygon(outline_tail, fill=self.bubble_color)

        #Draw author
        author_line_height = TextToImage.get_font_height(self.author_font)
        cursor_y = self.padding
        for line in author_lines:
            draw.text((self.padding, cursor_y), line, fill=self.text_color, font=self.author_font)
            cursor_y += author_line_height

        #Draw text
        text_line_height = TextToImage.get_font_height(self.text_font)
        cursor_y += self.padding
        for line in text_lines:
            draw.text((self.padding, cursor_y), line, fill=self.text_color, font=self.text_font)
            cursor_y += text_line_height

        #Draw score
        cursor_y += self.padding
        draw.text((self.padding, cursor_y), str(score), fill=self.text_color, font=self.text_font)
        cursor_y += text_line_height

        #Draw score hearth
        cursor_y -= text_line_height
        heart_image = Image.open("assets/images/heart.png").convert("RGBA").resize((text_line_height, text_line_height))
        score_width = TextToImage.get_text_width(str(score), self.text_font)
        image.paste(heart_image, (self.padding + score_width + 5, cursor_y), heart_image.split()[3])

        #Draw date
        date_text = str(date.strftime("%d %B %Y"))
        # date_text = str(datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%d %B %Y"))

        date_width = TextToImage.get_text_width(date_text, self.text_font)
        draw.text((self.image_width - date_width - self.padding, cursor_y), date_text, fill=self.text_color, font=self.text_font)

        image.save(f"{filepath}.png")

    def thread_to_images(self, thread):

        filepath = f"storage/images/threads/{thread.identifier}"
        if not os.path.exists(filepath):
            make_dir(filepath)
            self.generate(filepath, thread.author, thread.title, thread.score, thread.date)

        for comment in thread.comments:
            filepath = f"storage/images/comments/{comment.identifier}"
            if not os.path.exists(filepath):
                make_dir(filepath)
                self.generate(filepath, comment.author, comment.text, comment.score, comment.date)
