import re
import json
import requests
from bs4 import BeautifulSoup


URL = "https://www.pockettactics.com/coin-master/village-cost"
OUTPUT_FILE = "coin_master_village_cost.json"
DEBUG_HTML_FILE = "debug_response.html"


WORD_TO_NUMBER = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def clean_text(text: str) -> str:
    """清理換行、不斷行空白與多餘空白。"""
    if text is None:
        return ""
    text = text.replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def parse_level(text: str) -> int | None:
    """
    將 Village level 轉成整數。
    例如：
    - One -> 1
    - Two -> 2
    - 11 -> 11
    """
    text = clean_text(text).lower()

    if text.isdigit():
        return int(text)

    return WORD_TO_NUMBER.get(text)


def parse_total_coins(cost_text: str) -> int:
    """
    將英文成本轉成數字金幣。

    範例：
    - 3.1 million coins -> 3100000
    - 0.9 billion coins -> 900000000
    - 1,728.7 trillion coins -> 1728700000000000
    """
    text = clean_text(cost_text).lower()
    text = text.replace(",", "")

    match = re.search(r"([\d.]+)\s*(million|billion|trillion)", text)
    if not match:
        return 0

    number = float(match.group(1))
    unit = match.group(2)

    multiplier = {
        "million": 1_000_000,
        "billion": 1_000_000_000,
        "trillion": 1_000_000_000_000,
    }[unit]

    return int(number * multiplier)


def format_chinese_cost(total_coins: int) -> str:
    """
    將總金幣轉成中文單位。
    """
    if total_coins >= 1_000_000_000_000:
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

    if value.is_integer():
        value_text = str(int(value))
    else:
        value_text = f"{value:.4f}".rstrip("0").rstrip(".")

    return f"{value_text}{unit}金幣"


def find_target_table(soup: BeautifulSoup):
    """
    自動尋找包含 Coin Master village cost 資料的表格。

    不再依賴 #table_0，因為該 id 可能在 requests 抓到的 HTML 裡不存在。
    """
    tables = soup.select("table")

    for table in tables:
        table_text = clean_text(table.get_text(" ", strip=True)).lower()

        has_level = "village level" in table_text
        has_name = "coin master village name" in table_text
        has_cost = "coin master village cost" in table_text

        if has_level and has_name and has_cost:
            return table

    return None


def scrape():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()

    html = response.text

    # 存一份 debug HTML，方便出錯時檢查網站到底回了什麼
    with open(DEBUG_HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")

    table = find_target_table(soup)

    if not table:
        title = soup.title.get_text(strip=True) if soup.title else "無 title"
        raise RuntimeError(
            "找不到 Coin Master village cost 表格。\n"
            f"HTTP 狀態碼：{response.status_code}\n"
            f"頁面 title：{title}\n"
            f"已將回應 HTML 存成：{DEBUG_HTML_FILE}\n"
            "請打開 debug_response.html 檢查是否被導到反爬頁、驗證頁或不同版本頁面。"
        )

    tbody = table.select_one("tbody")
    rows = tbody.select("tr") if tbody else table.select("tr")

    data = []

    for row in rows:
        cells = row.select("td")

        if len(cells) < 3:
            continue

        level_text = clean_text(cells[0].get_text(" ", strip=True))
        name = clean_text(cells[1].get_text(" ", strip=True))
        original_cost = clean_text(cells[2].get_text(" ", strip=True))

        # 跳過表頭列
        if "village level" in level_text.lower():
            continue

        level = parse_level(level_text)
        if level is None:
            continue

        total_coins = parse_total_coins(original_cost)
        chinese_cost = format_chinese_cost(total_coins)

        item = {
            "編號": level,
            "名稱": name,
            "成本": chinese_cost,
            "總金幣": total_coins,
            "原始成本": original_cost,
        }

        data.append(item)

    return data


def main():
    data = scrape()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(json.dumps(data[:5], ensure_ascii=False, indent=2))
    print(f"\n完成，共抓到 {len(data)} 筆資料")
    print(f"已輸出：{OUTPUT_FILE}")


if __name__ == "__main__":
    main()
