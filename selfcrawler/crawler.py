# import json
#
# from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
# from langchain_openai import ChatOpenAI
#
# from selfcrawler.schema import ActionResponse, Content, MessageToMarkdown
# from selfcrawler.tools import ToolKit
#
# with open('/Users/lzx/Documents/GitHub/selfcrawler/reqdoc/demo.md', 'r') as f:
#     doc = f.read()
#
#
# def run():
#     model = ChatOpenAI(model="gpt-4o", temperature=0.8).bind_tools(tools=ToolKit.all_tools(), tool_choice='required')
#
#     messages = [
#         SystemMessage(content=[
#             Content.from_text(
#                 "现在你是一个网页导航助手，根据文档描述的内容，指导用户完成相应的操作，浏览器页面大小为 1280 x 720"),
#         ]),
#         HumanMessage(content=[
#             Content.from_text("任务描述与图片指引如下\n"),
#             Content.from_text("查找一个抖音号为：yuzi9244的信息\n"),
#             Content.from_text('# 第一歩：打开网页：https://union.bytedance.com/\n'),
#             Content.from_text('# 第二歩：完成登录\n'),
#             Content.from_text('# 第三歩：点击左侧`主播列表`按钮\n'),
#             Content.from_text('# 第四歩：在右侧主播搜索框中搜索该抖音号\n'),
#             Content.from_text('# 第五歩：获取该主播的粉丝数\n'),
#         ])
#     ]
#
#     for i in range(10):
#         result = model.invoke(messages)
#         print(result.pretty_print())
#
#         if result.additional_kwargs and 'tool_calls' in result.additional_kwargs:
#             for tool_call in result.additional_kwargs['tool_calls'][:1]:
#                 tool = tool_call['function']
#                 kwargs = json.loads(tool['arguments'])
#                 r: ActionResponse = ToolKit.get_func(tool['name'])(**kwargs)
#                 messages.append(AIMessage(content=[Content.from_text(r.content)]))
#
#                 c = []
#                 if r.reply:
#                     c.append(Content.from_text(r.reply))
#                 if r.base64_img:
#                     c.append(Content.from_text('执行以上操作后，当前浏览器页面如下: \n'))
#                     c.append(Content.from_base64(r.base64_img))
#                 messages.append(HumanMessage(content=c))
#
#         else:
#             messages.append(AIMessage(content=[Content.from_text(result.content)]))
#
#     MessageToMarkdown(messages=messages).to_html('/Users/lzx/Documents/GitHub/selfcrawler/reqdoc/aaa.html')
#
#
# import time
#
# from langchain_core.tools import tool
# from langchain_experimental.utilities import PythonREPL
#
# from selfcrawler.schema import ActionResponse
#
# python_repl = PythonREPL()
#
#
# class ToolKit:
#
#     @staticmethod
#     @tool
#     def open_url(url: str) -> None:
#         """在谷歌浏览器中打开该网页.
#
#         Args:
#             url: 需要打开的网页链接
#         """
#         python_repl.run("from playwright.sync_api import sync_playwright")
#         python_repl.run("import base64")
#         python_repl.run("playwright = sync_playwright().start()")
#         python_repl.run("browser = playwright.chromium.launch(headless=False)")
#         python_repl.run("context = browser.new_context(viewport={'width': 1280, 'height': 720})")
#         python_repl.run("page = context.new_page()")
#         python_repl.run(f'page.goto("{url}")')
#         python_repl.run("""page.evaluate(f"document.body.style.zoom = '{min(width / document.body.scrollWidth, height / document.body.scrollHeight)}';")""")
#         python_repl.run("page.wait_for_load_state('load')")
#         time.sleep(5)
#         base64_img = python_repl.run("print(base64.b64encode(page.screenshot(full_page=True)).decode('utf-8'))")
#         return ActionResponse(content=f'用浏览器打开链接：{url}', base64_img=base64_img)
#
#     @staticmethod
#     @tool
#     def click(x: int, y: int, wait: int) -> None:
#         """点击浏览器的某个位置.
#
#         Args:
#             x: 需要点击的x轴坐标.
#             y: 需要点击的y轴位置坐标.
#             wait: 预估等待加载时间
#         """
#         python_repl.run(f'page.mouse.click({x}, {y})')
#         time.sleep(wait)
#         base64_img = python_repl.run("print(base64.b64encode(page.screenshot(full_page=True)).decode('utf-8'))")
#         return ActionResponse(content=f'点击该位置 ({x}, {y})', base64_img=base64_img)
#
#     @staticmethod
#     @tool
#     def wait_for_user_reply(question: str):
#         """询问用户获取相关帮助和信息或者需要用户的自主完成某些操作
#
#         Args:
#             question: 询问的问题.
#         """
#         reply = input(question + '(按回车确认)\n')
#         base64_img = python_repl.run("print(base64.b64encode(page.screenshot(full_page=True)).decode('utf-8'))")
#         return ActionResponse(content=question, base64_img=base64_img, reply=reply)
#
#     @staticmethod
#     @tool
#     def wait_for_loading(wait: int):
#         """当页面未加载完毕时候等待若干秒
#
#         Args:
#             wait: 预估等待页面加载完成时间
#         """
#         time.sleep(wait)
#         base64_img = python_repl.run("print(base64.b64encode(page.screenshot(full_page=True)).decode('utf-8'))")
#         return ActionResponse(content='等待页面加载完成', base64_img=base64_img)
#
#     @classmethod
#     def all_tools(cls):
#         return [cls.open_url, cls.click, cls.wait_for_user_reply, cls.wait_for_loading]
#
#     @classmethod
#     def get_func(cls, name):
#         return getattr(cls, name).func
#
#
# class PageAction:
#
#     @staticmethod
#     @tool
#     def open_url(url: str):
#         """在谷歌浏览器中打开该网页
#
#         :param url: 需要打开的网页链接
#         """
#         print(url)
#
#     @staticmethod
#     @tool
#     def click_element(css_selector: str):
#         """根据 css_selector 定位页面元素并进行点击操作
#
#         :param css_selector: css 选择器
#         """
#         print(css_selector)
#
#     @staticmethod
#     @tool
#     def input_text(css_selector: str, text: str):
#         """根据 css_selector 定位页面元素并输入文本
#
#         :param css_selector: css 选择器
#         :param text: 需要输入的文本
#         """
#         print(css_selector, text)
#
#     @classmethod
#     def all_tools(cls):
#         return [cls.click_element, cls.open_url]
#
