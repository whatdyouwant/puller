import googlemaps
import time
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd  # 新增



# 1. 初始化 Google Maps 客户端
API_KEY = "AIzaSyBFmmKXcEqEwrrwvKCUwuYyoJRWTkbdfEs"  # 替换成你自己的 Google API Key
gmaps = googlemaps.Client(key=API_KEY)

def search_places(query, location, radius=5000):
    """搜索商家"""
    places = []
    response = gmaps.places_nearby(location=location, radius=radius, keyword=query)

    while True:
        places.extend(response.get("results", []))
        next_page_token = response.get("next_page_token")
        if not next_page_token:
            break
        time.sleep(2)  # 等待 token 生效
        response = gmaps.places_nearby(page_token=next_page_token)
    return places

def get_place_details(place_id):
    """获取商家详细信息"""
    fields = ["name", "formatted_address", "formatted_phone_number", "website"]
    response = gmaps.place(place_id=place_id, fields=fields)
    return response.get("result", {})

def extract_emails_from_website(url):
    """从官网页面提取邮箱"""
    if not url:
        return []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # 用正则匹配邮箱
        emails = set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", soup.get_text()))
        return list(emails)
    except Exception as e:
        print(f"⚠️ 无法访问 {url}: {e}")
        return []

if __name__ == "__main__":
    # 2. 设置多个迪拜的经纬度坐标，覆盖更大范围
    locations = [
        (25.276987, 55.296249),  # 市中心
        (25.204849, 55.270783),  # 迪拜老城区
        (25.197197, 55.274376),  # 迪拜码头附近
        (25.112222, 55.138889),  # 朱美拉
        (25.253174, 55.365673),  # 商业湾
    ]

    # 3. 多个关键词
    keywords = [
        "advertising agency",
        "marketing agency",
        "digital agency",
        "creative agency",
        "media agency",
        "branding agency",
        "广告公司",
        "市场营销公司"
    ]

    all_places = {}
    for loc in locations:
        for kw in keywords:
            print(f"搜索: {kw} @ {loc}")
            results = search_places(kw, loc, radius=10000)
            for place in results:
                pid = place["place_id"]
                all_places[pid] = place  # 用 place_id 去重

    data = []
    for pid, place in all_places.items():
        details = get_place_details(pid)
        name = details.get("name")
        addr = details.get("formatted_address")
        phone = details.get("formatted_phone_number")
        website = details.get("website")
        emails = extract_emails_from_website(website)
        data.append({
            "公司名": name,
            "地址": addr,
            "电话": phone,
            "官网": website,
            "邮箱": ", ".join(emails) if emails else "未找到"
        })
        print("公司名:", name)
        print("地址:", addr)
        print("电话:", phone)
        print("官网:", website)
        print("邮箱:", ", ".join(emails) if emails else "未找到")
        print("-" * 60)

    # 保存到 Excel
    df = pd.DataFrame(data)
    df.to_excel("dubai_agencies.xlsx", index=False)
