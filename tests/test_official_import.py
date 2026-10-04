import csv
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"tools"))
from import_taiwan_books import import_file,isbn_values

class OfficialBookImportTests(unittest.TestCase):
    def test_isbn_13(self):
        self.assertEqual(list(isbn_values("9786269813575")),["9786269813575"])
        self.assertEqual(list(isbn_values("9789573330752")),["9789573330752"])
        self.assertEqual(list(isbn_values("9786269813576")),[])

    def test_multiple_and_isbn10(self):
        self.assertEqual(set(isbn_values("9786269813575 ; 9789573330752")),
                         {"9786269813575","9789573330752"})
        self.assertEqual(list(isbn_values("0-306-40615-2")),["9780306406157"])

    def test_official_monthly_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=pathlib.Path(tmp)/"monthly.csv"
            with path.open("w",newline="",encoding="utf-8-sig") as f:
                writer=csv.DictWriter(f,fieldnames=["ISBN","申請書名","作者","出版機構","預訂出版日"])
                writer.writeheader()
                writer.writerow({"ISBN":"9786269813575","申請書名":"測試中文書名",
                                 "作者":"測試作者","出版機構":"測試出版社","預訂出版日":"2024-11-27"})
            books={}
            self.assertEqual(import_file(path,books),(1,0))
            self.assertEqual(books["9786269813575"]["title"],"測試中文書名")
            self.assertEqual(books["9786269813575"]["publisher"],"測試出版社")

    def test_nbinet_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=pathlib.Path(tmp)/"nbi.csv"
            with path.open("w",newline="",encoding="utf-8-sig") as f:
                writer=csv.DictWriter(f,fieldnames=["ISBN (020$a$c)","書名 (245$a$b)",
                    "編著者 (245$c)","出版項 (264)","出版年 (008/07-10)"])
                writer.writeheader()
                writer.writerow({"ISBN (020$a$c)":"9789573330752",
                    "書名 (245$a$b)":"24個比利 /","編著者 (245$c)":"丹尼爾．凱斯",
                    "出版項 (264)":"臺北市 : 皇冠文化, 2014","出版年 (008/07-10)":"2014"})
            books={}
            self.assertEqual(import_file(path,books),(1,0))
            self.assertEqual(books["9789573330752"]["publisher"],"皇冠文化")

if __name__=="__main__":unittest.main()
