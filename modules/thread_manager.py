from config import symbols_per_second, default_pause
from mutagen.mp3 import MP3
import re, inflect

# Initialize the inflect engine
p = inflect.engine()

class ThreadManager:
    def pick_comments_by_symbol_count(thread, symbol_count):
        print(f"Pick Comments lenght-{symbol_count}")
        total_length = 0
        max_comment_length = symbol_count / 3
        print(f"--max lenght - {max_comment_length}")
        comments = []
        for comment in thread.comments:
            if (symbol_count < 20):
                break

            comment_length = len(comment.text)

            if \
            comment_length < max_comment_length and \
            comment_length < symbol_count + 20 and \
            comment.text != "[removed]":
                comments.append(comment)
                symbol_count -= comment_length
                total_length += comment_length

        return comments, total_length

    def pick_thread_by_max_seconds(thread, seconds, banned_comments = []):
        max_symbol_count = symbols_per_second * seconds
        pause_in_symbols = (symbols_per_second / 1000) * default_pause
        total_length = 0
        pause_count = 0
        max_comment_length = max_symbol_count / 3
        current_symbol_count_left = max_symbol_count

        thread.title = ThreadManager.filter_text(thread.title)
        title_length = len(thread.title)
        current_symbol_count_left -= title_length + pause_in_symbols
        total_length += title_length
        pause_count += 1

        comments = []
        for comment in thread.comments:
            if (current_symbol_count_left < 20):
                break

            if comment.identifier in banned_comments:
                continue

            comment.text = ThreadManager.filter_text(comment.text)

            if(ThreadManager.is_bad_text(comment.text)):
                continue

            comment_length = ThreadManager.get_adjusted_text_symbols(comment.text)

            if \
            comment_length < max_comment_length and \
            comment_length < current_symbol_count_left + 20 and \
            comment.text != "[removed]":
                comments.append(comment)
                current_symbol_count_left -= comment_length + pause_in_symbols
                total_length += comment_length
                pause_count += 1

        print(f"Max symbols - {int(max_symbol_count)}; Total symbols- {total_length}; Pauses - {pause_count} ({int(pause_count * pause_in_symbols)})")
        return comments, total_length

    def filter_text(text):
        text = re.sub(r'[\r\n]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    def is_bad_text(text):
        if "_" in text:
            return True

        return False

    def get_adjusted_text_symbols(text):
        length = len(text)
        digit_count = sum(char.isdigit() for char in text)
        length = (length - digit_count) + (digit_count * 3)
        return length

    def get_most_stand_out_comment(thread):
        most_stand_out_comment = 0
        most_stand_out_comment_identifier = None
        for comment in thread.comments:
            comment_length = ThreadManager.get_adjusted_text_symbols(comment.text)
            mp3_length = MP3(f"storage/audio/comments/{comment.identifier}.mp3").info.length
            comment_symbols_per_second = comment_length / mp3_length

            if comment_symbols_per_second > symbols_per_second:
                diff = comment_symbols_per_second - symbols_per_second
            else:
                diff = symbols_per_second - comment_symbols_per_second

            if diff > most_stand_out_comment:
                most_stand_out_comment = diff
                most_stand_out_comment_identifier = comment.identifier

        return most_stand_out_comment_identifier

    def convert_numbers_in_text(text):
        def replace_number_with_words(match):
            number = int(match.group())
            return p.number_to_words(number)

        converted_text = re.sub(r'\d+', replace_number_with_words, text)
        return converted_text
