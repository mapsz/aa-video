import praw
import os
from datetime import datetime, timedelta
from config import reddit_config
from modules.models import Thread, Comment
from modules import get_session

class Reddit:
    def __init__(self):
        self.reddit = praw.Reddit( \
            client_id=reddit_config["client_id"], \
            client_secret=reddit_config["client_secret"], \
            user_agent=reddit_config["user_agent"] \
        )

    def fetch_top_threads(self, subreddit_name, limit=100):
        subreddit = self.reddit.subreddit(subreddit_name)

        top_threads = subreddit.top(time_filter="week", limit=100)

        sorted_threads = sorted(top_threads, key=lambda x: x.score, reverse=True)[:limit]

        threads = [
            Thread(
                source = Thread.REDDIT,
                identifier = submission.id,
                author = submission.author.name if submission.author else "[deleted]",
                score = int(submission.score),
                title = submission.title,
                date = datetime.fromtimestamp(submission.created_utc)
            )
            for submission in sorted_threads
        ]

        return threads

    def fetch_top_threads_for_date(self, subreddit_name, year, month, day, limit=5):
        start_time = datetime(year, month, day)
        end_time = start_time + timedelta(days=1)

        subreddit = self.reddit.subreddit(subreddit_name)

        top_threads = subreddit.top(time_filter="week", limit=100)

        filtered_threads = [
            submission for submission in top_threads
            if start_time <= datetime.utcfromtimestamp(submission.created_utc) < end_time
        ]

        sorted_threads = sorted(filtered_threads, key=lambda x: x.score, reverse=True)[:limit]

        threads = [
            Thread(
                source = Thread.REDDIT,
                identifier = submission.id,
                author = submission.author.name if submission.author else "[deleted]",
                score = int(submission.score),
                title = submission.title,
                date = datetime.fromtimestamp(submission.created_utc)
            )
            for submission in sorted_threads
        ]

        return threads

    def fetch_popular_comments(self, thread, comment_limit=50):
        print(f"fetch comments - {thread.identifier}")
        submission = self.reddit.submission(id=thread.identifier)
        submission.comments.replace_more(limit=0)

        popular_comments = sorted(submission.comments, key=lambda comment: comment.score, reverse=True)

        top_comments = popular_comments[:comment_limit]

        comments = []
        for submission in top_comments:
            comment = Comment(
                thread_id=thread.id,
                identifier=submission.id,
                author=submission.author.name if submission.author else "[deleted]",
                score=int(submission.score),
                text=submission.body,
                date=datetime.fromtimestamp(submission.created_utc),
                symbol_count=len(submission.body)
            )
            comments.append(comment)

        return comments

    def save_thread_to_file(self, thread, comments, symbol_count, filename):
        folder_path = "storage"
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, (f"{filename}.txt"))

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(f"Symbol Count:\n{symbol_count}\n\n")
            file.write(f"Title:\n{thread['title']}\n\n")
            for i, comment in enumerate(comments, start=1):
                file.write(f"Comment {i}:\n{comment}\n\n")

    def save(self, thread):
        session = get_session()
        session.add(thread)
        session.commit()
        session.close()

    def parse_threads(self, subreddit_name, year, month, day, limit=10):
        threads = self.fetch_top_threads_for_date(subreddit_name, year, month, day, limit=5)

        for thread in threads:
            comments = self.fetch_popular_comments(thread)

            thread, total_comments_lenght =  self.pick_comments_by_symbol_count(thread, comments,  700 - len(thread.title))

            thread = Thread.calculate_symbol_count(thread)

            self.save(thread)