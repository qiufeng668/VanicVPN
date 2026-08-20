import requests
import base64
import urllib.parse
import json

# 定义来源库的 Raw 链接 (跳过 MIX)
BASE_URL = "https://raw.githubusercontent.com/Vanic24/VPN/main/"
SOURCES = ["8EB", "9PB", "Lifetime", "Sub3", "Filter"]

def decode_base64(data):
    try:
        data = data.strip()
        data += "=" * ((4 - len(data) % 4) % 4)
        return base64.b64decode(data).decode('utf-8', errors='ignore')
    except Exception:
        return ""

def parse_and_check_node(link):
    link = link.strip()
    if not link:
        return None, False
    try:
        if link.startswith("vless://") or link.startswith("trojan://"):
            parsed = urllib.parse.urlparse(link)
            if not parsed.username or not parsed.hostname or not parsed.port:
                return None, False
            return (parsed.scheme, parsed.hostname, parsed.port), True

        elif link.startswith("vmess://"):
            node_data = json.loads(decode_base64(link[8:]))
            if not node_data.get("id") or not node_data.get("add") or not node_data.get("port"):
                return None, False
            return ("vmess", node_data.get("add"), node_data.get("port")), True
            
        elif link.startswith("ss://"):
            parsed = urllib.parse.urlparse(link)
            if parsed.hostname and parsed.port:
                return ("ss", parsed.hostname, parsed.port), True
            return None, False
    except Exception:
        return None, False
    return None, False

def main():
    unique_nodes = {}
    for source in SOURCES:
        try:
            response = requests.get(BASE_URL + source, timeout=10)
            if response.status_code != 200: continue
            
            raw_content = response.text
            decoded_content = decode_base64(raw_content)
            lines = decoded_content.splitlines() if decoded_content else raw_content.splitlines()
            
            for line in lines:
                key, is_valid = parse_and_check_node(line)
                if is_valid and key not in unique_nodes:
                    unique_nodes[key] = line
        except Exception:
            pass

    valid_links = list(unique_nodes.values())
    final_base64 = base64.b64encode("\n".join(valid_links).encode('utf-8')).decode('utf-8')
    
    with open("my_sub.txt", "w", encoding="utf-8") as f:
        f.write(final_base64)

if __name__ == "__main__":
    main()
