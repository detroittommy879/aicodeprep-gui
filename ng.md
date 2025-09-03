# NodeGraphQt

[![API Documentation](https://github.com/jchanvfx/NodeGraphQt/actions/workflows/sphinx_doc_build.yml/badge.svg)](https://github.com/jchanvfx/NodeGraphQt/actions/workflows/sphinx_doc_build.yml)
[![PyPI Package](https://github.com/jchanvfx/NodeGraphQt/actions/workflows/pypi_publish.yml/badge.svg)](https://github.com/jchanvfx/NodeGraphQt/actions/workflows/pypi_publish.yml)
![GitHub Repo stars](https://img.shields.io/github/stars/jchanvfx/NodeGraphQt?style=social)

<p align="center">
    <a href="https://jchanvfx.github.io/NodeGraphQt" target="_blank">
    <img src="https://raw.githubusercontent.com/jchanvfx/NodeGraphQt/main/docs/_images/logo.png" title="logo">
    </a>
</p>

NodeGraphQt is a node graph UI framework written in python using `Qt`.

<img src="https://raw.githubusercontent.com/jchanvfx/NodeGraphQt/main/docs/_images/screenshot.png" width="100%" title="NodeGraphQt">

## Install

NodeGraphQt is available on The Python Package Index (PyPI) [here](https://pypi.org/project/NodeGraphQt) so it can be installed with:

```
pip install NodeGraphQt
```

or you can download previous versions from the [releases](https://github.com/jchanvfx/NodeGraphQt/releases) page.

## Documentation

<a href="https://jchanvfx.github.io/NodeGraphQt" target="_blank">https://jchanvfx.github.io/NodeGraphQt</a>

See the [basic_example.py](/examples/basic_example.py) script to get started or check out the API example overview
<a href="https://jchanvfx.github.io/NodeGraphQt/api/examples/ex_overview.html#simple-example" target="_blank">here.</a>

## Vertical Layout

https://jchanvfx.github.io/NodeGraphQt/api/examples/ex_pipe.html#layout-direction

<img src="https://raw.githubusercontent.com/jchanvfx/NodeGraphQt/main/docs/_images/vertical_layout.png" width="800" title="Vertical Layout">

## Pipe Layout

https://jchanvfx.github.io/NodeGraphQt/api/examples/ex_pipe.html#layout-styles

<img src="https://raw.githubusercontent.com/jchanvfx/NodeGraphQt/main/docs/_images/pipe_layout_types.gif" width="600" title="Pipe Layout">

## Custom Widgets

https://jchanvfx.github.io/NodeGraphQt/api/custom_widgets.html

<img src="https://raw.githubusercontent.com/jchanvfx/NodeGraphQt/main/docs/_images/prop_bin.png" width="600" title="Properties Bin">

<img src="https://raw.githubusercontent.com/jchanvfx/NodeGraphQt/main/docs/_images/nodes_palette.png" width="450" title="Node Palette">

docs\builtin_widgets\NodesPaletteWidget.rst:
<code>
:hide-rtoc:

NodesPaletteWidget
##################

.. autosummary::
NodeGraphQt.NodesPaletteWidget

.. autoclass:: NodeGraphQt.NodesPaletteWidget
:members:
:exclude-members: mimeData, staticMetaObject

</code>

docs\builtin_widgets\NodesTreeWidget.rst:
<code>
:hide-rtoc:

NodesTreeWidget
###############

.. autosummary::
NodeGraphQt.NodesTreeWidget

.. autoclass:: NodeGraphQt.NodesTreeWidget
:members:
:exclude-members: mimeData, staticMetaObject

</code>

docs\builtin_widgets\PropertiesBinWidget.rst:
<code>
:hide-rtoc:

PropertiesBinWidget
###################

.. autosummary::
NodeGraphQt.PropertiesBinWidget

.. autoclass:: NodeGraphQt.PropertiesBinWidget
:members:
:exclude-members: staticMetaObject

</code>

docs\examples\ex_menu.rst:
<code>
Menu Overview
#############

.. currentmodule:: NodeGraphQt

| Examples for customizing context menus in `NodeGraphQt`.

Default Context Menu

---

The :class:`NodeGraphQt.NodeGraph` has a context menu can be accessed with
:meth:`NodeGraph.context_menu`.

It can also be populated it with a config file in `JSON` format by using
:meth:`NodeGraph.set_context_menu_from_file`.

.. image:: ../\_images/menu_hotkeys.png
:width: 300px

| Here's a couple links to the example config file and functions with a few essential menu commands.
| `example JSON config file <https://github.com/jchanvfx/NodeGraphQt/blob/main/examples/hotkeys/hotkeys.json>`_
| `example python hotkey functions <https://github.com/jchanvfx/NodeGraphQt/blob/main/examples/hotkeys/hotkey_functions.py>`_

Adding to the Graph Menu

---

The `"graph"` menu is the main context menu from the NodeGraph object, below
is an example where we add a `"Foo"` menu and then a `"Bar"` command with
the registered `my_test()` function.

.. code-block:: python
:linenos:

    from NodeGraphQt import NodeGraph

    # test function.
    def my_test(graph):
        selected_nodes = graph.selected_nodes()
        print('Number of nodes selected: {}'.format(len(selected_nodes)))

    # create node graph.
    node_graph = NodeGraph()

    # get the main context menu.
    context_menu = node_graph.get_context_menu('graph')

    # add a menu called "Foo".
    foo_menu = context_menu.add_menu('Foo')

    # add "Bar" command to the "Foo" menu.
    # we also assign a short cut key "Shift+t" for this example.
    foo_menu.add_command('Bar', my_test, 'Shift+t')

Adding to the Nodes Menu

---

Aside from the main context menu, the NodeGraph also has a nodes menu where you
can override context menus on a per node type basis.

| Below is an example for overriding a context menu for the node type `"io.github.jchanvfx.FooNode"`

.. code-block:: python
:linenos:

    from NodeGraphQt import BaseNode, NodeGraph

    # define a couple example nodes.
    class FooNode(BaseNode):

        __identifier__ = 'io.github.jchanvfx'
        NODE_NAME = 'foo node'

        def __init__(self):
            super(FooNode, self).__init__()
            self.add_input('in')
            self.add_output('out')

    class BarNode(FooNode):

        NODE_NAME = 'bar node'

    # define a test function.
    def test_func(graph, node):
        print('Clicked on node: {}'.format(node.name()))

    # create node graph and register node classes.
    node_graph = NodeGraph()
    node_graph.register_node(FooNode)
    node_graph.register_node(BarNode)

    # get the nodes menu.
    nodes_menu = node_graph.get_context_menu('nodes')

    # here we add override the context menu for "io.github.jchanvfx.FooNode".
    nodes_menu.add_command('Test',
                           func=test_func,
                           node_type='io.github.jchanvfx.FooNode')

    # create some nodes.
    foo_node = graph.create_node('io.github.jchanvfx.FooNode')
    bar_node = graph.create_node('io.github.jchanvfx', pos=[300, 100])

    # show widget.
    node_graph.widget.show()

Adding with Config files

---

Adding menus and commands can also be done through configs and python module files.

example python script containing a test function.

`../path/to/my/hotkeys/cmd_functions.py`

.. code-block:: python
:linenos:

    def graph_command(graph):
        """
        function that's triggered on the node graph context menu.

        Args:
            graph (NodeGraphQt.NodeGraph): node graph controller.
        """
        print(graph)

    def node_command(graph, node):
        """
        function that's triggered on a node's node context menu.

        Args:
            graph (NodeGraphQt.NodeGraph): node graph controller.
            node: (NodeGraphQt.NodeObject): node object triggered on.
        """
        print(graph)
        print(node.name())

example `json` config for the node graph context menu.

`../path/to/my/hotkeys/graph_commands.json`

.. code-block:: json
:linenos:

    [
      {
        "type":"menu",
        "label":"My Sub Menu",
        "items":[
          {
            "type":"command",
            "label":"Example Graph Command",
            "file":"../examples/hotkeys/cmd_functions.py",
            "function_name":"graph_command",
            "shortcut":"Shift+t",
          }
        ]
      }
    ]

example `json` config for the nodes context menu.

`../path/to/my/hotkeys/node_commands.json`

.. code-block:: json
:linenos:

    [
      {
        "type":"command",
        "label":"Example Graph Command",
        "file":"../examples/hotkeys/cmd_functions.py",
        "function_name":"node_command",
        "node_type":"io.github.jchanvfx.FooNode",
      }
    ]

In the main code where your node graph controller is defined we can just call the
:meth:`NodeGraph.set_context_menu_from_file`

.. code-block:: python
:linenos:

    from NodeGraphQt import NodeGraph

    node_graph = NodeGraph()
    node_graph.set_context_menu_from_file(
        '../path/to/a/hotkeys/graph_commands.json', menu='graph'
    )
    node_graph.set_context_menu_from_file(
        '../path/to/a/hotkeys/node_commands.json', menu='nodes'
    )

Adding with Serialized data

---

Alternatively if you do not prefer to have `json` config files the node graph also has a
:meth:`NodeGraph.set_context_menu` function.

here's an example.

.. code-block:: python
:linenos:

    from NodeGraphQt import NodeGraph

    data = [
        {
            'type': 'menu',
            'label': 'My Sub Menu',
            'items': [
                {
                    'type': 'command',
                    'label': 'Example Graph Command',
                    'file': '../examples/hotkeys/cmd_functions.py',
                    'function_name': 'graph_command',
                    'shortcut': 'Shift+t'
                },
            ]
        },
    ]

    node_graph = NodeGraph()
    node_graph.set_context_menu(menu_name='graph', data)

</code>

docs\examples\ex_node.rst:
<code>
Node Overview
#############

Creating Nodes

---

| Creating a node is done by calling the :func:`NodeGraphQt.NodeGraph.create_node` function.
| (`see example below` `line: 23`)

.. code-block:: python
:linenos:
:emphasize-lines: 23

    from Qt import QtWidgets
    from NodeGraphQt import BaseNode, NodeGraph

    class MyNode(BaseNode):

        __identifier__ = 'io.github.jchanvfx'
        NODE_NAME = 'my node'

        def __init__(self):
            super(MyNode, self).__init__()
            self.add_input('foo')
            self.add_input('hello')
            self.add_output('bar')
            self.add_output('world')

    if __name__ == '__main__':
        app = QtWidgets.QApplication([])

        node_graph = NodeGraph()
        node_graph.register_node(MyNode)
        node_graph.widget.show()

        # here we create a couple nodes in the node graph.
        node_a = node_graph.create_node('io.github.jchanvfx.MyNode', name='node a')
        node_b = node_graph.create_node('io.github.jchanvfx.MyNode', name='node b', pos=[300, 100])

        app.exec_()

|

Creating Node Widgets

---

The :class:`NodeGraphQt.BaseNode` class allows you to embed some basic widgets inside a node here's a
example to simply embed a `QComboBox` widget when reimplementing the `BaseNode`.

.. code-block:: python
:linenos:

    from NodeGraphQt import BaseNode

    class MyListNode(BaseNode):

        __identifier__ = 'io.github.jchanvfx'
        NODE_NAME = 'node'

        def __init__(self):
            super(MyListNode, self).__init__()

            items = ['apples', 'bananas', 'pears', 'mangos', 'oranges']
            self.add_combo_menu('my_list', 'My List', items)

To you update the widget you can call the
:meth:`NodeGraphQt.NodeObject.set_property` function.

.. code-block:: python
:linenos:

    node = MyListNode()
    node.set_property('my_list', 'mangos')

`functions for embedding widgets into a base node:`

- `QComboBox`: :meth:`NodeGraphQt.BaseNode.add_combo_menu`
- `QCheckBox`: :meth:`NodeGraphQt.BaseNode.add_checkbox`
- `QLineEdit`: :meth:`NodeGraphQt.BaseNode.add_text_input`

See: :ref:`Embedded Node Widgets` for more node widget types.

|

Embedding Custom Widgets

---

Here's an example to embed a custom widget where we subclass the
:class:`NodeGraphQt.NodeBaseWidget` and then add to the node with the
:meth:`NodeGraphQt.BaseNode.add_custom_widget` function.

.. code-block:: python
:linenos:
:emphasize-lines: 38, 96, 97

    from Qt import QtCore, QtWidgets
    from NodeGraphQt import BaseNode, NodeBaseWidget

    class MyCustomWidget(QtWidgets.QWidget):
        """
        Custom widget to be embedded inside a node.
        """

        def __init__(self, parent=None):
            super(MyCustomWidget, self).__init__(parent)
            self.combo_1 = QtWidgets.QComboBox()
            self.combo_1.addItems(['a', 'b', 'c'])
            self.combo_2 = QtWidgets.QComboBox()
            self.combo_2.addItems(['a', 'b', 'c'])
            self.btn_go = QtWidgets.QPushButton('Go')

            layout = QtWidgets.QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.combo_1)
            layout.addWidget(self.combo_2)
            layout.addWidget(self.btn_go)


    class NodeWidgetWrapper(NodeBaseWidget):
        """
        Wrapper that allows the widget to be added in a node object.
        """

        def __init__(self, parent=None):
            super(NodeWidgetWrapper, self).__init__(parent)

            # set the name for node property.
            self.set_name('my_widget')

            # set the label above the widget.
            self.set_label('Custom Widget')

            # set the custom widget.
            self.set_custom_widget(MyCustomWidget())

            # connect up the signals & slots.
            self.wire_signals()

        def wire_signals(self):
            widget = self.get_custom_widget()

            # wire up the combo boxes.
            widget.combo_1.currentIndexChanged.connect(self.on_value_changed)
            widget.combo_2.currentIndexChanged.connect(self.on_value_changed)

            # wire up the button.
            widget.btn_go.clicked.connect(self.on_btn_go_clicked)

        def on_btn_go_clicked(self):
            print('Clicked on node: "{}"'.format(self.node.name()))

        def get_value(self):
            widget = self.get_custom_widget()
            return '{}/{}'.format(widget.combo_1.currentText(),
                                  widget.combo_2.currentText())

        def set_value(self, value):
            value = value.split('/')
            if len(value) < 2:
                combo1_val = value[0]
                combo2_val = ''
            else:
                combo1_val, combo2_val = value
            widget = self.get_custom_widget()

            cb1_index = widget.combo_1.findText(combo1_val, QtCore.Qt.MatchExactly)
            cb2_index = widget.combo_1.findText(combo2_val, QtCore.Qt.MatchExactly)

            widget.combo_1.setCurrentIndex(cb1_index)
            widget.combo_2.setCurrentIndex(cb2_index)


    class MyNode(BaseNode):
        """
        Example node.
        """

        # set a unique node identifier.
        __identifier__ = 'io.github.jchanvfx'

        # set the initial default node name.
        NODE_NAME = 'my node'

        def __init__(self):
            super(MyNode, self).__init__()

            # create input and output port.
            self.add_input('in')
            self.add_output('out')

            # add custom widget to node with "node.view" as the parent.
            node_widget = NodeWidgetWrapper(self.view)
            self.add_custom_widget(node_widget, tab='Custom')

To hide/show the embedded widget on a :class:`NodeGraphQt.BaseNode` checkout the
:meth:`NodeGraphQt.BaseNode.hide_widget` and :meth:`NodeGraphQt.BaseNode.show_widget`
functions.

Connecting Nodes

---

There a multiple ways for connecting node ports here are a few examples below.

connecting nodes by the port index:

.. code-block:: python

    node_b.set_input(0, node_a.output(0))

connect nodes by the port name:

.. code-block:: python

    node_a.outputs()['bar'].connect_to(node_b.inputs()['foo'])

connecting nodes with the port objects:

.. code-block:: python

    # node_a "bar" output port.
    port_a = node_a.output(0)
    # node_b "foo" input port.
    port_b = node_b.inputs()['foo']
    # make the connection.
    port_a.connect_to(port_b)

`more on ports and connections.`

        - :func:`NodeGraphQt.BaseNode.input`
        - :func:`NodeGraphQt.BaseNode.output`
        - :func:`NodeGraphQt.BaseNode.set_input`
        - :func:`NodeGraphQt.BaseNode.set_output`
        - :func:`NodeGraphQt.BaseNode.inputs`
        - :func:`NodeGraphQt.BaseNode.outputs`
        - :func:`NodeGraphQt.Port.connect_to`
        - :func:`NodeGraphQt.Port.disconnect_from`

|

Connecting a PropertiesBin

---

Here's an example where we subclass the `NodeGraph` and connect it up to a
`PropertiesBinWidget` and have it show when a node is double clicked.

.. code-block:: python
:linenos:

    from Qt import QtCore, QtWidgets
    from NodeGraphQt import BaseNode, NodeGraph, PropertiesBinWidget


    class MyNode(BaseNode):

        __identifier__ = 'io.github.jchanvfx'
        NODE_NAME = 'my node'

        def __init__(self):
            super(MyNode, self).__init__()
            self.add_input('in')
            self.add_output('out')


    class MyNodeGraph(NodeGraph):

        def __init__(self, parent=None):
            super(MyNodeGraph, self).__init__(parent)

            # properties bin widget.
            self._prop_bin = PropertiesBinWidget(node_graph=self)
            self._prop_bin.setWindowFlags(QtCore.Qt.Tool)

            # wire signal.
            self.node_double_clicked.connect(self.display_prop_bin)

        def display_prop_bin(self, node):
            """
            function for displaying the properties bin when a node
            is double clicked
            """
            if not self._prop_bin.isVisible():
                self._prop_bin.show()


    if __name__ == '__main__':
        app = QtWidgets.QApplication([])

        node_graph = MyNodeGraph()
        node_graph.register_node(MyNode)
        node_graph.widget.show()

        node_a = node_graph.create_node('io.github.jchanvfx.MyNode')

        app.exec_()

`more on the properties bin and node_double_clicked signal`

    - :class:`NodeGraphQt.PropertiesBinWidget`
    - :attr:`NodeGraphQt.NodeGraph.node_double_clicked`

</code>

docs\examples\ex_overview.rst:
<code>
General Overview
################

User interface overview for the node graph.

.. image:: ../\_images/overview.png
:width: 70%

Navigation

---

+---------------+----------------------------------------------------+
| action | controls |
+===============+====================================================+
| Zoom In/Out | `Alt + MMB + Drag` or `Mouse Scroll Up/Down` |
+---------------+----------------------------------------------------+
| Pan | `Alt + LMB + Drag` or `MMB + Drag` |
+---------------+----------------------------------------------------+

Node Selection

---

.. image:: ../\_images/selection.png
:width: 500px

Nodes can be selected/unselected with the selection marquee using LMB + Drag

Tab Search

---

.. image:: ../\_images/node_search.png
:width: 269px

Nodes registered in the node graph can be created with the tab search widget.

+-------------------+----------+
| action | hotkey |
+===================+==========+
| Toggle Visibility | `Tab` |
+-------------------+----------+

Pipe Slicing

---

.. image:: ../\_images/slicer.png
:width: 600px

Connection pipes can be disconnected easily with the built in slice tool.

+---------------------+------------------------------+
| action | controls |
+=====================+==============================+
| Slice Connections | `Alt + Shift + LMB + Drag` |
+---------------------+------------------------------+

Additional Info:
To disable or enable the pipe slicer see
:meth:`NodeGraphQt.NodeGraph.set_pipe_slicing`

Basic Setup

---

Here's a basic example snippet for creating two nodes and connecting them together.

.. code-block:: python
:linenos:

    from Qt import QtWidgets
    from NodeGraphQt import NodeGraph, BaseNode


    # create a node class object inherited from BaseNode.
    class FooNode(BaseNode):

        # unique node identifier domain.
        __identifier__ = 'io.github.jchanvfx'

        # initial default node name.
        NODE_NAME = 'Foo Node'

        def __init__(self):
            super(FooNode, self).__init__()

            # create an input port.
            self.add_input('in', color=(180, 80, 0))

            # create an output port.
            self.add_output('out')


    if __name__ == '__main__':
        app = QtWidgets.QApplication([])

        # create node graph controller.
        graph = NodeGraph()

        # register the FooNode node class.
        graph.register_node(FooNode)

        # show the node graph widget.
        graph_widget = graph.widget
        graph_widget.show()

        # create two nodes.
        node_a = graph.create_node('io.github.jchanvfx.FooNode', name='node A')
        node_b = graph.create_node('io.github.jchanvfx.FooNode', name='node B', pos=(300, 50))

        # connect node_a to node_b
        node_a.set_output(0, node_b.input(0))

        app.exec_()

result:

.. image:: ../\_images/example_result.png
:width: 60%

</code>

docs\examples\ex_pipe.rst:
<code>
Pipe Overview
#############

Layout Styles

---

.. image:: ../\_images/pipe_layout_types.gif
:width: 650px

The :class:`NodeGraphQt.NodeGraph` class has 3 different pipe layout styles as
shown above this can be set easily with the :meth:`NodeGraphQt.NodeGraph.set_pipe_style`
function.

|
| Here's a example snippet for setting the pipe layout style to be "angled".

.. code-block:: python
:linenos:

    from NodeGraphQt import NodeGraph
    from NodeGraphQt.constants import PipeLayoutEnum

    graph = NodeGraph()
    graph.set_pipe_style(PipeLayoutEnum.ANGLE.value)

| There are 3 different pipe layout styles see: :attr:`NodeGraphQt.constants.PipeLayoutEnum`

.. note::

    If you've set up your node graph with the :meth:`NodeGraph.set_context_menu_from_file`
    function and the example
    `example JSON <https://github.com/jchanvfx/NodeGraphQt/blob/master/examples/hotkeys/hotkeys.json>`_
    then you'll already have the actions to set the pipe layout under the
    "Pipes" menu.

    .. image:: ../_images/pipe_layout_menu.png

Layout Direction

---

The :class:`NodeGraphQt.NodeGraph` pipes can also be set with a vertical layout
direction with the :meth:`NodeGraphQt.NodeGraph.set_layout_direction` function.

.. image:: ../\_images/vertical_layout.png

</code>

docs\examples\ex_port.rst:
<code>
Port Overview
#############

Creating Custom Shapes

---

| (_Implemented on_ `v0.1.1`)

To have custom port shapes the :meth:`NodeGraphQt.BaseNode.add_input` and
:meth:`NodeGraphQt.BaseNode.add_output` functions now have a `painter_func`
argument where you specify you custom port painter function.

.. image:: ../\_images/custom_ports.png
:width: 178px

|

Example Triangle Port

---

Here's an example function for drawing a triangle port.

.. code-block:: python
:linenos:

    def draw_triangle_port(painter, rect, info):
        """
        Custom paint function for drawing a Triangle shaped port.

        Args:
            painter (QtGui.QPainter): painter object.
            rect (QtCore.QRectF): port rect used to describe parameters needed to draw.
            info (dict): information describing the ports current state.
                {
                    'port_type': 'in',
                    'color': (0, 0, 0),
                    'border_color': (255, 255, 255),
                    'multi_connection': False,
                    'connected': False,
                    'hovered': False,
                }
        """
        painter.save()

        # create triangle polygon.
        size = int(rect.height() / 2)
        triangle = QtGui.QPolygonF()
        triangle.append(QtCore.QPointF(-size, size))
        triangle.append(QtCore.QPointF(0.0, -size))
        triangle.append(QtCore.QPointF(size, size))

        # map polygon to port position.
        transform = QtGui.QTransform()
        transform.translate(rect.center().x(), rect.center().y())
        port_poly = transform.map(triangle)

        # mouse over port color.
        if info['hovered']:
            color = QtGui.QColor(14, 45, 59)
            border_color = QtGui.QColor(136, 255, 35)
        # port connected color.
        elif info['connected']:
            color = QtGui.QColor(195, 60, 60)
            border_color = QtGui.QColor(200, 130, 70)
        # default port color
        else:
            color = QtGui.QColor(*info['color'])
            border_color = QtGui.QColor(*info['border_color'])

        pen = QtGui.QPen(border_color, 1.8)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)

        painter.setPen(pen)
        painter.setBrush(color)
        painter.drawPolygon(port_poly)

        painter.restore()

The `draw_triangle_port` painter function can then be passed to the `painter_func` arg.

.. code-block:: python
:linenos:
:emphasize-lines: 8

    from NodeGraphQt import BaseNode

    class MyListNode(BaseNode):

        def __init__(self):
            super(MyListNode, self).__init__()
            # create a input port with custom painter function.
            self.add_input('triangle', painter_func=draw_triangle_port)

|

Example Square Port

---

And here's another example function for drawing a Square port.

.. code-block:: python
:linenos:

    def draw_square_port(painter, rect, info):
        """
        Custom paint function for drawing a Square shaped port.

        Args:
            painter (QtGui.QPainter): painter object.
            rect (QtCore.QRectF): port rect used to describe parameters needed to draw.
            info (dict): information describing the ports current state.
                {
                    'port_type': 'in',
                    'color': (0, 0, 0),
                    'border_color': (255, 255, 255),
                    'multi_connection': False,
                    'connected': False,
                    'hovered': False,
                }
        """
        painter.save()

        # mouse over port color.
        if info['hovered']:
            color = QtGui.QColor(14, 45, 59)
            border_color = QtGui.QColor(136, 255, 35, 255)
        # port connected color.
        elif info['connected']:
            color = QtGui.QColor(195, 60, 60)
            border_color = QtGui.QColor(200, 130, 70)
        # default port color
        else:
            color = QtGui.QColor(*info['color'])
            border_color = QtGui.QColor(*info['border_color'])

        pen = QtGui.QPen(border_color, 1.8)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)

        painter.setPen(pen)
        painter.setBrush(color)
        painter.drawRect(rect)

        painter.restore()

Connection Constrains

---

From version `v0.6.0` port object can now have pipe connection constraints the functions implemented are:

- :meth:`NodeGraphQt.Port.add_accept_port_type`
- :meth:`NodeGraphQt.Port.add_reject_port_type`

this can also be set on the `BaseNode` level as well with:

- :meth:`NodeGraphQt.BaseNode.add_accept_port_type`
- :meth:`NodeGraphQt.BaseNode.add_accept_port_type`

Here's an example snippet to add pipe connection constraints to a port.

.. code-block:: python
:linenos:

    from NodeGraphQt import BaseNode
    from NodeGraphQt.constants import PortTypeEnum


    class BasicNodeA(BaseNode):

        # unique node identifier.
        __identifier__ = 'io.github.jchanvfx'

        # initial default node name.
        NODE_NAME = 'node A'

        def __init__(self):
            super(BasicNode, self).__init__()

            # create node output ports.
            self.add_output('output 1')
            self.add_output('output 2')


    class BasicNodeB(BaseNode):

        # unique node identifier.
        __identifier__ = 'io.github.jchanvfx'

        # initial default node name.
        NODE_NAME = 'node B'

        def __init__(self):
            super(BasicNode, self).__init__()

            # create node inputs.

            # port "in A" will only accept pipe connections from port "output 1"
            # under the node "BasicNodeA".
            in_port_a = self.add_input('in A')
            in_port_a.add_accept_port_type(
                port_name='output 1',
                port_type=PortTypeEnum.OUT.value,
                node_type='io.github.jchanvfx.BasicNodeA'
            )

            # port "in A" will reject pipe connections from port "output 1"
            # under the node "BasicNodeA".
            in_port_b = self.add_input('in B')
            in_port_b.add_reject_port_type(
                port_name='output 1',
                port_type=PortTypeEnum.OUT.value,
                node_type='io.github.jchanvfx.BasicNodeA'
            )

</code>

docs\graphs\NodeGraph.rst:
<code>
:hide-rtoc:

NodeGraph
#########

.. autosummary::
NodeGraphQt.NodeGraph

.. code-block:: python
:linenos:

    from Qt import QtWidgets
    from NodeGraphQt import NodeGraph

    if __name__ == '__main__':
        app = QtWidgets.QApplication([])

        node_graph = NodeGraph()

        widget = node_graph.widget
        widget.show()

        app.exec_()

---

.. autoclass:: NodeGraphQt.NodeGraph
:members:
:member-order: bysource
:exclude-members: staticMetaObject

</code>

docs\graphs\SubGraph.rst:
<code>
:hide-rtoc:

SubGraph
########

.. autosummary::
NodeGraphQt.SubGraph

.. autoclass:: NodeGraphQt.SubGraph
:members:
:exclude-members: staticMetaObject, delete_node, delete_nodes, is_root, sub_graphs, widget

</code>

docs\graphs_index_graphs.rst:
<code>
Graphs

######

`See` :ref:`Getting Started` `from the overview section.`

.. toctree::
:caption: Graph Classes
:name: graphstoc
:maxdepth: 2
:titlesonly:

    NodeGraph
    SubGraph

</code>

docs\host_apps\ex_app_nuke.rst:
<code>
Nuke

####

Creating a node graph widget in Nuke.

.. image:: ../\_images/app_nuke_example.png
:width: 800px

| Here is an example where the :attr:`NodeGraphQt.NodeGraph.widget` can be
registered as a panel in the compositing application NUKE.

.. code-block:: python
:linenos:

    from nukescripts import panels

    from Qt import QtWidgets, QtCore
    from NodeGraphQt import NodeGraph, BaseNode


    # create a simple test node class.
    class TestNode(BaseNode):

        __identifier__ = 'nodes.nuke'
        NODE_NAME = 'test node'

        def __init__(self):
            super(TestNode, self).__init__()
            self.add_input('in')
            self.add_output('out 1')
            self.add_output('out 2')


    # create the node graph controller and register our "TestNode".
    graph = NodeGraph()
    graph.register_node(TestNode)

    # create nodes.
    node_1 = graph.create_node('nodes.nuke.TestNode')
    node_2 = graph.create_node('nodes.nuke.TestNode')
    node_3 = graph.create_node('nodes.nuke.TestNode')

    # connect the nodes.
    node_1.set_output(0, node_2.input(0))
    node_2.set_output(1, node_3.input(0))

    # auto layout the nodes.
    graph.auto_layout_nodes()

    # create a backdrop node and wrap it to node_1 and node_2.
    backdrop = graph.create_node('Backdrop')
    backdrop.wrap_nodes([node_1, node_2])


    # create the wrapper widget.
    class CustomNodeGraph(QtWidgets.QWidget):

        def __init__(self, parent=None):
            super(CustomNodeGraph, self).__init__(parent)
            layout = QtWidgets.QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(graph.widget)

        @staticmethod
        def _set_nuke_zero_margin(widget_object):
            """
            Foundry Nuke hack for "nukescripts.panels.registerWidgetAsPanel" to
            remove the widget contents margin.

            sourced from: https://gist.github.com/maty974/4739917

            Args:
                widget_object (QtWidgets.QWidget): widget object.
            """
            if widget_object:
                parent_widget = widget_object.parentWidget().parentWidget()
                target_widgets = set()
                target_widgets.add(parent_widget)
                target_widgets.add(parent_widget.parentWidget().parentWidget())
                for widget_layout in target_widgets:
                    widget_layout.layout().setContentsMargins(0, 0, 0, 0)

        def event(self, event):
            if event.type() == QtCore.QEvent.Type.Show:
                try:
                    self._set_nuke_zero_margin(self)
                except Exception:
                    pass
            return super(CustomNodeGraph, self).event(event)

    # register the wrapper widget as a panel in Nuke.
    panels.registerWidgetAsPanel(
        widget='CustomNodeGraph',
        name='Custom Node Graph',
        id='nodegraphqt.graph.CustomNodeGraph'
    )

</code>

docs\host_apps\ex_app_silhouette.rst:
<code>
Silhouette
##########

Creating a node graph widget in Silhouette FX.

.. note::
Requires Silhouette `7.x` or above as previous versions don't
come built-in with its own PySide2 build or provide access to the
`QMainWindow` object.

.. image:: ../\_images/app_silhouette_example.png
:width: 800px

| Here is an example where the :attr:`NodeGraphQt.NodeGraph.widget` can be
registered as a dockable panel in the application .

.. code-block:: python
:linenos:

    import fx

    from Qt import QtWidgets, QtCore
    from NodeGraphQt import NodeGraph, BaseNode


    # create the widget wrapper that can be docked to the main window.
    class NodeGraphPanel(QtWidgets.QDockWidget):
        """
        Widget wrapper for the node graph that can be docked to
        the main window.
        """

        def __init__(self, graph, parent=None):
            super(NodeGraphPanel, self).__init__(parent)
            self.setObjectName('nodeGraphQt.NodeGraphPanel')
            self.setWindowTitle('Custom Node Graph')
            self.setWidget(graph.widget)


    # create a simple test node class.
    class TestNode(BaseNode):

        __identifier__ = 'nodes.silhouettefx'
        NODE_NAME = 'test node'

        def __init__(self):
            super(TestNode, self).__init__()
            self.add_input('in')
            self.add_output('out')


    # create the node graph controller and register our "TestNode"
    graph = NodeGraph()
    graph.register_node(TestNode)

    # create nodes.
    node_1 = graph.create_node('nodes.silhouette.TestNode')
    node_2 = graph.create_node('nodes.silhouette.TestNode')
    node_3 = graph.create_node('nodes.silhouette.TestNode')

    # create the node graph panel that can be docked.
    sfx_graph_panel = NodeGraphPanel(graph)

    # add the doc widget into the main silhouette window.
    sfx_window = fx.ui.mainWindow()
    sfx_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, sfx_graph_panel)

</code>

docs\host_apps_index_apps.rst:
<code>
Host Application Examples
#########################

| Here are a list of examples for implementing a custom node graph into the
host application.

.. toctree::
:caption: Host Applications
:name: appstoc
:maxdepth: 2
:titlesonly:

    ex_app_nuke
    ex_app_silhouette

</code>

docs\nodes\BackdropNode.rst:
<code>
:hide-rtoc:

BackdropNode
############

.. autoclass:: NodeGraphQt.BackdropNode
:members:
:member-order: bysource
:exclude-members: NODE_NAME

</code>

docs\nodes\BaseNode.rst:
<code>
:hide-rtoc:

BaseNode
########

.. autoclass:: NodeGraphQt.BaseNode
:members:
:exclude-members: NODE_NAME, update_model, set_layout_direction, set_property
:member-order: bysource

BaseNode (Circle)
#################

.. autoclass:: NodeGraphQt.BaseNodeCircle
:members:
:exclude-members: NODE_NAME, update_model, set_layout_direction
:member-order: bysource
</code>

docs\nodes\GroupNode.rst:
<code>
:hide-rtoc:

GroupNode
#########

.. autoclass:: NodeGraphQt.GroupNode
:members:
:exclude-members: NODE_NAME, add_input, add_output, delete_input, delete_output
:member-order: bysource
</code>

docs\nodes\NodeObject.rst:
<code>
:hide-rtoc:

NodeObject
##########

.. autoclass:: NodeGraphQt.NodeObject
:members:
:member-order: bysource
:special-members: **identifier**

</code>

docs\nodes\PortNode.rst:
<code>
:hide-rtoc:

Port Nodes
##########

| Port nodes are the nodes in a expanded :class:`NodeGraphQt.SubGraph` that
represent the ports from the parent :class:`NodeGraphQt.GroupNode` object.

**Classes:**

.. autosummary::
NodeGraphQt.nodes.port_node.PortInputNode
NodeGraphQt.nodes.port_node.PortOutputNode

---

.. hint::

    Port node objects can be accessed in a expanded
    :class:`NodeGraphQt.GroupNode` with:

    - :meth:`NodeGraphQt.SubGraph.get_node_by_port`,
    - :meth:`NodeGraphQt.SubGraph.get_input_port_nodes`,
    - :meth:`NodeGraphQt.SubGraph.get_output_port_nodes`

|

# PortInputNode

.. autoclass:: NodeGraphQt.nodes.port_node.PortInputNode
:members:
:member-order: bysource
:exclude-members: NODE_NAME

|

# PortOutputNode

.. autoclass:: NodeGraphQt.nodes.port_node.PortOutputNode
:members:
:member-order: bysource
:exclude-members: NODE_NAME

</code>

docs\nodes_index_nodes.rst:
<code>
Nodes

#####

| Node object types from the `NodeGraphQt` module.

.. toctree::
:caption: Node Classes
:name: nodestoc
:maxdepth: 2
:titlesonly:

    NodeObject
    BackdropNode
    BaseNode
    GroupNode
    PortNode

</code>

docs_static\custom.css:
<code>
:root{
--background:0 0% 100%;
--foreground:180 50% 20%;
--muted:210 40% 96.1%;
--muted-foreground:215.4 16.3% 46.9%;
--popover:0 0% 100%;
--popover-foreground:222.2 47.4% 11.2%;
--border:214.3 31.8% 91.4%;
--input:214.3 31.8% 91.4%;
--card:0 0% 100%;
--card-foreground:222.2 47.4% 11.2%;
--primary:222.2 47.4% 11.2%;
--primary-foreground:210 40% 98%;
--secondary:210 40% 96.1%;
--secondary-foreground:222.2 47.4% 11.2%;
--accent:210 40% 96.1%;
--accent-foreground:179 63% 46%;
--destructive:0 100% 50%;
--destructive-foreground:210 40% 98%;
--ring:215 20.2% 65.1%;
--radius:0.5rem;

    --caption-color: #d779a9;
    --a-link: #0081d7;

}
.dark {
--background: 250 20% 2%;
--foreground: 210 50% 80%;
--muted: 223 47% 11%;
--muted-foreground: 39 45% 64%;
--accent: 216 34% 17%;
--accent-foreground: 167 96% 38%;
--popover: 224 71% 4%;
--popover-foreground: 215 20.2% 65.1%;
--border: 216 34% 17%;
--input: 216 34% 17%;
--card: 224 71% 4%;
--card-foreground: 213 31% 91%;
--primary: 210 40% 98%;
--primary-foreground: 222.2 47.4% 1.2%;
--secondary: 222.2 47.4% 11.2%;
--secondary-foreground: 210 40% 98%;
--destructive: 0 63% 31%;
--destructive-foreground: 210 40% 98%;
--ring: 216 34% 17%;
--radius: 0.5rem;

    --caption-color: #7d2853;
    --a-link: #48cdf8;

}

.caption {
color: var(--caption-color);
}
#content a:not(.toc-backref) {
color: var(--a-link);
font-weight: 500;
text-decoration-line: none;
text-decoration-thickness: from-font;
text-underline-offset: 4px;
}
</code>

docs_static\pygments.css:
<code>
.linenos,
td.lineos {
margin: 0px 10px;
padding: 1px 8px;
color: #818181;
}
.linenos pre {
background-color: transparent;
color: #aaa;
-webkit-box-shadow: none;
-moz-box-shadow: none;
}
.hll {
background-color: #233150;
display: block;
}
.code {
background: #232629; !important;
}
.highlight pre {
background: #0b0d0f !important;
padding-left: 18px;
}
.highlight pre {
color: #2fb37a;
border: 1px solid #1c2a38;
border-radius: 10px;
-webkit-box-shadow: none;
-moz-box-shadow: none;
}

.highlight .c { color: #75715e } /_ Comment _/
.highlight .err { color: #960050; background-color: #1e0010 } /_ Error _/
.highlight .k { color: #66d9ef } /_ Keyword _/
.highlight .l { color: #ae81ff } /_ Literal _/
.highlight .n { color: #f8f8f2 } /_ Name _/
.highlight .o { color: #f92672 } /_ Operator _/
.highlight .p { color: #f8f8f2 } /_ Punctuation _/
.highlight .cm { color: #75715e } /_ Comment.Multiline _/
.highlight .cp { color: #75715e } /_ Comment.Preproc _/
.highlight .c1 { color: #75715e } /_ Comment.Single _/
.highlight .cs { color: #75715e } /_ Comment.Special _/
.highlight .ge { font-style: italic } /_ Generic.Emph _/
.highlight .gs { font-weight: bold } /_ Generic.Strong _/
.highlight .kc { color: #66d9ef } /_ Keyword.Constant _/
.highlight .kd { color: #66d9ef } /_ Keyword.Declaration _/
.highlight .kn { color: #f92672 } /_ Keyword.Namespace _/
.highlight .kp { color: #66d9ef } /_ Keyword.Pseudo _/
.highlight .kr { color: #66d9ef } /_ Keyword.Reserved _/
.highlight .kt { color: #66d9ef } /_ Keyword.Type _/
.highlight .ld { color: #e6db74 } /_ Literal.Date _/
.highlight .m { color: #ae81ff } /_ Literal.Number _/
.highlight .s { color: #e6db74 } /_ Literal.String _/
.highlight .na { color: #a6e22e } /_ Name.Attribute _/
.highlight .nb { color: #f8f8f2 } /_ Name.Builtin _/
.highlight .nc { color: #a6e22e } /_ Name.Class _/
.highlight .no { color: #66d9ef } /_ Name.Constant _/
.highlight .nd { color: #a6e22e } /_ Name.Decorator _/
.highlight .ni { color: #f8f8f2 } /_ Name.Entity _/
.highlight .ne { color: #a6e22e } /_ Name.Exception _/
.highlight .nf { color: #a6e22e } /_ Name.Function _/
.highlight .nl { color: #f8f8f2 } /_ Name.Label _/
.highlight .nn { color: #f8f8f2 } /_ Name.Namespace _/
.highlight .nx { color: #a6e22e } /_ Name.Other _/
.highlight .py { color: #f8f8f2 } /_ Name.Property _/
.highlight .nt { color: #f92672 } /_ Name.Tag _/
.highlight .nv { color: #f8f8f2 } /_ Name.Variable _/
.highlight .ow { color: #f92672 } /_ Operator.Word _/
.highlight .w { color: #f8f8f2 } /_ Text.Whitespace _/
.highlight .mf { color: #ae81ff } /_ Literal.Number.Float _/
.highlight .mh { color: #ae81ff } /_ Literal.Number.Hex _/
.highlight .mi { color: #ae81ff } /_ Literal.Number.Integer _/
.highlight .mo { color: #ae81ff } /_ Literal.Number.Oct _/
.highlight .sb { color: #e6db74 } /_ Literal.String.Backtick _/
.highlight .sc { color: #e6db74 } /_ Literal.String.Char _/
.highlight .sd { color: #e6db74 } /_ Literal.String.Doc _/
.highlight .s2 { color: #e6db74 } /_ Literal.String.Double _/
.highlight .se { color: #ae81ff } /_ Literal.String.Escape _/
.highlight .sh { color: #e6db74 } /_ Literal.String.Heredoc _/
.highlight .si { color: #e6db74 } /_ Literal.String.Interpol _/
.highlight .sx { color: #e6db74 } /_ Literal.String.Other _/
.highlight .sr { color: #e6db74 } /_ Literal.String.Regex _/
.highlight .s1 { color: #e6db74 } /_ Literal.String.Single _/
.highlight .ss { color: #e6db74 } /_ Literal.String.Symbol _/
.highlight .bp { color: #f8f8f2 } /_ Name.Builtin.Pseudo _/
.highlight .vc { color: #f8f8f2 } /_ Name.Variable.Class _/
.highlight .vg { color: #f8f8f2 } /_ Name.Variable.Global _/
.highlight .vi { color: #f8f8f2 } /_ Name.Variable.Instance _/
.highlight .il { color: #ae81ff } /_ Literal.Number.Integer.Long _/

</code>

docs_templates\searchbox.html:
<code>
{#- Template for the search box in the header. -#}
{%- if docsearch %}

  <div id="{{ docsearch_container[1:]|default('docsearch') }}"></div>
{%- else %}
  <form id="searchbox"
        action="{{ pathto('search') }}"
        method="get"
        class="relative flex items-center group"
        @keydown.k.window.meta="$refs.search.focus()">
    <input x-ref="search"
           name="q"
           id="search-input"
           type="search"
           aria-label="Search the docs"
           placeholder="{{ _('Search ...') }}"
           class="inline-flex items-center font-medium transition-colors bg-transparent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ring-offset-background border border-input hover:bg-accent focus:bg-accent hover:text-accent-foreground focus:text-accent-foreground hover:placeholder-accent-foreground py-2 px-4 relative h-9 w-full justify-start rounded-[0.5rem] text-sm text-muted-foreground sm:pr-12 md:w-40 lg:w-64" />
    <kbd class="pointer-events-none absolute right-1.5 top-2 hidden h-5 select-none text-muted-foreground items-center gap-1 rounded border border-border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex group-hover:bg-accent group-hover:text-accent-foreground">
      <span class="text-xs">&#x1F50D;&#xFE0E;</span>
    </kbd>
  </form>
{%- endif -%}

</code>

docs_templates\sidebar_toc.html:
<code>

<nav class="table w-full min-w-full my-6 lg:my-8">
  {%- if theme_globaltoc_includehidden|tobool %}
  {{ toctree(titles_only=true, collapse=False, includehidden=true) }}
  {%- else %}
  {{ toctree(titles_only=true, collapse=False) }}
  {%- endif %}
  <br>
  <code style="font-size: 0.65rem;">{{ project }} - v{{ release }}</code>
</nav>

</code>

docs_templates\toc.html:
<code>
{%- if meta is mapping %}
{%- if "hide-rtoc" not in meta %}
{#- Template for the on-page TOC -#}

<aside id="right-sidebar" class="hidden text-sm xl:block">
  <div class="sticky top-16 -mt-10 max-h-[calc(var(--vh)-4rem)] overflow-y-auto pt-6 space-y-2">
    {%- block toc_before %}{%- endblock -%}
    <p class="font-medium">Page Contents</p>
    {{ toc }}
    {%- block toc_after %}{%- endblock -%}
  </div>
</aside>
{%- endif %}
{%- endif %}

</code>

docs_themes\sphinxawesome_theme\breadcrumbs.html:
<code>
{#- Template file for the breadcrumbs. -#}
{%- set separator %}

<div class="mr-1">{{ theme_breadcrumbs_separator|default('/') }}</div>
{%- endset %}
<nav aria-label="{{ _('breadcrumbs') }}"
     class="flex items-center mb-4 space-x-1 text-sm text-muted-foreground">
  <a class="overflow-hidden text-ellipsis whitespace-nowrap hover:text-foreground"
     href="{{ pathto(master_doc) }}">
    <span class="hidden md:inline">{{ docstitle }}</span>
    <svg xmlns="http://www.w3.org/2000/svg"
         height="18"
         width="18"
         viewBox="0 96 960 960"
         aria-label="Home"
         fill="currentColor"
         stroke="none"
         class="md:hidden">
      <path d="M240 856h120V616h240v240h120V496L480 316 240 496v360Zm-80 80V456l320-240 320 240v480H520V696h-80v240H160Zm320-350Z" />
    </svg>
  </a>
  {{ separator }}
  {%- for doc in parents -%}
    <a class="hover:text-foreground overflow-hidden text-ellipsis whitespace-nowrap"
       href="{{ doc.link|e }}">{{ doc.title
    }}</a>
    {{ separator }}
  {%- endfor -%}
  <span aria-current="page"
        class="font-medium text-foreground overflow-hidden text-ellipsis whitespace-nowrap">{{ title
  }}</span>
</nav>

</code>

docs_themes\sphinxawesome_theme\deprecated.py:
<code>
"""Check for deprecated options.

This extension checks if you're using a deprecated option from the
sphinxawesome_theme from a version < 5.0.

Theme options in the `html_theme_options` dictionary are handled automatically.
Regular configuration options however need to be checked separately,
because the HTML theme is loaded _after_ the configuration is handled,
and extensions are already processed.

To load this extension, add:

.. code-block:: python
:caption: |conf|

extensions += ["sphinxawesome_theme.deprecated"]

:copyright: Kai Welke.
:license: MIT, see LICENSE for details
"""
from **future** import annotations

from typing import Any

from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util import logging

from . import **version**

logger = logging.getLogger(**name**)

def check_deprecated(app: Sphinx, config: Config) -> None: # noqa: C901
"""Check the Sphinx configuration for the deprecated options and migrate them automatically if possible."""
raw = config.\_raw_config
found_deprecated = False

    if "html_collapsible_definitions" in raw:
        logger.warning(
            "`html_collapsible_definitions` is deprecated. "
            "Use the `sphinx-design` extension instead."
        )
        found_deprecated = True

    if "html_awesome_headerlinks" in raw:
        logger.warning(
            "`html_awesome_headerlinks` is deprecated. "
            "Use `html_theme_options = {'awesome_headerlinks: True '} instead."
        )
        config.html_theme_options["awesome_headerlinks"] = raw[
            "html_awesome_headerlinks"
        ]
        found_deprecated = True

    if "html_awesome_external_links" in raw:
        logger.warning(
            "`html_awesome_external_links` is deprecated. "
            "Use `html_theme_options = {'awesome_external_links: True '} instead."
        )
        config.html_theme_options["awesome_external_links"] = raw[
            "html_awesome_external_links"
        ]
        found_deprecated = True

    # Since this won't have any effect, it shouldn't be a warning.
    if "html_awesome_code_headers" in raw:
        logger.info(
            "`html_awesome_code_headers` is deprecated. "
            "You can remove it from your Sphinx configuration."
        )
        found_deprecated = True

    if "html_awesome_docsearch" in raw:
        logger.warning(
            "`html_awesome_docsearch` is deprecated. "
            "Use the bundled `sphinxawesome_theme.docsearch` extension instead."
        )
        found_deprecated = True

        if raw["html_awesome_docsearch"]:
            app.setup_extension("sphinxawesome_theme.docsearch")

    if "docsearch_config" in raw:
        logger.warning(
            "Using the `docsearch_config` dictionary is deprecated. "
            "Load the bundled `sphinxawesome_theme.docsearch` extension and configure DocSearch with `docsearch_*` variables."
        )
        found_deprecated = True

        # Only process the docsearch options if the user actually wants DocSearch
        if (
            "sphinxawesome_theme.docsearch" in app.extensions
            and raw["docsearch_config"]
            and raw["html_awesome_docsearch"]
        ):
            ds_conf = raw["docsearch_config"]
            if "app_id" in ds_conf:
                config.docsearch_app_id = ds_conf["app_id"]  # type: ignore[attr-defined]

            if "api_key" in ds_conf:
                config.docsearch_api_key = ds_conf["api_key"]  # type: ignore[attr-defined]

            if "index_name" in ds_conf:
                config.docsearch_index_name = ds_conf["index_name"]  # type: ignore[attr-defined]

            if "container" in ds_conf:
                config.docsearch_container = ds_conf["container"]  # type: ignore[attr-defined]

    if found_deprecated is False:
        logger.info(
            "No deprecated options found. You can remove the `sphinxawesome_theme.deprecated` extension."
        )

def setup(app: Sphinx) -> dict[str, Any]:
"""Register the extension."""
if "sphinxawesome_theme" in app.config.extensions:
logger.warning(
"Including `sphinxawesome_theme` in your `extensions` is deprecated. "
'Setting `html_theme = "sphinxawesome_theme"` is enough. '
"You can load the optional `sphinxawesome_theme.docsearch` and `sphinxawesome_theme.highlighting` extensions."
)
app.setup_extension("sphinxawesome_theme.highlighting")
app.setup_extension("sphinxawesome_theme.docsearch")

    # If we don't register these options, Sphinx ignores them when evaluating the `conf.py` file.
    app.add_config_value(
        name="html_collapsible_definitions", default=False, rebuild="html", types=(bool)
    )
    app.add_config_value(
        name="html_awesome_external_links", default=False, rebuild="html", types=(bool)
    )
    app.add_config_value(
        name="html_awesome_docsearch", default=False, rebuild="html", types=(bool)
    )
    app.add_config_value(
        name="docsearch_config", default={}, rebuild="html", types=(dict)
    )
    app.add_config_value(
        name="html_awesome_headerlinks", default=True, rebuild="html", types=(str)
    )
    app.add_config_value(
        name="html_awesome_code_headers", default=True, rebuild="html", types=(str)
    )

    app.connect("config-inited", check_deprecated)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

</code>

docs_themes\sphinxawesome_theme\docsearch.py:
<code>
"""Add Algolia DocSearch to Sphinx.

This extension replaces the built-in search in Sphinx with Algolia DocSearch.
To load this extension, add:

.. code-block:: python
:caption: |conf|

extensions += ["sphinxawesome_theme.docsearch"]

:copyright: Kai Welke.
:license: MIT, see LICENSE for details
"""
from **future** import annotations

from dataclasses import dataclass, fields
from typing import Any

from docutils.nodes import Node
from sphinx.application import Sphinx
from sphinx.builders.dirhtml import DirectoryHTMLBuilder
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.config import Config
from sphinx.locale import \_\_
from sphinx.util import logging
from sphinx.util.display import progress_message

from . import **version**

logger = logging.getLogger(**name**)

@dataclass
class DocSearchConfig:
"""Configuration options for DocSearch.

    This class defines and documents the configuration options for the :py:mod:`sphinxawesome_theme.docsearch` extension.
    To configure DocSearch, you must use regular Python variables. For example:

    .. code-block:: python
       :caption: |conf|

       from sphinxawesome_theme.docsearch import DocSearchConfig

       config = DocSearchConfig(
           docsearch_app_id="DOCSEARCH_APP_ID"
           # Other options
       )

       docsearch_app_id = config.docsearch_app_id
    """

    docsearch_app_id: str
    """Your Algolia DocSearch application ID.

    You **must** provide an application ID or DocSearch won't work.
    """

    docsearch_api_key: str
    """Your Algolia DocSearch Search API key.

    You **must** provide your search API key or DocSearch won't work.

    .. caution::

       Don't expose your write API key.
    """

    docsearch_index_name: str
    """Your Algolia DocSearch index name.

    You **must** provide an index name or DocSearch won't work.
    """

    docsearch_container: str = "#docsearch"
    """A CSS selector where the DocSearch UI should be injected."""

    docsearch_placeholder: str | None = None
    """A placeholder for the search input.

    By default, DocSearch uses *Search docs*.
    """

    docsearch_initial_query: str | None = None
    """If you want to perform a search before the user starts typing."""

    docsearch_search_parameter: str | None = None
    """If you want to add `Algolia search parameter <https://www.algolia.com/doc/api-reference/search-api-parameters/>`_."""

    docsearch_missing_results_url: str | None = None
    """A URL for letting users send you feedback about your search.

    You can use the current query in the URL as ``${query}``. For example:

    .. code-block:: python

       docsearch_missing_results_url = "https://github.com/example/docs/issues/new?title=${query}"
    """

@progress_message("DocSearch: check config")
def check_config(app: Sphinx, config: Config) -> None:
"""Set up Algolia DocSearch.

    Log warnings if any of these configuration options are missing:

    - ``docsearch_app_id``
    - ``docsearch_api_key``
    - ``docsearch_index_name``
    """
    if not config.docsearch_app_id:
        logger.warning(
            __("You must provide your Algolia application ID for DocSearch to work.")
        )
    if not config.docsearch_api_key:
        logger.warning(
            __("You must provide your Algolia search API key for DocSearch to work.")
        )
    if not config.docsearch_index_name:
        logger.warning(
            __("You must provide your Algolia index name for DocSearch to work.")
        )

@progress_message("DocSearch: add assets")
def add_docsearch_assets(app: Sphinx, config: Config) -> None:
"""Add the docsearch.css file for DocSearch."""
app.add_css_file("docsearch.css", priority=150) # TODO: add_js_file (currently in `layout.html` I think)

def update_global_context(app: Sphinx, doctree: Node, docname: str) -> None:
"""Update global context with DocSearch configuration."""
if hasattr(app.builder, "globalcontext"):
app.builder.globalcontext["docsearch"] = True
app.builder.globalcontext["docsearch_app_id"] = app.config.docsearch_app_id
app.builder.globalcontext["docsearch_api_key"] = app.config.docsearch_api_key
app.builder.globalcontext[
"docsearch_index_name"
] = app.config.docsearch_index_name
app.builder.globalcontext[
"docsearch_container"
] = app.config.docsearch_container
app.builder.globalcontext[
"docsearch_initial_query"
] = app.config.docsearch_initial_query
app.builder.globalcontext[
"docsearch_placeholder"
] = app.config.docsearch_placeholder
app.builder.globalcontext[
"docsearch_search_parameter"
] = app.config.docsearch_search_parameter
app.builder.globalcontext[
"docsearch_missing_results_url"
] = app.config.docsearch_missing_results_url

def remove_script_files(
app: Sphinx,
pagename: str,
templatename: str,
context: dict[str, Any],
doctree: Node,
) -> None:
"""Remove Sphinx JavaScript files when using DocSearch."""
context["script_files"].remove("\_static/documentation_options.js")
context["script_files"].remove("\_static/doctools.js")
context["script_files"].remove("\_static/sphinx_highlight.js")

def setup(app: Sphinx) -> dict[str, Any]:
"""Register the extension.""" # Get the configuration from a single-source of truth # This makes it easy to document.
for option in fields(DocSearchConfig):
default = option.default if isinstance(option.default, str) else ""
app.add_config_value(option.name, default=default, rebuild="html", types=(str))

    app.connect("config-inited", check_config)
    app.connect("config-inited", add_docsearch_assets)
    app.connect("doctree-resolved", update_global_context)
    app.connect("html-page-context", remove_script_files)

    # Disable built-in search
    StandaloneHTMLBuilder.search = False
    DirectoryHTMLBuilder.search = False

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

</code>

docs_themes\sphinxawesome_theme\footer.html:
<code>
{#- Template for the footer. -#}

<footer class="py-6 border-t border-border md:py-0">
  {%- block footer_before %}{%- endblock footer_before %}
    <div class="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
      <div class="flex flex-col items-center gap-4 px-8 md:flex-row md:gap-2 md:px-0">
        <p class="text-sm leading-loose text-center text-muted-foreground md:text-left">
          {%- if show_copyright and copyright|length -%}
            {%- if hasdoc('copyright') -%}
              {%- trans path=pathto('copyright'), copyright=copyright|e -%}
              © <a href="{{ path }}">Copyright</a>{{ copyright }}
            {%- endtrans -%}
          {%- else -%}
            {%- trans copyright=copyright|e -%}
            © {{ copyright }}&nbsp;
          {%- endtrans -%}
        {%- endif -%}
      {%- endif -%}
      {%- if last_updated -%}
        {%- trans last_updated=last_updated|e -%}
        Last updated: {{ last_updated }}.&nbsp;
      {%- endtrans -%}
    {%- endif -%}
    {%- if show_sphinx -%}
      {%- trans sphinx_version=sphinx_version|e -%}
      Built with <a class="font-medium underline underline-offset-4"
    href="https://www.sphinx-doc.org"
    rel="noreferrer">Sphinx {{ sphinx_version }}</a>
    {%- endtrans -%}
  {%- endif -%}
</p>
</div>
</div>
{%- block footer_after %}{%- endblock footer_after %}
</footer>

</code>

docs_themes\sphinxawesome_theme\header.html:
<code>
{#- Template file for the header -#}

<header
  class="sticky top-0 z-40 w-full border-b shadow-sm border-border supports-backdrop-blur:bg-background/60 bg-background/95 backdrop-blur">

{#- Extra block at the top of the header #}
{%- block header_before %}{% endblock header_before -%}

  <div class="container flex items-center h-14">
    {#- show logo and extra header links on the left side of the header -#}
    {%- block header_left %}
    <div class="hidden mr-4 md:flex">
      {%- block header_logo %}
      <a href="{{ pathto(master_doc) }}" class="flex items-center mr-6">
        {%- if logo_url %}
          <img height="24" width="24" class="mr-2 dark:invert" src="{{ logo_url }}" alt="Logo" />
        {%- endif -%}
        {%- if theme_logo_dark and not logo_url %}
          <img width="24" height="24" class="mr-2 hidden dark:block" src="{{ pathto('_static/' + theme_logo_dark, 1) }}" alt="Logo" />
        {%- endif -%}
        {%- if theme_logo_light and not logo_url %}
        <img width="24" height="24" class="mr-2 dark:hidden" src="{{ pathto('_static/' + theme_logo_light, 1) }}" alt="Logo" />
        {%- endif -%}
        <span class="hidden font-bold sm:inline-block text-clip whitespace-nowrap">{{ docstitle }}</span>
      </a>
      {%- endblock header_logo %}

      {%- block header_main_nav %}
      {%- if theme_main_nav_links|tobool -%}
      <nav class="flex items-center space-x-6 text-sm font-medium">
        {%- for text,url in theme_main_nav_links.items() %}
        {%- set _active = "text-foreground" if pagename in url else "text-foreground/60" -%}
        {%- if url.startswith("http") %}
        <a href="{{ url }}" class="transition-colors hover:text-foreground/80 {{ _active }}" rel="noopener nofollow">{{
          text }}</a>
        {%- else %}
        <a href="{{ pathto(url) }}" class="transition-colors hover:text-foreground/80 {{ _active }}">{{ text }}</a>
        {%- endif %}
        {%- endfor %}
      </nav>
      {%- endif %}
      {%- endblock header_main_nav -%}
    </div>
    {%- endblock header_left %}

    {%- block mobile_menu %}
    {%- if sidebars|length >0 -%}
    <button
      class="inline-flex items-center justify-center h-10 px-0 py-2 mr-2 text-base font-medium transition-colors rounded-md hover:text-accent-foreground hover:bg-transparent md:hidden"
      type="button" @click="showSidebar = true">
      <svg xmlns="http://www.w3.org/2000/svg" height="24" width="24" viewBox="0 96 960 960" aria-hidden="true"
        fill="currentColor">
        <path
          d="M152.587 825.087q-19.152 0-32.326-13.174t-13.174-32.326q0-19.152 13.174-32.326t32.326-13.174h440q19.152 0 32.326 13.174t13.174 32.326q0 19.152-13.174 32.326t-32.326 13.174h-440Zm0-203.587q-19.152 0-32.326-13.174T107.087 576q0-19.152 13.174-32.326t32.326-13.174h320q19.152 0 32.326 13.174T518.087 576q0 19.152-13.174 32.326T472.587 621.5h-320Zm0-203.587q-19.152 0-32.326-13.174t-13.174-32.326q0-19.152 13.174-32.326t32.326-13.174h440q19.152 0 32.326 13.174t13.174 32.326q0 19.152-13.174 32.326t-32.326 13.174h-440ZM708.913 576l112.174 112.174q12.674 12.674 12.674 31.826t-12.674 31.826Q808.413 764.5 789.261 764.5t-31.826-12.674l-144-144Q600 594.391 600 576t13.435-31.826l144-144q12.674-12.674 31.826-12.674t31.826 12.674q12.674 12.674 12.674 31.826t-12.674 31.826L708.913 576Z" />
      </svg>
      <span class="sr-only">Toggle navigation menu</span>
    </button>
    {%- endif -%}
    {%- endblock mobile_menu %}

    {%- block header_right %}
    <div class="flex items-center justify-between flex-1 space-x-2 sm:space-x-4 md:justify-end">
      {%- if docsearch or hasdoc('search') %}
      <div class="flex-1 w-full md:w-auto md:flex-none">
        {%- include "searchbox.html" %}
      </div>
      {%- endif %}

      {%- block extra_header_link_icons %}
      <nav class="flex items-center space-x-1">
        {%- if theme_extra_header_link_icons|tobool %}
        {%- for text,url in theme_extra_header_link_icons.items() %}
        {%- if url is mapping %}
        <a href="{{ url.link }}" title="{{ text }}" rel="noopener nofollow">
          <div
            class="inline-flex items-center justify-center px-0 text-sm font-medium transition-colors rounded-md disabled:opacity-50 disabled:pointer-events-none hover:bg-accent hover:text-accent-foreground h-9 w-9">
            {{ url.icon }}
          </div>
        </a>
        {% endif %}
        {%- endfor %}
        {%- endif %}

        {%- block theme_switcher %}
        <button @click="darkMode = darkMode === 'light' ? 'dark' : 'light'"
          class="relative inline-flex items-center justify-center px-0 text-sm font-medium transition-colors rounded-md hover:bg-accent hover:text-accent-foreground h-9 w-9"
          type="button">
          <svg xmlns="http://www.w3.org/2000/svg" height="24" width="24" viewBox="0 96 960 960" fill="currentColor"
            class="absolute transition-all scale-100 rotate-0 dark:-rotate-90 dark:scale-0">
            <path
              d="M480 685q45.456 0 77.228-31.772Q589 621.456 589 576q0-45.456-31.772-77.228Q525.456 467 480 467q-45.456 0-77.228 31.772Q371 530.544 371 576q0 45.456 31.772 77.228Q434.544 685 480 685Zm0 91q-83 0-141.5-58.5T280 576q0-83 58.5-141.5T480 376q83 0 141.5 58.5T680 576q0 83-58.5 141.5T480 776ZM80 621.5q-19.152 0-32.326-13.174T34.5 576q0-19.152 13.174-32.326T80 530.5h80q19.152 0 32.326 13.174T205.5 576q0 19.152-13.174 32.326T160 621.5H80Zm720 0q-19.152 0-32.326-13.174T754.5 576q0-19.152 13.174-32.326T800 530.5h80q19.152 0 32.326 13.174T925.5 576q0 19.152-13.174 32.326T880 621.5h-80Zm-320-320q-19.152 0-32.326-13.174T434.5 256v-80q0-19.152 13.174-32.326T480 130.5q19.152 0 32.326 13.174T525.5 176v80q0 19.152-13.174 32.326T480 301.5Zm0 720q-19.152 0-32.326-13.17Q434.5 995.152 434.5 976v-80q0-19.152 13.174-32.326T480 850.5q19.152 0 32.326 13.174T525.5 896v80q0 19.152-13.174 32.33-13.174 13.17-32.326 13.17ZM222.174 382.065l-43-42Q165.5 327.391 166 308.239t13.174-33.065q13.435-13.674 32.587-13.674t32.065 13.674l42.239 43q12.674 13.435 12.555 31.706-.12 18.272-12.555 31.946-12.674 13.674-31.445 13.413-18.772-.261-32.446-13.174Zm494 494.761-42.239-43q-12.674-13.435-12.674-32.087t12.674-31.565Q686.609 756.5 705.38 757q18.772.5 32.446 13.174l43 41.761Q794.5 824.609 794 843.761t-13.174 33.065Q767.391 890.5 748.239 890.5t-32.065-13.674Zm-42-494.761Q660.5 369.391 661 350.62q.5-18.772 13.174-32.446l41.761-43Q728.609 261.5 747.761 262t33.065 13.174q13.674 13.435 13.674 32.587t-13.674 32.065l-43 42.239q-13.435 12.674-31.706 12.555-18.272-.12-31.946-12.555Zm-495 494.761Q165.5 863.391 165.5 844.239t13.674-32.065l43-42.239q13.435-12.674 32.087-12.674t31.565 12.674Q299.5 782.609 299 801.38q-.5 18.772-13.174 32.446l-41.761 43Q231.391 890.5 212.239 890t-33.065-13.174ZM480 576Z" />
          </svg>
          <svg xmlns="http://www.w3.org/2000/svg" height="24" width="24" viewBox="0 96 960 960" fill="currentColor"
            class="absolute transition-all scale-0 rotate-90 dark:rotate-0 dark:scale-100">
            <path
              d="M480 936q-151 0-255.5-104.5T120 576q0-138 90-239.5T440 218q25-3 39 18t-1 44q-17 26-25.5 55t-8.5 61q0 90 63 153t153 63q31 0 61.5-9t54.5-25q21-14 43-1.5t19 39.5q-14 138-117.5 229T480 936Zm0-80q88 0 158-48.5T740 681q-20 5-40 8t-40 3q-123 0-209.5-86.5T364 396q0-20 3-40t8-40q-78 32-126.5 102T200 576q0 116 82 198t198 82Zm-10-270Z" />
          </svg>
        </button>
        {%- endblock theme_switcher %}
      </nav>
      {%- endblock extra_header_link_icons %}
    </div>
    {%- endblock header_right %}

  </div>
  {%- block header_after %}{%- endblock header_after %}
</header>

</code>

docs_themes\sphinxawesome_theme\highlighting.py:
<code>
"""Add more highlighting options to Pygments.

This extension extends the Sphinx `code-block`
directive with new options:

- `:emphasize-added:`: highlight added lines
- `:emphasize-removed:`: highlight removed lines
- `:emphasize-text:`: highlight a single word, such as, a placeholder

To load this extension, add:

.. code-block:: python
:caption: File: conf.py

extensions += ["sphinxawesome_theme.highlighting"]

To achieve this, this extension makes a few larger changes:

1. Provide a new Sphinx directive: `AwesomeCodeBlock`.
   This parses the additional options and passes them to the syntax highlighter.

2. Provide a new Pygments HTML formatter `AwesomeHtmlFormatter`.
   This handles formatting the lines for added or removed options.
   This extension changes the output compared to the default Sphinx implementation.
   For example, each line is wrapped in a `<span>` element,
   and the whole code block is wrapped in a `<pre><code>..` element.
   For highlighted lines, this extension uses `<mark>`, `<ins>`, and `<del>` elements.

3. Define a new custom Pygments filter `AwesomePlaceholders`,
   which wraps each encountered placeholder word in a `Generic.Emphasized` token,
   such that we can style placeholders by CSS.

4. Monkey-patch the `PygmentsBridge.get_lexer` method to apply the `AwesomePlaceholders` filter,
   if the option for it is present.

5. Monkey-patch the `PygmentsBridge.highlight_block` method to pass the option for highlighting text to the `get_lexer` method.

:copyright: Copyright Kai Welke.
:license: MIT, see LICENSE for details.
"""
from **future** import annotations

import re
from typing import Any, Generator, Literal, Pattern, Tuple, Union

from docutils import nodes
from docutils.nodes import Node
from docutils.parsers.rst import directives
from pygments.filter import Filter
from pygments.formatters import HtmlFormatter
from pygments.lexer import Lexer
from pygments.token import Generic, \_TokenType
from pygments.util import get_list_opt
from sphinx.application import Sphinx
from sphinx.directives.code import CodeBlock
from sphinx.highlighting import PygmentsBridge
from sphinx.locale import \_\_
from sphinx.util import logging, parselinenos

from . import **version**

logger = logging.getLogger(**name**)

# type alias

TokenType = Union[_TokenType, int] # For Python 3.8
TokenStream = Generator[Tuple[TokenType, str], None, None]

def \_replace_placeholders(
ttype: \_TokenType, value: str, regex: Pattern[str]
) -> TokenStream:
"""Replace every occurence of `regex` with `Generic.Emph` token."""
last = 0
for match in regex.finditer(value):
start, end = match.start(), match.end()
if start != last:
yield ttype, value[last:start]
yield Generic.Emph, value[start:end]
last = end
if last != len(value):
yield ttype, value[last:]

# Without the comment, `mypy` throws a fit:

# Cannot subclass Filter, is type `Any`

class AwesomePlaceholders(Filter): # type: ignore[misc]
"""A Pygments filter for marking up placeholder text.

    You can define the text to highlight with the ``hl_text`` option.
    To add the filter to a Pygments lexer, use the ``add_filter`` method:

    .. code-block:: python

       f = AwesomePlaceholders(hl_text=TEXT)
       lexer.add_filter(AwesomePlaceholders(hl_text=TEXT))

    For more information, see the `Pygments documentation <https://pygments.org/docs/quickstart/>`__.
    """

    def __init__(self: AwesomePlaceholders, **options: str) -> None:
        """Create an instance of the ``AwesomePlaceholders`` filter."""
        Filter.__init__(self, **options)
        placeholders = get_list_opt(options, "hl_text", [])
        self.placeholders_re = re.compile(
            r"|".join([re.escape(x) for x in placeholders if x])
        )

    def filter(
        self: AwesomePlaceholders, _lexer: Any, stream: TokenStream
    ) -> TokenStream:
        """Filter on all tokens.

        The ``lexer`` instance is required by the parent class, but isn't used here.
        """
        regex = self.placeholders_re
        for ttype, value in stream:
            yield from _replace_placeholders(ttype, value, regex)

class AwesomeHtmlFormatter(HtmlFormatter): # type: ignore
"""Custom Pygments HTML formatter for highlighting added or removed lines.

    The method is similar to handling the ``hl_lines`` option in the regular HtmlFormatter.
    """

    def _get_line_numbers(
        self: AwesomeHtmlFormatter,
        options: dict[str, Any],
        which: Literal["hl_added", "hl_removed"],
    ) -> set[int]:
        """Get the lines to be added or removed."""
        line_numbers = set()
        for lineno in get_list_opt(options, which, []):
            try:
                line_numbers.add(int(lineno))
            except ValueError:
                pass
        return line_numbers

    def __init__(self: AwesomeHtmlFormatter, **options: Any) -> None:
        """Implement `hl_added` and `hl_removed` options.

        Also set the ``linespans`` and ``wrapcode`` options of the Pygments HTML formatter to ``True``.
        """
        self.added_lines = self._get_line_numbers(options, "hl_added")
        self.removed_lines = self._get_line_numbers(options, "hl_removed")

        # These options aren't compatible with `sphinx.ext.autodoc`
        # options["lineanchors"] = "code"
        options["linespans"] = "line"
        options["wrapcode"] = True

        super().__init__(**options)

    def _highlight_lines(
        self: AwesomeHtmlFormatter, tokensource: TokenStream
    ) -> TokenStream:
        """Highlight added, removed, and emphasized lines.

        In contrast to Pygments, use ``<mark>``, ``<ins>``, and ``<del>`` elements.
        """
        for i, (t, value) in enumerate(tokensource):
            if t != 1:
                yield t, value
            if i + 1 in self.hl_lines:
                yield 1, "<mark>%s</mark>" % value
            elif i + 1 in self.added_lines:
                yield 1, "<ins>%s</ins>" % value
            elif i + 1 in self.removed_lines:
                yield 1, "<del>%s</del>" % value
            else:
                yield 1, value

    def format_unencoded(
        self: AwesomeHtmlFormatter,
        tokensource: TokenStream,
        outfile: Any,
    ) -> None:
        """Overwrite method to handle emphasized, added, and removed lines.

        Unfortunately, the method doesn't extend easily, so I copy it from Pygments.
        """
        source = self._format_lines(tokensource)

        # As a special case, we wrap line numbers before line highlighting
        # so the line numbers get wrapped in the highlighting tag.
        if not self.nowrap and self.linenos == 2:
            source = self._wrap_inlinelinenos(source)

        # This is the only change I made from the original
        if self.hl_lines or self.added_lines or self.removed_lines:
            source = self._highlight_lines(source)

        if not self.nowrap:
            if self.lineanchors:
                source = self._wrap_lineanchors(source)
            if self.linespans:
                source = self._wrap_linespans(source)
            source = self.wrap(source)
            if self.linenos == 1:
                source = self._wrap_tablelinenos(source)
            source = self._wrap_div(source)
            if self.full:
                source = self._wrap_full(source, outfile)

        for _, piece in source:
            outfile.write(piece)

class AwesomeCodeBlock(CodeBlock):
"""An extension of the Sphinx `code-block` directive to handle additional options.

    - ``:emphasize-added:`` highlight added lines
    - ``:emphasize-removed:`` highlight removed lines
    - ``:emphasize-text:`` highlight placeholder text

    The job of the directive is to set the correct options to the ``literal_block`` node,
    which represents a code block in the parsed reStructuredText tree.
    When transforming the abstract tree to HTML,
    Sphinx passes these options to the ``highlight_block`` method,
    which is a wrapper around Pygments' ``highlight`` method.
    Handling these options is then a job of the ``AwesomePygmentsBridge``.
    """

    new_options = {
        "emphasize-added": directives.unchanged_required,
        "emphasize-removed": directives.unchanged_required,
        "emphasize-text": directives.unchanged_required,
    }

    option_spec = CodeBlock.option_spec
    option_spec.update(new_options)

    def _get_line_numbers(
        self: AwesomeCodeBlock, option: Literal["emphasize-added", "emphasize-removed"]
    ) -> list[int] | None:
        """Parse the line numbers for the ``:emphasize-added:`` and ``:emphasize-removed:`` options."""
        document = self.state.document
        location = self.state_machine.get_source_and_line(self.lineno)
        nlines = len(self.content)
        linespec = self.options.get(option)

        if not linespec:
            return None

        try:
            line_numbers = parselinenos(linespec, nlines)
            if any(i >= nlines for i in line_numbers):
                logger.warning(
                    __("line number spec is out of range(1-%d): %r")
                    % (nlines, linespec),
                    location=location,
                )
            return [i + 1 for i in line_numbers if i < nlines]
        except ValueError as err:
            return [document.reporter.warning(err, line=self.lineno)]

    def run(self: AwesomeCodeBlock) -> list[Node]:
        """Handle parsing extra options for highlighting."""
        literal_nodes = super().run()

        hl_added = self._get_line_numbers("emphasize-added")
        hl_removed = self._get_line_numbers("emphasize-removed")

        # `literal_nodes` is either `[literal_block]`, or `[caption, literal_block]`
        for node in literal_nodes:
            if isinstance(node, nodes.literal_block):
                extra_args = node.get("highlight_args", {})

                if hl_added is not None:
                    extra_args["hl_added"] = hl_added
                if hl_removed is not None:
                    extra_args["hl_removed"] = hl_removed
                if "emphasize-text" in self.options:
                    extra_args["hl_text"] = self.options["emphasize-text"]

        return literal_nodes

# These external references are needed, or you'll get a maximum recursion depth error

pygmentsbridge_get_lexer = PygmentsBridge.get_lexer
pygmentsbridge_highlight_block = PygmentsBridge.highlight_block

class AwesomePygmentsBridge(PygmentsBridge):
"""Monkey-patch the Pygments methods to handle highlighting placeholder text."""

    def get_lexer(
        self: AwesomePygmentsBridge,
        source: str,
        lang: str,
        opts: dict[str, Any] | None = None,
        force: bool = False,
        location: Any = None,
    ) -> Lexer:
        """Monkey-patch the ``PygmentsBridge.get_lexer`` method.

        Adds a filter to lexers if the ``hl_text`` option is present.
        """
        lexer = pygmentsbridge_get_lexer(self, source, lang, opts, force, location)

        if opts and "hl_text" in opts:
            lexer.add_filter(AwesomePlaceholders(hl_text=opts["hl_text"]))
        return lexer

    def highlight_block(
        self: AwesomePygmentsBridge,
        source: str,
        lang: str,
        opts: dict[str, Any] | None = None,
        force: bool = False,
        location: Any = None,
        **kwargs: Any,
    ) -> str:
        """Monkey-patch the ``PygmentsBridge.highlight_block`` method.

        This method is called, when Sphinx transforms the abstract document tree
        to HTML and encounters code blocks.
        The ``hl_text`` option is passed in the ``kwargs`` dictionary.
        For the ``get_lexer`` method, we need to pass it in the ``opts`` dictionary.
        """
        if opts is None:
            opts = {}

        hl_text = get_list_opt(kwargs, "hl_text", [])

        if hl_text:
            opts["hl_text"] = hl_text

        return pygmentsbridge_highlight_block(
            self, source, lang, opts, force, location, **kwargs
        )

def setup(app: Sphinx) -> dict[str, Any]:
"""Set up this internal extension."""
PygmentsBridge.html_formatter = AwesomeHtmlFormatter
PygmentsBridge.get_lexer = AwesomePygmentsBridge.get_lexer # type: ignore
PygmentsBridge.highlight_block = ( # type: ignore
AwesomePygmentsBridge.highlight_block # type: ignore
)
directives.register_directive("code-block", AwesomeCodeBlock)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

</code>

docs_themes\sphinxawesome_theme\jinja_functions.py:
<code>
"""Define custom filters for Jinja2 templates.

:copyright: Copyright, Kai Welke.
:license: MIT, see LICENSE for details.
"""
from **future** import annotations

import json
import posixpath
from functools import partial
from os import path
from typing import Any

from docutils.nodes import Node
from sphinx.application import Sphinx

def \_get_manifest_json(app: Sphinx) -> Any:
"""Read the `manifest.json` file.

    Webpack writes a file ``manifest.json`` in the theme's static directory.
    This file has the mapping between hashed and unhashed filenames.
    Returns a dictionary with this mapping.
    """
    if app.builder and app.builder.theme:  # type: ignore[attr-defined]
        # find the first 'manifest.json' file in the theme's directories
        for entry in app.builder.theme.get_theme_dirs()[::-1]:  # type: ignore[attr-defined] # noqa: E501,B950
            manifest = path.join(entry, "static", "manifest.json")
            if path.isfile(manifest):
                with open(manifest) as m:
                    return json.load(m)
    else:
        return {}

def \_make_asset_url(app: Sphinx, asset: str) -> Any:
"""Turn a _clean_ asset file name to a hashed one."""
manifest = \_get_manifest_json(app)

    # return the asset itself if it is not in the manifest
    return manifest.get(asset, asset)

def \_make_canonical(app: Sphinx, pagename: str) -> str:
"""Turn a filepath into the correct canonical link.

    Upstream Sphinx builds the wrong canonical links for the ``dirhtml`` builder.
    """
    canonical = posixpath.join(app.config.html_baseurl, pagename.replace("index", ""))
    if not canonical.endswith("/"):
        canonical += "/"
    return canonical

def setup_jinja(
app: Sphinx,
pagename: str,
templatename: str,
context: dict[str, Any],
doctree: Node,
) -> None:
"""Register a function as a Jinja2 filter."""
context["asset"] = partial(\_make_asset_url, app) # must override `pageurl` for directory builder
if app.builder.name == "dirhtml" and app.config.html_baseurl:
context["pageurl"] = \_make_canonical(app, pagename)

</code>

docs_themes\sphinxawesome_theme\jsonimpl.py:
<code>
"""Custom JSON serializer.

The awesome theme uses custom jinja2 helper functions which are
non-serializable by default. Hence, I need to use a custom JSON
serializer.

:copyright: Copyright Kai Welke.
:license: MIT, see LICENSE for details.
"""
from **future** import annotations

import json
from typing import IO, Any

class AwesomeJSONEncoder(json.JSONEncoder):
"""Custom JSON encoder for everything in the `context`."""

    def default(self: AwesomeJSONEncoder, obj: Any) -> str:
        """Return an empty string for anything that's not serializable by default."""
        return ""

def dump(obj: Any, fp: IO[str], *args: Any, \*\*kwargs: Any) -> None:
"""Dump JSON into file."""
kwargs["cls"] = AwesomeJSONEncoder
return json.dump(obj, fp, *args, \*\*kwargs)

def dumps(obj: Any, *args: Any, \*\*kwargs: Any) -> str:
"""Convert object to JSON string."""
kwargs["cls"] = AwesomeJSONEncoder
return json.dumps(obj, *args, \*\*kwargs)

def load(*args: Any, \*\*kwargs: Any) -> Any:
"""De-serialize JSON."""
return json.load(*args, \*\*kwargs)

def loads(*args: Any, \*\*kwargs: Any) -> Any:
"""De-serialize JSON."""
return json.loads(*args, \*\*kwargs)

</code>

docs_themes\sphinxawesome_theme\layout.html:
<code>
{%- macro script() %}
{%- for js in script_files %}
{{ js_tag(js) }}
{%- endfor %}

  <script src="{{ pathto(asset('_static/theme.js'), 1) }}" defer></script>

{%- if docsearch %}
<script src="{{ pathto(asset('_static/docsearch.js'), 1) }}" defer></script>
<script src="{{ pathto('_static/docsearch_config.js', 1) }}" defer></script>
{%- endif %}
{%- endmacro -%}

{%- set lang_attr = "en" if language == None else (language|replace('_','-')) -%}

{%- if not embedded and docstitle -%}
{%- if title == docstitle -%}
{%- set titlesuffix = "" -%}
{%- else -%}
{%- set titlesuffix = " | "|safe + docstitle|e -%}
{%- endif -%}
{%- else -%}
{%- set titlesuffix = "" -%}
{%- endif -%}

<!DOCTYPE html>
<html lang="{{ lang_attr }}"
      x-data="{ darkMode: localStorage.getItem('darkMode') || localStorage.setItem('darkMode', 'system'), activeSection: '' }"
      x-init="$watch('darkMode', val => localStorage.setItem('darkMode', val))"
      class="scroll-smooth"
      :class="{'dark': darkMode === 'dark' || (darkMode === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)}"
>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta charset="utf-8" />
  <meta name="theme-color" media="(prefers-color-scheme: light)" content="white" />
  <meta name="theme-color" metia="(prefers-color-scheme: dark)" content="black" />
  {{ metatags }}

{%- block htmltitle %}
<title>{{ title|striptags|e if title else docstitle }}{{ titlesuffix }}</title>
<meta property="og:title" content="{{ title|striptags|e if title else docstitle }}{{ titlesuffix }}" />
<meta name="twitter:title" content="{{ title|striptags|e if title else docstitle }}{{ titlesuffix }}" />
{%- endblock htmltitle %}

{#- Extra CSS files for overriding stuff #}
{%- for css in css_files %}
<link rel="stylesheet" href="{{ pathto(asset(css), 1) }}" />
{%- endfor %}

{%- if docsearch %}
<link rel="preconnect" href="https://{{ docsearch_app_id }}-dsn.algolia.net" crossorigin="anonymous" />
{% endif %}

{%- if pageurl %}
<link rel="canonical" href="{{ pageurl|e }}" />
{%- endif %}

{%- set _favicon_url = favicon_url | default(pathto('_static/' + (favicon or ""), 1)) %}
{%- if favicon_url or favicon %}
<link rel="icon" href="{{ _favicon_url }}" />
{%- endif %}

    {%- block linktags %}
      {%- if hasdoc('search') and not docsearch %}
        <link rel="search" title="{{ _('Search') }}" href="{{ pathto('search') }}" />
      {%- endif %}

      {%- if hasdoc('genindex') %}
        <link rel="index" title="{{ _('Index') }}" href="{{ pathto('genindex') }}" />
      {%- endif %}
      {%- if next %}
          <link rel="next" title="{{ next.title|striptags|e }}" href="{{ next.link|e }}" />
      {%- endif %}
      {%- if prev %}
          <link rel="prev" title="{{ prev.title|striptags|e }}" href="{{ prev.link|e }}" />
      {%- endif %}
    {%- endblock linktags %}

    <script>
    <!-- Prevent Flash of wrong theme -->
      const userPreference = localStorage.getItem('darkMode');
      let mode;
      if (userPreference === 'dark' || window.matchMedia('(prefers-color-scheme: dark)').matches) {
        mode = 'dark';
        document.documentElement.classList.add('dark');
      } else {
        mode = 'light';
      }
      if (!userPreference) {localStorage.setItem('darkMode', mode)}
    </script>

    {% block scripts %}
      {{ script() }}
    {% endblock scripts %}

    {%- block extrahead %}{%- endblock extrahead %}

</head>
<body x-data="{ showSidebar: false }" class="min-h-screen font-sans antialiased bg-background text-foreground" :class="{ 'overflow-hidden': showSidebar }">

{#- A blurry background screen for the mobile sidebar -#}
{%- if sidebars|length > 0 %}
<div x-cloak x-show="showSidebar" class="fixed inset-0 z-50 overflow-hidden bg-background/80 backdrop-blur-sm" @click.self="showSidebar = false"></div>
{%- endif %}

{#- The main page wrapper -#}

  <div id="page" class="relative flex flex-col min-h-screen">

    {#- Skip to content link -#}
    <a href="#content" class="absolute top-0 left-0 z-[100] block bg-background p-4 text-xl transition -translate-x-full opacity-0 focus:translate-x-0 focus:opacity-100">
      Skip to content
    </a>

    {%- block header %}
      {%- include "header.html" %}
    {%- endblock header %}

    <div class="flex-1">

      {%- set only_main_nav = sidebars == ["sidebar_main_nav_links.html"] %}

      {%- if not only_main_nav and sidebars|length > 0 -%}
        <div class="container flex-1 items-start md:grid md:grid-cols-[220px_minmax(0,1fr)] md:gap-6 lg:grid-cols-[240px_minmax(0,1fr)] lg:gap-10">
      {%- else -%}
        <div class="container items-start flex-1">
      {%- endif -%}

        {%- block sidebar %}
          {%- if sidebars|length > 0 %}
            {%- include "sidebar.html" %}
          {%- endif %}
        {%- endblock sidebar %}

        {%- block main %}
        <main class="relative py-6 lg:gap-10 lg:py-8 xl:grid xl:grid-cols-[1fr_300px]">
          {%- block body %}{%- endblock %}
        </main>
        {%- endblock main %}
      </div>
    </div>

    {%- block footer %}
      {%- include "footer.html" %}
    {%- endblock footer %}

  </div>
</body>
</html>

</code>

docs_themes\sphinxawesome_theme\logos.py:
<code>
"""Support different light and dark mode logos.

By default, Sphinx provides `html_logo` as an option
to add a logo to your documentation project.

The Awesome Theme lets you define separate logos for light and dark mode
via theme options:

.. code-block:: python

html_theme_options = {
"logo_light": "<path>/<filename>",
"logo_dark": "<path>/<filename>"
}

Provide a path relative to the Sphinx configuration directory (with the :file:`conf.py` file).

:copyright: Copyright Kai Welke.
:license: MIT, see LICENSE for details
"""
from **future** import annotations

import os
from pathlib import Path
from typing import Any

from docutils.nodes import Node
from sphinx.application import Sphinx
from sphinx.util import isurl, logging
from sphinx.util.fileutil import copy_asset_file

logger = logging.getLogger(**name**)

def get_theme_options(app: Sphinx) -> Any:
"""Return theme options for the application.

    Adapted from the ``pydata_sphinx_theme``.
    https://github.com/pydata/pydata-sphinx-theme/blob/f15ecfed59a2a5096c05496a3d817fef4ef9a0af/src/pydata_sphinx_theme/utils.py
    """
    if hasattr(app.builder, "theme_options"):
        return app.builder.theme_options
    elif hasattr(app.config, "html_theme_options"):
        return app.config.html_theme_options
    else:
        return {}

def update_config(app: Sphinx) -> None:
"""Update the configuration, handling the `builder-inited` event.

    Adapted from the ``pydata_sphinx_theme``:
    https://github.com/pydata/pydata-sphinx-theme/blob/f15ecfed59a2a5096c05496a3d817fef4ef9a0af/src/pydata_sphinx_theme/__init__.py
    """
    theme_options = get_theme_options(app)

    # Check logo config
    dark_logo = theme_options.get("logo_dark")
    light_logo = theme_options.get("logo_light")
    if app.config.html_logo and (dark_logo or light_logo):
        # For the rendering of the logos, see ``header.html`` and ``sidebar.html``
        logger.warning(
            "Conflicting theme options: use either `html_logo` or `logo_light` and `logo_dark`."
        )
    if (
        (dark_logo and not light_logo) or (light_logo and not dark_logo)
    ) and not app.config.html_logo:
        logger.warning("You must use `logo_light` and `logo_dark` together.")

def setup*logo_path(
app: Sphinx,
pagename: str,
templatename: str,
context: dict[str, Any],
doctree: Node,
) -> None:
"""Update the logo path for the templates."""
theme_options = get_theme_options(app)
for kind in ["dark", "light"]:
logo = theme_options.get(f"logo*{kind}")
if logo and not isurl(logo):
context[f"theme_logo_{kind}"] = os.path.basename(logo)

def copy_logos(app: Sphinx, exc: Exception | None) -> None:
"""Copy the light and dark logos."""
theme_options = get_theme_options(app)
static_dir = str(Path(app.builder.outdir) / "\_static")

    for kind in ["dark", "light"]:
        logo = theme_options.get(f"logo_{kind}")
        if logo and not isurl(logo):
            logo_path = Path(app.builder.confdir) / logo
            if not logo_path.exists():
                logger.warning("Path to logo %s does not exist.", logo)
            copy_asset_file(str(logo_path), static_dir)

</code>

docs_themes\sphinxawesome_theme\page.html:
<code>
{#- Template for the main docs page. #}

{%- extends "layout.html" -%}

{%- block body %}

{%- set only_main_nav = sidebars == ["sidebar_main_nav_links.html"] %}
{%- if not only_main_nav and sidebars|length > 0 %}

<div class="w-full min-w-0 mx-auto">
  {%- else %}
  <div class="w-full min-w-0 mx-auto max-w-prose">
    {%- endif %}

    {%- block body_before %}{%- endblock body_before -%}

    {%- if pagename != master_doc and theme_show_breadcrumbs|tobool %}
    {%- include "breadcrumbs.html" %}
    {%- endif %}

    <div id="content" role="main">
      {{ body }}
    </div>

    {%- if theme_show_prev_next|tobool %}
      {%- include "prev_next.html" %}
    {%- endif %}

    {%- block body_after %}{%- endblock body_after -%}

  </div>

{%- block on_page_toc %}
{%- if display_toc %}
{%- include "toc.html" %}
{%- endif %}
{%- endblock on_page_toc %}
{%- endblock body %}

</code>

docs_themes\sphinxawesome_theme\postprocess.py:
<code>
"""Post-process the HTML produced by Sphinx.

Some modifications can be done more easily on the finished HTML.

This module defines a simple pipeline:

1. Read all HTML files
2. Parse them with `BeautifulSoup`
3. Perform a chain of actions on the tree in place

See the `_modify_html()` function for the list of
transformations.

Note: This file is not processed by Webpack; don't use Tailwind utility classes.
They might not show up in the final CSS.

:copyright: Copyright Kai Welke.
:license: MIT, see LICENSE.
"""
from **future** import annotations

import os
import re
from dataclasses import dataclass

from bs4 import BeautifulSoup, Comment
from sphinx.application import Sphinx

from . import logos

@dataclass(frozen=True)
class Icons:
"""Icons from Material Design.

    See: https://material.io/resources/icons/
    """

    external_link: str = '<svg xmlns="http://www.w3.org/2000/svg" height="1em" width="1em" fill="currentColor" stroke="none" viewBox="0 96 960 960"><path d="M188 868q-11-11-11-28t11-28l436-436H400q-17 0-28.5-11.5T360 336q0-17 11.5-28.5T400 296h320q17 0 28.5 11.5T760 336v320q0 17-11.5 28.5T720 696q-17 0-28.5-11.5T680 656V432L244 868q-11 11-28 11t-28-11Z"/></svg>'
    chevron_right: str = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18px" height="18px" stroke="none" fill="currentColor"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>'
    permalinks_icon: str = '<svg xmlns="http://www.w3.org/2000/svg" height="1em" width="1em" viewBox="0 0 24 24"><path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/></svg>'

def _get_html_files(outdir: str) -> list[str]:
"""Get a list of HTML files."""
html_list = []
for root, _, files in os.walk(outdir):
html_list.extend(
[os.path.join(root, file) for file in files if file.endswith(".html")]
)
return html_list

def _collapsible_nav(tree: BeautifulSoup) -> None:
"""Make navigation links with children collapsible."""
for link in tree.select("#left-sidebar a"): # Check if the link has "children"
children = link.next_sibling
if children and children.name == "ul": # State must be available in the link and the list
li = link.parent
li[
"x-data"
] = "{ expanded: $el.classList.contains('current') ? true : false }"
link["@click"] = "expanded = !expanded" # The expandable class is a hack because we can't use Tailwind # I want to have \_only_ expandable links with `justify-between`
link["class"].append("expandable")
link[":class"] = "{ 'expanded' : expanded }"
children["x-show"] = "expanded"

            # Create a button with an icon inside to get focus behavior
            button = tree.new_tag(
                "button",
                attrs={"type": "button", "@click.prevent.stop": "expanded = !expanded"},
            )
            label = tree.new_tag("span", attrs={"class": "sr-only"})
            button.append(label)

            # create the icon
            svg = BeautifulSoup(Icons.chevron_right, "html.parser").svg
            button.append(svg)
            link.append(button)

def \_remove_empty_toctree(tree: BeautifulSoup) -> None:
"""Remove empty toctree divs.

    If you include a `toctree` with the `hidden` option,
    an empty `div` is inserted. Remove them.
    The empty `div` contains a single `end-of-line` character.
    """
    for div in tree("div", class_="toctree-wrapper"):
        children = list(div.children)
        if len(children) == 1 and not children[0].strip():
            div.extract()

def _headerlinks(tree: BeautifulSoup) -> None:
"""Make headerlinks copy their URL on click."""
for link in tree("a", class_="headerlink"):
link[
"@click.prevent"
] = "window.navigator.clipboard.writeText($el.href); $el.setAttribute('data-tooltip', 'Copied!'); setTimeout(() => $el.setAttribute('data-tooltip', 'Copy link to this element'), 2000)"
del link["title"]
link["aria-label"] = "Copy link to this element"
link["data-tooltip"] = "Copy link to this element"

def _scrollspy(tree: BeautifulSoup) -> None:
"""Add an active class to current TOC links in the right sidebar."""
for link in tree("a", class_="headerlink"):
if link.parent.name in ["h2", "h3"] or (
link.parent.name == "dt" and "sig" in link.parent["class"]
):
active_link = link["href"]
link[
"x-intersect.margin.0%.0%.-70%.0%"
] = f"activeSection = '{active_link}'"

    for link in tree.select("#right-sidebar a"):
        active_link = link["href"]
        link[":data-current"] = f"activeSection === '{active_link}'"

def \_external_links(tree: BeautifulSoup) -> None:
"""Add `rel="nofollow noopener"` to external links.

    The alternative was to copy `visit_reference` in the HTMLTranslator
    and change literally one line.
    """
    for link in tree("a", class_="reference external"):
        link["rel"] = "nofollow noopener"
        # append icon
        link.append(BeautifulSoup(Icons.external_link, "html.parser").svg)

def \_strip_comments(tree: BeautifulSoup) -> None:
"""Remove HTML comments from documents."""
comments = tree.find_all(string=lambda text: isinstance(text, Comment))
for c in comments:
c.extract()

def _code_headers(tree: BeautifulSoup) -> None:
"""Add the programming language to a code block.""" # Find all "<div class="highlight-<LANG> notranslate>" blocks
pattern = re.compile("highlight-(.\*) ")
for code_block in tree.find_all("div", class_=pattern):
hl_lang = None # Get the highlight language
classes_string = " ".join(code_block.get("class", []))
match = pattern.search(classes_string)
if match:
hl_lang = match.group(1).replace("default", "python")

        parent = code_block.parent

        # Deal with code blocks with captions
        if "literal-block-wrapper" in parent.get("class", []):
            caption = parent.select(".code-block-caption")[0]
            if caption:
                span = tree.new_tag("span", attrs={"class": "code-lang"})
                span.append(tree.new_string(hl_lang))
                caption.insert(0, span)
        else:
            # Code block without captions, we need to wrap them first
            wrapper = tree.new_tag("div", attrs={"class": "literal-block-wrapper"})
            caption = tree.new_tag("div", attrs={"class": "code-block-caption"})
            span = tree.new_tag("span", attrs={"class": "code-lang"})
            span.append(tree.new_string(hl_lang))
            caption.append(span)
            code_block.wrap(wrapper)
            wrapper.insert(0, caption)

def \_modify_html(html_filename: str, app: Sphinx) -> None:
"""Modify a single HTML document.

    1. The HTML document is parsed into a BeautifulSoup tree.
    2. The modifications are performed in order and in place.
    3. After these modifications, the HTML is written into a file,
    overwriting the original file.
    """
    with open(html_filename, encoding="utf-8") as html:
        tree = BeautifulSoup(html, "html.parser")

    theme_options = logos.get_theme_options(app)

    _collapsible_nav(tree)
    if theme_options.get("awesome_external_links"):
        _external_links(tree)
    _remove_empty_toctree(tree)
    _scrollspy(tree)
    if theme_options.get("awesome_headerlinks"):
        _headerlinks(tree)
    # _code_headers(tree)
    _strip_comments(tree)

    with open(html_filename, "w", encoding="utf-8") as out_file:
        out_file.write(str(tree))

def post_process_html(app: Sphinx, exc: Exception | None) -> None:
"""Perform modifications on the HTML after building.

    This is an extra function, that gets a list from all HTML
    files in the output directory, then runs the ``_modify_html``
    function on each of them.
    """
    if app.builder is not None and app.builder.name not in ["html", "dirhtml"]:
        return

    if exc is None:
        html_files = _get_html_files(app.outdir)

        for doc in html_files:
            _modify_html(doc, app)

</code>

docs_themes\sphinxawesome_theme\prev_next.html:
<code>
{#- Templates for previous/next links. -#}

<div class="flex justify-between items-center pt-6 mt-12 border-t border-border gap-4">
  {%- if prev %}
    <div class="mr-auto">
      <a href="{{ prev.link|e }}"
         class="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors border border-input hover:bg-accent hover:text-accent-foreground py-2 px-4">
        <svg xmlns="http://www.w3.org/2000/svg"
             width="24"
             height="24"
             viewBox="0 0 24 24"
             fill="none"
             stroke="currentColor"
             stroke-width="2"
             stroke-linecap="round"
             stroke-linejoin="round"
             class="mr-2 h-4 w-4">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
        {{ prev.title|striptags|e }}
      </a>
    </div>
  {%- endif %}
  {%- if next %}
    <div class="ml-auto">
      <a href="{{ next.link|e }}"
         class="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors border border-input hover:bg-accent hover:text-accent-foreground py-2 px-4">
        {{ next.title|striptags|e }}
        <svg xmlns="http://www.w3.org/2000/svg"
             width="24"
             height="24"
             viewBox="0 0 24 24"
             fill="none"
             stroke="currentColor"
             stroke-width="2"
             stroke-linecap="round"
             stroke-linejoin="round"
             class="ml-2 h-4 w-4">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
      </a>
    </div>
  {%- endif %}
</div>

</code>

docs_themes\sphinxawesome_theme\scrolltop.html:
<code>
{#-
A `scroll to top` button. Is shown at the bottom right if `show_scrolltop` is true.
-#}
<button data-scroll-to-top-target="scrollToTop"
        data-action="scroll-to-top#scroll"
        class="fixed bottom-8 right-8 p-2 z-10 rounded-sm bg-gray-700 text-xs text-white invisible opacity-0 transition-all duration-1000 hover:bg-gray-950 focus:bg-gray-950">
<svg xmlns="http://www.w3.org/2000/svg"
       height="14"
       viewBox="0 96 960 960"
       width="14"
       class="inline fill-current mb-[2px]"
       aria-hidden="true">
<path d="M450 896V370L202 618l-42-42 320-320 320 320-42 42-248-248v526h-60Z" />
</svg>
Back to top
</button>

</code>

docs_themes\sphinxawesome*theme\search.html:
<code>
{#- Template for the search results page. -#}
{% extends "page.html" %}
{% set title = *('Search') %}
{% block scripts %}
{{ super() }}

  <script src="{{ pathto('_static/searchtools.js', 1) }}" defer></script>
  <script src="{{ pathto('_static/language_data.js', 1) }}" defer></script>
  <script src="{{ pathto('searchindex.js', 1) }}" defer></script>

{% endblock scripts %}
{% block body %}

  <div class="w-full min-w-0 mx-auto">
    {%- if pagename != master_doc and theme_show_breadcrumbs|tobool %}
      {%- include "breadcrumbs.html" %}
    {%- endif %}
    <div id="content">
      <div id="fallback" class="my-8 text-sm text-red-700">
        <script>document.querySelector("#fallback").style.display = "none"</script>
        {%- trans %}Please activate Javascript to enable searching the documentation.{% endtrans -%}
      </div>
      <div id="search-results"></div>
    </div>
  </div>
{% endblock body %}

</code>

docs_themes\sphinxawesome_theme\searchbox.html:
<code>
{#- Template for the search box in the header. -#}
{%- if docsearch %}

  <div id="{{ docsearch_container[1:]|default('docsearch') }}"></div>
{%- else %}
  <form id="searchbox"
        action="{{ pathto('search') }}"
        method="get"
        class="relative flex items-center group"
        @keydown.k.window.meta="$refs.search.focus()">
    <input x-ref="search"
           name="q"
           id="search-input"
           type="search"
           aria-label="Search the docs"
           placeholder="{{ _('Search ...') }}"
           class="inline-flex items-center font-medium transition-colors bg-transparent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ring-offset-background border border-input hover:bg-accent focus:bg-accent hover:text-accent-foreground focus:text-accent-foreground hover:placeholder-accent-foreground py-2 px-4 relative h-9 w-full justify-start rounded-[0.5rem] text-sm text-muted-foreground sm:pr-12 md:w-40 lg:w-64" />
    <kbd class="pointer-events-none absolute right-1.5 top-2 hidden h-5 select-none text-muted-foreground items-center gap-1 rounded border border-border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex group-hover:bg-accent group-hover:text-accent-foreground">
      <span class="text-xs">⌘</span>
      K
    </kbd>
  </form>
{%- endif -%}

</code>

docs_themes\sphinxawesome_theme\sidebar.html:
<code>
{#- Template for the sidebar. -#}

{%- set only_main_nav = sidebars == ["sidebar_main_nav_links.html"] -%}

{%- if not only_main_nav and sidebars|length > 0 -%}

<aside id="left-sidebar"
  class="fixed inset-y-0 left-0 md:top-14 z-50 md:z-30 bg-background md:bg-transparent transition-all duration-100 -translate-x-full md:translate-x-0 ml-0 p-6 md:p-0 md:-ml-2 md:h-[calc(100vh-3.5rem)] w-5/6 md:w-full shrink-0 overflow-y-auto border-r border-border md:sticky"
  :aria-hidden="!showSidebar" :class="{ 'translate-x-0': showSidebar }">
  {%- else %}
  <aside id="left-sidebar"
    class="fixed inset-y-0 left-0 md:hidden z-50 bg-background transition-all duration-100 -translate-x-full ml-0 p-6 w-5/6 shrink-0 overflow-y-auto border-r border-border"
    :aria-hidden="!showSidebar" :class="{ 'translate-x-0': showSidebar }">
    {%- endif %}

    <a href="{{ pathto(master_doc) }}" class="!justify-start text-sm md:!hidden bg-background">
      {%- if logo_url %}
        <img height="16" width="16" class="mr-2 dark:invert" src="{{ logo_url }}" alt="Logo" />
      {%- endif -%}
      {%- if theme_logo_dark and not logo_url %}
        <img width="16" height="16" class="mr-2 hidden dark:block" src="{{ pathto('_static/' + theme_logo_dark, 1) }}" alt="Logo" />
      {%- endif -%}
      {%- if theme_logo_light and not logo_url %}
        <img width="16" height="16" class="mr-2 dark:hidden" src="{{ pathto('_static/' + theme_logo_light, 1) }}" alt="Logo" />
      {%- endif -%}
      <span class="font-bold text-clip whitespace-nowrap">{{ docstitle }}</span>
    </a>

    <div class="relative overflow-hidden md:overflow-auto my-4 md:my-0 h-[calc(100vh-8rem)] md:h-auto">
      <div class="overflow-y-auto h-full w-full relative pr-6">
        {%- for section in sidebars %}
        {%- include section %}
        {%- endfor %}
      </div>
    </div>
    <button type="button" @click="showSidebar = false"
      class="absolute md:hidden right-4 top-4 rounded-sm opacity-70 transition-opacity hover:opacity-100">
      <svg xmlns="http://www.w3.org/2000/svg" height="24" width="24" viewBox="0 96 960 960" fill="currentColor"
        stroke="none" class="h-4 w-4">
        <path
          d="M480 632 284 828q-11 11-28 11t-28-11q-11-11-11-28t11-28l196-196-196-196q-11-11-11-28t11-28q11-11 28-11t28 11l196 196 196-196q11-11 28-11t28 11q11 11 11 28t-11 28L536 576l196 196q11 11 11 28t-11 28q-11 11-28 11t-28-11L480 632Z" />
      </svg>
    </button>

  </aside>

</code>

docs_themes\sphinxawesome_theme\sidebar_main_nav_links.html:
<code>
{#- Template for the main navigation links in the sidebar -#}
{%- if theme_main_nav_links|tobool -%}

<nav class="flex md:hidden flex-col font-medium mt-4">
  {%- for text,url in theme_main_nav_links.items() %}
  {%- if url.startswith("http") %}
  <a href="{{ url }}" rel="nofollow noopener">{{ text }}</a>
  {%- else %}
  <a href="{{ pathto(url) }}">{{ text }}</a>
  {%- endif %}
  {%- endfor %}
</nav>
{%- endif %}

</code>

docs_themes\sphinxawesome_theme\sidebar_toc.html:
<code>

<nav class="table w-full min-w-full my-6 lg:my-8">
  {%- if theme_globaltoc_includehidden|tobool %}
  {{ toctree(titles_only=true, collapse=False, includehidden=true) }}
  {%- else %}
  {{ toctree(titles_only=true, collapse=False) }}
  {%- endif %}
</nav>

</code>

docs_themes\sphinxawesome_theme\theme.conf:
<code>
[theme]
inherit = basic
stylesheet = theme.css
pygments_style = bw
sidebars =
sidebar_main_nav_links.html,
sidebar_toc.html

[options]
show_breadcrumbs = True
show_prev_next = False
show_scrolltop = False
globaltoc_includehidden = True
breadcrumbs_separator = /
awesome_headerlinks = True
awesome_external_links = False
main_nav_links = False
extra_header_link_icons = False
logo_dark =
logo_light =

# deprecated

nav_include_hidden =
show_nav =
extra_header_links =

</code>

docs_themes\sphinxawesome_theme\toc.html:
<code>
{#- Template for the on-page TOC -#}

<aside id="right-sidebar" class="hidden text-sm xl:block">
  <div class="sticky top-16 -mt-10 max-h-[calc(var(--vh)-4rem)] overflow-y-auto pt-6 space-y-2">
    {%- block toc_before %}{%- endblock -%}
    <p class="font-medium">On this page</p>
    {{ toc }}
    {%- block toc_after %}{%- endblock -%}
  </div>
</aside>

</code>

docs_themes\sphinxawesome_theme\toc.py:
<code>
"""Manipulate the on-page TOC.

:copyright: Kai Welke.
:license: MIT
"""
from **future** import annotations

from typing import Any

from docutils import nodes
from docutils.nodes import Node
from sphinx.application import Sphinx
from sphinx.environment.adapters.toctree import TocTree
from sphinx.util.docutils import new_document

def change_toc(
app: Sphinx,
pagename: str,
templatename: str,
context: dict[str, Any],
doctree: Node,
) -> None:
"""Change the way the `{{ toc }}` helper works.

    By default, Sphinx includes the page title in the on-page TOC.
    We don't want that.

    Sphinx returns the following structure:

    <ul>
        <li><a href="#">Page title</a></li>
        <ul>
            <li><a href="#anchor">H2 and below</a></li>
        </ul>
    </ul>

    We first remove the `title` node. This gives us:

    <ul>
        <ul>
            <li><a href="#anchor">H2 and below</a></li>
        </ul>
    </ul>

    Then, we _outdent_ the tree.
    """
    toc = TocTree(app.builder.env).get_toc_for(pagename, app.builder)

    # Remove `h1` node
    findall = "findall" if hasattr(toc, "findall") else "traverse"
    # `findall` is docutils > 0.18
    for node in getattr(toc, findall)(nodes.reference):
        if node["refuri"] == "#":
            # Remove the `list_item` wrapping the `reference` node.
            node.parent.parent.remove(node.parent)

    # Outdent the new empty outer bullet lists
    doc = new_document("<partial node>")
    doc.append(toc)

    # Replace outer bullet lists with inner bullet lists
    for node in doc.findall(nodes.bullet_list):
        if (
            len(node.children) == 1
            and isinstance(node.next_node(), nodes.list_item)
            and isinstance(node.next_node().next_node(), nodes.bullet_list)
        ):
            doc.replace(node, node.next_node().next_node())

    if hasattr(app.builder, "_publisher"):
        app.builder._publisher.set_source(doc)
        app.builder._publisher.publish()
        context["toc"] = app.builder._publisher.writer.parts["fragment"]

</code>

docs_themes\sphinxawesome_theme\_\_init\_\_.py:
<code>
"""The Sphinx awesome theme as a Python package.

:copyright: Copyright Kai Welke.
:license: MIT, see LICENSE for details
"""

from **future** import annotations

from dataclasses import dataclass, field
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, TypedDict

from sphinx.application import Sphinx
from sphinx.util import logging
from sphinxcontrib.serializinghtml import JSONHTMLBuilder

from . import jinja_functions, jsonimpl, logos, postprocess, toc

logger = logging.getLogger(**name**)

try: # obtain version from `pyproject.toml` via `importlib.metadata.version()`
**version** = version(**name**)
except PackageNotFoundError: # pragma: no cover
**version** = "unknown"

class LinkIcon(TypedDict):
"""A link to an external resource, represented by an icon."""

    link: str
    """The absolute URL to an external resource."""
    icon: str
    """An SVG icon as a string."""

@dataclass
class ThemeOptions:
"""Helper class for configuring the Awesome Theme.

    Each attribute becomes a key in the :confval:`sphinx:html_theme_options` dictionary.
    """

    show_prev_next: bool = True
    """If ``True``, the theme includes links to the previous and next pages in the hierarchy."""

    show_breadcrumbs: bool = True
    """If ``True``, the theme includes `breadcrumbs <https://en.wikipedia.org/wiki/Breadcrumb_navigation>`_ links on every page except the root page."""

    breadcrumbs_separator: str = "/"
    """The separator for the breadcrumbs links."""

    awesome_headerlinks: bool = True
    """If ``True``, clicking a headerlink copies its URL to the clipboard."""

    show_scrolltop: bool = False
    """If ``True``, the theme shows a button that scrolls to the top of the page when clicked."""

    awesome_external_links: bool = False
    """If ``True``, the theme includes an icon after external links and adds ``rel="nofollow noopener"`` to the links' attributes."""

    main_nav_links: dict[str, str] = field(default_factory=dict)
    """A dictionary with links to include in the site header.

    The keys of this dictionary are the labels for the links.
    The values are absolute or relative URLs.
    """

    extra_header_link_icons: dict[str, LinkIcon] = field(default_factory=dict)
    """A dictionary with extra icons to include on the right of the search bar.

    The keys are labels for the link's ``title`` attribute.
    The values are themselves :class:`LinkIcon`.
    """

    logo_light: str | None = None
    """A path to a logo for the light mode. If you're using separate logos for light and dark mode, you **must** provide both logos."""

    logo_dark: str | None = None
    """A path to a logo for the dark mode. If you're using separate logos for light and dark mode, you **must** provide both logos."""

    globaltoc_includehidden: bool = True
    """If ``True``, the theme includes entries from *hidden*
    :sphinxdocs:`toctree <usage/restructuredtext/directives.html#directive-toctree>` directives in the sidebar.

    The ``toctree`` directive generates a list of links on the page where you include it,
    unless you set the ``:hidden:`` option.

    This option is inherited from the ``basic`` theme.
    """

    nav_include_hidden: None = None
    """Deprecated. Use `globaltoc_includehidden` instead.

    .. deprecated:: 5.0
    """

    show_nav: None = None
    """Deprecated. Use the `html_sidebars` option instead.

    .. deprecated:: 5.0
    """

    extra_header_links: None = None
    """Deprecated. Use either `main_nav_links` or `extra_header_link_icons` instead.

    .. deprecated:: 5.0
    """

def deprecated_options(app: Sphinx) -> None:
"""Checks for deprecated `html_theme_options`.

    Raises warnings and set the correct options.
    """
    theme_options = logos.get_theme_options(app)

    if (
        "nav_include_hidden" in theme_options
        and theme_options["nav_include_hidden"] is not None
    ):
        logger.warning(
            "Setting `nav_include_hidden` in `html_theme_options` is deprecated. "
            "Use `globaltoc_includehidden` in `html_theme_options` instead."
        )
        theme_options["globaltoc_includehidden"] = theme_options["nav_include_hidden"]
        del theme_options["nav_include_hidden"]

    if "show_nav" in theme_options and theme_options["show_nav"] is not None:
        logger.warning(
            "Toggling the sidebar with `show_nav` in `html_theme_options` is deprecated. "
            "Control the sidebar with the `html_sidebars` configuration option instead."
        )
        if theme_options["show_nav"] is False:
            app.builder.config.html_sidebars = {"**": []}  # type: ignore[attr-defined]
        del theme_options["show_nav"]

    if (
        "extra_header_links" in theme_options
        and theme_options["extra_header_links"] is not None
    ):
        logger.warning(
            "`extra_header_links` is deprecated. "
            "Use `main_nav_links` for text links (left side) and `extra_header_link_icons` for icon links (right side) instead."
        )

        extra_links = theme_options["extra_header_links"]
        print("EXTRA: ", extra_links)
        # Either we have `extra_header_links = { "label": "url" }
        main_nav_links = {
            key: value for key, value in extra_links.items() if isinstance(value, str)
        }
        theme_options["main_nav_links"] = main_nav_links

        # Or we have `extra_header_links` = { "label": { "link": "link", "icon": "icon" }}
        extra_link_icons = {
            key: value for key, value in extra_links.items() if isinstance(value, dict)
        }
        theme_options["extra_header_link_icons"] = extra_link_icons

        del theme_options["extra_header_links"]

def setup(app: Sphinx) -> dict[str, Any]:
"""Register the theme and its extensions wih Sphinx."""
here = Path(**file**).parent.resolve()

    app.add_html_theme(name="sphinxawesome_theme", theme_path=str(here))

    # Add the CSS overrides if we're using the `sphinx-design` extension
    if "sphinx_design" in app.config.extensions:
        app.add_css_file("awesome-sphinx-design.css", priority=900)

    # The theme is set up _after_ extensions are set up,
    # so I can't use internal extensions.
    # For the same reason, I also can't call the `config-inited` event
    app.connect("builder-inited", deprecated_options)
    app.connect("builder-inited", logos.update_config)
    app.connect("html-page-context", logos.setup_logo_path)
    app.connect("html-page-context", jinja_functions.setup_jinja)
    app.connect("html-page-context", toc.change_toc)
    app.connect("build-finished", logos.copy_logos)
    app.connect("build-finished", postprocess.post_process_html)

    JSONHTMLBuilder.out_suffix = ".json"
    JSONHTMLBuilder.implementation = jsonimpl
    JSONHTMLBuilder.indexer_format = jsonimpl

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

</code>

docs\conf.py:
<code>

# -_- coding: utf-8 -_-

#

# Configuration file for the Sphinx documentation builder.

#

# This file does only contain a selection of the most common options. For a

# full list see the documentation:

# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,

# add these directories to sys.path here. If the directory is relative to the

# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
from datetime import datetime

# make NodeGraphQt module available.

base_path = os.path.abspath('.')
root_path = os.path.split(base_path)[0]
sys.path.insert(0, root_path)

# required for the theme template.

sys.path.insert(0, os.path.abspath('\_themes'))

import NodeGraphQt
from sphinxawesome_theme.postprocess import Icons

# -- Project information -----------------------------------------------------

project = 'NodeGraphQt'
author = NodeGraphQt.pkg_info.**author**
copyright = '{}, {}'.format(datetime.now().year, author)

# The full version, including alpha/beta/rc tags

release = '{}'.format(NodeGraphQt.VERSION)

# The short X.Y version

version = '{0}.{1}'.format(\*NodeGraphQt.VERSION.split('.'))

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.

# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be

# extensions coming with Sphinx (named 'sphinx.ext.\*') or your custom

# ones.

extensions = [
'autodocsumm',
'sphinx.ext.autodoc',
'sphinx.ext.autosectionlabel',
'sphinx.ext.autosummary',
'sphinx.ext.coverage',
'sphinx.ext.graphviz',
'sphinx.ext.inheritance_diagram',
'sphinx.ext.intersphinx',
'sphinx.ext.napoleon',
# theme template related
'sphinxawesome_theme'
]

intersphinx_mapping = { # 'python': ('https://docs.python.org/3', None),
'PySide2': ('https://doc.qt.io/qtforpython/', None),
}

# inheritance diagram remapping.

inheritance_alias = {
'NodeGraphQt.base.graph.NodeGraph': 'NodeGraphQt.NodeGraph',
'NodeGraphQt.base.graph.SubGraph': 'NodeGraphQt.SubGraph',
'NodeGraphQt.base.node.NodeObject': 'NodeGraphQt.NodeObject',
'NodeGraphQt.base.port.Port': 'NodeGraphQt.Port',
'NodeGraphQt.nodes.backdrop_node.BackdropNode': 'NodeGraphQt.BackdropNode',
'NodeGraphQt.nodes.base_node.BaseNode': 'NodeGraphQt.BaseNode',
'NodeGraphQt.nodes.base_node_circle.BaseNodeCircle': 'NodeGraphQt.BaseNodeCircle',
'NodeGraphQt.nodes.group_node.GroupNode': 'NodeGraphQt.GroupNode',
}

# autodoc options.

autodoc_default_options = {
'autosummary': True,
'members': True,
'member-order': 'bysource',
'undoc-members': False,
}

# autosummary generate stubs.

autosummary_generate = True

# autosummary overwrite generated stubs files.

autosummary_generate_option = True

rst_prolog = '''
.. |version_str| replace:: v{0}
'''.format(release)

# Add any paths that contain templates here, relative to this directory.

templates_path = ['_templates']

# The suffix(es) of source filenames.

# You can specify multiple suffix as a list of string:

#

# source_suffix = ['.rst', '.md']

source_suffix = '.rst'

# The master toctree document.

master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation

# for a list of supported languages.

#

# This is also used if you do content translation via gettext catalogs.

# Usually you set "language" from the command line for these cases.

language = 'en'

# List of patterns, relative to source directory, that match files and

# directories to ignore when looking for source files.

# This pattern also affects html_static_path and html_extra_path.

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', "_themes"]

# The name of the Pygments (syntax highlighting) style to use.

pygments_style = 'monokai'

# -- Options for HTML output -------------------------------------------------

# If given, this must be the name of an image file (path relative to the

# configuration directory) that is the favicon of the docs.

# Modern browsers use this as the icon for tabs, windows and bookmarks.

# It should be a Windows-style icon file (.ico), which is 16x16 or 32x32

# pixels large. Default: None.

html_favicon = '\_images/favicon.png'
html_logo = None

# The theme to use for HTML and HTML Help pages. See the documentation for

# a list of builtin themes.

html_theme = 'sphinxawesome_theme'
html_theme_path = ['_themes']
html_show_sourcelink = False
html_show_sphinx = False
html_context = {
'display_github': True,
'github_user': 'jchanvfx',
'github_repo': 'NodeGraphQt',
'github_version': "main",
'conf_py_path': '/docs/',
'source_suffix': '.rst',
}

# Theme options are theme-specific and customize the look and feel of a theme

# further. For a list of options available for each theme, see the

# documentation.

html_title = 'NodeGraphQt'
html_permalinks_icon = (
'<svg xmlns="http://www.w3.org/2000/svg" '
'height="1em" width="1em" viewBox="0 0 24 24"'
'>'
'<path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 '
    '5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 '
    '0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/>'
'</svg>'
)
html_theme_options = {
'logo_light': '\_images/favicon.png',
'logo_dark': '\_images/favicon.png', # 'main_nav_links': { # 'Releases': 'https://github.com/jchanvfx/NodeGraphQt/releases', # },
'show_scrolltop': True,
'show_prev_next': True,
'awesome_external_links': True,
'extra_header_link_icons': {
"GitHub Repository": {
"link": "https://github.com/jchanvfx/NodeGraphQt",
"icon": (
'<svg height="26px" style="margin-top:-2px;display:inline" '
'viewBox="0 0 45 44" '
'fill="currentColor" xmlns="http://www.w3.org/2000/svg">'
'<path fill-rule="evenodd" clip-rule="evenodd" '
'd="M22.477.927C10.485.927.76 10.65.76 22.647c0 9.596 6.223 17.736 '
"14.853 20.608 1.087.2 1.483-.47 1.483-1.047 "
"0-.516-.019-1.881-.03-3.693-6.04 "
"1.312-7.315-2.912-7.315-2.912-.988-2.51-2.412-3.178-2.412-3.178-1.972-1.346.149-1.32.149-1.32 " # noqa
"2.18.154 3.327 2.24 3.327 2.24 1.937 3.318 5.084 2.36 6.321 "
"1.803.197-1.403.759-2.36 "
"1.379-2.903-4.823-.548-9.894-2.412-9.894-10.734 "
"0-2.37.847-4.31 2.236-5.828-.224-.55-.969-2.759.214-5.748 0 0 "
"1.822-.584 5.972 2.226 "
"1.732-.482 3.59-.722 5.437-.732 1.845.01 3.703.25 5.437.732 "
"4.147-2.81 5.967-2.226 "
"5.967-2.226 1.185 2.99.44 5.198.217 5.748 1.392 1.517 2.232 3.457 "
"2.232 5.828 0 "
"8.344-5.078 10.18-9.916 10.717.779.67 1.474 1.996 1.474 4.021 0 "
"2.904-.027 5.247-.027 "
"5.96 0 .58.392 1.256 1.493 1.044C37.981 40.375 44.2 32.24 44.2 "
'22.647c0-11.996-9.726-21.72-21.722-21.72" '
'fill="currentColor"/></svg>'
),
},
"PyPI Package": {
"link": "https://pypi.org/project/NodeGraphQt",
"icon": (
'<svg width="28px" height="28px" viewBox="0 0 20 20" '
'<svg fill="currentColor" viewBox="0 0 24 24" '
'xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" '
'stroke-width="0"></g><g id="SVGRepo_tracerCarrier" '
'stroke-linecap="round" stroke-linejoin="round"></g>'
'<g id="SVGRepo_iconCarrier">'
'<path d="M9.585 11.692h4.328s2.432.039 2.432-2.35V5.391S16.714'
                ' 3 11.936 3C7.362 3 7.647 4.983 7.647 4.983l.006 2.055h4.363v.'
                '617H5.92s-2.927-.332-2.927 4.282 2.555 4.45 2.555 4.45h1.524v-'
                '2.141s-.083-2.554 2.513-2.554zm-.056-5.74a.784.784 0 1 1 0-1.5'
                '7.784.784 0 1 1 0 1.57z"></path><path d="M18.452 7.532h-1.524v'
                '2.141s.083 2.554-2.513 2.554h-4.328s-2.432-.04-2.432 2.35v3.95'
                '1s-.369 2.391 4.409 2.391c4.573 0 4.288-1.983 4.288-1.983l-.00'
                '6-2.054h-4.363v-.617h6.097s2.927.332 2.927-4.282-2.555-4.451-2'
                '.555-4.451zm-3.981 10.436a.784.784 0 1 1 0 1.57.784.784 0 1 1 '
                '0-1.57z" /></path></g></svg>'
)
}
}
}

# Add any paths that contain custom static files (such as style sheets) here,

# relative to this directory. They are copied after the builtin static files,

# so a file named "default.css" will overwrite the builtin "default.css".

html_static_path = ['_static', '_images']
html_css_files = ['custom.css']

# Custom sidebar templates, must be a dictionary that maps document names

# to template names.

#

# The default sidebars (for documents that don't match any pattern) are

# defined by theme itself. Builtin themes are using these templates by

# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',

# 'searchbox.html']``.

html_sidebars = {
'\*\*': [
'sidebar_main_nav_links.html',
'sidebar_toc.html'
]
}

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.

htmlhelp_basename = 'NodeGraphQTdoc'

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples

# (source start file, name, description, authors, manual section).

man_pages = [
(master_doc, 'nodegraphqt', 'NodeGraphQt Documentation',
[author], 1)
]

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples

# (source start file, target name, title, author,

# dir menu entry, description, category)

texinfo_documents = [
(master_doc,
'NodeGraphQt', 'NodeGraphQT Documentation',
author,
'NodeGraphQt',
'Node graph framework that can be re-implemented into apps that supports PySide2.',
'Miscellaneous'),
]

# -- Options for autodoc ----------------------------------------------------

autodoc_member_order = 'groupwise'

# -- Options for image link -------------------------------------------------

html_scaled_image_link = False

</code>

docs\constants.rst:
<code>
Constants
#########

.. automodule:: NodeGraphQt.constants
:members:
:member-order: bysource

</code>

docs\index.rst:
<code>
NodeGraphQt |version_str|
#########################

.. image:: \_images/logo.png
:align: center

NodeGraphQt a node graph UI framework written in python that can be implemented.

.. image:: \_images/screenshot.png

Install

---

NodeGraphQt is available from the `The Python Package Index (PyPI) <https://pypi.org/project/NodeGraphQt/>`\_ so
you can install via `pip`.

.. code-block::

    pip install NodeGraphQt

or alternatively you can download the source `here <https://github.com/jchanvfx/NodeGraphQt/archive/refs/heads/main.zip>`\_.

Getting Started

---

To get started see the `basic_example.py <https://github.com/jchanvfx/NodeGraphQt/blob/main/examples/basic_example.py>`\_
script or checkout the :ref:`General Overview` section.

---

| Source: https://github.com/jchanvfx/NodeGraphQt
| Issues: https://github.com/jchanvfx/NodeGraphQt/issues

.. toctree::
:hidden:
:caption: Examples
:name: exmplstoc
:maxdepth: 1

    examples/ex_overview
    examples/ex_node
    examples/ex_port
    examples/ex_pipe
    examples/ex_menu
    host_apps/_index_apps

.. toctree::
:hidden:
:caption: API Reference
:name: apitoc
:maxdepth: 2
:titlesonly:

    constants
    graphs/_index_graphs
    nodes/_index_nodes
    port
    menu

.. toctree::
:hidden:
:caption: Widgets
:name: wdgtstoc
:maxdepth: 2

    node_widgets
    builtin_widgets/PropertiesBinWidget
    builtin_widgets/NodesPaletteWidget
    builtin_widgets/NodesTreeWidget

</code>

docs\make.bat:
<code>
@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=.
set BUILDDIR=\_build

if "%1" == "" goto help

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
echo.
echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
echo.installed, then set the SPHINXBUILD environment variable to point
echo.to the full path of the 'sphinx-build' executable. Alternatively you
echo.may add the Sphinx directory to PATH.
echo.
echo.If you don't have Sphinx installed, grab it from
echo.http://sphinx-doc.org/
exit /b 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%

:end
popd

</code>

docs\Makefile:
<code>

# Minimal makefile for Sphinx documentation

#

# You can set these variables from the command line.

SPHINXOPTS =
SPHINXBUILD = sphinx-build
SOURCEDIR = .
BUILDDIR = \_build

# Put it first so that "make" without argument is like "make help".

help:
@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new

# "make mode" option. $(O) is meant as a shortcut for $(SPHINXOPTS).

%: Makefile
@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
</code>

docs\menu.rst:
<code>
:hide-rtoc:

Menus

#####

| `See` :ref:`Menu Overview` `from the overview section.`

.. currentmodule:: NodeGraphQt

**Classes:**

.. autosummary::
NodeGraphMenu
NodesMenu
NodeGraphCommand

|

GraphMenu

---

| The context menu triggered from the node graph.

.. autoclass:: NodeGraphMenu
:members:
:exclude-members: qmenu
:member-order: bysource

|

NodesMenu

---

| The context menu triggered from a node.

.. autoclass:: NodesMenu
:members:
:member-order: bysource

|

NodeGraphCommand

---

.. autoclass:: NodeGraphCommand
:members:
:exclude-members: qaction
:member-order: bysource

</code>

docs\node_widgets.rst:
<code>
:hide-rtoc:

Embedded Node Widgets
#####################

| Embedded node widgets are the widgets that can be embedded into a
:class:`NodeGraphQt.BaseNode` and displayed in the node graph.

|
| To create your own widget embedded in a node see the
:ref:`Embedding Custom Widgets` example page.

**Classes:**

.. autosummary::
NodeGraphQt.NodeBaseWidget
NodeGraphQt.widgets.node_widgets.NodeCheckBox
NodeGraphQt.widgets.node_widgets.NodeComboBox
NodeGraphQt.widgets.node_widgets.NodeLineEdit

NodeBaseWidget

---

.. autoclass:: NodeGraphQt.NodeBaseWidget
:members:
:exclude-members: staticMetaObject, node, setToolTip, type\_, value, widget

NodeCheckBox

---

.. autoclass:: NodeGraphQt.widgets.node*widgets.NodeCheckBox
:members:
:exclude-members: staticMetaObject, widget, type*

NodeComboBox

---

.. autoclass:: NodeGraphQt.widgets.node*widgets.NodeComboBox
:members:
:exclude-members: staticMetaObject, widget, type*

NodeLineEdit

---

.. autoclass:: NodeGraphQt.widgets.node*widgets.NodeLineEdit
:members:
:exclude-members: staticMetaObject, widget, type*

</code>

docs\port.rst:
<code>
:hide-rtoc:

Port

####

.. autoclass:: NodeGraphQt.Port
:members:
:exclude-members: model, view
:member-order: bysource

</code>

examples\hotkeys\hotkeys.json:
<code>
[
{
"type":"menu",
"label":"&File",
"items":[
{
"type":"command",
"label":"Open...",
"file":"./hotkey_functions.py",
"function_name":"open_session",
"shortcut":"QtGui.QKeySequence.Open"
},
{
"type":"command",
"label":"Import...",
"file":"./hotkey_functions.py",
"function_name":"import_session",
"shortcut":""
},
{
"type":"command",
"label":"Clear Session...",
"file":"./hotkey_functions.py",
"function_name":"clear_session",
"shortcut":""
},
{
"type":"command",
"label":"Save...",
"file":"./hotkey_functions.py",
"function_name":"save_session",
"shortcut":"QtGui.QKeySequence.Save"
},
{
"type":"command",
"label":"Save As...",
"file":"./hotkey_functions.py",
"function_name":"save_session_as",
"shortcut":"Ctrl+Shift+S"
},
{
"type":"command",
"label":"Exit",
"file":"./hotkey_functions.py",
"function_name":"quit_qt",
"shortcut":"Ctrl+Shift+Q"
}
]
},
{
"type":"menu",
"label":"&Edit",
"items":[
{
"type":"command",
"label":"Clear Undo History",
"file":"./hotkey_functions.py",
"function_name":"clear_undo",
"shortcut":""
},
{
"type":"command",
"label":"Show Undo History",
"file":"./hotkey_functions.py",
"function_name":"show_undo_view",
"shortcut":""
},
{
"type":"separator"
},
{
"type":"command",
"label":"Copy",
"file":"./hotkey_functions.py",
"function_name":"copy_nodes",
"shortcut":"QtGui.QKeySequence.Copy"
},
{
"type":"command",
"label":"Cut",
"file":"./hotkey_functions.py",
"function_name":"cut_nodes",
"shortcut":"QtGui.QKeySequence.Cut"
},
{
"type":"command",
"label":"Paste",
"file":"./hotkey_functions.py",
"function_name":"paste_nodes",
"shortcut":"QtGui.QKeySequence.Paste"
},
{
"type":"command",
"label":"Delete",
"file":"./hotkey_functions.py",
"function_name":"delete_nodes",
"shortcut":"QtGui.QKeySequence.Delete"
},
{
"type":"separator"
},
{
"type":"command",
"label":"Select All",
"file":"./hotkey_functions.py",
"function_name":"select_all_nodes",
"shortcut":"Ctrl+A"
},
{
"type":"command",
"label":"Unselect All",
"file":"./hotkey_functions.py",
"function_name":"clear_node_selection",
"shortcut":"Ctrl+Shift+A"
},
{
"type":"command",
"label":"Invert Selection",
"file":"./hotkey_functions.py",
"function_name":"invert_node_selection"
},
{
"type":"command",
"label":"Enable/Disable",
"file":"./hotkey_functions.py",
"function_name":"disable_nodes",
"shortcut":"D"
},
{
"type":"command",
"label":"Duplicate",
"file":"./hotkey_functions.py",
"function_name":"duplicate_nodes",
"shortcut":"Alt+C"
},
{
"type":"command",
"label":"Extract",
"file":"./hotkey_functions.py",
"function_name":"extract_nodes",
"shortcut":"Ctrl+Shift+X"
},
{
"type":"command",
"label":"Clear Connections",
"file":"./hotkey_functions.py",
"function_name":"clear_node_connections",
"shortcut":"Ctrl+D"
},
{
"type":"command",
"label":"Fit to Selection",
"file":"./hotkey_functions.py",
"function_name":"fit_to_selection",
"shortcut":"F"
},
{
"type":"separator"
},
{
"type":"command",
"label":"Zoom In",
"file":"./hotkey_functions.py",
"function_name":"zoom_in",
"shortcut":"="
},
{
"type":"command",
"label":"Zoom Out",
"file":"./hotkey_functions.py",
"function_name":"zoom_out",
"shortcut":"-"
},
{
"type":"command",
"label":"Reset Zoom",
"file":"./hotkey_functions.py",
"function_name":"reset_zoom",
"shortcut":"H"
}
]
},
{
"type":"separator"
},
{
"type":"menu",
"label":"&Graph",
"items":[
{
"type":"menu",
"label":"&Background",
"items":[
{
"type":"command",
"label":"None",
"file":"./hotkey_functions.py",
"function_name":"bg_grid_none",
"shortcut":"Alt+1"
},
{
"type":"command",
"label":"Lines",
"file":"./hotkey_functions.py",
"function_name":"bg_grid_lines",
"shortcut":"Alt+2"
},
{
"type":"command",
"label":"Dots",
"file":"./hotkey_functions.py",
"function_name":"bg_grid_dots",
"shortcut":"Alt+3"
}
]
},
{
"type":"menu",
"label":"&Layout",
"items":[
{
"type":"command",
"label":"Horizontal",
"file":"./hotkey_functions.py",
"function_name":"layout_h_mode",
"shortcut":"Shift+1"
},
{
"type":"command",
"label":"Vertical",
"file":"./hotkey_functions.py",
"function_name":"layout_v_mode",
"shortcut":"Shift+2"
}
]
}
]
},
{
"type":"menu",
"label":"&Nodes",
"items":[
{
"type":"command",
"label":"Node Search",
"file":"./hotkey_functions.py",
"function_name":"toggle_node_search",
"shortcut":"Tab"
},
{
"type":"separator"
},
{
"type":"command",
"label":"Auto Layout Up Stream",
"file":"./hotkey_functions.py",
"function_name":"layout_graph_up",
"shortcut":"L"
},
{
"type":"command",
"label":"Auto Layout Down Stream",
"file":"./hotkey_functions.py",
"function_name":"layout_graph_down",
"shortcut":"Ctrl+L"
},
{
"type":"separator"
},
{
"type":"command",
"label":"Expand Group Node",
"file":"./hotkey_functions.py",
"function_name":"expand_group_node",
"shortcut":"Alt+Enter"
}
]
},
{
"type":"menu",
"label":"&Pipes",
"items":[
{
"type":"command",
"label":"Curved",
"file":"./hotkey_functions.py",
"function_name":"curved_pipe",
"shortcut":"Ctrl+1"
},
{
"type":"command",
"label":"Straight",
"file":"./hotkey_functions.py",
"function_name":"straight_pipe",
"shortcut":"Ctrl+2"
},
{
"type":"command",
"label":"Angle",
"file":"./hotkey_functions.py",
"function_name":"angle_pipe",
"shortcut":"Ctrl+3"
}
]
}
]

</code>

examples\hotkeys\hotkey_functions.py:
<code>
#!/usr/bin/python

# ------------------------------------------------------------------------------

# menu command functions

# ------------------------------------------------------------------------------

def zoom_in(graph):
"""
Set the node graph to zoom in by 0.1
"""
zoom = graph.get_zoom() + 0.1
graph.set_zoom(zoom)

def zoom_out(graph):
"""
Set the node graph to zoom in by 0.1
"""
zoom = graph.get_zoom() - 0.2
graph.set_zoom(zoom)

def reset_zoom(graph):
"""
Reset zoom level.
"""
graph.reset_zoom()

def layout_h_mode(graph):
"""
Set node graph layout direction to horizontal.
"""
graph.set_layout_direction(0)

def layout_v_mode(graph):
"""
Set node graph layout direction to vertical.
"""
graph.set_layout_direction(1)

def open_session(graph):
"""
Prompts a file open dialog to load a session.
"""
current = graph.current_session()
file_path = graph.load_dialog(current)
if file_path:
graph.load_session(file_path)

def import_session(graph):
"""
Prompts a file open dialog to load a session.
"""
current = graph.current_session()
file_path = graph.load_dialog(current)
if file_path:
graph.import_session(file_path)

def save_session(graph):
"""
Prompts a file save dialog to serialize a session if required.
"""
current = graph.current_session()
if current:
graph.save_session(current)
msg = 'Session layout saved:\n{}'.format(current)
viewer = graph.viewer()
viewer.message_dialog(msg, title='Session Saved')
else:
save_session_as(graph)

def save_session_as(graph):
"""
Prompts a file save dialog to serialize a session.
"""
current = graph.current_session()
file_path = graph.save_dialog(current)
if file_path:
graph.save_session(file_path)

def clear_session(graph):
"""
Prompts a warning dialog to new a node graph session.
"""
if graph.question_dialog('Clear Current Session?', 'Clear Session'):
graph.clear_session()

def quit_qt(graph):
"""
Quit the Qt application.
"""
from Qt import QtCore
QtCore.QCoreApplication.quit()

def clear_undo(graph):
"""
Prompts a warning dialog to clear undo.
"""
viewer = graph.viewer()
msg = 'Clear all undo history, Are you sure?'
if viewer.question_dialog('Clear Undo History', msg):
graph.clear_undo_stack()

def copy_nodes(graph):
"""
Copy nodes to the clipboard.
"""
graph.copy_nodes()

def cut_nodes(graph):
"""
Cut nodes to the clip board.
"""
graph.cut_nodes()

def paste_nodes(graph):
"""
Pastes nodes copied from the clipboard.
""" # by default the graph will inherite the global style # from the graph when pasting nodes. # to disable this behaviour set `adjust_graph_style` to False.
graph.paste_nodes(adjust_graph_style=False)

def delete_nodes(graph):
"""
Delete selected node.
"""
graph.delete_nodes(graph.selected_nodes())

def extract_nodes(graph):
"""
Extract selected nodes.
"""
graph.extract_nodes(graph.selected_nodes())

def clear_node_connections(graph):
"""
Clear port connection on selected nodes.
"""
graph.undo_stack().beginMacro('clear selected node connections')
for node in graph.selected_nodes():
for port in node.input_ports() + node.output_ports():
port.clear_connections()
graph.undo_stack().endMacro()

def select_all_nodes(graph):
"""
Select all nodes.
"""
graph.select_all()

def clear_node_selection(graph):
"""
Clear node selection.
"""
graph.clear_selection()

def invert_node_selection(graph):
"""
Invert node selection.
"""
graph.invert_selection()

def disable_nodes(graph):
"""
Toggle disable on selected nodes.
"""
graph.disable_nodes(graph.selected_nodes())

def duplicate_nodes(graph):
"""
Duplicated selected nodes.
"""
graph.duplicate_nodes(graph.selected_nodes())

def expand_group_node(graph):
"""
Expand selected group node.
"""
selected_nodes = graph.selected_nodes()
if not selected_nodes:
graph.message_dialog('Please select a "GroupNode" to expand.')
return
graph.expand_group_node(selected_nodes[0])

def fit_to_selection(graph):
"""
Sets the zoom level to fit selected nodes.
"""
graph.fit_to_selection()

def show_undo_view(graph):
"""
Show the undo list widget.
"""
graph.undo_view.show()

def curved_pipe(graph):
"""
Set node graph pipes layout as curved.
"""
from NodeGraphQt.constants import PipeLayoutEnum
graph.set_pipe_style(PipeLayoutEnum.CURVED.value)

def straight_pipe(graph):
"""
Set node graph pipes layout as straight.
"""
from NodeGraphQt.constants import PipeLayoutEnum
graph.set_pipe_style(PipeLayoutEnum.STRAIGHT.value)

def angle_pipe(graph):
"""
Set node graph pipes layout as angled.
"""
from NodeGraphQt.constants import PipeLayoutEnum
graph.set_pipe_style(PipeLayoutEnum.ANGLE.value)

def bg_grid_none(graph):
"""
Turn off the background patterns.
"""
from NodeGraphQt.constants import ViewerEnum
graph.set_grid_mode(ViewerEnum.GRID_DISPLAY_NONE.value)

def bg_grid_dots(graph):
"""
Set background node graph background with grid dots.
"""
from NodeGraphQt.constants import ViewerEnum
graph.set_grid_mode(ViewerEnum.GRID_DISPLAY_DOTS.value)

def bg_grid_lines(graph):
"""
Set background node graph background with grid lines.
"""
from NodeGraphQt.constants import ViewerEnum
graph.set_grid_mode(ViewerEnum.GRID_DISPLAY_LINES.value)

def layout_graph_down(graph):
"""
Auto layout the nodes down stream.
"""
nodes = graph.selected_nodes() or graph.all_nodes()
graph.auto_layout_nodes(nodes=nodes, down_stream=True)

def layout_graph_up(graph):
"""
Auto layout the nodes up stream.
"""
nodes = graph.selected_nodes() or graph.all_nodes()
graph.auto_layout_nodes(nodes=nodes, down_stream=False)

def toggle_node_search(graph):
"""
show/hide the node search widget.
"""
graph.toggle_node_search()

</code>

examples\hotkeys\_\_init\_\_.py:
<code>

</code>

examples\nodes\basic_nodes.py:
<code>
from NodeGraphQt import BaseNode, BaseNodeCircle

class BasicNodeA(BaseNode):
"""
A node class with 2 inputs and 2 outputs.
"""

    # unique node identifier.
    __identifier__ = 'nodes.basic'

    # initial default node name.
    NODE_NAME = 'node A'

    def __init__(self):
        super(BasicNodeA, self).__init__()

        # create node inputs.
        self.add_input('in A')
        self.add_input('in B')

        # create node outputs.
        self.add_output('out A')
        self.add_output('out B')

class BasicNodeB(BaseNode):
"""
A node class with 3 inputs and 3 outputs.
The last input and last output can take in multiple pipes.
"""

    # unique node identifier.
    __identifier__ = 'nodes.basic'

    # initial default node name.
    NODE_NAME = 'node B'

    def __init__(self):
        super(BasicNodeB, self).__init__()

        # create node inputs
        self.add_input('single 1')
        self.add_input('single 2')
        self.add_input('multi in', multi_input=True)

        # create node outputs
        self.add_output('single 1', multi_output=False)
        self.add_output('single 2', multi_output=False)
        self.add_output('multi out')

class CircleNode(BaseNodeCircle):
"""
A node class with 3 inputs and 3 outputs.
This node is a circular design.
"""

    # unique node identifier.
    __identifier__ = 'nodes.basic'

    # initial default node name.
    NODE_NAME = 'Circle Node'

    def __init__(self):
        super(CircleNode, self).__init__()
        self.set_color(10, 24, 38)

        # create node inputs
        p = self.add_input('in 1')
        p.add_accept_port_type(
            port_name='single 1',
            port_type='out',
            node_type='nodes.basic.BasicNodeB'
        )

        self.add_input('in 2')
        self.add_input('in 3', multi_input=True)
        self.add_input('in 4', display_name=False)
        self.add_input('in 5', display_name=False)

        # create node outputs
        self.add_output('out 1')
        self.add_output('out 2', multi_output=False)
        self.add_output('out 3', multi_output=True, display_name=False)
        self.add_output('out 4', multi_output=True, display_name=False)

</code>

examples\nodes\custom_ports_node.py:
<code>
#!/usr/bin/python
from Qt import QtCore, QtGui

from NodeGraphQt import BaseNode

def draw_triangle_port(painter, rect, info):
"""
Custom paint function for drawing a Triangle shaped port.

    Args:
        painter (QtGui.QPainter): painter object.
        rect (QtCore.QRectF): port rect used to describe parameters
                              needed to draw.
        info (dict): information describing the ports current state.
            {
                'port_type': 'in',
                'color': (0, 0, 0),
                'border_color': (255, 255, 255),
                'multi_connection': False,
                'connected': False,
                'hovered': False,
            }
    """
    painter.save()

    size = int(rect.height() / 2)
    triangle = QtGui.QPolygonF()
    triangle.append(QtCore.QPointF(-size, size))
    triangle.append(QtCore.QPointF(0.0, -size))
    triangle.append(QtCore.QPointF(size, size))

    transform = QtGui.QTransform()
    transform.translate(rect.center().x(), rect.center().y())
    port_poly = transform.map(triangle)

    # mouse over port color.
    if info['hovered']:
        color = QtGui.QColor(14, 45, 59)
        border_color = QtGui.QColor(136, 255, 35)
    # port connected color.
    elif info['connected']:
        color = QtGui.QColor(195, 60, 60)
        border_color = QtGui.QColor(200, 130, 70)
    # default port color
    else:
        color = QtGui.QColor(*info['color'])
        border_color = QtGui.QColor(*info['border_color'])

    pen = QtGui.QPen(border_color, 1.8)
    pen.setJoinStyle(QtCore.Qt.MiterJoin)

    painter.setPen(pen)
    painter.setBrush(color)
    painter.drawPolygon(port_poly)

    painter.restore()

def draw_square_port(painter, rect, info):
"""
Custom paint function for drawing a Square shaped port.

    Args:
        painter (QtGui.QPainter): painter object.
        rect (QtCore.QRectF): port rect used to describe parameters
                              needed to draw.
        info (dict): information describing the ports current state.
            {
                'port_type': 'in',
                'color': (0, 0, 0),
                'border_color': (255, 255, 255),
                'multi_connection': False,
                'connected': False,
                'hovered': False,
            }
    """
    painter.save()

    # mouse over port color.
    if info['hovered']:
        color = QtGui.QColor(14, 45, 59)
        border_color = QtGui.QColor(136, 255, 35, 255)
    # port connected color.
    elif info['connected']:
        color = QtGui.QColor(195, 60, 60)
        border_color = QtGui.QColor(200, 130, 70)
    # default port color
    else:
        color = QtGui.QColor(*info['color'])
        border_color = QtGui.QColor(*info['border_color'])

    pen = QtGui.QPen(border_color, 1.8)
    pen.setJoinStyle(QtCore.Qt.MiterJoin)

    painter.setPen(pen)
    painter.setBrush(color)
    painter.drawRect(rect)

    painter.restore()

class CustomPortsNode(BaseNode):
"""
example test node with custom shaped ports.
"""

    # set a unique node identifier.
    __identifier__ = 'nodes.custom.ports'

    # set the initial default node name.
    NODE_NAME = 'node'

    def __init__(self):
        super(CustomPortsNode, self).__init__()

        # create input and output port.
        self.add_input('in', color=(200, 10, 0))
        self.add_output('default')
        self.add_output('square', painter_func=draw_square_port)
        self.add_output('triangle', painter_func=draw_triangle_port)

</code>

examples\nodes\group_node.py:
<code>
from NodeGraphQt import GroupNode

class MyGroupNode(GroupNode):
"""
example test group node with a in port and out port.
"""

    # set a unique node identifier.
    __identifier__ = 'nodes.group'

    # set the initial default node name.
    NODE_NAME = 'group node'

    def __init__(self):
        super(MyGroupNode, self).__init__()
        self.set_color(50, 8, 25)

        # create input and output port.
        self.add_input('in')
        self.add_output('out')

</code>

examples\nodes\widget_nodes.py:
<code>
from NodeGraphQt import BaseNode

class DropdownMenuNode(BaseNode):
"""
An example node with a embedded added QCombobox menu.
"""

    # unique node identifier.
    __identifier__ = 'nodes.widget'

    # initial default node name.
    NODE_NAME = 'menu'

    def __init__(self):
        super(DropdownMenuNode, self).__init__()

        # create input & output ports
        self.add_input('in 1')
        self.add_output('out 1')
        self.add_output('out 2')

        # create the QComboBox menu.
        items = ['item 1', 'item 2', 'item 3']
        self.add_combo_menu('my_menu', 'Menu Test', items=items,
                            tooltip='example custom tooltip')

class TextInputNode(BaseNode):
"""
An example of a node with a embedded QLineEdit.
"""

    # unique node identifier.
    __identifier__ = 'nodes.widget'

    # initial default node name.
    NODE_NAME = 'text'

    def __init__(self):
        super(TextInputNode, self).__init__()

        # create input & output ports
        self.add_input('in')
        self.add_output('out')

        # create QLineEdit text input widget.
        self.add_text_input('my_input', 'Text Input', tab='widgets')

class CheckboxNode(BaseNode):
"""
An example of a node with 2 embedded QCheckBox widgets.
"""

    # set a unique node identifier.
    __identifier__ = 'nodes.widget'

    # set the initial default node name.
    NODE_NAME = 'checkbox'

    def __init__(self):
        super(CheckboxNode, self).__init__()

        # create the checkboxes.
        self.add_checkbox('cb_1', '', 'Checkbox 1', True)
        self.add_checkbox('cb_2', '', 'Checkbox 2', False)

        # create input and output port.
        self.add_input('in', color=(200, 100, 0))
        self.add_output('out', color=(0, 100, 200))

</code>

examples\nodes\_\_init\_\_.py:
<code>

</code>

examples\basic_example.py:
<code>
#!/usr/bin/python

# -_- coding: utf-8 -_-

import signal
from pathlib import Path

from Qt import QtCore, QtWidgets

# import example nodes from the "nodes" sub-package

from examples.nodes import basic_nodes, custom_ports_node, group_node, widget_nodes
from NodeGraphQt import (
NodeGraph,
NodesPaletteWidget,
NodesTreeWidget,
PropertiesBinWidget,
)
from NodeGraphQt.constants import LayoutDirectionEnum

BASE_PATH = Path(**file**).parent.resolve()

def main(): # handle SIGINT to make the app terminate on CTRL+C
signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtWidgets.QApplication([])

    # create graph controller.
    graph = NodeGraph()

    # set up context menu for the node graph.
    hotkey_path = Path(BASE_PATH, 'hotkeys', 'hotkeys.json')
    graph.set_context_menu_from_file(hotkey_path, 'graph')

    # registered example nodes.
    graph.register_nodes(
        [
            basic_nodes.BasicNodeA,
            basic_nodes.BasicNodeB,
            basic_nodes.CircleNode,
            custom_ports_node.CustomPortsNode,
            group_node.MyGroupNode,
            widget_nodes.DropdownMenuNode,
            widget_nodes.TextInputNode,
            widget_nodes.CheckboxNode,
        ]
    )

    # show the node graph widget.
    graph_widget = graph.widget
    graph_widget.resize(1100, 800)
    graph_widget.setWindowTitle("NodeGraphQt Example")
    graph_widget.show()

    # create node with custom text color and disable it.
    n_basic_a = graph.create_node(
        'nodes.basic.BasicNodeA', text_color='#feab20')
    n_basic_a.set_disabled(True)

    # create node with vertial alignment
    n_basic_a_vertical = graph.create_node(
        "nodes.basic.BasicNodeA", name="Vertical Node", text_color="#feab20"
    )

    # adjust layout of node to be vertical
    n_basic_a_vertical.set_layout_direction(1)

    # create node and set a custom icon.
    n_basic_b = graph.create_node(
        'nodes.basic.BasicNodeB', name='custom icon')
    n_basic_b.set_icon(Path(BASE_PATH, 'star.png'))

    # create node with the custom port shapes.
    n_custom_ports = graph.create_node(
        'nodes.custom.ports.CustomPortsNode', name='custom ports')

    # create node with the embedded QLineEdit widget.
    n_text_input = graph.create_node(
        'nodes.widget.TextInputNode', name='text node', color='#0a1e20')

    # create node with the embedded QCheckBox widgets.
    n_checkbox = graph.create_node(
        'nodes.widget.CheckboxNode', name='checkbox node')

    # create node with the QComboBox widget.
    n_combo_menu = graph.create_node(
        'nodes.widget.DropdownMenuNode', name='combobox node')

    # crete node with the circular design.
    n_circle = graph.create_node(
        'nodes.basic.CircleNode', name='circle node')

    # create group node.
    n_group = graph.create_node('nodes.group.MyGroupNode')

    # make node connections.

    # (connect nodes using the .set_output method)
    n_text_input.set_output(0, n_custom_ports.input(0))
    n_text_input.set_output(0, n_checkbox.input(0))
    n_text_input.set_output(0, n_combo_menu.input(0))
    # (connect nodes using the .set_input method)
    n_group.set_input(0, n_custom_ports.output(1))
    n_basic_b.set_input(2, n_checkbox.output(0))
    n_basic_b.set_input(2, n_combo_menu.output(1))
    # (connect nodes using the .connect_to method from the port object)
    port = n_basic_a.input(0)
    port.connect_to(n_basic_b.output(0))

    # auto layout nodes.
    graph.auto_layout_nodes()

    # crate a backdrop node and wrap it around
    # "custom port node" and "group node".
    n_backdrop = graph.create_node('Backdrop')
    n_backdrop.wrap_nodes([n_custom_ports, n_combo_menu])

    # fit nodes to the viewer.
    graph.clear_selection()
    graph.fit_to_selection()

    # adjust layout of node to be vertical (for all nodes).
    # graph.set_layout_direction(LayoutDirectionEnum.VERTICAL.value)

    # Custom builtin widgets from NodeGraphQt
    # ---------------------------------------

    # create a node properties bin widget.
    properties_bin = PropertiesBinWidget(node_graph=graph, parent=graph_widget)
    properties_bin.setWindowFlags(QtCore.Qt.Tool)

    # example show the node properties bin widget when a node is double-clicked.
    def display_properties_bin(node):
        if not properties_bin.isVisible():
            properties_bin.show()

    # wire function to "node_double_clicked" signal.
    graph.node_double_clicked.connect(display_properties_bin)

    # create a nodes tree widget.
    nodes_tree = NodesTreeWidget(node_graph=graph)
    nodes_tree.set_category_label('nodeGraphQt.nodes', 'Builtin Nodes')
    nodes_tree.set_category_label('nodes.custom.ports', 'Custom Port Nodes')
    nodes_tree.set_category_label('nodes.widget', 'Widget Nodes')
    nodes_tree.set_category_label('nodes.basic', 'Basic Nodes')
    nodes_tree.set_category_label('nodes.group', 'Group Nodes')
    # nodes_tree.show()

    # create a node palette widget.
    nodes_palette = NodesPaletteWidget(node_graph=graph)
    nodes_palette.set_category_label('nodeGraphQt.nodes', 'Builtin Nodes')
    nodes_palette.set_category_label('nodes.custom.ports', 'Custom Port Nodes')
    nodes_palette.set_category_label('nodes.widget', 'Widget Nodes')
    nodes_palette.set_category_label('nodes.basic', 'Basic Nodes')
    nodes_palette.set_category_label('nodes.group', 'Group Nodes')
    # nodes_palette.show()

    app.exec()

if **name** == '**main**':
main()

</code>

examples\_\_init\_\_.py:
<code>

</code>
