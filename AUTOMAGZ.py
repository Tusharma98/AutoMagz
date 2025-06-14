from newspaper import Article
from PIL import Image, ImageDraw, ImageFont, ImageOps
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from instagrapi import Client
import requests
import textwrap
import os

# === Setup ===
API_KEY = 'YOUR_API_KEY'
BASE_URL = 'https://newsapi.org/v2/top-headlines'
params = {
    'category': 'technology',
    'pageSize': 7,
    'apiKey': API_KEY
}

response = requests.get(BASE_URL, params=params)
articles = response.json().get("articles", [])
if not articles:
    print("⚠️ No articles found.")
    exit()

os.makedirs("images", exist_ok=True)
os.makedirs("pdf", exist_ok=True)

# === Constants ===
img_width, img_height = 1080, 1350
bg_color = (205, 92, 92)
title_bg_color = (40, 116, 166)
logo_path = "a-circular-logo-featuring-the-word-autom_7vAKmJVcQDGdz9D8P1l4cA_lGsAMVzaSQajwKj3m1jQVQ.jpeg"
pdf_path = "pdf/technology_news_report.pdf"
date_today = datetime.now().strftime("%d %b %Y")

# === Load Fonts ===
def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

headline_font = load_font("arialbd.ttf", 46)
snippet_font = load_font("arial.ttf", 32)
date_font = load_font("arial.ttf", 26)
title_font = load_font("arialbd.ttf", 80)
date_font_title = load_font("arial.ttf", 36)

# === Generate Title Page Image ===
title_img = Image.new("RGB", (img_width, img_height), title_bg_color)
draw = ImageDraw.Draw(title_img)

title_text = "AutoMagz Tech Today"

# Get text size
bbox = draw.textbbox((0, 0), title_text, font=title_font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Vertically and horizontally center the title text
text_x = (img_width - text_width) / 2
text_y = (img_height - text_height) / 2
draw.text((text_x, text_y), title_text, font=title_font, fill=(255, 255, 255))

# Draw Date at Top-Right
draw.text((img_width - 300, 60), f"📅 {date_today}", font=date_font_title, fill=(255, 255, 255))

# Paste Medium Logo at Bottom-Center with size 250x250
try:
    logo = Image.open(logo_path).convert("RGBA")
    logo = ImageOps.contain(logo, (250, 250))
    logo_x = (img_width - logo.width) // 2
    logo_y = img_height - logo.height - 50
    title_img.paste(logo, (logo_x, logo_y), logo)
    print("✅ Logo added to title page.")
except Exception as e:
    print(f"⚠️ Failed to add logo to title page: {e}")

# Save Title Image
title_image_path = "images/title_page.jpg"
title_img.save(title_image_path)
print("✅ Title page image saved.")

# === Setup PDF ===
c = canvas.Canvas(pdf_path, pagesize=letter)
pdf_width, pdf_height = letter
margin = 72  # 1 inch

# === Add Title Page to PDF ===
c.setFillColorRGB(40/255, 116/255, 166/255)
c.rect(0, 0, pdf_width, pdf_height, fill=1)
c.setFillColorRGB(1, 1, 1)
c.setFont("Helvetica-Bold", 36)
c.drawCentredString(pdf_width / 2, pdf_height / 2, title_text)
c.setFont("Helvetica", 18)
c.drawRightString(pdf_width - margin, margin + 30, f"📅 {date_today}")
c.showPage()

# === Generate Article Images and PDF Pages ===
for idx, article in enumerate(articles, start=1):
    title = article['title']
    url = article['url']

    try:
        news = Article(url)
        news.download()
        news.parse()
        full_text = news.text
    except:
        full_text = "⚠️ Unable to fetch full article."

    img = Image.new("RGB", (img_width, img_height), bg_color)
    draw = ImageDraw.Draw(img)

    wrapped_headline = textwrap.fill(textwrap.shorten(title, width=95, placeholder="..."), width=40)
    draw.text((60, 60), wrapped_headline, font=headline_font, fill=(255, 255, 255))

    snippet = full_text[:500] + "..." if len(full_text) > 500 else full_text
    wrapped_snippet = textwrap.fill(snippet, width=48)
    draw.text((60, 300), wrapped_snippet, font=snippet_font, fill=(255, 255, 255))

    draw.text((60, img_height - 60), f"📅 {date_today}", font=date_font, fill=(240, 240, 240))

    try:
        logo = Image.open(logo_path).convert("RGBA")
        logo = ImageOps.contain(logo, (100, 100))
        logo_position = (img_width - 100 - 30, img_height - 100 - 30)
        img.paste(logo, logo_position, logo)
        print(f"✅ Logo added for article {idx}")
    except Exception as e:
        print(f"⚠️ Failed to add logo for article {idx}: {e}")

    image_file = f"images/article_{idx}.jpg"
    img.save(image_file)
    print(f"✅ Image saved: {image_file}")

    # Add to PDF
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, pdf_height - margin - 20, f"{idx}. {title}")

    c.setFont("Helvetica", 12)
    text_obj = c.beginText(margin, pdf_height - margin - 50)
    wrapped_text = textwrap.wrap(full_text, 90)
    for line in wrapped_text:
        text_obj.textLine(line)
        if text_obj.getY() < margin:
            c.drawText(text_obj)
            c.showPage()
            text_obj = c.beginText(margin, pdf_height - margin)
            c.setFont("Helvetica", 12)
    c.drawText(text_obj)
    c.showPage()

c.save()
print(f"✅ PDF created at: {pdf_path}")
print("✅ All article images and report generated successfully.")

# === Prepare Instagram Caption with article links ===
caption_lines = [f"📰 Today's Tech Highlights - {date_today}\n"]
caption_lines.append("Read the full articles below:\n")

for idx, article in enumerate(articles, start=1):
    title = article['title']
    url = article['url']
    caption_lines.append(f"{idx}. {title}\n🔗 {url}\n")

caption_lines.append("#TechNews #Automation")

instagram_caption = "\n".join(caption_lines)

# === Upload to Instagram ===
USERNAME = "YOUR_USERNAME"
PASSWORD = "PASSWORD"

cl = Client()
try:
    cl.login(USERNAME, PASSWORD)
    print("✅ Logged into Instagram.")
except Exception as e:
    print(f"❌ Failed to login: {e}")
    exit()

image_folder = "images"
# Only include article images here, exclude title page from this list
image_files = sorted(
    [os.path.join(image_folder, file) for file in os.listdir(image_folder)
     if file.startswith("article_") and file.endswith(".jpg")]
)

# Add title page image only once at the beginning
image_files.insert(0, title_image_path)

try:
    media = cl.album_upload(
        paths=image_files,
        caption=instagram_caption
    )
    print("✅ Uploaded all images as an Instagram carousel post.")
except Exception as e:
    print(f"❌ Failed to upload carousel post: {e}")
