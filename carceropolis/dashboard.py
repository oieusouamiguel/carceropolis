import threading

import pandas as pd

from tornado.ioloop import IOLoop
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.layouts import widgetbox, row
from bokeh.models import ColumnDataSource, RangeSlider
from bokeh.models.widgets.inputs import Select
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.models import HoverTool


def load_db():
    df = pd.read_csv('test.csv')
    df.ano = df.ano.astype(str)
    return df


class Dashboard(object):
    '''
    This class represents a dashboard and should be instanciated
    for each user.
    The `generate` static method is used by the Bokeh server to
    instanciate dashboards.
    '''

    # TODO: maybe remove this?
    df = load_db()

    @staticmethod
    def generate(doc):
        '''
        Generate a new dashboard. This function should be passed
        to the Bokeh FunctionHandler.
        '''
        return Dashboard(Dashboard.df.copy(), doc)

    def __init__(self, df, doc):
        '''
        Called when a user connects. This dashboard should be used
        while the connection remain, and is used by only one user.
        '''

        self.chart_types = {
            'linha': self.plot_lines,
            'barras horizontais': self.plot_hbar,
            'barras verticais': self.plot_vbar,
            'círculos': self.plot_circles,
        }

        self.df = df
        self.doc = doc
        self.columns = sorted(df.columns)
        self.discrete = [x for x in self.columns if self.df[x].dtype == object]
        # continuous = [x for x in columns if x not in discrete]
        # discrete.append(continuous.pop(continuous.index('ano')))

        self.x_sel = Select(
            title='X-Axis', value='ano', options=self.columns)

        self.y_sel = Select(
            title='Y-Axis', value='pop_masc', options=self.columns)

        charts_names = list(self.chart_types)
        self.chart_type_sel = Select(
            title='Tipo de Gráfico',
            value=charts_names[2],
            options=charts_names)

        none_value = 'Nenhum'
        self.filter_options = [none_value]+self.columns
        self.filter_sel = Select(
            title='Filtro', value=self.filter_options[0],
            options=self.filter_options)

        self.filter_value_sel = Select(
            title='Valor', value=none_value,
            options=[none_value])

        controls = [
            self.x_sel,
            self.y_sel,
            self.chart_type_sel,
            self.filter_sel,
            self.filter_value_sel,
        ]

        # Bind callbacks
        [control.on_change('value', self.update) for control in controls]

        self.filter_range_sel = RangeSlider(
            start=0, end=10, range=(1, 9), step=1, title="Valores")
        self.filter_range_sel.on_change('range', self.update)
        controls.append(self.filter_range_sel)

        controls = widgetbox(controls, width=200)
        self.layout = row(controls, self.create_figure())

        doc.add_root(self.layout)

    def update(self, attr, old, new):
        '''
        Called when chart options are modified.
        '''
        self.layout.children[1] = self.create_figure()

    def plot_lines(self, fig, x, y, source):
        fig.line(x, y, source=source)
        # plot.line(x=xs, width=0.5, bottom=0, top=ys)

    def plot_vbar(self, fig, x, y, source):
        fig.vbar(x, 0.5, y, source=source)
        # plot.vbar(x=xs, width=0.5, bottom=0, top=ys)

    def plot_hbar(self, fig, x, y, source):
        fig.hbar(y=y, height=0.5, right=x, left=0, source=source)

    def plot_circles(self, fig, x, y, source):
        fig.circle(x, y, source=source)
        # plot.circle(x=xs, y=ys)

    def create_figure(self):
        '''
        Creates the chart.
        '''
        df = self.df

        if self.filter_sel.value != self.filter_options[0]:
            if self.filter_sel.value in self.discrete:
                self.filter_value_sel.options = sorted(
                    list(df[self.filter_sel.value].unique()))
                if self.filter_value_sel.value not in self.filter_value_sel.options:
                    self.filter_value_sel.value = self.filter_value_sel.options[0]
            else:
                # TODO: continuous, use range
                pass

            # filter df
            print(self.filter_value_sel.value)
            df = df[df[self.filter_sel.value] == self.filter_value_sel.value]
            # import IPython;IPython.embed()

        df = df.groupby(self.x_sel.value).sum()
        print(df)
        source = ColumnDataSource(data=df)

        xs = self.df[self.x_sel.value].values
        ys = self.df[self.y_sel.value].values
        x_title = self.x_sel.value.title()
        y_title = self.y_sel.value.title()

        kw = dict()
        if self.x_sel.value in self.discrete:
            kw['x_range'] = sorted(set(xs))
        if self.y_sel.value in self.discrete:
            kw['y_range'] = sorted(set(ys))
        kw['title'] = "%s vs %s" % (x_title, y_title)

        fig = figure(plot_height=600, plot_width=800,
                     tools='pan,box_zoom,reset,save', **kw)
        fig.xaxis.axis_label = x_title
        fig.yaxis.axis_label = y_title

        if self.x_sel.value in self.discrete:
            fig.xaxis.major_label_orientation = pd.np.pi / 4

        self.chart_types[self.chart_type_sel.value](
            fig, self.x_sel.value, self.y_sel.value, source)

        hover = HoverTool(tooltips=[
            ("index", "$index"),
            (self.x_sel.value, '@'+self.x_sel.value),
            (self.y_sel.value, '@'+self.y_sel.value),
        ])
        fig.add_tools(hover)

        return fig


class BackgroundBokeh(threading.Thread):

    def run(self):
        bokeh_app = Application(FunctionHandler(Dashboard.generate))
        io_loop = IOLoop.current()
        server = Server({'/bkapp': bokeh_app}, io_loop=io_loop,
                        allow_websocket_origin=["localhost:8000"])
        server.start()
        io_loop.start()

    def stop(self):
        IOLoop.current().stop()


bokeh_server = BackgroundBokeh()


def start_server():
    print('> Starting Bokeh server')
    bokeh_server.start()


def stop_server():
    print('> Stopping Bokeh server')
    bokeh_server.stop()
