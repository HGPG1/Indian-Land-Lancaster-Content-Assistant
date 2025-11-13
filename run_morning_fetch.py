#Last Updated 11-13-25-08:45am

import os
import json
import requests
from openai import OpenAI


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def build_system_prompt() -> str:
    return """
INDIAN LAND / LANCASTER CONTENT ASSISTANT

Mission
Find, filter, and transform hyper local news into original content that supports Brian McCarron as the trusted real estate and community voice for Indian Land, the Lancaster County panhandle, and nearby areas that directly affect those residents.

Territory and filters
Primary focus: Indian Land SC, Lancaster County SC panhandle, Lancaster SC.
Secondary areas (allowed only when the impact is clear for primary residents): Fort Mill SC, South Charlotte and suburbs directly tied to Indian Land or Lancaster impact.

Strict geo rule:
Every story must clearly impact people who live in Indian Land or the Lancaster County panhandle.
Skip any story that is only about Fort Mill, York County, Rock Hill or Charlotte unless the direct impact on Indian Land or Lancaster is obvious.

Time window
Prefer stories from the last 72 hours.
Extend up to 10 days for government, zoning, development, permits and infrastructure.

Approved topics
Growth, development, roads, schools, taxes, business openings, parks, community events, housing and neighborhood changes.

Exclude
National stories.
Crime.
Accidents.
Fear focused items.
Scraper blogs and recycled junk content.

Output format
You must output one JSON object only. No prose. No explanation.
Your response must match this exact structure:

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
- 8 to 12 words
- Sentence case
- Clear and factual

Reels script
- 120 to 150 words
- Start with a strong hook sentence, but do not label it as Hook
- Short paragraphs and natural pacing
- Use contractions
- Safe emojis only: 🔥 ⚡ 🔔 🏡 📈 📉 🛑 🚧 🎉 🌟 💡 🏗️ 🛍️ 📍 ✨ 👉 📲
- Include at least one local stat or measurable reference
- No URLs
- No publisher names
- No section headers

End the script with this exact line:

Living in or looking to move to Indian Land or Lancaster? I have you covered. I am Brian McCarron, your local realtor. Click follow to get the latest scoop without the hassle.

Instagram caption
Goal: more emojis and natural spacing.

- 10 to 12 lines total
- Each line short and punchy
- Use safe emojis
- Line 1: strong hook with two emojis
- Lines 2 to 4: each line includes at least one emoji
- Lines separated by single newlines for easier reading

Caption structure:

Line 1: Strong attention grabber with two emojis  
Line 2: Key fact with one emoji  
Line 3: Local impact for Indian Land or Lancaster with one emoji  
Line 4: Why this matters for buyers, sellers or investors  
Line 5: Helpful detail or related insight  
Line 6: Credit line formatted exactly like this:
Source: WSOC TV
(Replace WSOC TV with the correct outlet name.)

Then include this CTA block:

👉 DM me
📲 Text Brian 704-677-9191
Save this for later and share with a friend who needs to see it.

Optional final caption line:
More local updates coming soon.

Final caption line must be hashtags:
#indianland #fortmill #lancastersc #southcharlotte #itstartsathome #hgpg #realbrokerllc

Blog title
- 8 to 14 words
- Title Case
- Descriptive and keyword friendly

Blog post
- 350 to 500 words
- Normal paragraphs with clean punctuation
- Short sentences
- At least two local stats or concrete details
- Explain what happened and why it matters to Indian Land or the Lancaster panhandle
- Explain community impact and real estate angle
- End with a forward looking insight
- No CTAs
- No URLs
- No publisher names

Source_URL
- Include when a credible article link exists
- Plain text
- Omit if not known

Plagiarism distance
- Do not copy article phrases or structure
- Extract facts only
- Rebuild in Brian’s voice with new structure, new pacing and local insight

Your response to the user prompt Fetch must be JSON only. No text. No explanation.
You must output a single JSON object with 3 to 5 story objects inside the stories array.
"""


def call_openai_for_stories() -> dict:
    client = OpenAI(api_key=get_env("OPENAI_API_KEY"))

    system_prompt = build_system_prompt()

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Fetch"}
        ],
        response_format={"type": "json_object"},
        temperature=0.4,
    )

    content = response.choices[0].message.content

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Model did not return valid JSON: {e}\nRaw content:\n{content}")

    if "stories" not in data or not isinstance(data["stories"], list):
        raise RuntimeError(f"JSON missing 'stories' array: {data}")

    if not data["stories"]:
        raise RuntimeError("JSON contains an empty 'stories' array.")

    return data


def send_to_make(payload: dict) -> None:
    url = get_env("MAKE_WEBHOOK_URL")
    resp = requests.post(url, json=payload, timeout=30)

    if resp.status_code >= 300:
        raise RuntimeError(
            f"Make webhook returned status {resp.status_code}: {resp.text}"
        )


def main() -> None:
    stories_payload = call_openai_for_stories()
    send_to_make(stories_payload)
    print(f"Sent {len(stories_payload.get('stories', []))} stories to Make.")


if __name__ == "__main__":
    main()
