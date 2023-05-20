import os

import backtrader.plot
import tornado.template


class ChartJsPlot(backtrader.plot.Plot):
    def plot(self, strategy, figid=0, numfigs=1, iplot=True, start=None, end=None, **kwargs):
        with open("trading/chartjs/template.html", "rt", encoding="utf-8") as fh:
            template_str = fh.read()
        template = tornado.template.Template(template_str)
        del template_str
        with open("output/out.html", "wt", encoding="utf-8") as fh:
            fh.write(template.generate(
                dtimes = strategy.lines.datetime.plot(),
                data = strategy.datas[0],
            ))

    def show(self):
        os.startfile("output/out.html")
