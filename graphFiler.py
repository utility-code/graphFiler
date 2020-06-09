import math
import folderstats
from bokeh.io import output_file, show
from bokeh.models import (BoxSelectTool, Circle, EdgesAndLinkedNodes, HoverTool,
                          MultiLine, NodesAndLinkedEdges, Plot, Range1d, TapTool,)
from bokeh.palettes import Spectral8
from bokeh.plotting import from_networkx
import matplotlib.pyplot as plt
import networkx as nx
from bokeh.models import *
import numpy as np

def ret_name(x): return str(x).split("/")[-1]

def save_graph(fol_path):
    df = folderstats.folderstats(fol_path, ignore_hidden=True)

    df.loc[list(np.where(df["folder"]==True)[0]),"name"] = df[df["folder"]==True]["path"].apply(ret_name).values
    
#     df["name"] = df["name"]+"."+df["extension"]
    df_sorted = df.sort_values(by='id')

    G = nx.Graph()
    for i, row in df_sorted.iterrows():
        if row.parent:
            G.add_edge(row.id, row.parent)



    plot = Plot(plot_width=1000, plot_height=1000,
                x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))
    plot.title.text = "File System"

    plot.add_tools(TapTool(), BoxSelectTool(), BoxZoomTool(), ResetTool(),WheelZoomTool(),PanTool())

    graph_renderer = from_networkx(G, nx.spring_layout, scale=2, center=(0,0))


    graph_renderer.node_renderer.data_source.data["id"] = df_sorted["id"].astype('str').values


    graph_renderer.node_renderer.data_source.data["name"] = df_sorted["name"]
    graph_renderer.node_renderer.data_source.data["links"] = df_sorted["path"]
    graph_renderer.node_renderer.data_source.add(Spectral8, 'color')
    graph_renderer.node_renderer.glyph = Circle(size=20, fill_color="color")
    graph_renderer.node_renderer.selection_glyph = Circle(size=20, fill_color="color")
    graph_renderer.node_renderer.hover_glyph = Circle(size=20, fill_color="color")

    graph_renderer.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=5)
    graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=5)
    graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=5)

    graph_renderer.selection_policy = NodesAndLinkedEdges()
    graph_renderer.inspection_policy = EdgesAndLinkedNodes()

    pos = graph_renderer.layout_provider.graph_layout
    x,y=zip(*pos.values())

    url = "@links"

    code = """
    console.log(source.data)
    var data = source.data.file;
    var ind= cb_data.source.selected.indices;
    console.log(data[ind])
    window.open(data[ind])
    //window.location.href = data[ind]

    """

    source = ColumnDataSource({'x':x,'y':y, 'field': df_sorted["name"].values,'file': df_sorted["path"].values})
    labels = LabelSet(x='x', y='y', text='field', source=source)

    taptool = plot.select(type=TapTool)
    taptool.callback = CustomJS(args=dict(source = source), code=code)


    plot.renderers.append(graph_renderer)
    plot.renderers.append(labels)
    output_file("interactive_graphs.html")
    show(plot)

save_graph('/media/subhaditya/DATA/Github/PaperImplementations/')