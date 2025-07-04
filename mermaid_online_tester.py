#!/usr/bin/env python3
"""
Mermaid在线渲染服务测试工具
测试各种在线mermaid渲染API是否可用
"""

import requests
import base64
import zlib
import urllib.parse
import time
import os
from datetime import datetime

class MermaidOnlineTester:
    def __init__(self):
        # 您提供的测试mermaid代码
        self.test_code = """graph TD
  A[ Anyone ] -->|Can help | B( Go to github.com/yuzutech/kroki )
  B --> C{ How to contribute? }
  C --> D[ Reporting bugs ]
  C --> E[ Sharing ideas ]
  C --> F[ Advocating ]"""
        
        # 定义所有已知的在线mermaid渲染服务
        self.services = [
            {
                "name": "Kroki.io PNG",
                "url": "https://kroki.io/mermaid/png/{encoded}",
                "encoding": "zlib_base64",
                "timeout": 15,
                "description": "Kroki.io官方mermaid PNG渲染"
            },
            {
                "name": "Kroki.io SVG", 
                "url": "https://kroki.io/mermaid/svg/{encoded}",
                "encoding": "zlib_base64",
                "timeout": 15,
                "description": "Kroki.io官方mermaid SVG渲染"
            },
            {
                "name": "Mermaid.ink PNG",
                "url": "https://mermaid.ink/img/{encoded}",
                "encoding": "base64",
                "timeout": 10,
                "description": "Mermaid.ink PNG渲染服务"
            },
            {
                "name": "Mermaid.ink SVG",
                "url": "https://mermaid.ink/svg/{encoded}",
                "encoding": "base64",
                "timeout": 10,
                "description": "Mermaid.ink SVG渲染服务"
            },
            {
                "name": "QuickChart.io",
                "url": "https://quickchart.io/mermaid?c={encoded}",
                "encoding": "url_encode",
                "timeout": 10,
                "description": "QuickChart.io mermaid渲染"
            },
            {
                "name": "Mermaid Live Editor",
                "url": "https://mermaid-js.github.io/mermaid-live-editor/img/{encoded}",
                "encoding": "base64",
                "timeout": 10,
                "description": "官方Mermaid Live Editor"
            },
            {
                "name": "Mermaid Live (alternative)",
                "url": "https://mermaid.live/img/{encoded}",
                "encoding": "base64",
                "timeout": 10,
                "description": "Mermaid Live替代服务"
            },
            {
                "name": "Mermaid.ink (URL Safe)",
                "url": "https://mermaid.ink/img/{encoded}",
                "encoding": "base64_url",
                "timeout": 10,
                "description": "Mermaid.ink URL安全编码"
            }
        ]
        
        self.results = []
        self.working_services = []
    
    def encode_mermaid(self, code, method):
        """根据不同方法编码mermaid代码"""
        if method == "base64":
            return base64.b64encode(code.encode('utf-8')).decode('ascii')
        elif method == "base64_url":
            return base64.urlsafe_b64encode(code.encode('utf-8')).decode('ascii')
        elif method == "zlib_base64":
            compressed = zlib.compress(code.encode('utf-8'), 9)
            return base64.urlsafe_b64encode(compressed).decode('ascii')
        elif method == "url_encode":
            return urllib.parse.quote(code)
        else:
            return code
    
    def test_service(self, service):
        """测试单个服务"""
        name = service["name"]
        url_template = service["url"]
        encoding_method = service["encoding"]
        timeout = service["timeout"]
        description = service["description"]
        
        print(f"\n🔍 测试: {name}")
        print(f"📝 描述: {description}")
        
        try:
            # 编码mermaid代码
            encoded = self.encode_mermaid(self.test_code, encoding_method)
            
            # 构建完整URL
            if "{encoded}" in url_template:
                full_url = url_template.format(encoded=encoded)
            else:
                full_url = url_template + encoded
            
            print(f"🌐 URL: {full_url[:80]}...")
            print(f"⏱️  超时设置: {timeout}秒")
            
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'image/png,image/svg+xml,image/*,*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache'
            }
            
            # 发送请求
            start_time = time.time()
            response = requests.get(full_url, timeout=timeout, headers=headers)
            end_time = time.time()
            
            response_time = round(end_time - start_time, 2)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                content_length = len(response.content)
                
                print(f"✅ 成功! 响应时间: {response_time}秒")
                print(f"📊 Content-Type: {content_type}")
                print(f"📊 内容大小: {content_length} bytes")
                
                # 保存文件
                if 'image' in content_type:
                    # 确定文件扩展名
                    if 'png' in content_type:
                        ext = 'png'
                    elif 'svg' in content_type:
                        ext = 'svg'
                    elif 'jpeg' in content_type or 'jpg' in content_type:
                        ext = 'jpg'
                    else:
                        ext = 'img'
                    
                    filename = f"test_{name.lower().replace(' ', '_').replace('.', '_')}.{ext}"
                    
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    print(f"💾 已保存: {filename}")
                
                # 记录成功结果
                result = {
                    'name': name,
                    'status': 'success',
                    'response_time': response_time,
                    'content_type': content_type,
                    'content_length': content_length,
                    'url': full_url[:100] + '...' if len(full_url) > 100 else full_url
                }
                
                self.working_services.append(service)
                return result
                
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                if response.text:
                    print(f"📄 错误信息: {response.text[:200]}")
                
                return {
                    'name': name,
                    'status': 'http_error',
                    'status_code': response.status_code,
                    'response_time': response_time
                }
        
        except requests.exceptions.Timeout:
            print(f"❌ 超时 (>{timeout}秒)")
            return {
                'name': name,
                'status': 'timeout',
                'timeout': timeout
            }
        
        except requests.exceptions.ConnectionError as e:
            print(f"❌ 连接错误: {str(e)[:100]}")
            return {
                'name': name,
                'status': 'connection_error',
                'error': str(e)[:200]
            }
        
        except Exception as e:
            print(f"❌ 其他错误: {str(e)[:100]}")
            return {
                'name': name,
                'status': 'error',
                'error': str(e)[:200]
            }
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 Mermaid在线渲染服务测试工具")
        print("=" * 60)
        print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🧪 测试代码:")
        print(self.test_code)
        print("=" * 60)
        
        # 测试每个服务
        for i, service in enumerate(self.services, 1):
            print(f"\n[{i}/{len(self.services)}]", end="")
            result = self.test_service(service)
            self.results.append(result)
            
            # 添加延迟避免请求过快
            if i < len(self.services):
                time.sleep(1)
        
        # 生成报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📋 测试结果报告")
        print("=" * 60)
        
        # 统计结果
        success_count = len([r for r in self.results if r['status'] == 'success'])
        timeout_count = len([r for r in self.results if r['status'] == 'timeout'])
        error_count = len(self.results) - success_count - timeout_count
        
        print(f"📊 总体统计:")
        print(f"  ✅ 成功: {success_count} 个")
        print(f"  ⏱️  超时: {timeout_count} 个")
        print(f"  ❌ 错误: {error_count} 个")
        print(f"  📈 成功率: {success_count/len(self.results)*100:.1f}%")
        
        # 详细结果
        print(f"\n📝 详细结果:")
        for result in self.results:
            name = result['name']
            status = result['status']
            
            if status == 'success':
                response_time = result['response_time']
                content_type = result['content_type']
                size = result['content_length']
                print(f"  ✅ {name:<25} | {response_time}s | {content_type} | {size} bytes")
            elif status == 'timeout':
                timeout = result['timeout']
                print(f"  ⏱️  {name:<25} | 超时 (>{timeout}s)")
            elif status == 'http_error':
                status_code = result['status_code']
                print(f"  ❌ {name:<25} | HTTP {status_code}")
            else:
                print(f"  ❌ {name:<25} | 连接错误")
        
        # 推荐服务
        if self.working_services:
            print(f"\n🎯 推荐使用的服务:")
            for i, service in enumerate(self.working_services[:3], 1):
                print(f"  {i}. {service['name']} - {service['description']}")
            
            # 生成配置建议
            print(f"\n⚙️  配置建议:")
            best_service = self.working_services[0]
            print(f"  主要API: {best_service['url']}")
            print(f"  编码方式: {best_service['encoding']}")
            print(f"  超时设置: {best_service['timeout']}秒")
            
            if len(self.working_services) > 1:
                print(f"  备用API: {self.working_services[1]['url']}")
        else:
            print(f"\n😞 没有找到可用的mermaid在线渲染服务")
            print(f"\n💡 建议:")
            print(f"  1. 检查网络连接")
            print(f"  2. 检查防火墙设置")
            print(f"  3. 尝试使用VPN")
            print(f"  4. 考虑使用本地mermaid-cli")
        
        # 保存报告到文件
        self.save_report_to_file()
    
    def save_report_to_file(self):
        """保存报告到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"mermaid_test_report_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Mermaid在线渲染服务测试报告\n")
            f.write("=" * 40 + "\n")
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("测试代码:\n")
            f.write(self.test_code + "\n\n")
            
            f.write("测试结果:\n")
            for result in self.results:
                f.write(f"{result['name']}: {result['status']}\n")
            
            if self.working_services:
                f.write(f"\n可用服务:\n")
                for service in self.working_services:
                    f.write(f"- {service['name']}: {service['url']}\n")
        
        print(f"\n📄 报告已保存到: {filename}")

def main():
    """主函数"""
    tester = MermaidOnlineTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
