from config import symbols_per_second, default_pause
import re

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

    def pick_thread_by_max_seconds(thread, seconds):
        max_symbol_count = symbols_per_second * seconds
        pause_in_symbols = (symbols_per_second / 1000) * default_pause
        total_length = 0
        pause_count = 0
        max_comment_length = max_symbol_count / 3
        current_symbol_count = max_symbol_count

        thread.title = ThreadManager.filter_text(thread.title)
        title_length = len(thread.title)
        current_symbol_count -= title_length + pause_in_symbols
        total_length += title_length
        pause_count += 1

        comments = []
        for comment in thread.comments:
            if (current_symbol_count < 20):
                break

            comment.text = ThreadManager.filter_text(comment.text)

            comment_length = len(comment.text)

            if \
            comment_length < max_comment_length and \
            comment_length < current_symbol_count + 20 and \
            comment.text != "[removed]":
                comments.append(comment)
                current_symbol_count -= comment_length + pause_in_symbols
                total_length += comment_length
                pause_count += 1

        print(f"Max symbols - {int(max_symbol_count)}; Total symbols- {total_length}; Pauses - {pause_count} ({int(pause_count * pause_in_symbols)})")
        return comments, total_length

    def filter_text(text):
        text = re.sub(r'[\r\n]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text
