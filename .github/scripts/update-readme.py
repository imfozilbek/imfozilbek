import re
import html
import urllib.request

URL = "https://t.me/s/moyroadmap"
MAX_POSTS = 9
COLS = 3
MAX_TEXT = 120
README = "README.md"
START_TAG = "<!-- BLOG-POST-LIST:START -->"
END_TAG = "<!-- BLOG-POST-LIST:END -->"

# Fetch Telegram channel page
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
content = urllib.request.urlopen(req).read().decode("utf-8")

# Split into individual message blocks
blocks = re.split(r'(?=data-post="moyroadmap/\d+")', content)

posts = []
for block in blocks:
    post_match = re.search(r'data-post="moyroadmap/(\d+)"', block)
    if not post_match:
        continue

    post_id = post_match.group(1)
    link = f"https://t.me/moyroadmap/{post_id}"

    # Extract text
    text_match = re.search(
        r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>',
        block,
        re.DOTALL,
    )
    if not text_match:
        continue

    raw_text = text_match.group(1)
    clean = re.sub(r"<br\s*/?>", " ", raw_text)
    clean = re.sub(r"<[^>]+>", "", clean).strip()
    clean = html.unescape(clean)
    clean = " ".join(clean.split())

    if len(clean) > MAX_TEXT:
        clean = clean[:MAX_TEXT].rsplit(" ", 1)[0] + "..."

    # Extract image
    img_match = re.search(
        r"background-image:url\('(https://cdn[^']+)'\)", block
    )
    img_url = img_match.group(1) if img_match else None

    posts.append({"id": post_id, "text": clean, "link": link, "image": img_url})

# Take last N posts, newest first
posts = posts[-MAX_POSTS:]
posts.reverse()

# Build cards as HTML table (3 columns, 3 rows)
col_width = f"{100 // COLS}%"
cards = []
for p in posts:
    card = f'<td width="{col_width}" valign="top">\n'
    if p["image"]:
        card += f'<a href="{p["link"]}"><img src="{p["image"]}" width="100%" /></a>\n'
    card += f'<p><b>{p["text"]}</b></p>\n'
    card += f'<a href="{p["link"]}">Read more &rarr;</a>\n'
    card += "</td>"
    cards.append(card)

lines = []
for i in range(0, len(cards), COLS):
    lines.append("<tr>")
    for j in range(COLS):
        if i + j < len(cards):
            lines.append(cards[i + j])
    lines.append("</tr>")

posts_html = "<table>\n" + "\n".join(lines) + "\n</table>"

# Update README
with open(README, "r") as f:
    readme = f.read()

before = readme[: readme.index(START_TAG) + len(START_TAG)]
after = readme[readme.index(END_TAG) :]

with open(README, "w") as f:
    f.write(before + "\n" + posts_html + "\n" + after)

print(f"Updated {README} with {len(posts)} posts")
