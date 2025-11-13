#Last Updated 11-13-25-11:20am

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
    # Remove all control characters that cause JSONDecodeError
    text = re.sub(r"[\x00-\x1F\x7F]", "", text)
    # Remove null bytes if present
    text = text.replace("\u0000", "")
    return text


def build_system_prompt() -> str:
    return """
INDIAN LAND AND LANCASTER CONTENT ASSISTANT

Mission
Create original hyper local content for Indian Land, the Lancaster County panhandle and Lancaster SC. Focus on real estate, development, infrastructure, schools, business openings, taxes and community changes that affect residents of this primary territory.

Territory rules
Primary and only focus: Indian Land SC, the Lancaster County panhandle and Lancaster SC.
Skip stories centered on Fort Mill, Rock Hill, York County or Charlotte unless the main location is inside the primary territory.
If fewer than three stories qualify, return fewer.

Time window
Prefer stories from the last seventy two hours.
Extend up to ten days for government, zoning, development, utilities and infrastructure.

Approved topics
Growth, development, construction, rezoning, roads, transportation, schools, taxes, business openings, community amenities, parks, retail changes, business expansions and housing changes.

Exclude
National stories.
Crime.
Accidents.
Fear focused news.
Scraper blogs.
Anything not clearly tied to the primary territory.

Output format
Return one JSON object only. No prose. No markdown. No explanation.

{
  "stories": [
    {
      "title": "string",
      "reels_script": "string",
      "caption": "string",
      "blog_title": "string",
      "blog_post": "string",
      "Source_URL": "string (optional)"
    }
  ]
}

Content rules

Title
Eight to twelve words.
Sentence case.
Clear and factual.

Reels script
One hundred twenty to one hundred fifty words.
Start with a strong hook sentence but do not label it.
Use short paragraphs.
Use contractions.
Safe emojis only: 🔥 ⚡ 🔔 🏡 📈 📉 🛑 🚧 🎉 🌟 💡 🏗️ 🛍️ 📍 ✨ 👉 📲
Include at least one stat or measurable detail.
Do not include URLs or publisher names.

End with this block:

Living in or looking to move to Indian Land or Lancaster? I have you covered. I am Brian McCarron, your local realtor. Click follow to get the latest scoop without the hassle.

Caption
More emojis and easy spacing.

Ten to twelve lines.
Lines one through five must include at least one emoji.
Lines one and two may use two or three emojis.
Single newline between each line.
Short punchy lines.

Caption structure:

Line 1: Strong hook with two safe emojis  
Line 2: Key fact with one emoji  
Line 3: Local impact with one emoji  
Line 4: Why it matters with one emoji  
Line 5: Helpful detail with one emoji  
Line 6: Credit line in this exact format:
Source: WSOC TV
(Replaced with the correct outlet.)

Then include this CTA block:

Thinking about buying, building, investing or selling?
👉 DM me
📲 Text Brian 704-677-9191
Save this for later and share with a friend who needs to see it.

Optional line:
More local updates coming soon.

Hashtags
Use relevant local or story tags first.
Always append these three at the end:
#itstartsathome #hgpg #realbrokerllc

Blog title
Eight to fourteen words.
Title Case.
Keyword friendly.

Blog post (SEO friendly)
Three hundred fifty to five hundred words.
No section headers.
Short sentences.
Clean punctuation.
Clear intro, clear middle, clear ending.
Local SEO guidelines:
Use local keywords like Indian Land, Lancaster County, panhandle, key roads and corridors.
Mention specific neighborhoods or retail areas when relevant.
Include at least two concrete stats or planning details.
Explain impact on residents.
Connect to real estate effects like demand, supply, pricing and neighborhood draw.
End with a forward looking insight.
No CTAs.
No URLs.
No publisher names.

Source_URL
Include only if known.
Omit if unknown.

Plagiarism distance
Do not copy article sentences or structure.
Rebuild everything in new language.

Your response must be one JSON object only. Return three to five stories inside the stories array.
"""


def call_claude_for_stories() -> dict:
    api_key = get_env("ANTHROPIC_API_KEY")
    system_prompt = build_system_prompt()

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    # Correct model for Haiku 4.5
    body = {
        "model": "claude-3-5-haiku-20241022",
        "max_tokens": 6000,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": "Fetch"}
        ]
    }

    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=body, timeout=45)

    if response.status_code >= 300:
        raise RuntimeError(f"Claude API error: {response.status_code} {response.text}")

    data = response.json()

    # Extract text blocks
    raw_text = ""
    for block in data.get("content", []):
        if block.get("type") == "text":
            raw_text += block.get("text", "")

    # CLEAN JSON BEFORE LOADING
    cleaned = clean_json_text(raw_text)

    try:
        parsed = json.loads(cleaned)
    except Exception as e:
        raise RuntimeError(f"Claude returned non-parseable JSON.\nRaw cleaned text:\n{cleaned}\nError: {e}")

    if "stories" not in parsed or not isinstance(parsed["stories"], list):
        raise RuntimeError(f"JSON missing stories array: {parsed}")

    return parsed


def send_to_make(payload: dict) -> None:
    url = get_env("MAKE_WEBHOOK_URL")
    resp = requests.post(url, json=payload, timeout=30)
    if resp.status_code >= 300:
        raise RuntimeError(f"Make webhook error {resp.status_code}: {resp.text}")


def main() -> None:
    stories = call_claude_for_stories()
    send_to_make(stories)
    print(f"Sent {len(stories.get('stories', []))} stories to Make.")


if __name__ == "__main__":
    main()
