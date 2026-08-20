import requests
import base64
import urllib.parse
import json
import re

BASE_URL = "https://raw.githubusercontent.com/Vanic24/VPN/"
SOURCES = ["8EB", "9PB", "Lifetime", "Sub3", "Filter"]

def decode_base64(data):
    try:
        # 兼容 URL-Safe 格式，防止特殊字符导致解码崩溃
        data = data.replace("-", "+").replace("_", "/")
        # 暴力剔除所有非 Base64 合法字符
        data = re.sub(r'[^A-Za-z0-9+/=]', '', data)
        data += "=" * ((4 - len(data) % 4) % 4)
        return base64.b64decode(data).decode('utf-8', errors='ignore')
    except Exception:
        return ""

def parse_and_check_node(link):
    try:
        # 暴力正则提取：无论链接藏在多深的地方，直接挖出来
        match = re.search(r'((vless|vmess|trojan|ss|hysteria2|hy2)://[^\s"\'<>]+)', link, re.IGNORECASE)
        if not match: return None, False
        
        full_link = match.group(1)
        scheme = match.group(2).lower()
        
        if scheme in ["vless", "trojan"]:
            parsed = urllib.parse.urlparse(full_link)
            if not parsed.hostname or not parsed.port: return None, False
            return (scheme, parsed.hostname, parsed.port), full_link

        elif scheme == "vmess":
            node_data = json.loads(decode_base64(full_link[8:]))
            if not node_data.get("add") or not node_data.get("port"): return None, False
            return ("vmess", node_data.get("add"), node_data.get("port")), full_link
            
        elif scheme == "ss":
            return ("ss", full_link.split("#")[0], 0), full_link
            
    except Exception:
        pass
    return None, False

def main():
    unique_nodes = {}
    for source in SOURCES:
        url = f"{BASE_URL}main/{source}"
        print(f"\n正在分析: {url}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                raw_text = response.text
                print(f"  -> ✅ 获取成功！数据大小: {len(raw_text)} 字节")
                
                decoded_text = decode_base64(raw_text)
                all_lines = raw_text.splitlines() + decoded_text.splitlines()
                
                valid_count = 0
                for line in all_lines:
                    key, actual_link = parse_and_check_node(line)
                    if actual_link and key not in unique_nodes:
                        unique_nodes[key] = actual_link
                        valid_count += 1
                        
                print(f"  -> 🔍 从中清洗出 {valid_count} 个有效去重节点。")
                
                # X光透视：如果完全没提取出来，打印开头数据以便排错
                if valid_count == 0:
                    print("  -> ⚠️ 警告：未提取到标准链接！对方格式可能是 YAML 等特殊格式。")
                    print("  -> 🔽🔽🔽 源数据前500字符 🔽🔽🔽")
                    print(raw_text[:500])
                    print("  -> 🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼")
                    
        except Exception as e:
            print(f"  -> ❌ 请求出错: {e}")

    valid_links = list(unique_nodes.values())
    print(f"\n🎉 总结：最终共保留 {len(valid_links)} 个节点！")
    
    if valid_links:
        final_base64 = base64.b64encode("\n".join(valid_links).encode('utf-8')).decode('utf-8')
    else:
        final_base64 = base64.b64encode("vless://test@127.0.0.1:8080?encryption=none#什么都没抓到_请把最后一次日志截图发给AI".encode('utf-8')).decode('utf-8')
        
    with open("my_sub.txt", "w", encoding="utf-8") as f:
        f.write(final_base64)

if __name__ == "__main__":
    main()
