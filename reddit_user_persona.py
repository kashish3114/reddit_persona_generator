import praw
import openai
import os
import re
from dotenv import load_dotenv
from urllib.parse import urlparse
from datetime import datetime
from groq import Groq
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)

MAX_ITEMS = 10

def extract_username(url):
    path = urlparse(url).path
    return path.split('/')[2] if len(path.split('/')) > 2 else None

def clean(text):
    return re.sub(r'\s+', ' ', text.strip())

def fetch_user_data(username):
    redditor = reddit.redditor(username)
    posts, comments = [], []

    try:
        for post in redditor.submissions.new(limit=MAX_ITEMS):
            posts.append(f"Title: {clean(post.title)}\nBody: {clean(post.selftext)}\nLink: https://www.reddit.com{post.permalink}")

        for comment in redditor.comments.new(limit=MAX_ITEMS):
            comments.append(f"Comment: {clean(comment.body)}\nLink: https://www.reddit.com{comment.permalink}")
    except Exception as e:
        print(f"[!] Error: {e}")
    
    return posts, comments

def build_prompt(username, posts, comments):
    post_block = "\n\n".join(posts)
    comment_block = "\n\n".join(comments)

    return f"""
You are an AI assistant that generates high-quality UX-style user personas based on Reddit data. Use the following format:

────────────────────────────────────────────
👤 NAME: (Name or Unknown)
🎂 AGE: (Estimate if possible)
💼 OCCUPATION:
📍 LOCATION:
📶 STATUS: (Single, Married, etc.)
🧠 ARCHETYPE: (e.g., The Explorer, The Creator)
🌟 TIER: (Early Adopter, Lurker, etc.)

────────────────────────────────────────────
🎯 TRAITS
• Practical / Adaptable / Curious / Tech-savvy etc.

────────────────────────────────────────────
💬 BEHAVIOUR & HABITS
• Bullet point habits from Reddit activity

────────────────────────────────────────────
😤 FRUSTRATIONS
• Bullet point complaints or difficulties mentioned

────────────────────────────────────────────
🎯 GOALS & NEEDS
• Bullet point goals and desires inferred from posts

────────────────────────────────────────────
🔥 MOTIVATIONS
Rate with bars:
- Convenience: ██████████
- Wellness:    ████████
- Speed:       ███████
- Preferences: ██████
- Comfort:     ████████
- Dietary:     ██████

────────────────────────────────────────────
🧠 PERSONALITY
• Introvert – Extrovert  
• Intuition – Sensing  
• Feeling – Thinking  
• Judging – Perceiving

────────────────────────────────────────────
🧾 CITATIONS
Use bullet points with quotes and Reddit links to support each insight.

POSTS:
{post_block}

COMMENTS:
{comment_block}
"""

def generate_persona(prompt):
    response = client.chat.completions.create(
       model="llama3-8b-8192", 

        messages=[
            {"role": "system", "content": "You are an expert in behavioral profiling and UX personas."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content


def save_output(username, content):
    filename = f"sample_output/user_persona_{username}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    os.makedirs("sample_output", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[✅] Persona saved: {filename}")

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python reddit_user_persona.py <reddit_profile_url>")
        return

    profile_url = sys.argv[1]
    username = extract_username(profile_url)

    print(f"[🔍] Fetching data for u/{username}...")
    posts, comments = fetch_user_data(username)

    if not posts and not comments:
        print("[-] No content found.")
        return

    prompt = build_prompt(username, posts, comments)
    print("[🤖] Generating persona via Groq...")
    persona = generate_persona(prompt)
    save_output(username, persona)

if __name__ == "__main__":
    main()
