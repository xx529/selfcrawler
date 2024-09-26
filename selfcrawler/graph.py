from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from selfcrawler.node import BrowserNode, CriticNode, NavigatorNode
from selfcrawler.schema import GraphState
from selfcrawler.utils import Browser
from pathlib import Path

load_dotenv()

for file in (Path(__file__).parent.parent / 'reqdoc' / 'prompt').iterdir():
    file.unlink()

navigator = NavigatorNode()
browser = BrowserNode()
critic = CriticNode()

graph = StateGraph(GraphState)
graph.add_node(navigator.name, navigator)
graph.add_node(browser.name, browser)
graph.add_node(critic.name, critic)

graph.add_edge(START, navigator.name)
graph.add_edge(browser.name, critic.name)

graph.add_conditional_edges(
    source=critic.name,
    path=critic.router(browser_node_name=browser.name, navigator_node_name=navigator.name),
    path_map={browser.name: browser.name, navigator.name: navigator.name}
)

graph.add_conditional_edges(
    navigator.name,
    path=navigator.router(browser_node_name=browser.name, end_node_name=END),
    path_map={browser.name: browser.name, END: END}
)

app = graph.compile()

with open(Path(__file__).parent.parent / 'graph.png', 'wb') as f:
    f.write(app.get_graph().draw_mermaid_png())

state = GraphState(
    messages=[],
    browser=Browser(),
    action='',
    task_finish=False,
    last_screenshot='',
    code_error=[],
    action_response='',
    suggestion='',
    done='',
    todo='',
    code_error_analysis='',
    is_action_finish='',
)

app.invoke(state, {'recursion_limit': 100})
# for event in app.·stream(state, stream_mode='values'):
#     print(event)
