import json
from typing import Callable

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from selfcrawler.prompt import browser_prompt, critic_prompt, save_prompt_completion
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

        state['action'] = input("请输入浏览器操作描述：\n")

        # result: Navigate = self.model.invoke(state['messages'])
        # print(result)

        # if result.is_task_finish is True:
        #     state['is_task_finish'] = True
        #
        # if state['action'] in ['exit', 'bye', 'gg']:
        #     state['is_task_finish'] = True
        #
        # if state['messages'][-1].content in ['exit', 'bye', 'gg']:
        #     state['is_task_finish'] = True
        #
        # if result.question:
        #     state['messages'].append(AIMessage(content=result.question))
        #     state['question'] = result.question
        #
        # elif result.action:
        #     state['messages'].append(AIMessage(content=result.action))
        #     state['action'] = result.action
        #
        # save_prompt_completion(state['messages'], self.name)
        # state['sender'] = self.prefix
        return state

    @staticmethod
    def router(browser_node_name: str, end_node_name: str, user_node_name: str):

        def _router(state: GraphState) -> str:
            if state['is_task_finish'] is True:
                return end_node_name
            if state['action']:
                return browser_node_name
            if state['question']:
                return user_node_name
            else:
                raise Exception("NavigatorNode router error")

        return _router


class BrowserNode(BaseNode):
    prefix = 'BROWSER'

    def __init__(self, name: str = ''):
        super().__init__(name=name)
        self.model = ChatOpenAI(model="gpt-4o", temperature=0.8).bind_tools(Browser.actions())

    def __call__(self, state: GraphState) -> GraphState:

        if (browser := state['browser']).started is False:
            browser.start()

        state['last_screenshot'] = browser.screenshot()
        prompt = browser_prompt(
            task_desc=state['action'],
            suggestion=state['suggestion'],
            done=state['done'],
            todo=state['todo'],
            html_content=browser.get_html_content(),
            screenshot=browser.screenshot(),
            code_error_analysis=state['code_error_analysis']
        )

        result = self.model.invoke([prompt])
        print(result.model_dump_json(indent=4))

        if result.tool_calls:
            msg = AIMessage(content=[Content.from_text(f"```json\n{json.dumps(result.tool_calls, indent=4)}\n```")])
            for tool_call in result.tool_calls:
                func_name = tool_call['name']
                kwargs = tool_call['args']
                err = browser.exec_func(func_name, kwargs)
                if err:
                    state['code_error'].append(err)
        else:
            state['action_response'] = result.content
            msg = AIMessage(content=[Content.from_text(result.content)])

        save_prompt_completion([prompt, msg], self.name)
        state['sender'] = self.prefix
        return state


class CriticNode(BaseNode):
    prefix = 'CRITIC'

    def __init__(self, name: str = ''):
        super().__init__(name=name)
        self.model = ChatOpenAI(model="gpt-4o", temperature=0.8).with_structured_output(ActionFeedBack)

    def __call__(self, state: GraphState):

        prompt = critic_prompt(
            task_desc=state['action'],
            last_screenshot=state['last_screenshot'],
            current_screenshot=state['browser'].screenshot(),
            code_error=state['code_error'],
            action_response=state['action_response']
        )

        result: ActionFeedBack = self.model.invoke([prompt])
        print(result.model_dump_json(indent=4))

        state['is_action_finish'] = result.is_action_finish
        state['code_error'] = []
        state['action_response'] = ''

        if not result.is_action_finish:
            state['suggestion'] = result.suggestion
            state['done'] = result.done
            state['todo'] = result.todo
            state['code_error_analysis'] = result.code_error_analysis
        else:
            state['suggestion'] = ''
            state['done'] = ''
            state['todo'] = ''
            state['code_error_analysis'] = ''

        save_prompt_completion([prompt, AIMessage(content=result.model_dump_json(indent=4))], self.name)
        state['sender'] = self.prefix
        return state

    @staticmethod
    def router(browser_node_name: str, navigator_node_name: str):

        def _router(state: GraphState) -> str:
            if state['is_action_finish'] is True:
                return navigator_node_name
            else:
                return browser_node_name

        return _router


class UserNode(BaseNode):
    prefix = 'USER'

    def __init__(self, name: str = ''):
        super().__init__(name=name)

    def __call__(self, state: GraphState) -> GraphState:
        response = input(f"{state['question']}\n请输入提示：\n")
        state['messages'].append(HumanMessage(content=response))
        state['sender'] = self.prefix
        return state
