import concurrent.futures
import re
import requests

# ----------------- 频道配置 -----------------
# 需排除的广东频道关键词
GUANGDONG_EXCLUDES = ["广东影视", "4K", "4k", "广东少儿", "嘉佳卡通", "南方购物"]

# 公开台标基础库链接 (使用 Fanmingming live logo 库)
LOGO_BASE = (
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/"
)

# 频道定义与分类
CHANNEL_CONFIGS = [
    # CCTV 频道分类
    {
        "group": "央视频道",
        "channels": [
            {"name": "CCTV-1 综合", "logo": f"{LOGO_BASE}CCTV1.png"},
            {"name": "CCTV-2 财经", "logo": f"{LOGO_BASE}CCTV2.png"},
            {"name": "CCTV-3 综艺", "logo": f"{LOGO_BASE}CCTV3.png"},
            {"name": "CCTV-4 中文国际", "logo": f"{LOGO_BASE}CCTV4.png"},
            {"name": "CCTV-5 体育", "logo": f"{LOGO_BASE}CCTV5.png"},
            {"name": "CCTV-5+ 体育赛事", "logo": f"{LOGO_BASE}CCTV5+.png"},
            {"name": "CCTV-6 电影", "logo": f"{LOGO_BASE}CCTV6.png"},
            {"name": "CCTV-7 国防军事", "logo": f"{LOGO_BASE}CCTV7.png"},
            {"name": "CCTV-8 电视剧", "logo": f"{LOGO_BASE}CCTV8.png"},
            {"name": "CCTV-9 纪录", "logo": f"{LOGO_BASE}CCTV9.png"},
            {"name": "CCTV-10 科教", "logo": f"{LOGO_BASE}CCTV10.png"},
            {"name": "CCTV-11 戏曲", "logo": f"{LOGO_BASE}CCTV11.png"},
            {"name": "CCTV-12 社会与法", "logo": f"{LOGO_BASE}CCTV12.png"},
            {"name": "CCTV-13 新闻", "logo": f"{LOGO_BASE}CCTV13.png"},
            {"name": "CCTV-14 少儿", "logo": f"{LOGO_BASE}CCTV14.png"},
            {"name": "CCTV-15 音乐", "logo": f"{LOGO_BASE}CCTV15.png"},
            {"name": "CCTV-16 奥林匹克", "logo": f"{LOGO_BASE}CCTV16.png"},
            {"name": "CCTV-17 农业农村", "logo": f"{LOGO_BASE}CCTV17.png"},
        ],
    },
# 广东卫视频道分类 (包含新增频道，并过滤排除名单)
    {
        "group": "广东频道",
        "channels": [
            {"name": "广东卫视", "logo": f"{LOGO_BASE}广东卫视.png"},
            {"name": "大湾区卫视", "logo": f"{LOGO_BASE}大湾区卫视.png"},
            {"name": "广东新闻", "logo": f"{LOGO_BASE}广东新闻.png"},
            {"name": "广东珠江", "logo": f"{LOGO_BASE}广东珠江.png"},
            {"name": "广东体育", "logo": f"{LOGO_BASE}广东体育.png"},
            {"name": "广东民生", "logo": f"{LOGO_BASE}广东民生.png"},
            {"name": "广州综合", "logo": f"{LOGO_BASE}广州综合.png"},
            {"name": "广州影视", "logo": f"{LOGO_BASE}广州影视.png"},
            # ---- 新增频道 ----
            {"name": "岭南戏曲", "logo": f"{LOGO_BASE}岭南戏曲.png"},
            {"name": "广东移动", "logo": f"{LOGO_BASE}广东移动.png"},
            {"name": "广东纪录片", "logo": f"{LOGO_BASE}广东纪录片.png"},
            {"name": "广东健康", "logo": f"{LOGO_BASE}广东健康.png"},
            {"name": "GRTN生活", "logo": f"{LOGO_BASE}GRTN生活.png"},
        ],
    },
    # TVB / 无綫电视分类
    {
        "group": "無綫電視",
        "channels": [
            {"name": "翡翠台", "logo": f"{LOGO_BASE}翡翠台.png"},
            {"name": "J2 / TVB Plus", "logo": f"{LOGO_BASE}J2.png"},
            {"name": "無綫新闻台", "logo": f"{LOGO_BASE}無綫新聞台.png"},
            {"name": "明珠台", "logo": f"{LOGO_BASE}明珠台.png"},
            {"name": "财经体育资讯台", "logo": f"{LOGO_BASE}財經體育資訊台.png"},
        ],
    },
    # ViuTV 分类
    {
        "group": "ViuTV",
        "channels": [
            {"name": "ViuTV (99台)", "logo": f"{LOGO_BASE}ViuTV.png"},
            {"name": "ViuTVsix (96台)", "logo": f"{LOGO_BASE}ViuTVsix.png"},
        ],
    },
]

