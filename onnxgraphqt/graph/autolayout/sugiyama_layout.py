import networkx as nx
import grandalf as grand
from grandalf.layouts import SugiyamaLayout

__all__ = ["sugiyama_layout"]


def sugiyama_layout(g: nx.Graph):
    gg = grand.utils.convert_nextworkx_graph_to_grandalf(g) # undocumented function

    class defaultview(object):
        w, h = 400, 100
    for v in gg.V(): v.view = defaultview()
    if len(gg.C) == 0:
        return {}
    sug = SugiyamaLayout(gg.C[0])
    sug.init_all(optimize=False)
    sug.draw()

    pos = {v.data: (v.view.xy[0], v.view.xy[1]) for v in gg.C[0].sV} # Extracts the positions
    return pos
