#!/usr/bin/env python3
"""
Zenfusion Site Auditor v1.0 — Technical SEO crawler for Shopify stores.
Crawls an entire website and detects technical SEO issues in 13 categories.
Output matches SiteChecker CSV format for SRS integration.

Usage: python3 site_auditor.py <domain> [--limit N] [--output path]
"""

import requests, csv, json, os, sys, re, time
from urllib.parse import urljoin, urlparse, urldefrag, parse_qs
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from collections import defaultdict, Counter

# === CONFIG ===
REQUEST_TIMEOUT = 30
DELAY = 0.5
MAX_PAGES_DEFAULT = 500
USER_AGENT = "Mozilla/5.0 (compatible; ZenfusionSiteAuditor/1.0)"

# === SEVERITY ===
CRITICAL = "Critical"
WARNING = "Warning"
OPPORTUNITY = "Opportunity"
NOTICE = "Notice"

# === ISSUE -> (category, severity) MAP ===
ISSUE_MAP = {
    "Canonical points to a noindex URL": ("Indexability", CRITICAL),
    "Canonical is missing": ("Indexability", WARNING),
    "Canonical != URL": ("Indexability", NOTICE),
    "Meta noindex pages": ("Indexability", NOTICE),
    "Meta nofollow pages": ("Indexability", NOTICE),
    "More than one <body> tag on page": ("Indexability", CRITICAL),
    "More than one <head> tag on page": ("Indexability", CRITICAL),
    "More than one <html> tag on page": ("Indexability", CRITICAL),
    "Multiple viewport <meta> tags": ("Indexability", CRITICAL),
    "HTML lang attribute missing": ("Indexability", WARNING),
    "Description is missing": ("Content relevance", WARNING),
    "Description is empty": ("Content relevance", WARNING),
    "Description is too long": ("Content relevance", NOTICE),
    "Description is too short": ("Content relevance", NOTICE),
    "H1 is missing": ("Content relevance", WARNING),
    "H1 duplicates": ("Content relevance", WARNING),
    "H1 too long": ("Content relevance", NOTICE),
    "H1 too short": ("Content relevance", NOTICE),
    "H1 = Title": ("Content relevance", NOTICE),
    "H2 is missing": ("Content relevance", WARNING),
    "H2 starts with a lowercase letter": ("Content relevance", NOTICE),
    "H2 has other tags inside": ("Content relevance", OPPORTUNITY),
    "Title too long": ("Content relevance", NOTICE),
    "Title too short": ("Content relevance", NOTICE),
    "Text to code ratio < 10%": ("Content relevance", NOTICE),
    "Page has alt tags with one word": ("Content relevance", OPPORTUNITY),
    "Page has no strong importance elements": ("Content relevance", OPPORTUNITY),
    "Page has no list markdown": ("Content relevance", OPPORTUNITY),
    "Paragraphs are missing": ("Content relevance", OPPORTUNITY),
    "Page has identical headings": ("Duplicate content", CRITICAL),
    "Page has identical alt tags": ("Duplicate content", OPPORTUNITY),
    "H1 = Alt": ("Duplicate content", OPPORTUNITY),
    "More than one h1 on page": ("Duplicate content", NOTICE),
    "Page has internal links to 3xx pages": ("Links", WARNING),
    "Page has internal links to 4xx pages": ("Links", WARNING),
    "Broken jump link": ("Links", WARNING),
    "Page has broken links to external websites": ("Links", WARNING),
    "Page has nofollow outgoing internal links": ("Links", NOTICE),
    "Has an internal link with no anchor text": ("Links", OPPORTUNITY),
    "Page has more than 2 links to internal page with same anchor": ("Links", NOTICE),
    "Page has internal backlinks with same anchor": ("Links", OPPORTUNITY),
    "Page has less than 10 internal backlinks": ("Links", OPPORTUNITY),
    "Page has more than 100 internal links": ("Links", NOTICE),
    "Page has outbound internal links with one word anchor": ("Links", OPPORTUNITY),
    "Page has link with URL in onclick": ("Links", NOTICE),
    "Page has anchored image with no alt text": ("Links", WARNING),
    "Page size is over 1.5 MB": ("Page speed", WARNING),
    "Avoid excessive DOM size": ("Page speed", WARNING),
    "Avoid excessive DOM width": ("Page speed", WARNING),
    "Defer offscreen images": ("Page speed", OPPORTUNITY),
    "Add dimensions to images": ("Page speed", OPPORTUNITY),
    "Serve images in next-gen formats": ("Page speed", OPPORTUNITY),
    "Use video formats for animated content": ("Page speed", OPPORTUNITY),
    "Comments in code >1000 symbols": ("Page speed", OPPORTUNITY),
    "Comments in code has more than 1000 symbols": ("Page speed", OPPORTUNITY),
    "Page has HTTP link to www.w3.org": ("Security", NOTICE),
    "Page contains form with GET method": ("Security", NOTICE),
    "4xx client errors": ("Internal", CRITICAL),
    "3xx redirects": ("Internal", WARNING),
    "301 redirects": ("Internal", WARNING),
    "URL contains upper case characters": ("Internal", WARNING),
    "Long URLs": ("Internal", NOTICE),
    "More than three parameters in URL": ("Internal", NOTICE),
    "Whitespace in URL": ("Internal", NOTICE),
    "No Google Tag Manager code": ("Internal", NOTICE),
    "Multiple Google Tag Manager codes": ("Internal", NOTICE),
    "Paginated parameters in URL": ("Internal", NOTICE),
    "Internal URL redirect broken": ("Redirects", CRITICAL),
    "Twitter card incomplete": ("Social media", WARNING),
    "Twitter card missing": ("Social media", WARNING),
    "Open Graph tags incomplete": ("Social media", WARNING),
    "Open Graph tags missing": ("Social media", WARNING),
    "Headings hierarchy is broken": ("Code validation", OPPORTUNITY),
    "Page has identical HTML id attributes": ("Code validation", WARNING),
    "Table has no caption": ("Code validation", OPPORTUNITY),
    "Page has tags with style attributes": ("Code validation", NOTICE),
    "Page has 0 impressions": ("Search traffic", CRITICAL),
    "Page has at least 1 click": ("Search traffic", OPPORTUNITY),
}


