# 📰 AutoMagz Tech News Bot

AutoMagz is an automated Instagram news magazine bot that fetches the latest headlines from **NewsAPI**, generates a visually appealing **gradient magazine-style image**, and uploads it directly to **Instagram** using Python.

This project is perfect for content automation, digital journalism, and tech portfolios.

---

## 🚀 Features

✅ Fetches top headlines using [NewsAPI.org](https://newsapi.org) 

✅ Automatically generates an image with a gradient background

✅ Add Auto caption with ful article link.  

✅ Adds logos, date, and news source branding.

✅ Posts the news image to Instagram using [instagrapi](https://github.com/adw0rd/instagrapi)  

✅ Can be scheduled to post daily with a cron job or cloud service.

---

## 🧠 How It Works

1. Calls the NewsAPI to get the latest news from a specified country.
2. Uses **Pillow** to create a vertical 1080x1350 magazine-style image.
3. Adds:
   - Gradient red background
   - Headline (wrapped and styled)
   - Source, date, and bot handle
   - Logo (optional PNG/JPEG)
4. Saves the image to `/output` folder.
5. Posts the image to Instagram using your credentials.
