import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, jsonify
import requests

load_dotenv()
BOOKS_KEY = os.getenv("BOOKS_KEY")
BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"

app = Flask(__name__)

def pages(title):
    params = {'q': f'intitle:{title}', 'maxResults':1}
    response = requests.get(BOOKS_URL, params = params)
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        print("Items:", items)
        if items:
            volume_info = items[0]["volumeInfo"]
            page_count = volume_info.get("pageCount")
            actual_title = volume_info.get("title", title)  # fallback to input title
            return page_count, actual_title
        return None, None

def get_cover(title):
    params = {'q': title, 'maxResults':1}
    response = requests.get(BOOKS_URL, params = params)
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        print("Items:", items)
        if items:
            volume_info = items[0]["volumeInfo"]
            cover_url = volume_info.get('imageLinks', {}).get('thumbnail', '')
            return cover_url
        return "Book not found or page count not available" 
    
def find_reading_time(page_count, wpm):
    if page_count is not None and wpm:
        words = page_count * 200
        reading_time = int(words / wpm)
        return reading_time
    return None

    
@app.route("/", methods=['GET', "POST"])
def index():
    page_count = None
    reading_time_hours = None
    reading_time_minutes = None
    book_title = None

    if request.method == "POST":
        title = request.form.get("title")
        wpm_str = request.form.get("wpm")
        try:
            wpm = int(wpm_str)
        except (TypeError, ValueError):
            wpm = None

        page_count, book_title = pages(title)

        if page_count is not None and wpm:
            total_minutes = page_count * 275 / wpm
            hours = int(total_minutes // 60)
            minutes = int(total_minutes % 60)
            reading_time_hours = hours
            reading_time_minutes = minutes

    return render_template(
        "index.html",
        page_count=page_count,
        reading_time_hours=reading_time_hours,
        reading_time_minutes=reading_time_minutes,
        book_title=book_title

    )



if __name__ == '__main__':
    app.run(debug=True)