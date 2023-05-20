import os

import backtrader.plot
import tornado.template

class ChartJsPlot(backtrader.plot.Plot):
    def plot(self, strategy, figid=0, numfigs=1, iplot=True, start=None, end=None, **kwargs):
        with open("out.html", "wt", encoding="utf-8") as fh:
            dtimes = strategy.lines.datetime.plot()
            data0 = strategy.datas[0]
            
            fh.write("<html>")
            fh.write(
            """
            <head>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.js"></script>
            </head>
            """)
            fh.write("<body>")
            fh.write(
            """
            <canvas id="myChart" style="width:100%%;max-width:700px"></canvas>
            <script>        
            new Chart("myChart", {{
                type: "line",
                data: {{
                    labels: [{}],
                    datasets: [
                        {{
                            data: [{}],
                            label: "AAPL"
                        }},
                    ]
                }},
                options:{{
                    legend: {{ display: true }},
                }}
            }});
            </script>
            """.format(
                ",".join([f"'{i}'" for i in dtimes]),
                ",".join([1,2,3])
            ))
            fh.write("</body>")
            fh.write("</html>")

    def show(self):
        os.startfile("out.html")
