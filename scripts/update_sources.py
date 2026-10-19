import concurrent.futures
import re
import requests

# ----------------- 频道配置 -----------------
# 需排除的广东频道关键词
GUANGDONG_EXCLUDES = ["广东影视", "4K", "4k", "广东少儿", "嘉佳卡通", "南方购物"]

# 公开台标基础库链接 (Fanmingming live logo 库)
LOGO_BASE = "https://raw.githubusercontent.com/fanmingming/live/main/tv/"

# 频道定义与分类，`aliases` 为用于匹配上游源的各种可能名称/关键字
CHANNEL_CONFIGS = [
    {
        "group": "央视频道",
        "channels": [
            {"name": "CCTV-1 综合", "aliases": ["CCTV1", "CCTV-1", "CCTV1综合", "CCTV-1综合"], "logo": f"{LOGO_BASE}CCTV1.png"},
            {"name": "CCTV-2 财经", "aliases": ["CCTV2", "CCTV-2", "CCTV2财经"], "logo": f"{LOGO_BASE}CCTV2.png"},
            {"name": "CCTV-3 综艺", "aliases": ["CCTV3", "CCTV-3", "CCTV3综艺"], "logo": f"{LOGO_BASE}CCTV3.png"},
            {"name": "CCTV-4 中文国际", "aliases": ["CCTV4", "CCTV-4", "CCTV4中文国际"], "logo": f"{LOGO_BASE}CCTV4.png"},
            {"name": "CCTV-5 体育", "aliases": ["CCTV5", "CCTV-5", "CCTV5体育"], "logo": f"{LOGO_BASE}CCTV5.png"},
            {"name": "CCTV-5+ 体育赛事", "aliases": ["CCTV5+", "CCTV-5+", "CCTV5+体育赛事"], "logo": f"{LOGO_BASE}CCTV5+.png"},
            {"name": "CCTV-6 电影", "aliases": ["CCTV6", "CCTV-6", "CCTV6电影"], "logo": f"{LOGO_BASE}CCTV6.png"},
            {"name": "CCTV-7 国防军事", "aliases": ["CCTV7", "CCTV-7", "CCTV7国防军事"], "logo": f"{LOGO_BASE}CCTV7.png"},
            {"name": "CCTV-8 电视剧", "aliases": ["CCTV8", "CCTV-8", "CCTV8电视剧"], "logo": f"{LOGO_BASE}CCTV8.png"},
            {"name": "CCTV-9 纪录", "aliases": ["CCTV9", "CCTV-9", "CCTV9纪录"], "logo": f"{LOGO_BASE}CCTV9.png"},
            {"name": "CCTV-10 科教", "aliases": ["CCTV10", "CCTV-10", "CCTV10科教"], "logo": f"{LOGO_BASE}CCTV10.png"},
            {"name": "CCTV-11 戏曲", "aliases": ["CCTV11", "CCTV-11", "CCTV11戏曲"], "logo": f"{LOGO_BASE}CCTV11.png"},
            {"name": "CCTV-12 社会与法", "aliases": ["CCTV12", "CCTV-12", "CCTV12社会与法"], "logo": f"{LOGO_BASE}CCTV12.png"},
            {"name": "CCTV-13 新闻", "aliases": ["CCTV13", "CCTV-13", "CCTV13新闻"], "logo": f"{LOGO_BASE}CCTV13.png"},
            {"name": "CCTV-14 少儿", "aliases": ["CCTV14", "CCTV-14", "CCTV14少儿"], "logo": f"{LOGO_BASE}CCTV14.png"},
            {"name": "CCTV-15 音乐", "aliases": ["CCTV15", "CCTV-15", "CCTV15音乐"], "logo": f"{LOGO_BASE}CCTV15.png"},
            {"name": "CCTV-16 奥林匹克", "aliases": ["CCTV16", "CCTV-16", "CCTV16奥林匹克"], "logo": f"{LOGO_BASE}CCTV16.png"},
            {"name": "CCTV-17 农业农村", "aliases": ["CCTV17", "CCTV-17", "CCTV17农业农村"], "logo": f"{LOGO_BASE}CCTV17.png"},
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
]


def check_stream_validity(url, timeout=4):
    """验证 HTTP/HLS 流连接有效性"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        # 尝试用 GET 获取一小段响应
        response = requests.get(url, headers=headers, stream=True, timeout=timeout, verify=False)
        if response.status_code in [200, 206, 301, 302]:
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
        except Exception as e:
            print(f"下载失败: {source}")
        return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_one, UPSTREAM_SOURCES)
        for lines in results:
            all_lines.extend(lines)
            
    return all_lines


def parse_m3u(lines):
    """解析 M3U 内容，按频道全名/名称关键字映射 URL 列表"""
    stream_map = [] # 存储字典 [{"name": raw_title, "url": stream_url}]
    current_name = None

    for line in lines:
        line = line.strip()
        if line.startswith("#EXTINF"):
            # 优先提取 tvg-name，其次提取标号后面的名称
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


def find_candidate_urls(aliases, stream_map):
    """根据别名在抓取到的流中匹配链接"""
    candidates = []
    for item in stream_map:
        title = item["title"].upper().replace(" ", "")
        for alias in aliases:
            clean_alias = alias.upper().replace(" ", "")
            # 精确包含或匹配
            if clean_alias in title or title in clean_alias:
                candidates.append(item["url"])
                break
    # 保持顺序去重
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
            ch_aliases = ch.get("aliases", [ch_name])
            ch_logo = ch["logo"]

            # 过滤排除名单
            if group_name == "广东频道" and any(ex in ch_name for ex in GUANGDONG_EXCLUDES):
                print(f"[SKIP] {ch_name} (在排除名单中)")
                continue

            # 获取该频道的所有候选 URL
            candidate_urls = find_candidate_urls(ch_aliases, stream_map)

            # 测速/有效性判断 (取前 8 个候选源测试)
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
                print(f"[✓ SUCCESS] {ch_name} (找到有效源)")
            else:
                print(f"[✗ FAIL] {ch_name} (未查找到有效源)")

    # 导出文件
    with open("iptv.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_content))
    print("\n✅ iptv.m3u 文件更新完成！")


if __name__ == "__main__":
    main()
