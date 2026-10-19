import concurrent.futures
import re
import requests

# ----------------- 频道配置 -----------------
# 需排除的广东频道关键词
GUANGDONG_EXCLUDES = ["广东影视", "4K", "4k", "广东少儿", "嘉佳卡通", "南方购物"]

# 公开台标基础库链接 (Fanmingming live logo 库)
LOGO_BASE = "https://raw.githubusercontent.com/fanmingming/live/main/tv/"

# 频道定义与分类
# CCTV 频道使用精准正则模式 (regex_pattern) 解决 CCTV1 匹配到 CCTV10-17 的问题
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



def check_stream_validity(url, timeout=4):
    """验证流有效性：防范返回 HTML 错误提示页的伪 200"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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


def fetch_upstream_m3u():
    """并发下载上游公开 M3U 源文件"""
    all_lines = []
    
    def fetch_one(source):
        try:
            resp = requests.get(source, timeout=8)
            if resp.status_code == 200:
                return resp.text.splitlines()
        except Exception:
            pass
        return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_one, UPSTREAM_SOURCES)
        for lines in results:
            all_lines.extend(lines)
            
    return all_lines


def parse_m3u(lines):
    """解析 M3U 内容，提取频道标题与链接"""
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
            
    return stream_map


def find_candidate_urls(ch_config, stream_map):
    """精准查找频道的候选 URL"""
    candidates = []
    
    # 优先处理正则（如 CCTV 频道，解决 CCTV1 匹配到 CCTV10-17 问题）
    if "regex" in ch_config:
        pattern = re.compile(ch_config["regex"], re.IGNORECASE)
        for item in stream_map:
            title = item["title"].replace(" ", "")
            if pattern.search(title):
                candidates.append(item["url"])
    # 其次使用别名列表匹配
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
    print("正在抓取上游直播源...")
    upstream_lines = fetch_upstream_m3u()
    stream_map = parse_m3u(upstream_lines)
    print(f"共解析得到 {len(stream_map)} 个备选频道流链接")

    m3u_content = [
        '#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml"'
    ]

    for group_info in CHANNEL_CONFIGS:
        group_name = group_info["group"]
        print(f"\n--- 处理分类: {group_name} ---")
        
        for ch in group_info["channels"]:
            ch_name = ch["name"]
            ch_logo = ch["logo"]

            # 过滤广东频道排除名单
            if group_name == "广东频道" and any(ex in ch_name for ex in GUANGDONG_EXCLUDES):
                print(f"[SKIP] {ch_name} (在排除名单中)")
                continue

            # 精准获取候选 URL
            candidate_urls = find_candidate_urls(ch, stream_map)

            # 测速验证
            valid_url = None
            if candidate_urls:
                with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                    future_to_url = {
                        executor.submit(check_stream_validity, url): url
                        for url in candidate_urls[:8]
                    }
                    for future in concurrent.futures.as_completed(future_to_url):
                        url = future_to_url[future]
                        if future.result():
                            valid_url = url
                            break

            if valid_url:
                extinf = f'#EXTINF:-1 tvg-name="{ch_name}" tvg-logo="{ch_logo}" group-title="{group_name}",{ch_name}'
                m3u_content.append(extinf)
                m3u_content.append(valid_url)
                print(f"[✓ SUCCESS] {ch_name} (成功找到有效源)")
            else:
                print(f"[✗ FAIL] {ch_name} (未找到有效源)")

    # 输出保存
    with open("iptv.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_content))
    print("\n✅ iptv.m3u 文件更新完成！")


if __name__ == "__main__":
    main()
