import time

from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL

from selfcrawler.schema import ActionResponse

python_repl = PythonREPL()


class ToolKit:

    @staticmethod
    @tool
    def open_url(url: str) -> None:
        """在谷歌浏览器中打开该网页.

        Args:
            url: 需要打开的网页链接
        """
        python_repl.run("from playwright.sync_api import sync_playwright")
        python_repl.run("import base64")
        python_repl.run("playwright = sync_playwright().start()")
        python_repl.run("browser = playwright.chromium.launch(headless=False)")
        python_repl.run("context = browser.new_context(viewport={'width': 1280, 'height': 720})")
        python_repl.run("page = context.new_page()")
        python_repl.run(f'page.goto("{url}")')
        python_repl.run("""page.evaluate(f"document.body.style.zoom = '{min(width / document.body.scrollWidth, height / document.body.scrollHeight)}';")""")
        python_repl.run("page.wait_for_load_state('load')")
        time.sleep(5)
        base64_img = python_repl.run("print(base64.b64encode(page.screenshot(full_page=True)).decode('utf-8'))")
        return ActionResponse(content=f'用浏览器打开链接：{url}', base64_img=base64_img)

    @staticmethod
    @tool
    def click(x: int, y: int, wait: int) -> None:
        """点击浏览器的某个位置.

        Args:
            x: 需要点击的x轴坐标.
            y: 需要点击的y轴位置坐标.
            wait: 预估等待加载时间
        """
        python_repl.run(f'page.mouse.click({x}, {y})')
        time.sleep(wait)
        base64_img = python_repl.run("print(base64.b64encode(page.screenshot(full_page=True)).decode('utf-8'))")
        return ActionResponse(content=f'点击该位置 ({x}, {y})', base64_img=base64_img)

    @staticmethod
    @tool
    def wait_for_user_reply(question: str):
        """询问用户获取相关帮助和信息或者需要用户的自主完成某些操作

        Args:
            question: 询问的问题.
        """
        reply = input(question + '(按回车确认)\n')
        base64_img = python_repl.run("print(base64.b64encode(page.screenshot(full_page=True)).decode('utf-8'))")
        return ActionResponse(content=question, base64_img=base64_img, reply=reply)

    @staticmethod
    @tool
    def wait_for_loading(wait: int):
        """当页面未加载完毕时候等待若干秒

        Args:
            wait: 预估等待页面加载完成时间
        """
        time.sleep(wait)
        base64_img = python_repl.run("print(base64.b64encode(page.screenshot(full_page=True)).decode('utf-8'))")
        return ActionResponse(content='等待页面加载完成', base64_img=base64_img)

    @classmethod
    def all_tools(cls):
        return [cls.open_url, cls.click, cls.wait_for_user_reply, cls.wait_for_loading]

    @classmethod
    def get_func(cls, name):
        return getattr(cls, name).func
