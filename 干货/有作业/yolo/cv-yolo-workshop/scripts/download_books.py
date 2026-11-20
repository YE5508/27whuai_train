"""Fetch six selected book covers from Open Library; preserve sources and hashes."""
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOKS = [
    ('alice', "Alice's Adventures in Wonderland", 'Lewis Carroll'),
    ('sherlock', 'The Adventures of Sherlock Holmes', 'Arthur Conan Doyle'),
    ('jungle', 'The Jungle Book', 'Rudyard Kipling'),
    ('treasure', 'Treasure Island', 'Robert Louis Stevenson'),
    ('pride', 'Pride and Prejudice', 'Jane Austen'),
    ('oz', 'The Wonderful Wizard of Oz', 'L. Frank Baum'),
]


def fetch(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'BookORBHomework/1.0 (small educational book-cover experiment)'})
            with urllib.request.urlopen(req, timeout=35) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            # Respect server throttling instead of repeatedly issuing requests.
            if exc.code in (403, 429) or attempt == 2:
                raise
            time.sleep(3 * (attempt + 1))
        except Exception:
            if attempt == 2:
                raise
            time.sleep(3 * (attempt + 1))


def main():
    import cv2
    import numpy as np

    manifest = ROOT / 'book_sources.json'
    previous = json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else []
    records = []
    for name, title, author in BOOKS:
        target = ROOT / f'book_{name}.jpg'
        cached = next((r for r in previous if r['book'] == name), None)
        if cached and target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != cached['sha256']:
                raise ValueError(f'Existing image changed: {target}')
            records.append(cached)
            print(target.name, 'already verified', flush=True)
            continue
        params = dict(title=title, author=author, limit=5,
                      fields='key,title,author_name,cover_i,first_publish_year')
        query_url = 'https://openlibrary.org/search.json?' + urllib.parse.urlencode(params)
        data = json.loads(fetch(query_url))
        book = next((d for d in data['docs'] if d.get('cover_i')), None)
        if book is None:
            raise ValueError(f'No cover for {title}')
        image_url = f'https://covers.openlibrary.org/b/id/{book["cover_i"]}-L.jpg?default=false'
        content = fetch(image_url)
        image = cv2.imdecode(np.frombuffer(content, np.uint8), cv2.IMREAD_COLOR)
        if image is None or min(image.shape[:2]) < 100:
            raise ValueError('Missing/invalid cover: ' + image_url)
        if target.exists() and target.read_bytes() != content:
            raise FileExistsError(f'Refusing to overwrite different image: {target}')
        target.write_bytes(content)
        records.append(dict(
            book=name, file=target.name, title=book['title'], authors=book.get('author_name', []),
            source_page='https://openlibrary.org' + book['key'],
            search_url=query_url, download_url=image_url, cover_id=book['cover_i'],
            downloaded_at=datetime.now(timezone.utc).isoformat(),
            sha256=hashlib.sha256(content).hexdigest(), bytes=len(content),
            width=int(image.shape[1]), height=int(image.shape[0]),
            license='Cover-specific license not supplied by API; rights remain with respective holders.',
            usage_reference='https://openlibrary.org/dev/docs/api/covers'))
        manifest.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'{target.name}: {book["title"]}, {image.shape[1]}x{image.shape[0]}, {len(content)} bytes', flush=True)
        time.sleep(1.1)
    manifest.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
