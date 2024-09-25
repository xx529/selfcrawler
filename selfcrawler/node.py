from typing import Callable

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from selfcrawler.prompt import browser_prompt, critic_prompt, save_html
from selfcrawler.schema import ActionFeedBack, Content, GraphState, Navigate
from selfcrawler.utils import Browser


class BaseNode:
    prefix = ''

    def __init__(self, name: str = ''):
        self.name = f'{self.prefix}_{name}'

    def __call__(self, state: GraphState) -> GraphState:
        return state

    def router(self, *args, **kwargs) -> Callable[[GraphState], str]:
        return None


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


class CriticNode(BaseNode):
    prefix = 'CRITIC'

    def __init__(self, name: str = ''):
        super().__init__(name=name)
        self.model = ChatOpenAI(model="gpt-4o", temperature=0.8).with_structured_output(ActionFeedBack)

    def __call__(self, state: GraphState):

        print(state['action_error'])
        prompt = critic_prompt(
            task_desc=state['action'],
            last_screenshot=state['last_screenshot'],
            current_screenshot=state['browser'].screenshot(),
            action_error=state['action_error']
        )

        result = self.model.invoke([prompt])

        if result.finish is False:
            state['suggestion'] = result.suggestion
            state['have_done'] = result.have_done
            state['to_do'] = result.to_do
            state['error_analysis'] = result.error_analysis
        else:
            state['suggestion'] = ''
            state['have_done'] = ''
            state['to_do'] = ''
            state['error_analysis'] = ''

        print(result.model_dump_json(indent=4))
        save_html([prompt, AIMessage(content=result.model_dump_json(indent=4))], self.name)
        return state

    @staticmethod
    def router(browser_node_name: str, end_node_name: str):

        def _router(state: GraphState) -> str:
            if state['suggestion'] == '':
                return end_node_name
            else:
                return browser_node_name

        return _router


class BrowserNode(BaseNode):
    prefix = 'BROWSER'

    def __init__(self, name: str = ''):
        super().__init__(name=name)
        self.model = ChatOpenAI(model="gpt-4o", temperature=0.8).bind_tools(Browser.actions(), tool_choice='required')

    def __call__(self, state: GraphState) -> GraphState:

        if (browser := state['browser']).started is False:
            browser.start()

        state['last_screenshot'] = browser.screenshot()
        prompt = browser_prompt(
            task_desc=state['action'],
            suggestion=state['suggestion'],
            have_done=state['have_done'],
            to_do=state['to_do'],
            html_content=browser.get_html_content(),
            screenshot=browser.screenshot(),
            error_analysis=state['error_analysis']
        )

        result = self.model.invoke([prompt])
        print(result.model_dump_json(indent=4))

        if result.tool_calls:
            for tool_call in result.tool_calls:
                func_name = tool_call['name']
                kwargs = tool_call['args']
                err = browser.exec_func(func_name, kwargs)
                if err:
                    state['action_error'].append(err)
        save_html([prompt, result], self.name)
        return state
