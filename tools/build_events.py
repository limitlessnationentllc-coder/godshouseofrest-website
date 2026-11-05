#!/usr/bin/env python3
"""Rebuild events.html lists, events/<slug>.html pages, and sitemap event URLs from _data/events.json.
Run: python3 tools/build_events.py   (a daily GitHub Action runs this and commits changes)"""
import json, re, html, datetime as dt, os
from zoneinfo import ZoneInfo
from PIL import Image
PT = ZoneInfo("America/Los_Angeles")
BASE = "https://godshouseofrest.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
now = dt.datetime.now(PT)
E = [e for e in json.load(open("_data/events.json"))["events"] if not e.get("needsDate")]
def start(e): return dt.datetime.fromisoformat(e["startDate"])
def end(e): return dt.datetime.fromisoformat(e["endDate"]) if e.get("endDate") else start(e) + dt.timedelta(hours=4)
def esc(s): return html.escape(s, quote=True)
def fmt_time(e):
    s = start(e).astimezone(PT); t = s.strftime("%-I:%M %p")
    if e.get("endDate"):
        t += " to " + end(e).astimezone(PT).strftime("%-I:%M %p")
    return t
def fmt_date(e): return start(e).astimezone(PT).strftime("%A, %B %-d, %Y")
def where(e):
    if not e.get("locationVisible"): return "Details shared with registered families"
    if e.get("locationName"): return f'{e["locationName"]}, {e["city"]}, CA'
    return "618 E Street Suite H, Chula Vista, CA 91910"
def img_tag(e, cls="", lazy=True):
    p = e.get("flyerImage")
    if not p or not os.path.exists(p.lstrip("/")): return ""
    w, h = Image.open(p.lstrip("/")).size
    return f'<img src="{p}" alt="{esc(e["flyerAlt"])}" width="{w}" height="{h}" {"loading=\"lazy\" " if lazy else ""}style="width:100%;height:auto;border-radius:12px;display:block">'
def row(e):
    s = start(e).astimezone(PT); past = end(e) < now
    return f'''    <div class="event-row" data-category="{e["category"]}" data-end="{end(e).isoformat()}" data-start="{start(e).isoformat()}">
      <div class="event-date-box"><div class="event-date-month">{s.strftime("%b")}</div><div class="event-date-day">{s.day}</div></div>
      <div class="event-meta">
        <span class="event-tag tag-{e["category"]}">{e["category"].title()}</span>
        <div class="event-title"><a href="/events/{e["slug"]}" style="color:inherit;text-decoration:none">{esc(e["title"])}</a></div>
        <div class="event-details"><span>{fmt_date(e)}, {fmt_time(e)}</span><span>{esc(where(e))}</span></div>
      </div>
      <div class="event-cta-wrap"><a href="/events/{e["slug"]}" class="btn-secondary" style="font-size:13px;padding:10px 20px;white-space:nowrap">{"See recap" if past else "Details"}</a></div>
    </div>'''
up = sorted([e for e in E if end(e) >= now], key=start)
pa = sorted([e for e in E if end(e) < now], key=start, reverse=True)
def lists():
    u = "\n".join(row(e) for e in up) or '    <p class="events-empty" style="color:var(--text-muted)">No upcoming events right now. Join us Sundays at 11:00 AM and Tuesdays at 7:00 PM for Bible study.</p>'
    p = "\n".join(row(e) for e in pa)
    return f'<!--UPCOMING-START-->\n  <div class="events-list" id="eventsList">\n{u}\n  </div>\n<!--UPCOMING-END-->', f'<!--PAST-START-->\n  <div class="events-list" id="pastList">\n{p}\n  </div>\n<!--PAST-END-->'
s = open("events.html", encoding="utf-8").read()
U, P = lists()
if "<!--UPCOMING-START-->" not in s:
    a = s.index('  <div class="events-list" id="eventsList">')
    b = s.index('  <div class="recurring-section">')
    s = s[:a] + U + "\n\n" + b_marker if False else s[:a] + U + "\n\n" + s[b:]
    s = s.replace("Events This Month", "Upcoming Events")
    # past section inserted after recurring section end handled below
    m = s.index('<footer>')
    sec_end = s.rfind('</section>', 0, m)
    past_sec = f'''</section>

<section class="section" id="past-events" style="padding-top:0">
  <div class="section-label reveal">Recap</div>
  <h2 class="section-title reveal reveal-delay-1">Past Events</h2>
  {P}
'''
    s = s[:sec_end] + past_sec + s[sec_end:]
