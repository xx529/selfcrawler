from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from langchain_core.messages import HumanMessage

from selfcrawler.node import BrowserNode, CriticNode, NavigatorNode, UserNode
from selfcrawler.schema import GraphState
from selfcrawler.utils import Browser
from pathlib import Path

load_dotenv()

for file in (Path(__file__).parent.parent / 'reqdoc' / 'prompt').iterdir():
    file.unlink()

navigator = NavigatorNode()
browser = BrowserNode()
critic = CriticNode()
# user = UserNode()

graph = StateGraph(GraphState)
graph.add_node(navigator.name, navigator)
# graph.add_node(user.name, user)
graph.add_node(browser.name, browser)
graph.add_node(critic.name, critic)

graph.add_edge(START, navigator.name)
graph.add_edge(browser.name, critic.name)
# graph.add_edge(user.name, navigator.name)

# graph.add_conditional_edges(
#     navigator.name,
#     path=navigator.router(browser_node_name=browser.name, end_node_name=END, user_node_name=user.name),
#     path_map={browser.name: browser.name, END: END, user.name: user.name}
# )

graph.add_conditional_edges(
    navigator.name,
    path=navigator.router(browser_node_name=browser.name, end_node_name=END, user_node_name=''),
    path_map={browser.name: browser.name, END: END}
)

graph.add_conditional_edges(
    source=critic.name,
    path=critic.router(browser_node_name=browser.name, navigator_node_name=navigator.name),
    path_map={browser.name: browser.name, navigator.name: navigator.name}
)

app = graph.compile()

with open(Path(__file__).parent.parent / 'graph.png', 'wb') as f:
    f.write(app.get_graph().draw_mermaid_png())

state = GraphState(
    messages=[HumanMessage(content='采用账户密码登录网站，')],
    browser=Browser(),
    sender=UserNode.prefix,
    action='',
    question='',
    question_response='',
    is_task_finish=False,
    last_screenshot='',
    code_error=[],
    action_response='',
    suggestion='',
    done='',
    todo='',
    code_error_analysis='',
    is_action_finish='',
)

# app.invoke(state, {'recursion_limit': 100})
# for event in app.·stream(state, stream_mode='values'):
#     print(event)
