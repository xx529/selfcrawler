from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from selfcrawler.schema import Content, GraphState, Navigate
from selfcrawler.utils import Browser


class BaseNode:
    prefix = ''

    def __init__(self, name: str = ''):
        self.name = f'{self.prefix}_{name}'

    def __call__(self, state: GraphState) -> GraphState:
        return state


class NavigatorNode(BaseNode):
    prefix = 'NAVIGATOR'

    def __init__(self, name: str = ''):
        super().__init__(name=name)
        self.model = ChatOpenAI(model="gpt-4o", temperature=0.8).with_structured_output(Navigate)

    def __call__(self, state: GraphState) -> GraphState:
        result = self.model.invoke(state['messages'])

        if result.question:
            content = Content.from_text(result.question)
            state['question'] = result.question
        elif result.action:
            content = Content.from_text(result.action)
            state['action'] = result.action
        else:
            state['finish'] = True
            content = Content.from_text("出现错误了，强制退出")

        state['messages'].append(AIMessage(content=[content]))
        return state


class PageOperatorNode(BaseNode):
    prefix = 'OPERATOR'

    def __init__(self, name: str = ''):
        super().__init__(name=name)
        self.model = ChatOpenAI(model="gpt-4o", temperature=0.8).bind_tools(Browser.actions(), tool_choice='required')

    def __call__(self, state: GraphState) -> GraphState:

        if (browser := state['browser']).started is False:
            browser.start()

        prompt = f"""
            这是你的任务：
            {state['action']}
        
            遵守以下规则：
            1. 如果以下 html 没有内容，则需要先打开网页，如果已经有内容则直接进行下一步。
            2. 创建CSS选择器时，确保它们是唯一且具体的，以便即使存在多个相同类型的元素（例如多个h1元素），也能仅选择一个元素。
            3. 避免单独使用通用标签如'h1'。相反，结合其他属性或结构关系来形成唯一的选择器。
            4. CSS 选择器必须符合 playwright 的 page.locator 方法的要求。
            5. 如果页面有相关问题的答案，请直接回答问题，不要进行其他操作。
        
            以下是当前页面的HTML代码
            ```html
            {browser.get_html_content()}
            ```
        """

        print(prompt)

        result = self.model.invoke([HumanMessage(content=[
            Content.from_text(prompt),
            Content.from_text('以下是当前浏览器页面的截图'),
            Content.from_base64(browser.screenshot())
        ])])
        print(result.model_dump_json(indent=4))

        if result.tool_calls:
            for tool_call in result.tool_calls:
                func_name = tool_call['name']
                kwargs = tool_call['args']
                browser.exec_func(func_name, kwargs)

        return state


from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()
messages = [
    SystemMessage(content=[
        Content.from_text(
            "现在你是一个网页导航助手，根据文档描述的内容，指导用户完成相应的操作，浏览器页面大小为 1280 x 720"),
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

s = GraphState(
    # messages=messages,
    action='打开网页：https://union.bytedance.com/',
    question='',
    finish=False,
    browser=Browser()
)
operator = PageOperatorNode()

a = operator(s)



s['action'] = '确认登录'

a = operator(s)

with open('aaa.html', 'w') as f:
    f.write(s['browser'].get_html_content(simplify=False))
