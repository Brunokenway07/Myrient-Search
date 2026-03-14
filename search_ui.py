from flask import Flask, request, render_template_string
import json, urllib.parse, re

DATA_FILE = "myrient_links.json"
RESULTS_PER_PAGE = 100

app = Flask(__name__)

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Myrient Search</title>
    <style>
        body { font-family: Arial, sans-serif; margin:40px; background:#111; color:#eee; }
        input, select, button { padding:8px; margin:5px; border-radius:4px; border:none; }
        a { color:#4da6ff; text-decoration:none; }
        .card { background:#1c1c1c; padding:15px; margin:10px 0; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.4); }
        .file-row { display:flex; justify-content:space-between; align-items:center; margin-top:10px; font-size:14px; }
        .file-name { font-weight:bold; }
        details { margin-top:8px; }
        .pagination a { margin:5px; padding:6px 12px; background:#333; border-radius:4px; }
        .tree { font-family: monospace; white-space: pre; margin-left:10px; font-size:13px; }
        .help { cursor:pointer; font-size:14px; margin-left:10px; color:#aaa; }
        .tooltip { display:none; background:#222; padding:10px; border-radius:8px; font-size:12px; color:#ccc; width:300px; margin-top:10px; }
        .help:hover + .tooltip { display:block; }
    </style>
</head>
<body>
<h1 style="display:inline-block;">Myrient Search</h1>
<span class="help">❓</span>
<div class="tooltip">
    <b>Search Tips:</b><br>
    - Use quotes for exact phrase: "game iso"<br>
    - Use AND/OR for logic: game AND iso OR rom<br>
    - Use -word to exclude: game -demo<br>
    - Filter by extension: ext=iso<br>
</div>

<form method="get">
    <input type="text" name="q" placeholder="Search words or phrase..." value="{{q}}">
    <input type="text" name="ext" placeholder="Extension (zip, iso...)" value="{{ext}}">
    <select name="sort">
        <option value="">Sort by...</option>
        <option value="title" {% if sort=='title' %}selected{% endif %}>Title (A-Z)</option>
        <option value="size" {% if sort=='size' %}selected{% endif %}>Size (largest first)</option>
        <option value="date" {% if sort=='date' %}selected{% endif %}>Date (newest first)</option>
    </select>
    <button type="submit">Search</button>
</form>

<p>{{total}} files found</p>

{% for r in results %}
<div class="card">
    <details>
        <summary>{{r['top_folder']}}</summary>
        <div class="tree">{{r['nested_tree']|safe}}</div>
    </details>
    <div class="file-row">
        <div class="file-name">
            <a href="{{r['link']}}" target="_blank">{{r['title']}}</a>
        </div>
        <div>
            {% if r['size'] %}Size: {{r['size']}}{% endif %}
            {% if r['date'] %} | Date: {{r['date']}}{% endif %}
        </div>
    </div>
</div>
{% endfor %}

<div class="pagination">
{% if page > 1 %}
    <a href="?q={{q}}&ext={{ext}}&sort={{sort}}&page={{page-1}}">Previous</a>
{% endif %}
{% if page < total_pages %}
    <a href="?q={{q}}&ext={{ext}}&sort={{sort}}&page={{page+1}}">Next</a>
{% endif %}
</div>

</body>
</html>
"""

def build_tree(link):
    path = link.replace("https://myrient.erista.me/files/", "")
    parts = [urllib.parse.unquote(p) for p in path.split("/") if p]

    if not parts:
        return "", ""

    top_folder = parts[0]

    tree_lines = []
    indent = ""
    for p in parts[1:-1]:
        tree_lines.append(indent + "📂 " + p)
        indent += "    "
    tree_lines.append(indent + "📄 " + parts[-1])

    tree_html = "<br>".join(tree_lines)
    return top_folder, tree_html

def parse_size_filter(token, size_bytes):
    match = re.match(r"size([<>]=?)(\d+)([KMGTP]?B?)", token)
    if not match or size_bytes is None:
        return True
    op, num, unit = match.groups()
    unit = unit.upper()
    multiplier = 1
    if unit.startswith("K"): multiplier = 1024
    elif unit.startswith("M"): multiplier = 1024**2
    elif unit.startswith("G"): multiplier = 1024**3
    elif unit.startswith("T"): multiplier = 1024**4
    threshold = int(num) * multiplier
    if op == ">": return size_bytes > threshold
    if op == "<": return size_bytes < threshold
    if op == ">=": return size_bytes >= threshold
    if op == "<=": return size_bytes <= threshold
    return True

def advanced_filter(results, q, ext):
    if q:
        tokens = q.lower().split()
        filtered = []
        for r in results:
            text = r["title"].lower()
            size_bytes = r.get("size_bytes")
            include = True
            or_match = False
            for t in tokens:
                if t.startswith("size"):
                    if not parse_size_filter(t, size_bytes):
                        include = False
                        break
                elif t == "and":
                    continue
                elif t == "or":
                    or_match = True
                elif t.startswith("-"):
                    if t[1:] in text:
                        include = False
                        break
                else:
                    if t not in text:
                        if not or_match:
                            include = False
                            break
            if include:
                filtered.append(r)
        results = filtered

    if ext:
        results = [r for r in results if r["link"].lower().endswith("." + ext)]

    results = [r for r in results if r["title"] not in [".", ".."]]
    return results

@app.route("/")
def search():
    q = request.args.get("q", "").strip()
    ext = request.args.get("ext", "").lower().strip()
    sort = request.args.get("sort", "")
    page = request.args.get("page", 1, type=int)

    results = advanced_filter(data, q, ext)

    # Add folder info before counting
    for r in results:
        top, nested = build_tree(r["link"])
        r["top_folder"] = top
        r["nested_tree"] = nested

    if sort == "title":
        results = sorted(results, key=lambda r: r["title"].lower())
    elif sort == "size":
        results = sorted(results, key=lambda r: r.get("size_bytes") or 0, reverse=True)
    elif sort == "date":
        results = sorted(results, key=lambda r: r.get("date") or "", reverse=True)

    total = len(results)
    folder_count = len(set(r["top_folder"] for r in results if r.get("top_folder")))
    total_pages = (total // RESULTS_PER_PAGE) + (1 if total % RESULTS_PER_PAGE else 0)
    start = (page - 1) * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    page_results = results[start:end]

    return render_template_string(
        HTML_TEMPLATE,
        results=page_results,
        total=total,
        folder_count=folder_count,
        q=q,
        ext=ext,
        sort=sort,
        page=page,
        total_pages=total_pages
    )

if __name__ == "__main__":
    app.run(port=5000)
