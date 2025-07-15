# Reddit User Persona Generator

This project generates a UX-style user persona from a given Reddit profile using scraped posts/comments and Groq's LLaMA3 API.

## 🛠️ Technologies Used
- Python 3.11+
- PRAW (Reddit API)
- Groq API (LLaMA3 8B)
- dotenv for secrets

## 🚀 How to Run

1. Clone the repo
2. Set up `.env` file with:
GROQ_API_KEY=your_groq_key
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_custom_agent

3. Install dependencies:
pip install -r requirements.txt


4. Run:
python reddit_user_persona.py https://www.reddit.com/user/kojied/

bash


The persona will be saved inside `sample_output/`.

## 📄 Sample Output
See: sample_output/user_persona_kojied_20250715_2323.txt
