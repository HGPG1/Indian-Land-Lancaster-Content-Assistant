#Last Updated 11-13-25-3:45pm

import os
import json
import requests
import re

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def clean_json_text(text: str) -> str:
    """
    Remove control characters that break json.loads.
    """
    text = re.sub(r"[\x00-\x1F\x7F]", "", text)
    text = text.replace("\u0000", "")
    return text


def format_blog_paragraphs(text: str) -> str:
    """
    Enforce paragraph spacing for blog posts.
    If the model returns a single block, split into short paragraphs.
    """
    if not text:
        return text

    text = text.replace("\r\n", "\n").strip()

    # If it already has blank-line paragraphs, keep them
    if "\n\n" in text:
        return text

    # Rough sentence split
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return text

    paragraphs = []
    current = []

    for s in sentences:
        current.append(s)
        if len(current) >= 3:
            paragraphs.append(" ".join(current))
            current = []

    if current:
        paragraphs.append(" ".join(current))

    return "\n\n".join(paragraphs)


def build_system_prompt() -> str:
    return """
INDIAN LAND AND LANCASTER CONTENT ASSISTANT

Mission
You are given real local articles about Indian Land SC, the Lancaster County panhandle and Lancaster SC.
Your job is to turn each article into one piece of content with:
- a strong but honest title
- a neighbor style reels script
- an emoji forward caption
- a clear SEO friendly blog post

Territory rules
Primary focus: Indian Land SC, the Lancaster County panhandle and Lancaster SC.
If an article is not about this territory or does not clearly affect it, do not try to force it. If the article is clearly outside this area, reply with an empty JSON object {}.

Facts and safety
Use only the information in the provided article plus safe, obvious implications.
Do not invent specific projects, votes, square footage, names, dates or dollar amounts that are not in the article.
You may generalize or simplify details, but do not add new facts.

Output format
For each article you will be asked to return one JSON object only.
No commentary.
No markdown.
No explanation.

Each story JSON must match:

{
  "title": "string",
  "reels_script": "string",
  "caption": "string",
  "blog_title": "string",
  "blog_post": "string",
  "Source_URL": "string"
}

Source_URL should be the article URL provided by the user.

--------------------------------------------------
TITLE RULES
Eight to twelve words.
Sentence case.
Clear and factual.
No clickbait.
No hype terms.
--------------------------------------------------

--------------------------------------------------
REELS SCRIPT – EXACT 14-LINE LAYOUT
Write the reels script in this exact 14-line layout.
Never change the number of lines.
Never remove the blank lines.
Never merge lines.
No emojis anywhere in the reels script.

Line 1: A friendly, relatable hook like you are standing with a neighbor at a backyard BBQ. Use plain words. Make it feel like real conversation. Examples of tone only (do not copy): "Here is something folks around Indian Land have been talking about.", "You might have seen this starting to take shape along 521.", "Neighbors keep asking about this one.", "If you live anywhere near 521, you will notice this."

Line 2: Empty line.

Line 3: One short sentence explaining what happened.

Line 4: One short sentence naming exactly where it is happening (Indian Land or Lancaster).

Line 5: Empty line.

Line 6: One sentence with a clear number, dollar amount, date, size, count or other measurable stat from the article. Numbers should be realistic and based on the article.

Line 7: Empty line.

Line 8: One short sentence about how this affects daily life for Indian Land or Lancaster residents.

Line 9: One short sentence about why this matters for buyers, sellers or investors in the area.

Line 10: Empty line.

Line 11: Living in or looking to move to Indian Land or Lancaster?
Line 12: I have you covered.
Line 13: I am Brian McCarron, your local realtor.
Line 14: Click follow to get the latest scoop without the hassle.

Tone rules for reels
Talk like a neighbor at a cookout.
Use everyday language.
Short sentences only.
Avoid formal words and phrases such as: "infrastructure investment", "strategic initiative", "significant transformation", "proactive approach", "robust growth", "comprehensive plan", "represents an opportunity", "economic hub".
Avoid news anchor language.
Do not sound like a government press release.
Keep it simple, human and local.
--------------------------------------------------

--------------------------------------------------
INSTAGRAM CAPTION RULES
Goal: fast, scannable, emoji-first formatting.

Rules:
- Ten to twelve lines total.
- Lines 1 to 5 must each begin with exactly one emoji from the safe list:
🚗 🏡 📈 📉 💰 🔨 🚧 🌟 💡 📍 ✨ 👉 📲 📌 🔁 🏗️ 🛍️
- Emojis only at the start of lines, not inside the lines.
- One newline between each line.
- Lines short and direct.

Caption structure:
Line 1: Emoji + strong hook.
Line 2: Emoji + key fact from the article.
Line 3: Emoji + local impact for Indian Land or Lancaster.
Line 4: Emoji + why it matters for homeowners, buyers or sellers.
Line 5: Emoji + helpful detail or timing note.
Line 6: Credit line (no emoji). Example:
Source: Lancaster News

Then this exact CTA block, with no blank line between the last CTA line and the hashtags:

Thinking about buying, building, investing or selling?
👉 DM me
📲 Text Brian 704-677-9191
📌🔁 Save this for later and share with a friend who needs to see it.
#indianland #lancastersc #itstartsathome #hgpg #realbrokerllc

Hashtag rules:
The hashtags must be on the line directly under the save line with no extra blank line between.
Use #indianland when the story is about Indian Land.
Use #lancastersc when the story is about Lancaster.
For other tags you may add one or two relevant local tags before the three static ones.
Always include these three static tags at the end, in this order:
#itstartsathome #hgpg #realbrokerllc
--------------------------------------------------

--------------------------------------------------
BLOG TITLE
Eight to fourteen words.
Title Case.
Include local keywords naturally (Indian Land, Lancaster County, Highway 521, the panhandle) when they fit.
--------------------------------------------------

--------------------------------------------------
BLOG POST – SEO OPTIMIZED AND HUMAN
Three hundred fifty to five hundred words.
Aim for about four hundred to four hundred fifty words.
Use multiple short paragraphs separated by a single blank line between each paragraph.
Do not write one large block of text.
No section headers.

Paragraph structure:
1. One or two sentences that say what happened and where. Mention Indian Land or the Lancaster County panhandle if the article supports that.
2. Two or three sentences with specific details. Include at least one measurable detail such as a number, dollar amount, size, date, traffic count, capacity, enrollment or similar. Use numbers that are present or clearly supported by the article.
3. Two or three sentences about daily life and community impact. Explain how this change affects traffic, schools, services, shopping, parks or quality of life for local residents.
4. Two or three sentences about the real estate angle. Explain how this may affect demand, supply, prices, neighborhood appeal or timing for buyers and sellers.
5. Two or three sentences with a clear forward looking insight for the next year or two. Help residents understand what to watch for next.

Tone for blogs:
Sound like a local real estate expert explaining the news to a client.
Use plain, clear language.
Use short sentences.
Avoid formal phrases like: "significant commercial development", "strategic growth pattern", "positioning the area as a key economic hub", "represents a proactive approach", "robust investment", "in summary", "overall", "moreover".
Do not sound like a government statement or corporate press release.
Make it readable and helpful.

SEO guidelines:
Use local keywords naturally when they match the article.
Include at least two concrete local stats, numbers, counts or specific details from the article.
Do not include CTAs in the blog.
Do not include URLs in the blog body.
Do not mention publisher names in the blog body.
--------------------------------------------------

Source_URL
Source_URL must be set to the article URL provided in the user prompt.

Plagiarism distance
Rewrite everything using new sentence structure and new pacing.
Do not mirror article sentences.
"""


