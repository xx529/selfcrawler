from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from selfcrawler.node import BrowserNode, CriticNode
from selfcrawler.schema import GraphState
from selfcrawler.utils import Browser
from pathlib import Path

load_dotenv()

browser_node = BrowserNode()
critic_node = CriticNode()

graph = StateGraph(GraphState)
graph.add_node(browser_node.name, browser_node)
graph.add_node(critic_node.name, critic_node)

graph.add_edge(START, browser_node.name)
graph.add_edge(browser_node.name, critic_node.name)
graph.add_conditional_edges(
    critic_node.name,
    critic_node.router(browser_node_name=browser_node.name, end_node_name=END)
)

app = graph.compile()

with open(Path(__file__).parent.parent / 'graph.png', 'wb') as f:
    f.write(app.get_graph().draw_mermaid_png())


# state = GraphState(
#     messages=[],
#     action='打开网站 https://home.qa.lightai.cn/',
#     question='',
#     finish=False,
#     suggestion='',
#     to_do='',
#     have_done='',
#     error_analysis='',
#     last_screenshot='',
#     action_error=[],
#     browser=Browser()
# )
#
# app.invoke(state)
