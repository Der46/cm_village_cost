import json
import re
from bs4 import BeautifulSoup
import requests

# 目標網址與輸出設定
URL = "https://thenerdstash.com/coin-master-all-village-list-and-their-build-cost/"
OUTPUT_FILE = "coin_master_village_cost.json"
DEBUG_HTML_FILE = "debug_response.html"


def clean_text(text: str) -> str:
    """清理換行、不斷行空白與前後多餘空白。"""
    if not text:
        return ""
    text = text.replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def parse_total_coins(cost_text: str) -> int:
    """將成本字串（包含 million, billion, trillion, quadrillion）轉成純數值金幣。"""
    text = clean_text(cost_text).lower().replace(",", "")

    match = re.search(r"([\d.]+)\s*(million|billion|trillion|quadrillion)", text)
    if not match:
        return 0

    number = float(match.group(1))
    unit = match.group(2)

    multiplier = {
        "million": 1_000_000,
        "billion": 1_000_000_000,
        "trillion": 1_000_000_000_000,
        "quadrillion": 1_000_000_000_000_000,  # 支援千兆單位
    }.get(unit, 1)

    return int(number * multiplier)


def format_chinese_cost(total_coins: int) -> str:
    """將金幣數值轉成中文簡潔單位（萬、億、兆、千兆）。"""
    if total_coins >= 1_000_000_000_000_000:
        value = total_coins / 1_000_000_000_000_000
        unit = "千兆"
    elif total_coins >= 1_000_000_000_000:
        value = total_coins / 1_000_000_000_000
        unit = "兆"
    elif total_coins >= 100_000_000:
        value = total_coins / 100_000_000
        unit = "億"
    elif total_coins >= 10_000:
        value = total_coins / 10_000
        unit = "萬"
    else:
        return f"{total_coins}金幣"

    value_text = (
        str(int(value))
        if value.is_integer()
        else f"{value:.4f}".rstrip("0").rstrip(".")
    )
    return f"{value_text}{unit}金幣"


def scrape():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # 定位包含文章表格的元素
    table = soup.select_one("figure.wp-block-table table")

    if not table:
        with open(DEBUG_HTML_FILE, "w", encoding="utf-8") as f:
            f.write(response.text)
        raise RuntimeError(
            f"找不到目標表格，已輸出 HTML 檔案至 {DEBUG_HTML_FILE} 供檢查。"
        )

    # 取得資料列（略過 thead）
    rows = (
        table.select("tbody tr")
        if table.select_one("tbody")
        else table.select("tr")
    )
    data = []

    for row in rows:
        cells = row.select("td")
        if len(cells) < 3:
            continue

        level_raw = clean_text(cells[0].get_text())
        name = clean_text(cells[1].get_text())
        cost_raw = clean_text(cells[2].get_text())

        # 表頭防呆過濾
        if not level_raw.isdigit():
            continue

        level = int(level_raw)
        total_coins = parse_total_coins(cost_raw)
        chinese_cost = format_chinese_cost(total_coins)

        data.append(
            {
                "Village Level": level,
                "Village Name": name,
                "Village Cost": cost_raw,
                "總金幣數值": total_coins,
                "中文換算": chinese_cost,
            }
        )

    return data


def main():
    results = scrape()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("前 5 筆預覽：")
    print(json.dumps(results[:5], ensure_ascii=False, indent=2))
    print(f"\n爬取完成，共計 {len(results)} 個村莊資料。")
    print(f"檔案已儲存至：{OUTPUT_FILE}")


if __name__ == "__main__":
    main()
