import requests
import yaml

BASE_URL = "https://raw.githubusercontent.com/Vanic24/VPN/main/"
SOURCES = ["8EB", "9PB", "Lifetime", "Sub3", "Filter"]

def main():
    unique_nodes = {}

    for source in SOURCES:
        url = f"{BASE_URL}{source}"
        print(f"正在分析 Clash 订阅源: {url}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # 解析 Clash 的 YAML 配置
                config = yaml.safe_load(response.text)
                if not config or 'proxies' not in config:
                    print("  -> ⚠️ 未找到 proxies 节点列表")
                    continue

                proxies = config['proxies']
                valid_count = 0

                for p in proxies:
                    # 提取关键信息用于去重和过滤
                    p_type = p.get('type')
                    server = p.get('server')
                    port = p.get('port')

                    # 1. 过滤：缺少关键基础信息的无效节点
                    if not p_type or not server or not port:
                        continue

                    # 2. 过滤：缺少密码/认证信息的无效节点
                    if p_type in ['vless', 'vmess'] and not p.get('uuid'):
                        continue
                    if p_type in ['trojan', 'ss'] and not p.get('password'):
                        continue

                    # 3. 去重：按 (server, port, type) 作为唯一身份卡
                    key = (server, port, p_type)
                    if key not in unique_nodes:
                        unique_nodes[key] = p
                        valid_count += 1

                print(f"  -> ✅ 成功清洗并保留 {valid_count} 个节点！")
            else:
                print(f"  -> ❌ 请求失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"  -> ❌ 解析出错: {e}")

    valid_links = list(unique_nodes.values())
    print(f"\n🎉 总结：最终共保留 {len(valid_links)} 个有效且不重复的节点！")

    # 将清洗后的节点重新打包成纯净的 Clash 格式
    final_config = {'proxies': valid_links}

    # 写入 my_sub.txt，Karing 可以无缝识别
    with open("my_sub.txt", "w", encoding="utf-8") as f:
        if valid_links:
            yaml.dump(final_config, f, allow_unicode=True, sort_keys=False)
        else:
            # 如果依然失败，给一个占位符防止空文件报错
            f.write("proxies:\n  - name: '依然没抓到_请联系AI'\n    type: vless\n    server: 127.0.0.1\n    port: 8080\n    uuid: '00000000-0000-0000-0000-000000000000'")

if __name__ == "__main__":
    main()