# 公开直播源聚合源接口（用于检索备选源）
UPSTREAM_SOURCES = [
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/cn.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/hk.m3u",
]


def check_stream_validity(url, timeout=5):
    """验证 HTTP/HLS 流是否能够成功访问"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(
            url, headers=headers, stream=True, timeout=timeout
        )
        if response.status_code == 200:
            return True
    except Exception:
        pass
    return False


def fetch_upstream_m3u():
    """下载上游公开 M3U 源文件"""
    all_lines = []
    for source in UPSTREAM_SOURCES:
        try:
            resp = requests.get(source, timeout=10)
            if resp.status_code == 200:
                all_lines.extend(resp.text.splitlines())
        except Exception as e:
            print(f"Fetch upstream failed: {source}, Error: {e}")
    return all_lines


def parse_m3u(lines):
    """解析 M3U 内容，提取频道名与对应的 URL"""
    streams = {}
    current_name = None

    for line in lines:
        line = line.strip()
        if line.startswith("#EXTINF"):
            # 提取 tvg-name 或逗号后面的频道名称
            match = re.search(r'tvg-name="([^"]+)"', line)
            if match:
                current_name = match.group(1).upper()
            else:
                parts = line.split(",")
                if len(parts) > 1:
                    current_name = parts[-1].strip().upper()
        elif line and not line.startswith("#") and current_name:
            if current_name not in streams:
                streams[current_name] = []
            streams[current_name].append(line)
            current_name = None
    return streams


def main():
    print("正在抓取上游直播源...")
    upstream_lines = fetch_upstream_m3u()
    parsed_streams = parse_m3u(upstream_lines)

    m3u_content = [
        '#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml"'
    ]  # 附带通用EPG链接

    for group_info in CHANNEL_CONFIGS:
        group_name = group_info["group"]
        for ch in group_info["channels"]:
            ch_name = ch["name"]
            ch_logo = ch["logo"]

            # 排除规则拦截
            if group_name == "广东频道" and any(
                ex in ch_name for ex in GUANGDONG_EXCLUDES
            ):
                continue

            # 查找候选链接
            candidate_urls = []
            # 模糊匹配频道名字
            clean_ch_name = re.sub(r"[^\w]", "", ch_name).upper()
            for key, urls in parsed_streams.items():
                clean_key = re.sub(r"[^\w]", "", key).upper()
                if clean_ch_name in clean_key or clean_key in clean_ch_name:
                    candidate_urls.extend(urls)

            # 去重
            candidate_urls = list(dict.fromkeys(candidate_urls))

            # 测试链接有效性 (并发测试)
            valid_url = None
            if candidate_urls:
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=5
                ) as executor:
                    future_to_url = {
                        executor.submit(
                            check_stream_validity, url
                        ): url
                        for url in candidate_urls[:5]  # 只测前5个源
                    }
                    for future in concurrent.futures.as_completed(
                        future_to_url
                    ):
                        url = future_to_url[future]
                        if future.result():
                            valid_url = url
                            break  # 找到一个可用的即停止

            if valid_url:
                extinf = f'#EXTINF:-1 tvg-name="{ch_name}" tvg-logo="{ch_logo}" group-title="{group_name}",{ch_name}'
                m3u_content.append(extinf)
                m3u_content.append(valid_url)
                print(f"[SUCCESS] {group_name} - {ch_name}: 可用")
            else:
                print(f"[FAIL] {group_name} - {ch_name}: 未找到可用有效源")

    # 保存生成文件
    with open("iptv.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_content))
    print("\niptv.m3u 文件生成完毕！")


if __name__ == "__main__":
    main()
