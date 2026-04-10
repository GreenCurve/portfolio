# shiny/app.py
import random
from shiny import App, ui, render, reactive

# ─────────────────────────────────────────
# OOP Layer
# ─────────────────────────────────────────

class DataGenerator:
    """Responsible for producing synthetic data."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)

    def generate(self, n_points: int, noise: float) -> dict:
        x = list(range(n_points))
        y = [round(i * 2.5 + random.uniform(-noise, noise), 2) for i in x]
        return {"x": x, "y": y}


class DataSummary:
    """Responsible for computing statistics from data."""

    def __init__(self, data: dict):
        self.data = data

    def mean_y(self) -> float:
        return round(sum(self.data["y"]) / len(self.data["y"]), 2)

    def max_y(self) -> float:
        return max(self.data["y"])

    def min_y(self) -> float:
        return min(self.data["y"])

    def to_text(self) -> str:
        return (
            f"Mean: {self.mean_y()} | "
            f"Min: {self.min_y()} | "
            f"Max: {self.max_y()}"
        )


class ChartBuilder:
    """Responsible for rendering an HTML bar chart from data."""

    def __init__(self, data: dict):
        self.data = data

    def render_html(self) -> str:
        max_val = max(self.data["y"]) or 1
        bars = ""
        for x_val, y_val in zip(self.data["x"], self.data["y"]):
            height = int((y_val / max_val) * 200)
            bars += f"""
            <div style="display:inline-block; margin:2px; text-align:center;">
              <div style="
                width:28px; height:{height}px;
                background: linear-gradient(180deg, #ff9f43, #e67e22);
                border-radius:4px 4px 0 0;
              "></div>
              <div style="font-size:10px; color:#555;">{x_val}</div>
            </div>"""
        return f"""
        <div style="
          display:flex; align-items:flex-end;
          padding:20px; background:#f9f9f9;
          border-radius:8px; flex-wrap:wrap;
        ">{bars}</div>"""


# ─────────────────────────────────────────
# Shiny UI
# ─────────────────────────────────────────

app_ui = ui.page_fluid(
    ui.h2("📊 Interactive Data Explorer"),
    ui.p("Adjust the sliders to regenerate the data. Built with OOP in Python."),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_slider("n_points", "Number of Points", 5, 30, 15),
            ui.input_slider("noise", "Noise Level", 0, 50, 10),
            ui.input_action_button("regenerate", "🔄 Regenerate", class_="btn-primary"),
        ),
        ui.output_ui("chart"),
        ui.output_text("summary"),
    ),
)

# ─────────────────────────────────────────
# Shiny Server
# ─────────────────────────────────────────

def server(input, output, session):

    @reactive.event(input.regenerate, ignore_none=False)
    def get_data():
        seed = random.randint(0, 9999)
        generator = DataGenerator(seed=seed)
        return generator.generate(
            n_points=input.n_points(),
            noise=input.noise()
        )

    @output
    @render.ui
    def chart():
        data = get_data()
        builder = ChartBuilder(data)
        return ui.HTML(builder.render_html())

    @output
    @render.text
    def summary():
        data = get_data()
        stats = DataSummary(data)
        return stats.to_text()


app = App(app_ui, server)