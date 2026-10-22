<p align="center">
  <img src="icon.svg" width="128" height="128" alt="村落建造金額計算器 icon" />
</p>

<h1 align="center">村落建造金額計算器</h1>

<p align="center">
  Coin Master 村落建造金額查詢與試算工具 · 純前端、免安裝、手機友善
</p>

---

## 功能

- **可蓋到哪一村**：輸入目前所在村落與身上金幣，計算從現在開始最多能蓋到第幾村，以及距離下一村還差多少。
- **折扣試算**：可選擇 10%～40% off 等建造折扣，即時重新計算。
- **單一村落查詢**：查詢任一村落的建造總金額，並列出各折扣下的金額。
- **多語系**：繁體中文、English、Tiếng Việt、日本語、한국어、ไทย、Bahasa Indonesia、Español、Português。
- **可加入主畫面**：附 SVG / PNG App icon 與 Web App Manifest，可在手機上「加入主畫面」當成 App 使用。

## 檔案結構

| 檔案 | 說明 |
| --- | --- |
| `index.html` | 主頁面（HTML / CSS / JS 皆在同一檔） |
| `villages_cost.json` | 各村落等級、名稱與建造金額資料 |
| `i18n.json` | 多語系翻譯字串 |
| `scrape_coin_master.py` | 從公開網頁抓取村落金額資料的爬蟲 |
| `icon.svg` / `icon-180.png` / `icon-512.png` | App icon |
| `manifest.webmanifest` | PWA manifest |

## 本機執行

頁面會用 `fetch` 讀取 JSON，因此需要透過 HTTP 開啟（直接雙擊 `index.html` 會被瀏覽器擋下）：

```bash
python -m http.server 8000
```

接著開啟 <http://localhost:8000>。

也可以直接部署到 GitHub Pages 或任何靜態網站空間。

## 更新村落資料

```bash
pip install requests beautifulsoup4
python scrape_coin_master.py
```

爬蟲會輸出 `coin_master_village_cost.json`，確認內容無誤後覆蓋 `villages_cost.json` 即可。

每筆資料格式：

```json
{
  "Village Level": 1,
  "Village Name": "Land of Vikings",
  "Village Cost": "3.9 million",
  "總金幣數值": 3900000,
  "中文換算": "390萬金幣"
}
```

## 免責聲明

本專案為非官方的玩家工具，與 Moon Active 及 Coin Master 無任何關聯。數據參考公開網頁與社群整理資料，僅供參考，實際金額請以遊戲內顯示為準。