def call_claude_for_article(article: dict) -> dict:
    api_key = get_env("ANTHROPIC_API_KEY")
    system_prompt = build_system_prompt()

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    article_title = article.get("title", "").strip()
    article_url = article.get("url", "").strip()
    article_source = article.get("source", "").strip()
    article_published = article.get("published", "").strip()
    article_content = article.get("content", "").strip()

    user_prompt = f"""
You are given a single real local article.

ARTICLE TITLE:
{article_title}

ARTICLE URL:
{article_url}

ARTICLE SOURCE:
{article_source}

ARTICLE PUBLISHED:
{article_published}

ARTICLE CONTENT:
{article_content}

Using only the information above and safe, obvious implications, create one JSON object for a story that follows all style and formatting rules from the system prompt.

Return only one JSON object with this exact shape:

{{
  "title": "string",
  "reels_script": "string",
  "caption": "string",
  "blog_title": "string",
  "blog_post": "string",
  "Source_URL": "{article_url}"
}}

Do not add extra keys.
Do not wrap it in markdown.
Do not add any text before or after the JSON.
"""

    body = {
        "model": "claude-3-5-haiku-20241022",
        "max_tokens": 5000,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_prompt}
        ]
    }

    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=body, timeout=60)

    if response.status_code >= 300:
        raise RuntimeError(f"Claude API error: {response.status_code} {response.text}")

    data = response.json()

    raw_text = ""
    for block in data.get("content", []):
        if block.get("type") == "text":
            raw_text += block.get("text", "")

    cleaned = clean_json_text(raw_text)

    if not cleaned.strip():
        raise RuntimeError("Claude returned empty content for article.")

    try:
        story = json.loads(cleaned)
    except Exception as e:
        raise RuntimeError(
            f"Claude returned non-parseable JSON for one article.\nRaw cleaned text:\n{cleaned}\nError: {e}"
        )

    if not isinstance(story, dict):
        raise RuntimeError(f"Claude JSON for one article is not an object: {story}")

    return story


def send_to_make(payload: dict) -> None:
    url = get_env("MAKE_WEBHOOK_URL")
    resp = requests.post(url, json=payload, timeout=30)
    if resp.status_code >= 300:
        raise RuntimeError(f"Make webhook error {resp.status_code}: {resp.text}")


def main() -> None:
    articles_json = os.getenv("ARTICLES_JSON", "").strip()
    if not articles_json:
        raise RuntimeError("ARTICLES_JSON env var is empty. This workflow expects real articles JSON from Atlas/Make.")

    try:
        articles_payload = json.loads(articles_json)
    except Exception as e:
        raise RuntimeError(f"Could not parse ARTICLES_JSON. Value:\n{articles_json}\nError: {e}")

    articles = articles_payload.get("articles", [])
    if not isinstance(articles, list) or not articles:
        raise RuntimeError(f"ARTICLES_JSON.articles is missing or empty: {articles_payload}")

    stories = []

    for idx, article in enumerate(articles, start=1):
        if not isinstance(article, dict):
            continue
        story = call_claude_for_article(article)

        # Skip if the model chose to return an empty object {}
        if not story:
            continue

        # Enforce blog paragraph spacing
        if isinstance(story.get("blog_post"), str):
            story["blog_post"] = format_blog_paragraphs(story["blog_post"])

        stories.append(story)

    if not stories:
        raise RuntimeError("No valid stories were generated from the provided articles.")

    payload = {"stories": stories}
    send_to_make(payload)
    print(f"Sent {len(stories)} stories to Make.")


if __name__ == "__main__":
    main()
