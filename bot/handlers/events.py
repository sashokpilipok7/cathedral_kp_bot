import asyncio
import html
import json
import re
import urllib.request

WP_URL = "https://wp.cathedralkp.org.ua/wp-json/wp/v2/"
WEB_URL = "https://www.cathedralkp.org.ua/"
EVENTS_URL = 'https://wp.cathedralkp.org.ua/wp-json/wp/v2/events?_embed=wp:term&per_page=3&page=1'


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

async def fetch_events():
    loop = asyncio.get_running_loop()

    def get_data():
        req = urllib.request.Request(EVENTS_URL, headers=HEADERS)
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))

    return await loop.run_in_executor(None, get_data)


def events(update, context):
    """
    /events:
    Відображає події
    """
    from .index import get_menu_markup

    data = asyncio.run(fetch_events())

    if not data:
        update.message.reply_text('Подій не знайдено.', reply_markup=get_menu_markup())
        return

    items = []
    for event in data:
        raw_title = event.get('title', {}).get('rendered', '')
        title = html.unescape(re.sub(r'<[^>]+>', '', raw_title).strip())

        acf = event.get('acf') or {}
        image_preview = acf.get("cover_image") or event.get('image')
        event_date = acf.get('event_date') or event.get('date', '')
        category = acf.get('category', '')

        raw_excerpt = event.get('excerpt', {}).get('rendered', '')
        excerpt = html.unescape(re.sub(r'<[^>]+>', '', raw_excerpt).strip())
        link = f"{WEB_URL}events/{event.get('id')}"

        item = "📌 <b>" + html.escape(title) + "</b>"
        if image_preview:
            item += f'\n  <a href="{html.escape(image_preview)}">&#8205;</a>'
        if event_date:
            item += "\n📅 " + html.escape(str(event_date))
        if category:
            item += "\n🏷 " + html.escape(str(category))
        if excerpt:
            item += "\n\n" + html.escape(excerpt)
        if link:
            item += '\n🔗 <a href="{}">Детальніше</a>'.format(html.escape(link))

        items.append(item)

    text = "\n\n".join(items)
    update.message.reply_text(text, parse_mode='HTML', reply_markup=get_menu_markup())
