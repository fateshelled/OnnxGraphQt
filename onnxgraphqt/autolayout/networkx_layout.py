import networkx as nx
import numpy as np

from .. import LayoutBackend, layout_backend

# const options = {};
# options.nodesep = 20;
# options.ranksep = 20;


class GraphLayerOut:
    """
    MIT License

    Copyright (c) Lutz Roeder

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    """

    def __init__(self):
        self.viewGraph = nx.DiGraph()
        self._nodeKey = 0
        self._arguments = {}
        self._nodes = {}
        self.nodes = []
        self.inputs = []
        self.outputs = []

    def _addNode(self, value: dict):
        self._nodes[id(value)] = value
        self.viewGraph.add_node(id(value))
        return id(value)

    def createNode(self, node):
        value = node
        self._nodeKey += 1
        # value["name"] = str(self._nodeKey)
        # value.name = node.name;
        self.nodes.append(value)
        return self._addNode(value)

    def createInput(self, value):
        # print("createInput", value)
        self._nodeKey += 1
        # value["name"] = str(self._nodeKey)
        self.inputs.append(value)
        return self._addNode(value)

    def createArgument(self, argument):
        name = argument["name"]
        if name not in self._arguments:
            self._arguments[name] = self._addNode(argument)
        return self._arguments[name]

    def createOutput(self, output):
        value = output
        self._nodeKey += 1
        # value["name"] = str(self._nodeKey)
        self.outputs.append(value)
        return self._addNode(value)

    def add(self, graph):
        clusters = set()
        clusterParentMap = {}
        groups = graph.get("groups", None)
        if groups:
            for node in graph["nodes"]:
                gr = node.get("group", None)
                if gr:
                    path = gr.split("/")
                    while len(path) > 0:
                        name = path.join("/")
                        path.pop()
                        clusterParentMap[name] = path.join("/")

        for input in graph.get("inputs", ()):
            viewInput = self.createInput(input)
            for argument in input.get("arguments", ()):
                argO = self.createArgument(argument)
                self.viewGraph.add_edge(viewInput, argO)

        for node in graph.get("nodes", ()):
            viewNode = self.createNode(node)

            inputs = node.get("inputs", ())
            for input in inputs:
                for argument in input.get("arguments", ()):
                    if argument["name"] != "" and not argument["initializer"]:
                        argO = self.createArgument(argument)
                        self.viewGraph.add_edge(argO, viewNode)

            outputs = node.get("outputs", ())

            chain = node.get("chain", ())
            if chain:
                chainOutputs = node.chain[-1].get("outputs", ())
                if chainOutputs:
                    outputs = chainOutputs

            for output in outputs:
                for argument in output.get("arguments", ()):
                    if not argument:
                        raise view.Error("Invalid null argument in '" + self.model.identifier + "'.")

                    if argument.get("name", "") != "":
                        argO = self.createArgument(argument)
                        self.viewGraph.add_edge(viewNode, argO)

            cD = node.get("controlDependencies", ())
            if cD:
                for argument in cD:
                    argO = self.createArgument(argument)
                    self.viewGraph.add_edge(argO, viewNode)
                    # .to(viewNode, true)

            def createCluster(name):
                if not clusters.has(name):
                    self.setNode({name: name, rx: 5, ry: 5})
                    clusters.add(name)
                    parent = clusterParentMap.get(name)
                    if parent:
                        createCluster(parent)
                        self.setParent(name, parent)

            if groups:
                groupName = node.group
                if groupName and groupName.length > 0:
                    if not clusterParentMap.has(groupName):
                        lastIndex = groupName.lastIndexOf("/")
                        if lastIndex != -1:
                            groupName = groupName.substring(0, lastIndex)
                            if not clusterParentMap.has(groupName):
                                groupName = null
                        else:
                            groupName = null
                    if groupName:
                        createCluster(groupName + "\ngroup")
                        self.setParent(viewNode.name, groupName + "\ngroup")

        for output in graph.get("outputs", ()):
            viewOutput = self.createOutput(output)
            for argument in output.get("arguments", ()):
                argO = self.createArgument(argument)
                self.viewGraph.add_edge(argO, viewOutput)


class LayoutTransformer:
    __slots__ = ()

    LAYOUTER = None

    @classmethod
    def do_layout(cls, graph):
        raise NotImplementedError

    @classmethod
    def layout(cls, graph):
        l = cls.do_layout(graph)
        k = l.keys()
        v = list(l.values())
        v = np.array(v)
        return k, cls.postprocess(v)

    @classmethod
    def postprocess(cls, v):
        v -= v.mean(axis=0)
        v /= v.std(axis=0)
        return v


class TopoLayout(LayoutTransformer):
    """You need https://github.com/networkx/networkx/pull/3792 to use this"""

    __slots__ = ()

    @classmethod
    def do_layout(cls, graph):
        from networkx.drawing import topo_layout

        return topo_layout(graph)[0]


class SugiyamaLayout(LayoutTransformer):
    """You need https://github.com/networkx/networkx/pull/5991 to use this and the deps mentioned in https://github.com/KOLANICH-libs/networkx/blob/sugiyama_layout/networkx/drawing/nx_msagl.py"""

    __slots__ = ()

    @classmethod
    def do_layout(cls, graph):
        from math import pi

        from networkx.drawing.nx_msagl import sugiyama_layout, SugiyamaLayoutSettings, PlaneTransformation
        s = SugiyamaLayoutSettings()
        s.Transformation = PlaneTransformation.Rotation(pi)
        s.NodeSeparation = 20
        s.LayerSeparation = 20
        #s.MinNodeHeight
        #s.MinNodeWidth

        return sugiyama_layout(graph, s)


class GraphVizLayout(LayoutTransformer):
    """You need https://github.com/pygraphviz/pygraphviz to use this"""

    __slots__ = ()

    @classmethod
    def do_layout(cls, graph):
        from networkx.drawing.nx_agraph import graphviz_layout

        return graphviz_layout(graph, prog="dot")

    @classmethod
    def postprocess(cls, v):
        return -super().postprocess(v)


layouter_chooser = {
    LayoutBackend.networkx_graphviz: GraphVizLayout,
    LayoutBackend.networkx_topo: TopoLayout,
    LayoutBackend.networkx_msagl_sugiyama: SugiyamaLayout,
}

LAYOUTER = layouter_chooser[layout_backend]


def request_networkx_layout(graph_data):
    viewGraph = GraphLayerOut()
    viewGraph.add(graph_data)

    k, v = LAYOUTER.layout(viewGraph.viewGraph)
    v *= np.array([20, 1000])  # IDK, we need to eliminate it and normalize on screen size, but this data is not passed to backend, and returning the whitened data results into poor rendering

    for iD, (x, y) in zip(k, v):
        v = viewGraph._nodes[iD]
        v["layout"] = {"x": x, "y": y}

    response = {}
    response["inputs"] = {}
    response["nodes"] = {}
    response["outputs"] = {}

    for v in viewGraph.inputs:
        response["inputs"][v["name"]] = v["layout"]
    for v in viewGraph.outputs:
        response["outputs"][v["name"]] = v["layout"]
    for v in viewGraph.nodes:
        response["nodes"][v["name"]] = v["layout"]

    return response
