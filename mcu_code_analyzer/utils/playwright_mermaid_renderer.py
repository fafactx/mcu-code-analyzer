"""
Playwright本地Mermaid渲染器
使用Playwright在本地无头浏览器中渲染Mermaid图表
"""

import os
import tempfile
import base64
import io
from pathlib import Path
from typing import Optional, Tuple, Union
from PIL import Image


class PlaywrightMermaidRenderer:
    """Playwright Mermaid本地渲染器"""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self._initialized = False

    def _initialize_playwright(self):
        """初始化Playwright"""
        if self._initialized:
            return True

        try:
            from playwright.sync_api import sync_playwright
            self.playwright = sync_playwright()
            self.playwright_context = self.playwright.__enter__()

            # 启动浏览器（无头模式）
            self.browser = self.playwright_context.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )

            self._initialized = True
            return True

        except ImportError:
            print("❌ Playwright未安装，请运行: pip install playwright && playwright install chromium")
            return False
        except Exception as e:
            print(f"❌ Playwright初始化失败: {e}")
            return False

    def _get_mermaid_html_template(self, mermaid_code: str, theme: str = "default") -> str:
        """生成包含Mermaid的HTML模板"""

        # 获取本地mermaid.js文件路径
        script_dir = Path(__file__).parent.parent
        mermaid_js_path = script_dir / "assets" / "mermaid.min.js"

        # 尝试读取本地mermaid.js
        mermaid_js_content = ""
        if mermaid_js_path.exists():
            try:
                with open(mermaid_js_path, 'r', encoding='utf-8') as f:
                    mermaid_js_content = f.read()
            except Exception as e:
                print(f"⚠️ 无法读取本地mermaid.js: {e}")

        # 如果没有本地文件，使用CDN
        if not mermaid_js_content:
            mermaid_script = '<script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>'
        else:
            mermaid_script = f'<script>{mermaid_js_content}</script>'

        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mermaid Diagram</title>
    {mermaid_script}
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background-color: white;
            width: 100%;
            height: 100vh;
            overflow: hidden;
        }}
        .mermaid {{
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            height: 100%;
            min-height: 100vh;
        }}
        #diagram {{
            max-width: none !important;
            width: auto !important;
            height: auto !important;
        }}
        /* 确保SVG能够正确缩放 */
        .mermaid svg {{
            max-width: none !important;
            width: auto !important;
            height: auto !important;
        }}
    </style>
</head>
<body>
    <div class="mermaid" id="diagram">
{mermaid_code}
    </div>

    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: '{theme}',
            securityLevel: 'loose',
            fontFamily: 'Arial, sans-serif',
            fontSize: 16,
            flowchart: {{
                useMaxWidth: false,
                htmlLabels: true,
                curve: 'basis'
            }},
            themeVariables: {{
                primaryColor: '#ffffff',
                primaryTextColor: '#000000',
                primaryBorderColor: '#000000',
                lineColor: '#000000'
            }}
        }});

        // 等待渲染完成
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('DOM loaded, starting Mermaid rendering...');

            mermaid.run().then(() => {{
                console.log('Mermaid rendering completed');

                // 获取SVG元素并调整尺寸
                const svg = document.querySelector('.mermaid svg');
                if (svg) {{
                    // 移除width和height属性，让SVG自然缩放
                    svg.removeAttribute('width');
                    svg.removeAttribute('height');
                    svg.style.width = 'auto';
                    svg.style.height = 'auto';
                    svg.style.maxWidth = 'none';
                    svg.style.maxHeight = 'none';
                }}

                document.body.setAttribute('data-mermaid-ready', 'true');
            }}).catch((error) => {{
                console.error('Mermaid rendering failed:', error);
                document.body.setAttribute('data-mermaid-error', error.message);
            }});
        }});
    </script>
