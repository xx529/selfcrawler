from langgraph.graph import StateGraph, END, START

from selfcrawler.node import PageOperatorNode, NavigatorNode
from selfcrawler.schema import GraphState


operator_node = PageOperatorNode()
navigator_node = NavigatorNode()

graph = StateGraph(GraphState)
graph.add_node(operator_node.name, operator_node)
graph.add_node(navigator_node.name, navigator_node)

graph.add_edge()

app = graph.compile()

app.get_graph().draw_png('graph.png')