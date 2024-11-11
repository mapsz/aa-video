import praw
import os
from datetime import datetime, timedelta

client_id = "DkSK4Os-yWHhw1lXHTJ42g"
client_secret = "T34xu2bH_OMNeQzgDFmHcGr3spH1ZQ"
user_agent = "AmbassadorAcrobatic7"

reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)

def fetch_top_threads_for_date(subreddit_name, year, month, day, limit=5):
    start_time = datetime(year, month, day)
    end_time = start_time + timedelta(days=1)

    subreddit = reddit.subreddit(subreddit_name)

    top_threads = subreddit.top(time_filter="week", limit=100)

    filtered_threads = [
        submission for submission in top_threads
        if start_time <= datetime.utcfromtimestamp(submission.created_utc) < end_time
    ]

    sorted_threads = sorted(filtered_threads, key=lambda x: x.score, reverse=True)[:limit]

    threads = [
        {"id": submission.id, "title": submission.title, "score": submission.score}
        for submission in sorted_threads
    ]

    return threads

def fetch_popular_comments(submission_id, comment_limit=10):
    submission = reddit.submission(id=submission_id)
    submission.comments.replace_more(limit=0)

    popular_comments = sorted(submission.comments, key=lambda comment: comment.score, reverse=True)

    comments_data = []
    for comment in popular_comments:
        author = comment.author.name if comment.author else "[удален]"
        comment_data = {
            "author": author,
            "score": comment.score,
            "text": comment.body
        }
        comments_data.append(comment_data)

    return comments_data

def pick_comments_by_symbol_count(comments, symbol_count):
    print(f"Pick Comments lenght-{symbol_count}")
    total_length = 0
    max_comment_length = symbol_count / 3
    print(f"--max lenght - {max_comment_length}")
    picked_comments = []
    for comment in comments:
        if (symbol_count < 20):
            break

        comment_length = len(comment["text"])

        if \
        comment_length < max_comment_length and \
        comment_length < symbol_count + 20 and \
        comment["text"] != "[removed]":
            picked_comments.append(comment)
            symbol_count -= comment_length
            total_length += comment_length
            print(f"--comment - {comment_length}")
            print(f"--left - {symbol_count}")

    print(f"--total - {total_length}\n")
    return picked_comments, total_length

def save_thread_to_file(thread, comments, symbol_count, filename):
    folder_path = "storage"
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, filename)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(f"Symbol Count:\n{symbol_count}\n\n")
        file.write(f"Title:\n{thread["title"]}\n\n")
        for i, comment in enumerate(comments, start=1):
            file.write(f"Comment {i}:\n{comment}\n\n")

threads = fetch_top_threads_for_date("AskReddit", 2024, 11, 10, limit=5)

for thread in threads:
    comments = fetch_popular_comments(thread["id"])

    thread_title_lenght = len(thread["title"])
    comments, total_comments_lenght = pick_comments_by_symbol_count(comments,  700 - thread_title_lenght)

    save_thread_to_file(thread, comments, total_comments_lenght + thread_title_lenght, thread["id"] + ".txt")