def load_env():
    env_path = os.path.expanduser("~/.hermes/.env")
    env = {}
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env


ENV = load_env()
SCRAPEOWL_KEY = ENV.get("SCRAPEOWL_API_KEY", "")


def fetch_page(url, timeout=REQUEST_TIMEOUT):
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        if resp.status_code == 200 and len(resp.text) > 500:
            return resp.status_code, resp.text, resp.url, dict(resp.headers)
    except Exception:
        pass
    if SCRAPEOWL_KEY:
        try:
            api_url = "https://api.scrapeowl.com/v1/"
            params = {"api_key": SCRAPEOWL_KEY, "url": url, "render_js": "1"}
            resp = requests.get(api_url, params=params, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    return 200, data.get("data", ""), url, {}
        except Exception:
            pass
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, verify=False)
        return resp.status_code, resp.text, resp.url, dict(resp.headers)
    except Exception as e:
        return 0, "", url, {"error": str(e)}


def get_domain_root(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def is_same_domain(url, root_domain):
    parsed = urlparse(url)
    root_parsed = urlparse(root_domain)
    root_netloc = root_parsed.netloc.replace("www.", "")
    url_netloc = parsed.netloc.replace("www.", "")
    return url_netloc == root_netloc or url_netloc.endswith("." + root_netloc)


def normalize_url(url):
    url, _ = urldefrag(url)
    return url.rstrip("/") if url != "/" else url


def check_robots(url):
    root = get_domain_root(url)
    rp = RobotFileParser()
    try:
        rp.set_url(f"{root}/robots.txt")
        rp.read()
    except Exception:
        pass
    return rp


def get_sitemaps(root_url):
    sitemaps = []
    try:
        resp = requests.get(f"{root_url}/sitemap.xml", headers={"User-Agent": USER_AGENT}, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "xml")
            for sm in soup.find_all("sitemap"):
                loc = sm.find("loc")
                if loc:
                    sitemaps.append({"url": loc.text, "type": "sitemap"})
            for u in soup.find_all("url"):
                loc = u.find("loc")
                if loc:
                    sitemaps.append({"url": loc.text, "type": "url"})
    except Exception:
        pass
    return sitemaps


def analyze_page(url, html, status_code, all_pages_status, internal_links_map, title_map, desc_map, headings_map, alt_map=None):
    issues = {CRITICAL: [], WARNING: [], OPPORTUNITY: [], NOTICE: []}
    if not html or status_code == 0:
        if 400 <= status_code < 500:
            issues[CRITICAL].append("4xx client errors")
        return issues

    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.text.strip() if title_tag else ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    desc = desc_tag.get("content", "").strip() if desc_tag else ""
    canonical_tag = soup.find("link", rel="canonical")
    canonical = canonical_tag.get("href", "").strip() if canonical_tag else ""
    robots_meta = soup.find("meta", attrs={"name": "robots"})
    robots_content = robots_meta.get("content", "").lower() if robots_meta else ""

    # Indexability
    if "noindex" in robots_content:
        issues[NOTICE].append("Meta noindex pages")
    if "nofollow" in robots_content:
        issues[NOTICE].append("Meta nofollow pages")
    if not canonical and status_code == 200:
        issues[WARNING].append("Canonical is missing")
    if canonical and canonical.rstrip("/") != url.rstrip("/"):
        issues[NOTICE].append("Canonical != URL")
    if "noindex" in robots_content and canonical:
        issues[CRITICAL].append("Canonical points to a noindex URL")
    for tag in ["body", "head", "html"]:
        if len(soup.find_all(tag)) > 1:
            issues[CRITICAL].append(f"More than one <{tag}> tag on page")
    viewports = soup.find_all("meta", attrs={"name": "viewport"})
    if len(viewports) > 1:
        issues[CRITICAL].append("Multiple viewport <meta> tags")
    html_tag = soup.find("html")
    if html_tag and not html_tag.get("lang"):
        issues[WARNING].append("HTML lang attribute missing")

    # Content relevance
    if not desc_tag:
        issues[WARNING].append("Description is missing")
    elif not desc:
        issues[WARNING].append("Description is empty")
    elif len(desc) > 160:
        issues[NOTICE].append("Description is too long")
    elif len(desc) < 70:
        issues[NOTICE].append("Description is too short")

    h1_tags = soup.find_all("h1")
    h2_tags = soup.find_all("h2")
    if not h1_tags:
        issues[WARNING].append("H1 is missing")
    elif len(h1_tags) > 1:
        issues[NOTICE].append("More than one h1 on page")
    else:
        h1 = h1_tags[0].get_text(strip=True)
        if len(h1) > 60:
            issues[NOTICE].append("H1 too long")
        elif len(h1) < 10:
            issues[NOTICE].append("H1 too short")
        if h1 and h1[0].islower():
            issues[NOTICE].append("H1 = Title" if title and h1.lower() == title.lower() else "")
    if title and h1_tags and h1_tags[0].get_text(strip=True).lower() == title.lower():
        issues[NOTICE].append("H1 = Title")
    if not h2_tags:
        issues[WARNING].append("H2 is missing")
    else:
        for h2 in h2_tags:
            h2_text = h2.get_text(strip=True)
            if h2_text and h2_text[0].islower():
                issues[NOTICE].append("H2 starts with a lowercase letter")
            if h2.find("a") or h2.find("span") or h2.find("div"):
                issues[OPPORTUNITY].append("H2 has other tags inside")
    if title:
        if len(title) > 60:
            issues[NOTICE].append("Title too long")
        elif len(title) < 30:
            issues[NOTICE].append("Title too short")
    text = soup.get_text(strip=True)
    if len(html) > 0 and len(text) / len(html) < 0.10:
        issues[NOTICE].append("Text to code ratio < 10%")

    # Links
    links = soup.find_all("a", href=True)
    internal_links = []
    nofollow_internal = 0
    no_anchor = 0
    onclick_count = 0
    anchor_map = defaultdict(list)
    for a in links:
        href = a.get("href", "").strip()
        text_link = a.get_text(strip=True)
        if href == "#":
            continue
        if "javascript:" in href.lower():
            continue
        absolute = urljoin(url, href)
        if is_same_domain(absolute, url):
            internal_links.append(absolute)
            rel = a.get("rel", [])
            if isinstance(rel, list) and "nofollow" in [r.lower() for r in rel]:
                nofollow_internal += 1
            if not text_link:
                no_anchor += 1
            anchor_map[normalize_url(absolute)].append(text_link)
        if a.get("onclick"):
            onclick_count += 1

    link_3xx = link_4xx = 0
    for link_url in set(internal_links):
        sc = all_pages_status.get(normalize_url(link_url), 0)
        if 300 <= sc < 400:
            link_3xx += 1
        elif 400 <= sc < 500:
            link_4xx += 1
    if link_3xx:
        issues[WARNING].append("Page has internal links to 3xx pages")
    if link_4xx:
        issues[WARNING].append("Page has internal links to 4xx pages")
    if nofollow_internal:
        issues[NOTICE].append("Page has nofollow outgoing internal links")
    if no_anchor:
        issues[OPPORTUNITY].append("Has an internal link with no anchor text")
    if onclick_count:
        issues[NOTICE].append("Page has link with URL in onclick")
    for u, anchors in anchor_map.items():
        for a_text, cnt in Counter(anchors).items():
            if cnt > 2:
                issues[NOTICE].append("Page has more than 2 links to internal page with same anchor")
                break
    backlinks = internal_links_map.get(normalize_url(url), [])
    if len(backlinks) < 10:
        issues[OPPORTUNITY].append("Page has less than 10 internal backlinks")
    if len(set(backlinks)) < len(backlinks):
        issues[OPPORTUNITY].append("Page has internal backlinks with same anchor")
    if len(internal_links) > 100:
        issues[NOTICE].append("Page has more than 100 internal links")

    # Page speed
    page_size = len(html.encode("utf-8"))
    if page_size > 1500000:
        issues[WARNING].append("Page size is over 1.5 MB")
    all_tags = soup.find_all(True)
    if len(all_tags) > 1500:
        issues[WARNING].append("Avoid excessive DOM size")
    # DOM width = max number of children at any level (siblings)
    max_width = 0
    for tag in all_tags:
        children = tag.find_all(recursive=False)
        if len(children) > max_width:
            max_width = len(children)
    if max_width > 100:  # SiteChecker threshold for excessive DOM width
        issues[WARNING].append("Avoid excessive DOM width")
    images = soup.find_all("img")
    if sum(1 for img in images if not img.get("width") or not img.get("height")) > 0:
        issues[OPPORTUNITY].append("Add dimensions to images")
    if sum(1 for img in images if not img.get("loading") == "lazy" and not img.get("data-src")) > 5:
        issues[OPPORTUNITY].append("Defer offscreen images")
    if images and not any("webp" in str(img.get("src", "")) or "avif" in str(img.get("src", "")) for img in images):
        issues[OPPORTUNITY].append("Serve images in next-gen formats")
    if soup.find_all("img", src=re.compile(r"\.gif$", re.I)):
        issues[OPPORTUNITY].append("Use video formats for animated content")
    # Comments >1000 symbols — use regex on raw HTML (BeautifulSoup Comment type is unreliable)
    long_comments = re.findall(r"<!--(.{1000,}?)-->", html, re.DOTALL)
    if long_comments:
        issues[OPPORTUNITY].append("Comments in code has more than 1000 symbols")

    # Security
    if soup.find_all("a", href=re.compile(r"http://www\.w3\.org")):
        issues[NOTICE].append("Page has HTTP link to www.w3.org")
    if soup.find_all("form", method=re.compile(r"^get$", re.I)):
        issues[NOTICE].append("Page contains form with GET method")

    # Internal URL
    parsed = urlparse(url)
    if any(c.isupper() for c in parsed.path):
        issues[WARNING].append("URL contains upper case characters")
    if len(url) > 100:
        issues[NOTICE].append("Long URLs")
    params = parse_qs(parsed.query)
    if len(params) > 3:
        issues[NOTICE].append("More than three parameters in URL")
    if " " in url:
        issues[NOTICE].append("Whitespace in URL")
    if "page" in params or "p" in params:
        issues[NOTICE].append("Paginated parameters in URL")
    gtm = len(re.findall(r"gtag/js|googletagmanager\.com/gtm\.js", html))
    if gtm == 0:
        issues[NOTICE].append("No Google Tag Manager code")
    elif gtm > 1:
        issues[NOTICE].append("Multiple Google Tag Manager codes")

    # Redirects
    if 300 <= status_code < 400:
        issues[WARNING].append("3xx redirects")
        if status_code == 301:
            issues[WARNING].append("301 redirects")
    if status_code >= 400:
        issues[CRITICAL].append("4xx client errors")

    # Social media
    og_fields = ["og:title", "og:description", "og:image", "og:url", "og:type"]
    og_found = sum(1 for og in og_fields if soup.find("meta", attrs={"property": og}))
    if og_found < 3:
        issues[WARNING].append("Open Graph tags incomplete" if og_found else "Open Graph tags missing")
    # Twitter card: SiteChecker checks card, title, description, image, site, creator
    tw_fields = ["twitter:card", "twitter:title", "twitter:description", "twitter:image"]
    tw_found = sum(1 for tw in tw_fields if soup.find("meta", attrs={"name": tw}) or soup.find("meta", attrs={"property": tw}))
    if tw_found < 4:
        issues[WARNING].append("Twitter card incomplete" if tw_found else "Twitter card missing")

    # Code validation
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    prev = 0
    for h in headings:
        level = int(h.name[1])
        if level > prev + 1 and prev > 0:
            issues[OPPORTUNITY].append("Headings hierarchy is broken")
            break
        prev = level
    id_tags = [t.get("id") for t in soup.find_all(id=True)]
    if len(id_tags) != len(set(id_tags)):
        issues[WARNING].append("Page has identical HTML id attributes")
    if soup.find_all("table") and any(not t.find("caption") for t in soup.find_all("table")):
        issues[OPPORTUNITY].append("Table has no caption")
    if soup.find_all(attrs={"style": True}):
        issues[NOTICE].append("Page has tags with style attributes")

    # Store for cross-page analysis
    title_map[url] = title
    desc_map[url] = desc
    headings_map[url] = [h.get_text(strip=True) for h in headings]

    # Alt text checks
    alt_texts = [img.get("alt", "") for img in images]
    # Store alt texts for cross-page dedup
    if alt_map is not None:
        alt_map[url] = [a for a in alt_texts if a]
    if sum(1 for a in alt_texts if a and len(a.split()) == 1) > 0:
        issues[OPPORTUNITY].append("Page has alt tags with one word")
    if h1_tags and images:
        h1_text = h1_tags[0].get_text(strip=True)
        if any(img.get("alt", "") == h1_text for img in images):
            issues[OPPORTUNITY].append("H1 = Alt")
    if not soup.find_all(["strong", "b"]):
        issues[OPPORTUNITY].append("Page has no strong importance elements")
    if not soup.find_all(["ul", "ol"]):
        issues[OPPORTUNITY].append("Page has no list markdown")
    if not soup.find_all("p"):
        issues[OPPORTUNITY].append("Paragraphs are missing")

    # Clean empty entries
    for k in issues:
        issues[k] = [i for i in issues[k] if i]
    return issues


def compute_weight(url, internal_links_map):
    parsed = urlparse(url)
    if parsed.path in ["", "/"]:
        return 100.0
    backlinks = internal_links_map.get(normalize_url(url), [])
    max_backlinks = max((len(v) for v in internal_links_map.values()), default=1)
    if max_backlinks == 0:
        return 0.0
    return round((len(backlinks) / max_backlinks) * 100, 3)


def compute_site_health(all_page_issues, total_pages):
    if total_pages == 0:
        return 0
    c = sum(len(p[CRITICAL]) for p in all_page_issues.values())
    w = sum(len(p[WARNING]) for p in all_page_issues.values())
    o = sum(len(p[OPPORTUNITY]) for p in all_page_issues.values())
    n = sum(len(p[NOTICE]) for p in all_page_issues.values())
    if c + w + o + n == 0:
        return 100
    penalty = (c * 3 + w * 1.5 + o * 0.5 + n * 0.1) / total_pages
    return round(max(0, 100 - penalty), 1)


def crawl_site(start_url, max_pages=500):
    root = get_domain_root(start_url)
    rp = check_robots(start_url)
    visited = set()
    queue = [start_url]
    all_pages = {}
    all_pages_status = {}
    internal_links_map = defaultdict(list)
    title_map, desc_map, headings_map = {}, {}, {}
    alt_map = {}  # url -> [alt texts]

    print(f"\n{'='*70}")
    print(f"  ZENFUSION SITE AUDITOR v1.0")
    print(f"{'='*70}")
    print(f"  Domain: {root}")
    print(f"  Max pages: {max_pages}")
    print(f"  ScrapeOwl: {'ON' if SCRAPEOWL_KEY else 'OFF'}")
    print(f"{'='*70}\n")

    sitemaps = get_sitemaps(root)
    print(f"  Sitemaps: {len(sitemaps)} entries found")
    for sm in sitemaps:
        if sm["type"] == "url" and is_same_domain(sm["url"], start_url):
            queue.append(sm["url"])

    page_count = 0
    while queue and page_count < max_pages:
        url = queue.pop(0)
        norm = normalize_url(url)
        if norm in visited:
            continue
        visited.add(norm)
        if rp and not rp.can_fetch(USER_AGENT, url):
            continue
        if any(url.lower().endswith(ext) for ext in [".jpg", ".png", ".gif", ".css", ".js", ".svg", ".ico"]):
            continue
        time.sleep(DELAY)
        page_count += 1
        if page_count % 10 == 0:
            print(f"  Crawled {page_count} pages...")
        status, html, final_url, headers = fetch_page(url)
        all_pages_status[norm] = status
        all_pages[url] = {"status": status, "html": html, "headers": headers, "final_url": final_url}
        if status == 200 and html:
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a.get("href", "").strip()
                if href and href != "#" and not href.startswith("javascript:"):
                    absolute = urljoin(url, href)
                    if is_same_domain(absolute, start_url):
                        target_norm = normalize_url(absolute)
                        internal_links_map[target_norm].append(a.get_text(strip=True))
                        if target_norm not in visited and absolute not in queue:
                            if len(queue) < max_pages * 2:
                                queue.append(absolute)

    print(f"\n  Crawl complete: {page_count} pages fetched")

    all_page_issues = {}
    for url, pd in all_pages.items():
        all_page_issues[url] = analyze_page(
            url, pd["html"], pd["status"], all_pages_status, internal_links_map, title_map, desc_map, headings_map, alt_map
        )

    # Cross-page duplicate checks
    title_counts = Counter(t for t in title_map.values() if t)
    desc_counts = Counter(d for d in desc_map.values() if d)
    # Build alt text -> set of URLs mapping for identical alt tag detection
    alt_text_urls = defaultdict(set)
    for url, alts in alt_map.items():
        for a in alts:
            alt_text_urls[a].add(url)

    for url in all_page_issues:
        title = title_map.get(url, "")
        desc = desc_map.get(url, "")
        if title and title_counts[title] > 1:
            all_page_issues[url][CRITICAL].append("Page has identical headings")
        if desc and desc_counts[desc] > 1:
            all_page_issues[url][WARNING].append("Description duplicates")
        # Check if this page has alt tags that appear on other pages
        page_alts = alt_map.get(url, [])
        if any(len(alt_text_urls.get(a, set())) > 1 for a in page_alts):
            all_page_issues[url][OPPORTUNITY].append("Page has identical alt tags")

    all_page_data = []
    for url, issues in all_page_issues.items():
        weight = compute_weight(url, internal_links_map)
        title = title_map.get(url, "")
        desc = desc_map.get(url, "")
        status = all_pages_status.get(normalize_url(url), 0)
        crits = sorted(set(issues[CRITICAL]))
        warns = sorted(set(issues[WARNING]))
        opps = sorted(set(issues[OPPORTUNITY]))
        nots = sorted(set(issues[NOTICE]))
        all_page_data.append({
            "url": url, "status_code": status, "indexation": "Indexable",
            "title": title, "description": desc, "weight": weight,
            "criticals_count": len(crits), "warnings_count": len(warns),
            "opportunities_count": len(opps), "notices_count": len(nots),
            "criticals": ", ".join(crits), "warnings": ", ".join(warns),
            "opportunities": ", ".join(opps), "notices": ", ".join(nots),
        })

    health = compute_site_health(all_page_issues, len(all_page_issues))

    cat_summary = defaultdict(lambda: {"criticals": 0, "warnings": 0, "opportunities": 0, "notices": 0, "pages": set()})
    sev_key_map = {CRITICAL: "criticals", WARNING: "warnings", OPPORTUNITY: "opportunities", NOTICE: "notices"}
    for url, issues in all_page_issues.items():
        for sev, items in issues.items():
            for item in items:
                cat = ISSUE_MAP.get(item, ("Other", sev))[0]
                cat_summary[cat][sev_key_map[sev]] += 1
                cat_summary[cat]["pages"].add(url)

    return all_page_data, health, cat_summary, sitemaps


def save_csv(page_data, output_path):
    fields = ["Url", "Status Code", "Indexation", "Title", "Description", "Weight",
              "# Criticals", "# Warnings", "# Opportunities", "# Notices",
              "Criticals", "Warnings", "Opportunities", "Notices"]
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for p in page_data:
            w.writerow({"Url": p["url"], "Status Code": p["status_code"], "Indexation": p["indexation"],
                         "Title": p["title"], "Description": p["description"], "Weight": p["weight"],
                         "# Criticals": p["criticals_count"], "# Warnings": p["warnings_count"],
                         "# Opportunities": p["opportunities_count"], "# Notices": p["notices_count"],
                         "Criticals": p["criticals"], "Warnings": p["warnings"],
                         "Opportunities": p["opportunities"], "Notices": p["notices"]})


def save_json(page_data, health, cat_summary, sitemaps, output_path):
    result = {
        "site_health_score": health,
        "total_pages": len(page_data),
        "total_criticals": sum(p["criticals_count"] for p in page_data),
        "total_warnings": sum(p["warnings_count"] for p in page_data),
        "total_opportunities": sum(p["opportunities_count"] for p in page_data),
        "total_notices": sum(p["notices_count"] for p in page_data),
        "category_summary": {cat: {"criticals": v["criticals"], "warnings": v["warnings"],
                                    "opportunities": v["opportunities"], "notices": v["notices"],
                                    "pages_affected": len(v["pages"])}
                              for cat, v in cat_summary.items()},
        "sitemaps": len(sitemaps),
        "pages": page_data,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


def print_summary(health, cat_summary, page_data):
    c = sum(p["criticals_count"] for p in page_data)
    w = sum(p["warnings_count"] for p in page_data)
    o = sum(p["opportunities_count"] for p in page_data)
    n = sum(p["notices_count"] for p in page_data)
    print(f"\n{'='*70}")
    print(f"  SITE AUDIT COMPLETE")
    print(f"{'='*70}")
    print(f"  Website Score: {health}/100")
    print(f"  Total Pages: {len(page_data)}")
    print(f"  Criticals: {c} | Warnings: {w} | Opportunities: {o} | Notices: {n}")
    print(f"\n{'='*70}")
    print(f"  CATEGORY BREAKDOWN")
    print(f"{'='*70}")
    for cat, v in sorted(cat_summary.items(), key=lambda x: -(x[1]["criticals"] + x[1]["warnings"])):
        total = v["criticals"] + v["warnings"] + v["opportunities"] + v["notices"]
        if total == 0:
            continue
        print(f"  {cat}: {total} issues ({v['criticals']}C/{v['warnings']}W/{v['opportunities']}O/{v['notices']}N) - {len(v['pages'])} pages")
    print(f"\n  Report generated by Zenfusion Site Auditor v1.0")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 site_auditor.py <domain> [--limit N] [--output path]")
        sys.exit(1)
    domain = sys.argv[1]
    if not domain.startswith("http"):
        domain = "https://" + domain
    max_pages = MAX_PAGES_DEFAULT
    output_dir = os.path.expanduser("~/.hermes/audits/site-auditor")
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--limit" and i + 1 < len(sys.argv):
            max_pages = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    os.makedirs(output_dir, exist_ok=True)
    page_data, health, cat_summary, sitemaps = crawl_site(domain, max_pages)
    domain_name = urlparse(domain).netloc.replace("www.", "").replace(".", "_")
    csv_path = os.path.join(output_dir, f"{domain_name}_site_audit.csv")
    json_path = os.path.join(output_dir, f"{domain_name}_site_audit.json")
    save_csv(page_data, csv_path)
    save_json(page_data, health, cat_summary, sitemaps, json_path)
    print_summary(health, cat_summary, page_data)
    print(f"\n  CSV: {csv_path}")
    print(f"  JSON: {json_path}")


if __name__ == "__main__":
    main()
