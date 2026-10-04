# 倫倫的圖書館

純前端家庭藏書管理網站，支援掃描 ISBN-13、輸入 ISBN-10/13。藏書保存在瀏覽器 localStorage；請定期匯出 JSON 備份。

## ISBN 查詢順序

1. 經核對的繁體中文補充書目：`data/book-corrections.json`
2. 國家圖書館／NBINet 官方書目：`data/taiwan-books.json`
3. Google Books（優先補封面，不覆蓋已有中文書目）
4. Open Library（備援）

手動新增的藏書不會自動上傳至 GitHub 共用資料庫。

## 自動擴充台灣官方資料

GitHub Actions：[`Update Taiwan book catalog`](https://github.com/niy0115/eliot-library/actions/workflows/update-taiwan-books.yml)。

- 匯入國圖 2024 年度新增書目、NBINet 2026 年第 2 季，以及國圖 2025 年 6 月至 2026 年 6 月每月新書預告資料。
- 執行 `tools/download_official_books.py` 下載資料，再以 `tools/import_taiwan_books.py` 去重並合併至 `data/taiwan-books.json`。
- 每月 8 日自動檢查，也能到 Actions 頁面選擇 **Run workflow** 手動執行；更新匯入程式也會觸發。
- 部分官網下載失敗時保留原書目、不刪除資料，並在 Actions 日誌列出警告。若所有來源失敗，任務不會覆蓋資料庫。
- 月報目前使用官方下載頁面已列出的 2025/06～2026/06 檔案；未來新月份發布後，需更新下載清單。

若你已下載其他年度／月份的授權 CSV，可直接執行：

```bash
python tools/import_taiwan_books.py path/to/official.csv
```

資料來源及授權（政府資料開放授權條款第 1 版）：
- [NBINet 圖書聯合目錄](https://data.gov.tw/dataset/7502)
- [國家圖書館館藏書目](https://data.gov.tw/dataset/27311)
- [臺灣出版新書預告書訊](https://data.gov.tw/dataset/6730)
- [政府資料開放授權條款](https://data.gov.tw/license)

網站仍為 GitHub Pages 靜態網站，不需要書目查詢 API 金鑰或後端服務。大量資料需先於 GitHub Actions 轉成 JSON，手機只負責讀取索引。

## Authentication

無登入、API 金鑰或 Token。藏書保存在同一瀏覽器，不會跨裝置同步。
