# Trunking-Ordering

線槽訂貨靜態網站。開啟倉庫根目錄的 `index.html`。

配件目錄、尺寸與型號計算都在這個頁面裡，沒有另外的後端。`_build.py` 與 `_ui.html` 只保留為產生頁面的來源，網站不會執行它們。

GitHub Pages 以倉庫根目錄發佈，並用 `.nojekyll` 略過 Jekyll，讓 `index.html`、圖示、`manifest.webmanifest`、目錄 PDF，以及底線開頭的來源檔案按原檔提供。
