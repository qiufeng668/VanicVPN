import requests
import base64
import urllib.parse
import json
import re

# 基础链接（先不指定 main 或 master）
BASE_URL = "https://raw.githubusercontent.com/Vanic24/VPN/"
SOURCES = ["8EB", "9PB", "Lifetime", "Sub3", "Filter"]

def decode_base64(data):
    try:
        # 去除所有空白字符后再解码
        data = re.sub(r'\s+', '', data)
        data += "=" * ((4 - len(data) % 4) % 4)
        return base64.b64decode(data).decode('utf-8', errors='ignore')
    except Exception:
        return ""

def parse_and_check_node(link):
    link = link.strip()
    if not link: return None, False
    try:
        if link.startswith("vless://") or link.startswith("trojan://"):
            parsed = urllib.parse.urlparse(link)
            if not parsed.hostname or not parsed.port: return None, False
            return (parsed.scheme, parsed.hostname, parsed.port), True

        elif link.startswith("vmess://"):
            try:
                node_data = json.loads(decode_base64(link[8:]))
                if not node_data.get("add") or not node_data.get("port"): return None, False
                return ("vmess", node_data.get("add"), node_data.get("port")), True
            except Exception:
                return None, False
            
        elif link.startswith("ss://"):
            return ("ss", link.split("#")[0]), True
            
    except Exception:
        pass
    return None, False

def main():
    unique_nodes = {}
    for source in SOURCES:
        # 自动尝试 main 分支 和 master 分支
        urls_to_try = [f"{BASE_URL}main/{source}", f"{BASE_URL}master/{source}"]
        success = False
        
        for url in urls_to_try:
            print(f"正在尝试获取: {url}")
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    raw_text = response.text
                    print(f"  -> ✅ 获取成功！数据大小: {len(raw_text)} 字节")
                    success = True
                    
                    # 暴力双重解析：无论原格式是 Base64 还是纯文本，全混在一起提取
                    decoded_text = decode_base64(raw_text)
                    all_lines = raw_text.splitlines() + decoded_text.splitlines()
                    
                    valid_count = 0
                    for line in all_lines:
                        line = line.strip()
                        # 只筛选真正的节点链接
                        if not line.startswith(("vless://", "vmess://", "trojan://", "ss://")):
                            continue
                            
                        key, is_valid = parse_and_check_node(line)
                        if is_valid and key not in unique_nodes:
                            unique_nodes[key] = line
                            valid_count += 1
                            
                    print(f"  -> 🔍 从中清洗出 {valid_count} 个有效去重节点。")
                    break # 成功了就不再尝试另一个分支了
                else:
                    print(f"  -> ❌ 状态码 {response.status_code}")
            except Exception as e:
                print(f"  -> ⚠️ 请求出错: {e}")
                
        if not success:
            print(f"  -> ❌ 来源 {source} 彻底获取失败。")

    valid_links = list(unique_nodes.values())
    print(f"\n🎉 总结：最终共保留 {len(valid_links)} 个节点！")
    
    # 打包保存
    if valid_links:
        final_base64 = base64.b64encode("\n".join(valid_links).encode('utf-8')).decode('utf-8')
    else:
        # 如果什么都没抓到，写入一段测试提示，防止生成空文件
        final_base64 = base64.b64encode("vless://test@127.0.0.1:8080?encryption=none#什么都没抓到_请看日志".encode('utf-8')).decode('utf-8')
        
    with open("my_sub.txt", "w", encoding="utf-8") as f:
        f.write(final_base64)

if __name__ == "__main__":
    main()
