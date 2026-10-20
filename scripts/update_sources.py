import concurrent.futures
import os
import re
import requests

# ----------------- 频道配置 -----------------
GUANGDONG_EXCLUDES = ["广东影视", "4K", "4k", "广东少儿", "嘉佳卡通", "南方购物"]
LOGO_BASE = "https://raw.githubusercontent.com/fanmingming/live/main/tv/"

CHANNEL_CONFIGS = [
    {
        "group": "央视频道",
        "channels": [
            {"name": "CCTV-1 综合", "regex": r"^CCTV[-_\s]*1(?!\d)", "logo": f"{LOGO_BASE}CCTV1.png"},
            {"name": "CCTV-2 财经", "regex": r"^CCTV[-_\s]*2(?!\d)", "logo": f"{LOGO_BASE}CCTV2.png"},
            {"name": "CCTV-3 综艺", "regex": r"^CCTV[-_\s]*3(?!\d)", "logo": f"{LOGO_BASE}CCTV3.png"},
            {"name": "CCTV-4 中文国际", "regex": r"^CCTV[-_\s]*4(?!\d)", "logo": f"{LOGO_BASE}CCTV4.png"},
            {"name": "CCTV-5 体育", "regex": r"^CCTV[-_\s]*5(?!\d|\+)", "logo": f"{LOGO_BASE}CCTV5.png"},
            {"name": "CCTV-5+ 体育赛事", "regex": r"^CCTV[-_\s]*5\+", "logo": f"{LOGO_BASE}CCTV5+.png"},
            {"name": "CCTV-6 电影", "regex": r"^CCTV[-_\s]*6(?!\d)", "logo": f"{LOGO_BASE}CCTV6.png"},
            {"name": "CCTV-7 国防军事", "regex": r"^CCTV[-_\s]*7(?!\d)", "logo": f"{LOGO_BASE}CCTV7.png"},
            {"name": "CCTV-8 电视剧", "regex": r"^CCTV[-_\s]*8(?!\d)", "logo": f"{LOGO_BASE}CCTV8.png"},
            {"name": "CCTV-9 纪录", "regex": r"^CCTV[-_\s]*9(?!\d)", "logo": f"{LOGO_BASE}CCTV9.png"},
            {"name": "CCTV-10 科教", "regex": r"^CCTV[-_\s]*10(?!\d)", "logo": f"{LOGO_BASE}CCTV10.png"},
            {"name": "CCTV-11 戏曲", "regex": r"^CCTV[-_\s]*11(?!\d)", "logo": f"{LOGO_BASE}CCTV11.png"},
            {"name": "CCTV-12 社会与法", "regex": r"^CCTV[-_\s]*12(?!\d)", "logo": f"{LOGO_BASE}CCTV12.png"},
            {"name": "CCTV-13 新闻", "regex": r"^CCTV[-_\s]*13(?!\d)", "logo": f"{LOGO_BASE}CCTV13.png"},
            {"name": "CCTV-14 少儿", "regex": r"^CCTV[-_\s]*14(?!\d)", "logo": f"{LOGO_BASE}CCTV14.png"},
            {"name": "CCTV-15 音乐", "regex": r"^CCTV[-_\s]*15(?!\d)", "logo": f"{LOGO_BASE}CCTV15.png"},
            {"name": "CCTV-16 奥林匹克", "regex": r"^CCTV[-_\s]*16(?!\d)", "logo": f"{LOGO_BASE}CCTV16.png"},
            {"name": "CCTV-17 农业农村", "regex": r"^CCTV[-_\s]*17(?!\d)", "logo": f"{LOGO_BASE}CCTV17.png"},
        ],
    },
    {
        "group": "广东频道",
        "channels": [
            {"name": "广东卫视", "aliases": ["广东卫视"], "logo": f"{LOGO_BASE}广东卫视.png"},
            {"name": "大湾区卫视", "aliases": ["大湾区卫视", "南方卫视"], "logo": f"{LOGO_BASE}大湾区卫视.png"},
            {"name": "广东新闻", "aliases": ["广东新闻", "广东新闻频道"], "logo": f"{LOGO_BASE}广东新闻.png"},
            {"name": "广东珠江", "aliases": ["广东珠江", "珠江频道", "广东珠江台"], "logo": f"{LOGO_BASE}广东珠江.png"},
            {"name": "广东体育", "aliases": ["广东体育", "广东体育台"], "logo": f"{LOGO_BASE}广东体育.png"},
            {"name": "广东民生", "aliases": ["广东民生", "广东公共", "民生频道"], "logo": f"{LOGO_BASE}广东民生.png"},
            {"name": "广州综合", "aliases": ["广州综合", "广州综合频道"], "logo": f"{LOGO_BASE}广州综合.png"},
            {"name": "广州影视", "aliases": ["广州影视", "广州影视频道"], "logo": f"{LOGO_BASE}广州影视.png"},
            {"name": "岭南戏曲", "aliases": ["岭南戏曲"], "logo": f"{LOGO_BASE}岭南戏曲.png"},
            {"name": "广东移动", "aliases": ["广东移动", "广东移动频道"], "logo": f"{LOGO_BASE}广东移动.png"},
            {"name": "广东纪录片", "aliases": ["广东纪录", "广东纪录片"], "logo": f"{LOGO_BASE}广东纪录片.png"},
            {"name": "广东健康", "aliases": ["广东健康", "广东健康频道"], "logo": f"{LOGO_BASE}广东健康.png"},
            {"name": "GRTN生活", "aliases": ["GRTN生活", "广东生活", "GRTN生活频道"], "logo": f"{LOGO_BASE}GRTN生活.png"},
        ],
    },
    {
        "group": "無綫電視",
        "channels": [
            {"name": "翡翠台", "aliases": ["翡翠台", "Jade", "TVB翡翠台", "TVB Jade"], "logo": f"{LOGO_BASE}翡翠台.png"},
            {"name": "J2 / TVB Plus", "aliases": ["J2", "TVB Plus", "TVBPlus"], "logo": f"{LOGO_BASE}J2.png"},
            {"name": "無綫新聞台", "aliases": ["無綫新聞台", "无线新闻台", "TVB News", "TVB新闻台"], "logo": f"{LOGO_BASE}無綫新聞台.png"},
            {"name": "明珠台", "aliases": ["明珠台", "Pearl", "TVB Pearl", "TVB明珠台"], "logo": f"{LOGO_BASE}明珠台.png"},
            {"name": "財經體育資訊台", "aliases": ["財經體育資訊台", "财经体育资讯台", "TVB Finance"], "logo": f"{LOGO_BASE}財經體育資訊台.png"},
        ],
    },
    {
        "group": "ViuTV",
        "channels": [
            {"name": "ViuTV", "aliases": ["ViuTV", "ViuTV 99", "CH99 ViuTV", "Viu TV"], "logo": f"{LOGO_BASE}ViuTV.png"},
            {"name": "ViuTVsix", "aliases": ["ViuTVsix", "ViuTVsix 96", "CH96 ViuTVsix", "ViuTV Six"], "logo": f"{LOGO_BASE}ViuTVsix.png"},
        ],
    },
]