else:
    s = re.sub(r"<!--UPCOMING-START-->.*?<!--UPCOMING-END-->", lambda m: U, s, flags=re.S)
    s = re.sub(r"<!--PAST-START-->.*?<!--PAST-END-->", lambda m: P, s, flags=re.S)
# event-list JSON-LD for events.html
open("events.html", "w", encoding="utf-8").write(s)

# client sorter (idempotent)
JS = '''<script>/*events-sort*/(function(){var n=Date.now(),u=document.getElementById('eventsList'),p=document.getElementById('pastList');if(!u||!p)return;
document.querySelectorAll('#eventsList .event-row').forEach(function(r){if(Date.parse(r.dataset.end)<n){p.insertBefore(r,p.firstChild);var a=r.querySelector('.btn-secondary');if(a)a.textContent='See recap';}});
var rows=[].slice.call(p.querySelectorAll('.event-row')).sort(function(a,b){return Date.parse(b.dataset.start)-Date.parse(a.dataset.start)});rows.forEach(function(r){p.appendChild(r)});
if(!u.querySelector('.event-row')&&!u.querySelector('.events-empty')){u.innerHTML='<p class="events-empty" style="color:var(--text-muted)">No upcoming events right now. Join us Sundays at 11:00 AM and Tuesdays at 7:00 PM for Bible study.</p>';}})();</script>'''
s = open("events.html", encoding="utf-8").read()
if "/*events-sort*/" not in s:
    s = s.replace("</body>", JS + "\n</body>")
open("events.html", "w", encoding="utf-8").write(s)

