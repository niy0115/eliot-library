#!/usr/bin/env python3
"""Merge authorized NCL/NBINet CSVs into the static ISBN catalog.

Usage: python tools/import_taiwan_books.py official1.csv [official2.csv ...]
The source files are published under Taiwan's Open Government Data License v1.
"""
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "taiwan-books.json"
FIELDS = {
    "isbn": ("ISBN", "ISBN (020$a$c)", "ISBN (020$a)", "國際標準書號", "國際標準書號(ISBN)"),
    "title": ("申請書名", "書名", "題名", "書名 (245$a$b)", "書名 (245$a$d)", "書名/題名", "title"),
    "author": ("作者", "著者", "編著者 (245$c)", "author"),
    "publisher": ("出版機構", "出版社", "出版者", "出版項", "出版項 (264)", "出版項 (260)", "publisher"),
    "date": ("預訂出版日", "出版日期", "出版年", "出版年 (008/07-10)", "出版年份", "date", "year"),
}
def field(row, names):
    norm = {str(k).strip().lower().replace(" ", ""): v for k,v in row.items() if k}
    for name in names:
        v = norm.get(name.strip().lower().replace(" ", ""))
        if v:
            return str(v).replace("\x1e", "").strip()
    return ""

def isbn_values(raw):
    # Handles ISBN in brackets, multiple ISBNs, and ISBN-10 (including X).
    for chunk in re.findall(r"(?<![0-9])(?:97[89][0-9 \-]{10,20}|[0-9][0-9 \-]{8,16}[0-9Xx])(?![0-9])", raw):
        digits = re.sub(r"[^0-9Xx]", "", chunk).upper()
        if len(digits) == 10:
            if sum((10-i)*(10 if n=="X" else int(n)) for i,n in enumerate(digits)) % 11:
                continue
            stem = "978" + digits[:9]
            chk = (10-sum(int(n)*(1 if i%2==0 else 3) for i,n in enumerate(stem))%10)%10
            digits = stem+str(chk)
        if len(digits) != 13 or not digits.startswith(("978","979")):
            continue
        if sum(int(n)*(1 if i%2==0 else 3) for i,n in enumerate(digits))%10:
            continue
        yield digits

def parse_publisher(raw):
    # NBINet MARC publication statements look like "[臺北市] : 某某出版, 2024".
    match = re.search(r":\s*([^,;，；]+)", raw)
    return match.group(1).strip(" []/") if match else raw.rstrip(" /;")

def has_chinese(s):
    return bool(re.search(r"[\u3400-\u9fff]", s or ""))

def import_file(path, books):
    for encoding in ("utf-8-sig", "cp950", "utf-16"):
        try:
            with path.open(encoding=encoding, newline="") as f:
                rows=list(csv.DictReader(f))
            break
        except UnicodeError:
            continue
    else:
        raise ValueError(f"Unsupported CSV encoding: {path}")
    if not rows or not any(field(r,FIELDS["isbn"]) for r in rows[:50]):
        raise ValueError(f"Cannot identify ISBN column: {path}")
    new=updated=0
    for row in rows:
        title=field(row,FIELDS["title"]).rstrip(" /;")
        if not title: continue
        author=field(row,FIELDS["author"]).rstrip(" /;")
        publisher=parse_publisher(field(row,FIELDS["publisher"]))
        pubdate=field(row,FIELDS["date"])
        for isbn in set(isbn_values(field(row,FIELDS["isbn"]))):
            incoming={"title":title,"author":author,"publisher":publisher,"date":pubdate}
            old=books.get(isbn)
            if not old:
                books[isbn]=incoming
                new+=1
            elif has_chinese(title) and not has_chinese(old.get("title","")):
                books[isbn]=incoming
                updated+=1
            else:
                # Preserve existing edition-specific metadata, filling only blanks.
                for k in ("author","publisher","date"):
                    if not old.get(k) and incoming[k]:
                        old[k]=incoming[k]
    return new,updated

def main():
    if len(sys.argv)<2: raise SystemExit(__doc__)
    data=json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {"books":{}}
    books=data.setdefault("books",{})
    for name in sys.argv[1:]:
        path=Path(name)
        new,updated=import_file(path,books)
        print(f"{path.name}: +{new} ISBN, {updated} improved Chinese titles")
    data["source"]="Taiwan National Central Library (NCL) / NBINet open bibliographic datasets; https://data.gov.tw/dataset/7502, /27311, /6730"
    data["license"]="Taiwan Open Government Data License, version 1.0; https://data.gov.tw/license"
    data["updatedAt"]=date.today().isoformat()
    OUT.write_text(json.dumps(data,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    print(f"Total unique ISBN-13 records: {len(books)}")
if __name__=="__main__":main()
