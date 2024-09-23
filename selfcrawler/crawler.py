import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from selfcrawler.schema import ActionResponse, Content, MessageToMarkdown
from selfcrawler.tools import ToolKit

with open('/Users/lzx/Documents/GitHub/selfcrawler/reqdoc/demo.md', 'r') as f:
    doc = f.read()


def run():
    model = ChatOpenAI(model="gpt-4o", temperature=0.8).bind_tools(tools=ToolKit.all_tools(), tool_choice='required')

    messages = [
        SystemMessage(content=[
            Content.from_text(
                "现在你是一个网页助手，根据文档描述的内容，指导用户完成相应的操作，浏览器页面大小为 1280 x 720"),
        ]),
        HumanMessage(content=[
            Content.from_text("任务描述与图片指引如下\n"),
            Content.from_text("查找一个抖音号为：yuzi9244的信息\n"),
            Content.from_text('# 第一歩：打开网页：https://union.bytedance.com/\n'),
            Content.from_text('# 第二歩：完成登录\n'),
            Content.from_text('# 第三歩：点击左侧`主播列表`按钮\n'),
            Content.from_text('# 第四歩：在右侧主播搜索框中搜索该抖音号\n'),
            Content.from_text('# 第五歩：获取该主播的粉丝数\n'),
        ])
    ]

    for i in range(10):
        result = model.invoke(messages)
        print(result.pretty_print())

        if result.additional_kwargs and 'tool_calls' in result.additional_kwargs:
            for tool_call in result.additional_kwargs['tool_calls'][:1]:
                tool = tool_call['function']
                kwargs = json.loads(tool['arguments'])
                r: ActionResponse = ToolKit.get_func(tool['name'])(**kwargs)
                messages.append(AIMessage(content=[Content.from_text(r.content)]))

                c = []
                if r.reply:
                    c.append(Content.from_text(r.reply))
                if r.base64_img:
                    c.append(Content.from_text('执行以上操作后，当前浏览器页面如下: \n'))
                    c.append(Content.from_base64(r.base64_img))
                messages.append(HumanMessage(content=c))

        else:
            messages.append(AIMessage(content=[Content.from_text(result.content)]))

    MessageToMarkdown(messages=messages).to_html('/Users/lzx/Documents/GitHub/selfcrawler/reqdoc/aaa.html')



from playwright.sync_api import sync_playwright

def show_notification(url, message, output_path):
    with sync_playwright() as p:
        # 启动一个浏览器实例
        browser = p.chromium.launch(headless=False)  # headless=False 表示以非无头模式启动浏览器
        # 创建一个新的页面
        page = browser.new_page()
        # 导航到目标网址
        page.goto(url)

        # 注入 CSS 和 JS 来显示提示框
        page.add_style_tag(content='''
            .custom-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                z-index: 10000;
                opacity: 0;
                transition: opacity 0.5s ease-in-out;
            }
            .custom-notification.show {
                opacity: 1;
            }
        ''')

        page.evaluate(f'''
            (() => {{
                const notification = document.createElement('div');
                notification.classList.add('custom-notification');
                notification.textContent = "{message}";
                document.body.appendChild(notification);
                setTimeout(() => {{
                    notification.classList.add('show');
                }}, 100);
                setTimeout(() => {{
                    notification.classList.remove('show');
                    setTimeout(() => {{
                        notification.remove();
                    }}, 500);
                }}, 3000);
            }})();
        ''')

        # 截取当前页面的截图
        page.screenshot(path=output_path)

        # 关闭浏览器
        browser.close()

# 使用示例
show_notification(
    url='https://example.com',
    message='This is a notification!',
    output_path='screenshot_with_notification.png'
)
