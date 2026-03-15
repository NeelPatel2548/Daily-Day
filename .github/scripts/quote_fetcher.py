"""
quote_fetcher.py — fetches a daily quote from free APIs
"""

import random
import requests

FALLBACK = [
    ("The secret of getting ahead is getting started.", "Mark Twain"),
    ("It always seems impossible until it's done.", "Nelson Mandela"),
    ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("In the middle of every difficulty lies opportunity.", "Albert Einstein"),
    ("You are never too old to set another goal or dream a new dream.", "C.S. Lewis"),
    ("Act as if what you do makes a difference. It does.", "William James"),
    ("Success is not final, failure is not fatal: it is the courage to continue.", "Winston Churchill"),
    ("Hardships often prepare ordinary people for an extraordinary destiny.", "C.S. Lewis"),
    ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
    ("You miss 100% of the shots you don't take.", "Wayne Gretzky"),
    ("Whether you think you can or you think you can't, you're right.", "Henry Ford"),
    ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
    ("Spread love everywhere you go.", "Mother Teresa"),
    ("Do not go where the path may lead; go instead where there is no path.", "Ralph Waldo Emerson"),
    ("You will face many defeats in life, but never let yourself be defeated.", "Maya Angelou"),
    ("In the end, it's not the years in your life that count, it's the life in your years.", "Abraham Lincoln"),
    ("Never let the fear of striking out keep you from playing the game.", "Babe Ruth"),
    ("Life is either a daring adventure or nothing at all.", "Helen Keller"),
    ("Many of life's failures are people who did not realize how close they were to success.", "Thomas A. Edison"),
    ("If life were predictable it would cease to be life and be without flavor.", "Eleanor Roosevelt"),
    ("If you look at what you have in life, you'll always have more.", "Oprah Winfrey"),
    ("It always seems impossible until it's done.", "Nelson Mandela"),
    ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
    ("You have to be burning with an idea, or a problem, or a wrong that you want to right.", "Steve Jobs"),
    ("I have not failed. I've just found 10,000 ways that won't work.", "Thomas Edison"),
    ("A person who never made a mistake never tried anything new.", "Albert Einstein"),
    ("The mind is everything. What you think you become.", "Buddha"),
    ("An unexamined life is not worth living.", "Socrates"),
    ("Life is what happens when you're busy making other plans.", "John Lennon"),
]


def fetch_quote() -> tuple[str, str]:
    apis = [
        {
            "url": "https://zenquotes.io/api/random",
            "parse": lambda r: (r.json()[0]["q"], r.json()[0]["a"]),
        },
        {
            "url": "https://api.quotable.io/random?maxLength=180",
            "parse": lambda r: (r.json()["content"], r.json()["author"]),
        },
    ]

    for api in apis:
        try:
            resp = requests.get(api["url"], timeout=8)
            if resp.status_code == 200:
                quote, author = api["parse"](resp)
                if quote and author and len(quote) > 10:
                    return quote.strip(), author.strip()
        except Exception:
            continue

    return random.choice(FALLBACK)
