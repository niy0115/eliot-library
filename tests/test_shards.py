import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"tools"))
from split_taiwan_books import split_catalog

class TaiwanShardTests(unittest.TestCase):
    def test_split_and_lookup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            catalog=root/"books.json"
            catalog.write_text(json.dumps({"updatedAt":"2026-10-04","books":{
                "9786269813575":{"title":"中文童書"},
                "9789573330752":{"title":"24個比利"},
                "9786267063859":{"title":"東海岸十六夜"}}}),encoding="utf-8")
            dest=root/"shards"
            manifest=split_catalog(catalog,dest)
            self.assertEqual(manifest["prefixLength"],6)
            self.assertEqual(manifest["bookCount"],3)
            self.assertEqual(manifest["prefixes"],["978626","978957"])
            match=json.loads((dest/"978626.json").read_text(encoding="utf-8"))
            self.assertEqual(match["books"]["9786269813575"]["title"],"中文童書")
            self.assertNotIn("9789573330752",match["books"])
            self.assertEqual(json.loads((dest/"manifest.json").read_text(encoding="utf-8")),manifest)
            catalog.write_text(json.dumps({"books":{"9789573330752":{"title":"24個比利"}}}),encoding="utf-8")
            split_catalog(catalog,dest)
            self.assertFalse((dest/"978626.json").exists())
if __name__=="__main__":
    unittest.main()
