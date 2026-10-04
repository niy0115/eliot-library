#!/usr/bin/env python3
"""Build small static ISBN-prefix files from the full official catalog.

The source catalog remains available for importing future official CSVs.
The website downloads manifest.json and only the matching ISBN-prefix file.
"""
import json
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"data"/"taiwan-books.json"
DEST=ROOT/"data"/"taiwan-shards"
PREFIX_LENGTH=6

def split_catalog(catalog_path=CATALOG, output_dir=DEST, prefix_length=PREFIX_LENGTH):
    catalog=json.loads(Path(catalog_path).read_text(encoding="utf-8"))
    books=catalog.get("books",{})
    shards={}
    for isbn,book in books.items():
        if len(isbn)!=13 or not isbn.isdigit() or not isbn.startswith(("978","979")):
            continue
        prefix=isbn[:prefix_length]
        shards.setdefault(prefix,{})[isbn]=book
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    # Generate all new files first, then remove obsolete shards.
    generated=set()
    for prefix,entries in sorted(shards.items()):
        output=output_dir/(prefix+".json")
        output.write_text(json.dumps({"books":entries},ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
        generated.add(output.name)
    manifest={"prefixLength":prefix_length,"prefixes":sorted(shards),
              "updatedAt":catalog.get("updatedAt"),"bookCount":sum(map(len,shards.values()))}
    (output_dir/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    for old in output_dir.glob("*.json"):
        if old.name!="manifest.json" and old.name not in generated:
            old.unlink()
    print(f"Created {len(shards)} ISBN-prefix shards for {manifest['bookCount']} books")
    return manifest

if __name__=="__main__":
    split_catalog()
