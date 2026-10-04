# 倫倫的圖書館

純前端 ISBN 掃描與家庭藏書管理網站。資料保存在瀏覽器 localStorage，可匯出／匯入 JSON 備份。

## ISBN 查詢順序

1. Google Books（公開查詢）
2. Open Library（公開查詢）
3. 本地台灣書目索引 `data/taiwan-books.json`

目前台灣書目索引**僅建立空白結構，尚未匯入官方資料**；沒有書目時會要求手動填寫。切勿將尚未確認的書目資料當成查詢結果。

## 匯入官方台灣書目 CSV

取得國家圖書館或 NBINet **授權允許再利用**的 CSV 後，在專案根目錄執行：

```bash
python tools/import_taiwan_books.py path/to/official.csv
```

匯入器支援 UTF-8 BOM／CP950、常見的 ISBN／書名／作者／出版社／出版日期欄名，並驗證 ISBN-13 校驗碼。請先檢查來源欄位與授權條款；匯入後確認 `data/taiwan-books.json` 的書目品質，再 commit 與部署。

官方入口：
- https://isbn.ncl.edu.tw/NEW_ISBNNet/index.php
- https://data.gov.tw/

注意：GitHub Pages 不支援直接以伺服器程式即時抓取國圖網站。這個方案是將獲准再利用的 CSV 預先整理成 JSON，提供前端靜態查詢。更新 CSV 後須重新匯入並部署。

## Authentication

沒有使用者登入、API 金鑰或 Token。藏書儲存在本機瀏覽器，不會跨裝置同步。請定期匯出備份。
