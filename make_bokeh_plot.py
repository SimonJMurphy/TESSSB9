import numpy as np
import pandas as pd
from bokeh.plotting import figure
from bokeh.io import show, output_notebook
import bokeh
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.models import HoverTool,  WheelZoomTool, ColorBar
from bokeh.palettes import Viridis
from bokeh.transform import linear_cmap

tf = pd.read_csv("plot_df.csv")

output_file("index.html", title='TESSSB9')
source = ColumnDataSource(
        data=dict(
            x=tf['logp'].values,
            y=tf['e'].values,
            fts = tf['fts'].values,
            lks = tf['lks'].values,
            scaled_fts = tf['scaled_fts'].values,
            folded_lks = tf['folded_lks'].values,
            TIC = tf["TIC"].values,
            Sys = tf["SysNum"].values,
            Orb = tf["OrbNum"].values,
            color = tf["numRVs"].values
        )
    )
hover = HoverTool(# height="200" alt="@imgs" width="500"
        tooltips="""
        <div style="font-family: verdana; width : 430px; position: fixed; left: 100px; top: 50px; border: 2px solid @color; background: #f5f5f5; padding: 10px">
            <div>
                <img
                    src="@lks" alt="lks" width="420"
                    border="2"
                ></img>
            </div>
            <div>
                <img
                    src="@scaled_fts" alt="scaled_fts" width="420"
                    border="2"
                ></img>
            </div>
            <div>
                <span style="font-size: 17px; font-weight: bold;">TIC @TIC, SB9 system @Sys orbit @Orb</span>
            </div>
        </div>
        """
    )
wheel = WheelZoomTool()
p = figure(#plot_width=900, plot_height=900, 
           tools=[hover, 'zoom_in', 'undo', wheel, 'reset', 'box_zoom'],
           title="TESSSB9", 
           toolbar_location="above",
           sizing_mode='stretch_both',
           x_range=(-1,5), y_range=(0,1),
            output_backend="webgl"
          )

mapper = linear_cmap(
    field_name="color",
    palette=bokeh.palettes.Viridis256,
    low=0,
    high=20,
)

p.circle('x', 'y',radius=0.01,fill_alpha=0.6,source=source,line_color=mapper,color=mapper)
p.xaxis.axis_label = 'log period, d'
p.yaxis.axis_label = 'eccentricity'
p.xaxis.axis_label_text_font_size = "18pt"
p.yaxis.axis_label_text_font_size = "18pt"
p.xaxis.major_label_text_font_size = "15pt"
p.yaxis.major_label_text_font_size = "15pt"
p.title.text_font_size = "15pt"
p.xaxis.axis_label_text_font_style = 'normal'
p.yaxis.axis_label_text_font_style = 'normal'
p.toolbar.active_scroll=wheel
color_bar = ColorBar(color_mapper=mapper["transform"], width=8, location=(0, 0), major_label_overrides={'0': 'NumRV=0', '20': '>20'})
p.add_layout(color_bar, "right")
show(p)