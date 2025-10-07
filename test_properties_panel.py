
import sys
from PySide6 import QtWidgets
from aicodeprep_gui.pro.flow.flow_dock import FlowStudioDock

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dock = FlowStudioDock()

    graph = dock.graph
    from aicodeprep_gui.pro.flow.nodes.llm_nodes import OpenRouterNode
    for i in range(5):
        node = OpenRouterNode()
        graph.add_node(node)

    nodes = [n for n in graph.all_nodes() if isinstance(n, OpenRouterNode)]
    for i, node in enumerate(nodes):
        node.set_property("model", f"model{i+1}")

    for node in nodes:
        node.set_selected(True)

    app.processEvents()

    prop_bin = dock.properties_bin
    if prop_bin:
        for node_widget in prop_bin.findChildren(QtWidgets.QWidget):
            if "NodePropEditorWidget" in node_widget.__class__.__name__:
                for child in node_widget.findChildren(QtWidgets.QLineEdit):
                    if child.objectName() == "model":
                        print(f"Model property widget text: {child.text()}")

    dock.show()
    sys.exit(app.exec())