</body>
</html>
        """

        return html_template

    def render_to_png(self, mermaid_code: str, width: int = 1200, height: int = 800,
                     theme: str = "default", scale: float = 2.0) -> Optional[bytes]:
        """渲染Mermaid为PNG字节数据"""

        if not self._initialize_playwright():
            return None

        try:
            # 创建新页面，设置高DPI
            page = self.browser.new_page()
            page.set_viewport_size({"width": width, "height": height})

            # 设置设备像素比以提高渲染质量
            page.evaluate(f"() => {{ Object.defineProperty(window, 'devicePixelRatio', {{ value: {scale} }}); }}")

            # 生成HTML内容
            html_content = self._get_mermaid_html_template(mermaid_code, theme)

            # 加载HTML
            page.set_content(html_content)

            # 等待Mermaid渲染完成
            try:
                # 等待渲染完成标志
                page.wait_for_function(
                    "document.body.getAttribute('data-mermaid-ready') === 'true' || document.body.getAttribute('data-mermaid-error')",
                    timeout=30000
                )

                # 检查是否有错误
                error = page.evaluate("document.body.getAttribute('data-mermaid-error')")
                if error:
                    print(f"❌ Mermaid渲染错误: {error}")
                    return None

            except Exception as e:
                print(f"⚠️ 等待渲染超时，尝试继续: {e}")

            # 等待SVG元素出现
            try:
                page.wait_for_selector('.mermaid svg', timeout=10000)

                # 获取SVG元素的实际尺寸
                svg_box = page.evaluate("""
                    () => {
                        const svg = document.querySelector('.mermaid svg');
                        if (svg) {
                            const rect = svg.getBoundingClientRect();
                            const bbox = svg.getBBox();
                            return {
                                x: Math.max(0, rect.left - 20),
                                y: Math.max(0, rect.top - 20),
                                width: Math.max(bbox.width + 40, rect.width + 40),
                                height: Math.max(bbox.height + 40, rect.height + 40)
                            };
                        }
                        return null;
                    }
                """)

                if svg_box:
                    print(f"📐 SVG实际尺寸: {svg_box['width']}x{svg_box['height']}")
                    # 截取SVG区域
                    screenshot_bytes = page.screenshot(
                        type='png',
                        clip=svg_box,
                        scale='device'
                    )
                else:
                    print("⚠️ 无法获取SVG尺寸，使用全页面截图")
                    screenshot_bytes = page.screenshot(
                        type='png',
                        full_page=True,
                        scale='device'
                    )

            except Exception as e:
                print(f"⚠️ SVG处理失败: {e}，使用全页面截图")
                screenshot_bytes = page.screenshot(
                    type='png',
                    full_page=True,
                    scale='device'
                )

            page.close()
            return screenshot_bytes

        except Exception as e:
            print(f"❌ PNG渲染失败: {e}")
            return None

    def render_to_svg(self, mermaid_code: str, theme: str = "default") -> Optional[str]:
        """渲染Mermaid为SVG字符串"""

        if not self._initialize_playwright():
            return None

        try:
            # 创建新页面
            page = self.browser.new_page()

            # 生成HTML内容
            html_content = self._get_mermaid_html_template(mermaid_code, theme)

            # 加载HTML
            page.set_content(html_content)

            # 等待Mermaid渲染完成
            try:
                page.wait_for_function(
                    "document.body.getAttribute('data-mermaid-ready') === 'true' || document.body.getAttribute('data-mermaid-error')",
                    timeout=30000
                )

                # 检查是否有错误
                error = page.evaluate("document.body.getAttribute('data-mermaid-error')")
                if error:
                    print(f"❌ Mermaid渲染错误: {error}")
                    return None

            except Exception as e:
                print(f"⚠️ 等待渲染超时，尝试继续: {e}")

            # 等待SVG元素
            try:
                page.wait_for_selector('.mermaid svg', timeout=10000)
            except:
                print("⚠️ 未找到SVG元素")
                return None

            # 提取SVG内容
            svg_content = page.evaluate("""
                () => {
                    const svg = document.querySelector('.mermaid svg');
                    return svg ? svg.outerHTML : null;
                }
            """)

            page.close()
            return svg_content

        except Exception as e:
            print(f"❌ SVG渲染失败: {e}")
            return None

    def render_to_pil_image(self, mermaid_code: str, width: int = 1200, height: int = 800,
                           theme: str = "default", scale: float = 2.0) -> Optional[Image.Image]:
        """渲染Mermaid为PIL Image对象"""

        png_bytes = self.render_to_png(mermaid_code, width, height, theme, scale)
        if not png_bytes:
            return None

        try:
            return Image.open(io.BytesIO(png_bytes))
        except Exception as e:
            print(f"❌ 转换为PIL Image失败: {e}")
            return None

    def close(self):
        """关闭浏览器和Playwright"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.__exit__(None, None, None)
        except:
            pass
        finally:
            self._initialized = False

    def __del__(self):
        """析构函数"""
        self.close()


# 全局渲染器实例
_global_renderer = None

def get_mermaid_renderer() -> PlaywrightMermaidRenderer:
    """获取全局Mermaid渲染器实例"""
    global _global_renderer
    if _global_renderer is None:
        _global_renderer = PlaywrightMermaidRenderer()
    return _global_renderer

def render_mermaid_to_pil(mermaid_code: str, width: int = 1200, height: int = 800,
                         theme: str = "default", scale: float = 2.0) -> Optional[Image.Image]:
    """便捷函数：渲染Mermaid为PIL Image"""
    renderer = get_mermaid_renderer()
    return renderer.render_to_pil_image(mermaid_code, width, height, theme, scale)

def render_mermaid_to_png_bytes(mermaid_code: str, width: int = 1200, height: int = 800,
                               theme: str = "default", scale: float = 2.0) -> Optional[bytes]:
    """便捷函数：渲染Mermaid为PNG字节数据"""
    renderer = get_mermaid_renderer()
    return renderer.render_to_png(mermaid_code, width, height, theme, scale)

def render_mermaid_to_svg(mermaid_code: str, theme: str = "default") -> Optional[str]:
    """便捷函数：渲染Mermaid为SVG字符串"""
    renderer = get_mermaid_renderer()
    return renderer.render_to_svg(mermaid_code, theme)


# 测试函数
def test_playwright_rendering():
    """测试Playwright渲染功能"""
    print("🧪 测试Playwright Mermaid渲染...")

    test_mermaid = """
graph TD
    A[开始] --> B{判断条件}
    B -->|是| C[执行操作1]
    B -->|否| D[执行操作2]
    C --> E[结束]
    D --> E
    """

    try:
        # 测试PNG渲染
        print("📸 测试PNG渲染...")
        pil_image = render_mermaid_to_pil(test_mermaid)
        if pil_image:
            print(f"✅ PNG渲染成功，尺寸: {pil_image.size}")
        else:
            print("❌ PNG渲染失败")

        # 测试SVG渲染
        print("🎨 测试SVG渲染...")
        svg_content = render_mermaid_to_svg(test_mermaid)
        if svg_content:
            print(f"✅ SVG渲染成功，长度: {len(svg_content)} 字符")
        else:
            print("❌ SVG渲染失败")

    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    test_playwright_rendering()
