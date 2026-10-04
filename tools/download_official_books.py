#!/usr/bin/env python3
"""Download current official NCL open-data CSVs, then merge using import_taiwan_books.py.
Source links verified against https://data.gov.tw/dataset/6730,
/dataset/27311 and /dataset/7502 on 2026-10-04.
"""
import pathlib
import subprocess
import sys
import tempfile
import urllib.request

ROOT=pathlib.Path(__file__).resolve().parents[1]
MONTHLY_BASE="https://isbn.ncl.edu.tw/NEW_ISBNNet/opendata/"
SOURCES=[
    ("ncl-2024-annual.csv","https://www.ncl.edu.tw/OpenDataFile/0Q160688598693591195/1bcea559-39ad-4e31-a881-b241a9b8fdee"),
    ("nbinet-2026-q2.csv","https://www.ncl.edu.tw/OpenDataFile/0Q155002975285157159/a3de23b3-e48c-4cd9-bb2c-374de4abecde"),
    *[(f"new-isbn-{month}.csv",MONTHLY_BASE+month+"_isbn.csv") for month in
      ("202506","202507","202508","202509","202510","202511","202512",
       "202601","202602","202603","202604")],
    ("new-isbn-202605.csv","https://www.ncl.edu.tw/OpenDataFile/0Q169585372033888603/90706411-13fd-4bfc-b3f1-ba83142a243c"),
    ("new-isbn-202606.csv","https://www.ncl.edu.tw/OpenDataFile/0Q169585372033888603/e7328d32-8d7b-4bef-8f0a-b9f53cb50aa8"),
]

def main():
    with tempfile.TemporaryDirectory() as tmp:
        files=[]
        failures=[]
        for filename,url in SOURCES:
            path=pathlib.Path(tmp)/filename
            try:
                req=urllib.request.Request(url,headers={"User-Agent":"eliot-library/1.0 (public bibliographic dataset importer)"})
                with urllib.request.urlopen(req,timeout=50) as response, path.open("wb") as dest:
                    while True:
                        chunk=response.read(1024*1024)
                        if not chunk:break
                        dest.write(chunk)
                        if dest.tell()>70*1024*1024:raise ValueError("Dataset too large")
                if path.stat().st_size<100:raise ValueError("Empty or invalid download")
                files.append(str(path))
                print(f"OK: {filename} ({path.stat().st_size:,} bytes)",flush=True)
            except Exception as error:
                failures.append(filename)
                print(f"WARNING: {filename}: {error}",file=sys.stderr,flush=True)
        if not files:
            raise SystemExit("All official downloads failed; existing catalog unchanged")
        # Individual invalid datasets are rejected without corrupting the existing catalog.
        successful=0
        for filename in files:
            result=subprocess.run(
                [sys.executable,str(ROOT/"tools/import_taiwan_books.py"),filename],
                text=True,capture_output=True)
            if result.returncode:
                print(f"WARNING: Cannot parse {pathlib.Path(filename).name}: {result.stderr}",file=sys.stderr)
                failures.append(pathlib.Path(filename).name)
            else:
                successful+=1
                print(result.stdout,flush=True)
        if not successful:
            raise SystemExit("No CSV could be imported; catalog unchanged")
        print(f"Imported {successful}/{len(SOURCES)} official datasets")
        if failures:
            print("Sources requiring recheck:",", ".join(failures))

if __name__=="__main__":
    main()
