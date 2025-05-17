import requests
import time
from bs4 import BeautifulSoup

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1373114015504400549/UtYx9NA4sWhJry-hddtYxDYT6ko1skLD6Ibpr2PFPsvpXzcRSBZm8-iwHOO1KCUPFF9w"

last_inventory = None

def fetch_inventory():
    url = "https://growagarden.gg/stocks"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"请求失败: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # 这里你需要根据页面实际结构修改解析逻辑
    # 下面示范简单解析，假设种子、商店、gear都在不同id里
    inventory = {
        "EggShop": [],
        "SeedShop": [],
        "GearShop": []
    }

    # 示例：抓取 EggShop 里的蛋名
    egg_section = soup.find(id="egg-shop")
    if egg_section:
        for item in egg_section.find_all(class_="item-name"):
            inventory["EggShop"].append(item.get_text(strip=True))

    seed_section = soup.find(id="seed-shop")
    if seed_section:
        for item in seed_section.find_all(class_="item-name"):
            inventory["SeedShop"].append(item.get_text(strip=True))

    gear_section = soup.find(id="gear-shop")
    if gear_section:
        for item in gear_section.find_all(class_="item-name"):
            inventory["GearShop"].append(item.get_text(strip=True))

    return inventory

def inventory_changed(new_inv):
    global last_inventory
    if last_inventory is None:
        return True
    return new_inv != last_inventory

def send_discord(inventory):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    content = f"🌟 **Grow a Garden 库存更新** \n时间: {now}\n\n"

    for shop, items in inventory.items():
        content += f"**{shop}**:\n"
        if items:
            for i in items:
                content += f"- {i}\n"
        else:
            content += "无数据\n"
        content += "\n"

    data = {"content": content}
    r = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if r.status_code == 204:
        print(f"{now} - 消息发送成功")
    else:
        print(f"{now} - 消息发送失败: {r.status_code} {r.text}")

def main_loop():
    global last_inventory
    while True:
        inv = fetch_inventory()
        if inv:
            if inventory_changed(inv):
                send_discord(inv)
                last_inventory = inv
            else:
                print(f"{time.strftime('%H:%M:%S')} - 库存无变化")
        else:
            print(f"{time.strftime('%H:%M:%S')} - 抓取失败")

        print("等待 3 分钟后重新抓取...")
        time.sleep(180)  # 180秒 = 3分钟

if __name__ == "__main__":
    main_loop()