# per-event pages
s = open("events.html", encoding="utf-8").read()
cut = s.index('<section class="section">')
head, foot = s[:cut], s[s.index("<footer>"):]
def absurl(t): return re.sub(r'(href|src)="(?!https?:|/|#|mailto:|tel:|data:)([^"]+)"', r'\1="/\2"', t)
head, foot = absurl(head), absurl(foot)
head = re.sub(r'<script type="application/ld\+json">.*?</script>', '', head, count=1, flags=re.S) if False else head
head = re.sub(r"<style>.*?</style>", lambda m: m.group(0), head, flags=re.S)
nxt = up[0] if up else None
for e in E:
    past = end(e) < now
    t = f'{e["title"]} | God\'s House of Rest Church | Chula Vista'
    d = e["description"]
    url = f'{BASE}/events/{e["slug"]}'
    h = head
    h = re.sub(r"<title>.*?</title>", f"<title>{esc(t)}</title>", h, flags=re.S)
    h = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{esc(d[:155])}">', h)
    h = re.sub(r'<meta property="og:title" content=".*?">', f'<meta property="og:title" content="{esc(e["title"])} | God\'s House of Rest">', h)
    h = re.sub(r'<meta property="og:description" content=".*?">', f'<meta property="og:description" content="{esc(d[:155])}">', h)
    h = re.sub(r'<meta property="og:url" content=".*?">', f'<meta property="og:url" content="{url}">', h)
    h = re.sub(r'<link rel="canonical" href=".*?">', f'<link rel="canonical" href="{url}">', h)
    if e.get("flyerImage"):
        h = re.sub(r'(og:image" content=")[^"]*', rf'\g<1>{BASE}{e["flyerImage"]}', h)
        h = re.sub(r'(twitter:image" content=")[^"]*', rf'\g<1>{BASE}{e["flyerImage"]}', h)
    h = re.sub(r"<h1>.*?</h1>", f"<h1>{esc(e['title'])}</h1>", h, count=1, flags=re.S)
    h = re.sub(r'<p class="page-hero-sub">.*?</p>', f'<p class="page-hero-sub">{fmt_date(e)}</p>', h, count=1, flags=re.S)
    loc = {"@type": "Place", "name": e.get("locationName", "God's House of Rest Church"),
           "address": {"@type": "PostalAddress", "streetAddress": e.get("street", "618 E Street Suite H"), "addressLocality": e.get("city", "Chula Vista"), "addressRegion": "CA", "postalCode": e.get("zip", "91910"), "addressCountry": "US"}} if e.get("locationVisible") else {"@type": "Place", "name": "God's House of Rest Church", "address": {"@type": "PostalAddress", "addressLocality": "Chula Vista", "addressRegion": "CA", "addressCountry": "US"}}
    ld = {"@context": "https://schema.org", "@type": "Event", "name": e["title"], "description": d,
          "startDate": e["startDate"], "endDate": end(e).isoformat() if e.get("endDate") else None,
          "eventStatus": "https://schema.org/EventScheduled", "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
          "location": loc, "organizer": {"@type": "Organization", "name": "God's House of Rest Church", "url": BASE + "/"},
          "isAccessibleForFree": True}
    if e.get("flyerImage"): ld["image"] = BASE + e["flyerImage"]
    ld = {k: v for k, v in ld.items() if v is not None}
    banner = ""
    if past:
        link = f' See what is next: <a href="/events/{nxt["slug"]}" style="color:var(--amber)">{esc(nxt["title"])}</a>.' if nxt else ' Join us Sundays at 11:00 AM.'
        banner = f'<div class="event-passed" style="background:rgba(200,134,10,0.12);border:1px solid rgba(200,134,10,0.35);border-radius:10px;padding:14px 18px;margin-bottom:28px;color:var(--text)">This event has passed.{link}</div>'
    extra = ""
    if e["slug"] == "make-it-holy-2026":
        extra = '''
  <h2 class="section-title" style="margin-top:40px">Make It Holy 2026 Recap</h2>
  <p>The excitement, the laughter, the fellowship, and the presence of God made this night special. We are grateful for every volunteer who poured in time, hard work, creativity, and love. God blessed us all, and we give Him all the glory. See you next year.</p>
  <div class="reel-embed" style="max-width:340px;width:100%;aspect-ratio:9/16;margin:24px auto;"><iframe src="https://www.facebook.com/plugins/video.php?href=https%3A%2F%2Fwww.facebook.com%2Freel%2F4213586215442140%2F&amp;show_text=false&amp;width=340" title="Make It Holy 2026 recap video, God's House of Rest Church, Chula Vista" style="border:none;width:100%;height:100%;" scrolling="no" frameborder="0" allowfullscreen="true" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share" loading="lazy"></iframe></div>
<script type="application/ld+json">''' + json.dumps({"@context": "https://schema.org", "@type": "VideoObject", "name": "Make It Holy 2026 Recap", "description": "Recap of Make It Holy 2026, the 2nd annual trunk-or-treat at God's House of Rest Church in Chula Vista, CA.", "thumbnailUrl": BASE + "/images/events/ghorc-make-it-holy-2026-recap-thumbnail.webp", "uploadDate": "2026-11-02", "embedUrl": "https://www.facebook.com/plugins/video.php?href=https%3A%2F%2Fwww.facebook.com%2Freel%2F4213586215442140%2F", "publisher": {"@type": "Organization", "name": "God's House of Rest Church", "url": BASE + "/"}}) + "</script>"
    cta = '<p style="margin-top:32px"><a class="btn-primary" href="/contact.html">Contact us</a> &nbsp; <a href="/events" style="color:var(--amber)">All events</a></p>' if not past else '<p style="margin-top:32px"><a class="btn-primary" href="/events">See all events</a></p>'
    body = f'''<section class="section">
<div style="max-width:760px;margin:0 auto">
  {banner}
  <p><strong>{fmt_date(e)}, {fmt_time(e)}</strong></p>
  <p>{esc(where(e))}</p>
  <p>{esc(d)}</p>
  {img_tag(e) and '<div style="max-width:420px;margin:28px 0">' + img_tag(e) + '</div>'}
  {extra}
  {cta}
</div>
</section>
<script type="application/ld+json">{json.dumps(ld)}</script>
'''
    open(f"events/{e['slug']}.html", "w", encoding="utf-8").write(h + body + foot)

# sitemap
sm = open("sitemap.xml", encoding="utf-8").read()
sm = re.sub(r"\s*<url><loc>%s/events/[^<]*</loc>.*?</url>" % re.escape(BASE), "", sm, flags=re.S)
add = "".join(f"\n  <url><loc>{BASE}/events/{e['slug']}</loc><lastmod>{now.date()}</lastmod></url>" for e in E)
sm = sm.replace("</urlset>", add + "\n</urlset>")
open("sitemap.xml", "w", encoding="utf-8").write(sm)
print("upcoming", len(up), "past", len(pa))