# 补充更多覆盖广东台、港台直播源的上游公开库
UPSTREAM_SOURCES = [
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/cn.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/hk.m3u",
    "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u",
    "http://124.71.19.220/c/1",
    "https://raw.githubusercontent.com/zilong7728/Collect-IPTV/refs/heads/main/best_sorted.m3u",
    "https://guovin.github.io/iptv-api/result.m3u",
    "https://raw.githubusercontent.com/vbskycn/iptv/refs/heads/master/tv/iptv4.m3u",
    "https://live.yang-1989.eu.org/Live.m3u",
    "https://raw.githubusercontent.com/suxuang/myIPTV/refs/heads/main/ipv4.m3u",
    "https://raw.githubusercontent.com/CCSH/IPTV/refs/heads/main/live.m3u",
]

def search_github_code_sources():
    token = os.getenv("GH_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
        
    github_urls = []
    queries = [
        "filename:iptv.m3u CCTV1",
        "filename:live.m3u 翡翠台",
        "extension:m3u ViuTV 99",
    ]
    
    print("\n🔍 开始通过 GitHub API 动态检索最新开源直播源代码库...")
    for query in queries:
        try:
            url = f"https://api.github.com/search/code?q={query}&sort=indexed&order=desc"
            resp = requests.get(url, headers=headers, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("items", [])[:3]:
                    raw_url = item.get("html_url", "").replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                    if raw_url and raw_url not in github_urls:
                        github_urls.append(raw_url)
                        print(f"找到 GitHub 代码源: {raw_url}")
        except Exception as e:
            print(f"检索 GitHub 代码失败 (Query: {query}): {e}")
            
    return github_urls

def check_stream_validity(url, timeout=4):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, stream=True, timeout=timeout, verify=False)
        if response.status_code in [200, 206]:
            content_sample = next(response.iter_content(chunk_size=1024), b"").decode("utf-8", errors="ignore").lower()
            if "<html" in content_sample or "<body" in content_sample or "error" in content_sample:
                return False
            return True
    except Exception:
        pass
    return False

def fetch_upstream_m3u(sources):
    all_lines = []
    
    def fetch_one(source):
        try:
            resp = requests.get(source, timeout=8)
            if resp.status_code == 200:
                return resp.text.splitlines()
        except Exception:
            pass
        return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        results = executor.map(fetch_one, sources)
        for lines in results:
            all_lines.extend(lines)
            
    return all_lines

def parse_m3u_and_txt(lines):
    stream_map = []
    current_name = None

    for line in lines:
        line = line.strip()
        if line.startswith("#EXTINF"):
            match = re.search(r'tvg-name="([^"]+)"', line)
            if match:
                current_name = match.group(1).strip()
            else:
                parts = line.split(",")
                if len(parts) > 1:
                    current_name = parts[-1].strip()
        elif line and not line.startswith("#") and current_name:
            stream_map.append({"title": current_name, "url": line})
            current_name = None
        elif "," in line and "://" in line:
            parts = line.split(",")
            if len(parts) == 2:
                stream_map.append({"title": parts[0].strip(), "url": parts[1].strip()})
            
    return stream_map

def find_candidate_urls(ch_config, stream_map):
    candidates = []
    
    if "regex" in ch_config:
        pattern = re.compile(ch_config["regex"], re.IGNORECASE)
        for item in stream_map:
            title = item["title"].replace(" ", "")
            if pattern.search(title):
                candidates.append(item["url"])
    elif "aliases" in ch_config:
        aliases = ch_config["aliases"]
        for item in stream_map:
            title = item["title"].upper().replace(" ", "")
            for alias in aliases:
                clean_alias = alias.upper().replace(" ", "")
                if clean_alias in title or title in clean_alias:
                    candidates.append(item["url"])
                    break

    return list(dict.fromkeys(candidates))

def main():
    github_dynamic_sources = search_github_code_sources()
    all_sources = list(dict.fromkeys(UPSTREAM_SOURCES + github_dynamic_sources))
    
    print(f"\n开始抓取共 {len(all_sources)} 个上游直播源...")
    upstream_lines = fetch_upstream_m3u(all_sources)
    stream_map = parse_m3u_and_txt(upstream_lines)
    print(f"共解析得到 {len(stream_map)} 个备选频道流链接")

    # 准备两份文件的内容容器
    m3u1_content = ['#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml"']  # 方案1：带 线路1, 线路2
    m3u2_content = ['#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml"']  # 方案2：同名聚合，播放器自带换源

    for group_info in CHANNEL_CONFIGS:
        group_name = group_info["group"]
        print(f"\n--- 处理分类: {group_name} ---")
        
        for ch in group_info["channels"]:
            ch_name = ch["name"]
            ch_logo = ch["logo"]

            if group_name == "广东频道" and any(ex in ch_name for ex in GUANGDONG_EXCLUDES):
                print(f"[SKIP] {ch_name} (在排除名单中)")
                continue

            candidate_urls = find_candidate_urls(ch, stream_map)

            valid_urls = []
            if candidate_urls:
                with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                    future_to_url = {
                        executor.submit(check_stream_validity, url): url
                        for url in candidate_urls[:12]
                    }
                    for future in concurrent.futures.as_completed(future_to_url):
                        url = future_to_url[future]
                        if future.result():
                            valid_urls.append(url)
                            if len(valid_urls) >= 4:
                                break

            if valid_urls:
                # 写入方案一 (iptv.m3u: 带线路后缀)
                for idx, v_url in enumerate(valid_urls, start=1):
                    line_name = f"{ch_name} 线路{idx}"
                    extinf1 = f'#EXTINF:-1 tvg-name="{ch_name}" tvg-logo="{ch_logo}" group-title="{group_name}",{line_name}'
                    m3u1_content.append(extinf1)
                    m3u1_content.append(v_url)

                # 写入方案二 (iptv2.m3u: 频道名完全相同，由播放器原生识别为同频道多源)
                for v_url in valid_urls:
                    extinf2 = f'#EXTINF:-1 tvg-name="{ch_name}" tvg-logo="{ch_logo}" group-title="{group_name}",{ch_name}'
                    m3u2_content.append(extinf2)
                    m3u2_content.append(v_url)

                print(f"[✓ SUCCESS] {ch_name} (成功聚合 {len(valid_urls)} 条有效线路)")
            else:
                print(f"[✗ FAIL] {ch_name} (未找到有效源)")

    # 导出文件 1
    with open("iptv.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u1_content))
    
    # 导出文件 2
    with open("iptv2.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u2_content))
        
    print("\n✅ iptv.m3u 和 iptv2.m3u 文件全部生成完毕！")

if __name__ == "__main__":
    main()
