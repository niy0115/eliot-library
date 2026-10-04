#!/usr/bin/env python3
"""Import authorized NCL/NBINet CSV exports into the static ISBN catalog.

Usage: python tools/import_taiwan_books.py path/to/official.csv [more.csv ...]
Only import datasets whose redistribution terms permit use in this project.
"""
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "taiwan-books.json"
FIELDS = {
    "isbn": ("ISBN", "isbn", "ISBN (020$a$c)", "國際標準書號", "國際標準書號(ISBN)"),
    "title": ("書名", "題名", "書名 (245$a$b)", "書名/題名", "title", "Title"),
    "author": ("作者", "著者", "編著者 (245$c)", "author", "Author"),
    "publisher": ("出版社", "出版者", "出版項 (264)", "出版項 (260)", "publisher", "Publisher"),
    "date": ("出版日期", "出版年", "出版年 (008/07-10)", "出版年份", "date", "year"),
}
def field(row, names):
    normalized = {k.strip().lower().replace(" ",""): v for k,v in row.items() if k}
    for name in names:
        v = normalized.get(name.strip().lower().replace(" ",""))
        if v: return str(v).replace("\\x1e", "").strip()
    return ""

def parse_publisher(raw):
    match = re.search(r":;?\\s*([^;,]+)", raw)
    return match.group(1).strip(" []") if match else raw

def import_file(path, books):
    count = 0
    for encoding in ("utf-8-sig", "cp950"):
        try:
            with path.open(encoding=encoding, newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError(f"Unsupported CSV encoding: {path}")
    if not rows or not any(field(r, FIELDS["isbn"]) for r in rows[:50]):
        raise ValueError(f"Cannot identify ISBN column in {path}; inspect CSV headers")
    for row in rows:
        raw = field(row, FIELDS["isbn"])
        title = field(row, FIELDS["title"]).rstrip(" /;")
        if not title: continue
        for isbn in set(re.findall(r"(?<!\\d)(?:97[89])[\\d -]{10,17}(?!\\d)", raw)):
            isbn = re.sub(r"[^0-9]", "", isbn)
            if len(isbn) != 13: continue
            # ISBN-13 checksum
            if sum(int(n)*(1 if i%2==0 else 3) for i,n in enumerate(isbn))%10: continue
            if isbn not in books:
                books[isbn] = {"title": title, "author": field(row,FIELDS["author"]),
                               "publisher": parse_publisher(field(row,FIELDS["publisher"])),
                               "date": field(row,FIELDS["date"])}
                count += 1
    return count

def main():
    if len(sys.argv) < 2: raise SystemExit(__doc__)
    data = json.loads(OUT.read_text(encoding="utf-8"))
    books = data.setdefault("books", {})
    for name in sys.argv[1:]:
        path = Path(name)
        print(f"{path}: {import_file(path, books)} new ISBN records")
    data["updatedAt"] = date.today().isoformat()
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"Total ISBN records: {len(books)}")
if __name__ == "__main__": main()
