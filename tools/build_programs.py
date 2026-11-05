#!/usr/bin/env python3
"""Build program pages (vbs, youth, womens-ministry, holy-week, community) from _data/events.json. Run after build_events.py."""
import json, re, html, os, datetime as dt
from zoneinfo import ZoneInfo
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PT = ZoneInfo("America/Los_Angeles"); now = dt.datetime.now(PT); BASE = "https://godshouseofrest.com"
E = [e for e in json.load(open("_data/events.json"))["events"] if not e.get("needsDate")]
esc = lambda s: html.escape(s, quote=True)
st = lambda e: dt.datetime.fromisoformat(e["startDate"])
en = lambda e: dt.datetime.fromisoformat(e["endDate"]) if e.get("endDate") else st(e) + dt.timedelta(hours=4)
P = {
 "vbs": ("Vacation Bible School", "Free Vacation Bible School at God's House of Rest Church in Chula Vista for ages 4 to 13. Seed of Truth, Spy Academy.", "Each summer our children dig into God's Word through games, lessons, and fellowship. VBS 2026 was Seed of Truth, Spy Academy, free for ages 4 to 13."),
 "youth": ("Youth Ministry", "Youth ministry at God's House of Rest Church in Chula Vista: Youth Sunday, movie nights, trunk-or-treat, and more.", "Our youth and children's ministry gives young people a place to learn, laugh, and grow in faith."),
 "womens-ministry": ("Women's Ministry", "Women's ministry at God's House of Rest Church in Chula Vista: brunches, game nights, and fellowship.", "Women of God's House of Rest gather for fellowship, encouragement, and purpose. New dates will be posted here as they are confirmed."),
 "holy-week": ("Holy Week", "Holy Week at God's House of Rest Church in Chula Vista: daily devotionals from Palm Sunday to Resurrection Sunday.", "Walk through Holy Week with us. Each day has one verse, one focus, and one action."),
 "community": ("Community Outreach", "Community events and outreach from God's House of Rest Church in Chula Vista.", "We serve our neighbors in Chula Vista and the South Bay through walks, picnics, and conversations."),
}
DEVO = [("Palm Sunday, March 29","Worship with us at 11:00 AM as Holy Week begins.","",""),
 ("Monday: Clean the Temple","Matthew 21:12-13","Removing what does not belong","Remove one distraction today."),
 ("Wednesday: Check Your Heart","Psalm 51:10","Repentance and motives","Write down what you need to repent from."),
 ("Thursday: Serve Like Jesus","John 13:14-15","Humility and service","Serve someone quietly."),
 ("Resurrection Sunday, April 5","Worship with us at 11:00 AM. He is risen.","","")]
s = open("events.html", encoding="utf-8").read()
cut = s.index('<section class="section">'); head, foot = s[:cut], s[s.index("<footer>"):]
ab = lambda t: re.sub(r'(href|src)="(?!https?:|/|#|mailto:|tel:|data:)([^"]+)"', r'\1="/\2"', t)
head, foot = ab(head), ab(foot)
def card(e):
    past = en(e) < now; s_ = st(e).astimezone(PT)
    return f'<li style="margin:10px 0"><a href="/events/{e["slug"]}" style="color:var(--amber)">{esc(e["title"])}</a> <span style="color:var(--text-muted)">{s_.strftime("%B %-d, %Y")}{" (past)" if past else ""}</span></li>'
for slug, (title, desc, intro) in P.items():
    ev = [e for e in E if e.get("program") == slug]
    up = sorted([e for e in ev if en(e) >= now], key=st); pa = sorted([e for e in ev if en(e) < now], key=st, reverse=True)
    h = head
    url = f"{BASE}/{slug}"
    h = re.sub(r"<title>.*?</title>", f"<title>{esc(title)} | God's House of Rest Church | Chula Vista</title>", h, flags=re.S)
    h = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{esc(desc)}">', h)
    h = re.sub(r'<meta property="og:title" content=".*?">', f'<meta property="og:title" content="{esc(title)} | God\'s House of Rest">', h)
    h = re.sub(r'<meta property="og:description" content=".*?">', f'<meta property="og:description" content="{esc(desc)}">', h)
    h = re.sub(r'<meta property="og:url" content=".*?">', f'<meta property="og:url" content="{url}">', h)
    h = re.sub(r'<link rel="canonical" href=".*?">', f'<link rel="canonical" href="{url}">', h)
    h = re.sub(r"<h1>.*?</h1>", f"<h1>{esc(title)}</h1>", h, count=1, flags=re.S)
    h = re.sub(r'<p class="page-hero-sub">.*?</p>', f'<p class="page-hero-sub">{esc(intro)}</p>', h, count=1, flags=re.S)
    b = '<section class="section"><div style="max-width:760px;margin:0 auto">'
    if slug == "holy-week":
        for d_ in DEVO:
            b += f'<div style="border:1px solid rgba(200,134,10,0.25);border-radius:12px;padding:20px 24px;margin:16px 0"><h3 style="margin:0 0 8px">{esc(d_[0])}</h3><p style="margin:0 0 6px">{esc(d_[1])}</p>'
            if d_[2]: b += f'<p style="margin:0 0 6px"><strong>Focus:</strong> {esc(d_[2])}</p><p style="margin:0"><strong>Action:</strong> {esc(d_[3])}</p>'
            b += '</div>'
        b += '<p style="color:var(--text-muted)">Devotionals for Tuesday, Friday, and Saturday will be added.</p>'
    if up:
        b += '<h2 class="section-title">Upcoming</h2><ul style="list-style:none;padding:0">' + "".join(card(e) for e in up) + "</ul>"
    elif slug != "holy-week":
        b += '<h2 class="section-title">Upcoming</h2><p>No dates posted yet. Call (619) 931-9344 or check back soon.</p>'
    if pa: b += '<h2 class="section-title" style="margin-top:40px">Past Events</h2><ul style="list-style:none;padding:0">' + "".join(card(e) for e in pa) + "</ul>"
    b += '<p style="margin-top:32px"><a class="btn-primary" href="/contact.html">Get in touch</a> &nbsp; <a href="/events" style="color:var(--amber)">All events</a></p></div></section>\n'
    open(f"{slug}.html", "w", encoding="utf-8").write(h + b + foot)
sm = open("sitemap.xml", encoding="utf-8").read()
sm = re.sub(r"\s*<url><loc>%s/(%s)</loc>.*?</url>" % (re.escape(BASE), "|".join(P)), "", sm, flags=re.S)
sm = sm.replace("</urlset>", "".join(f"\n  <url><loc>{BASE}/{k}</loc><lastmod>{now.date()}</lastmod></url>" for k in P) + "\n</urlset>")
open("sitemap.xml", "w", encoding="utf-8").write(sm)
