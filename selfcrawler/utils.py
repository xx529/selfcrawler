import time

from bs4 import BeautifulSoup
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL


class Browser:

    def __init__(self):
        self.repl = PythonREPL()
        self.started = False

    def start(self):
        self.run("from playwright.sync_api import sync_playwright")
        self.run("playwright = sync_playwright().start()")
        self.run("browser = playwright.chromium.launch(headless=False)")
        self.run("page = browser.new_page()")
        self.run("page.set_default_timeout(5000)")
        self.started = True

    def get_html_content(self, simplify=True):
        html_content = self.repl.run("print(page.content())")

        if simplify:
            html_content = self.simplify_html(html_content)

        return html_content

    def screenshot(self):
        self.repl.run("import base64")
        base64_img = self.repl.run("print(base64.b64encode(page.screenshot(full_page=True)).decode('utf-8'))")
        return base64_img

    def exec_func(self, name: str, kwargs: dict):
        if 'self' in kwargs:
            kwargs.pop('self')
        return getattr(self, name).func(self, **kwargs)

    def run(self, code: str):
        resp = self.repl.run(code)
        print(resp)
        return resp

    @tool
    def open_url(self, url: str, wait: int = 5):
        """在谷歌浏览器中打开该网页.

        Args:
            url: 需要打开的网页链接
            wait: 预估页面加载时间
        """
        error = self.run(f'page.goto("{url}")')
        time.sleep(wait)
        return error

    @tool
    def click_element(self, css_selector: str):
        """根据 css_selector 定位页面元素并进行点击操作

        Args:
            css_selector: css 选择器
        """
        error = self.run(f"""page.locator("{css_selector}").click()""")
        return error

    @tool
    def input_text(self, css_selector: str, text: str):
        """根据 css_selector 定位页面元素并输入文本

        Args:
            css_selector: css 选择器
            text: 输入的文本
        """
        error = self.run(f"""page.fill("{css_selector}", "{text}")""")
        return error

    @tool
    def go_back(self):
        """
        浏览器回退操作
        """
        error = self.run("page.go_back()")
        return error

    @tool
    def wait(self, seconds: int):
        """
        预估操作后等待页面加载时间
        Args:
            seconds: 等待时间
        """
        time.sleep(seconds)
        return None

    @classmethod
    def actions(cls):
        return [cls.open_url, cls.click_element, cls.input_text]

    @staticmethod
    def simplify_html(html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'lxml')
        for element in soup(['script', 'style']):
            element.decompose()
        return str(soup).replace('\n', '')
