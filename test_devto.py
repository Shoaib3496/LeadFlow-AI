from scraper.devto_scraper import fetch_devto_posts

posts = fetch_devto_posts(5)

for post in posts:
    print(post)