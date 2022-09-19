import os, sys

from enum import Enum

__all__ = ("LayoutBackend", "layout_backend")


class LayoutBackend(Enum):
    nx_gv = networkx_graphviz = "nx_gv"
    nx_topo = networkx_topo = "nx_topo"
    nx_msagl_sugiyama = networkx_msagl_sugiyama = "nx_msagl_sugiyama"
    node_dagre = "node_dagre"


LAYOUT_BACKEND_PARAM_NAME = "ONNX_GRAPH_QT_LAYOUT_BACKEND"
DEFAULT_BACKEND = LayoutBackend.networkx_graphviz


def getLayoutBackendParam() -> LayoutBackend:
    return LayoutBackend(os.environ.get(LAYOUT_BACKEND_PARAM_NAME, DEFAULT_BACKEND))


layout_backend = getLayoutBackendParam()

print("layout_backend (controlled by ONNX_GRAPH_QT_LAYOUT_BACKEND):", layout_backend, file=sys.stderr)
