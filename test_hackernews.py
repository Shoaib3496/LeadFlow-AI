from scraper.hackernews_scraper import fetch_hackernews_posts

posts = fetch_hackernews_posts(5)

for post in posts:

    print(post)