# shiny/app.py
import random
import math
from shiny import App, ui, render, reactive

# ─────────────────────────────────────────
# OOP Layer — Inheritance & Polymorphism
# ─────────────────────────────────────────

class DataGenerator:
    """Base class for all data generators. Defines the interface."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)

    def generate(self, n_points: int, noise: float) -> dict:
        """To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement generate()")

    def name(self) -> str:
        raise NotImplementedError("Subclasses must implement name()")


class LinearDataGenerator(DataGenerator):
    """Generates data following a linear trend with noise."""

    def name(self) -> str:
        return "Linear Trend"

    def generate(self, n_points: int, noise: float) -> dict:
        random.seed(self.seed)
        x = list(range(n_points))
        y = [round(i * 2.5 + random.uniform(-noise, noise), 2) for i in x]
        return {"x": x, "y": y}


class RandomWalkGenerator(DataGenerator):
    """Generates data using a random walk (each step builds on the last)."""

    def name(self) -> str:
        return "Random Walk"

    def generate(self, n_points: int, noise: float) -> dict:
        random.seed(self.seed)
        x = list(range(n_points))
        y = [0.0]
        for _ in range(n_points - 1):
            step = random.uniform(-noise, noise)
            y.append(round(y[-1] + step, 2))
        return {"x": x, "y": y}


class SineWaveGenerator(DataGenerator):
    """Generates a sine wave with noise."""

    def name(self) -> str:
        return "Sine Wave"

    def generate(self, n_points: int, noise: float) -> dict:
        random.seed(self.seed)
        x = list(range(n_points))
        y = [
            round(math.sin(i / n_points * 2 * math.pi) * 50 + random.uniform(-noise, noise), 2)
            for i in x
        ]
        return {"x": x, "y": y}


class ExponentialDataGenerator(DataGenerator):
    """Generates exponentially growing data with noise."""

    def name(self) -> str:
        return "Exponential Growth"

    def generate(self, n_points: int, noise: float) -> dict:
        random.seed(self.seed)
        x = list(range(n_points))
        y = [
            round(math.exp(i / n_points * 3) + random.uniform(-noise, noise), 2)
            for i in x
        ]
        return {"x": x, "y": y}


# Factory — maps UI selection to the right subclass
GENERATORS = {
    "Linear Trend":        LinearDataGenerator,
    "Random Walk":         RandomWalkGenerator,
    "Sine Wave":           SineWaveGenerator,
    "Exponential Growth":  ExponentialDataGenerator,
}


# ─────────────────────────────────────────
# Encapsulation — DataSummary
# ─────────────────────────────────────────

class DataSummary:
    """Encapsulates all statistical logic for a dataset."""

    def __init__(self, data: dict):
        self._data = data
        self._y = data["y"]

    def mean(self) -> float:
        return round(sum(self._y) / len(self._y), 2)

    def maximum(self) -> float:
        return round(max(self._y), 2)

    def minimum(self) -> float:
        return round(min(self._y), 2)

    def range(self) -> float:
        return round(self.maximum() - self.minimum(), 2)

    def to_text(self) -> str:
        return (
            f"Mean: {self.mean()}  |  "
            f"Min: {self.minimum()}  |  "
            f"Max: {self.maximum()}  |  "
            f"Range: {self.range()}"
        )


# ─────────────────────────────────────────
# ChartBuilder — Rendering
# ─────────────────────────────────────────

class ChartBuilder:
    """Responsible for rendering an HTML bar chart from data."""

    # Polymorphism in action — works with output of ANY generator
    def __init__(self, data: dict, color_top: str = "#ff9f43", color_bottom: str = "#e67e22"):
        self.data = data
        self.color_top = color_top
        self.color_bottom = color_bottom

    def render_html(self) -> str:
        y_vals = self.data["y"]
        min_val = min(y_vals)
        # Shift all values so minimum is 0 (handles negatives)
        shifted = [v - min_val for v in y_vals]
        max_val = max(shifted) or 1

        bars = ""
        for x_val, y_val, s_val in zip(self.data["x"], y_vals, shifted):
            height = max(4, int((s_val / max_val) * 200))
            bars += f"""
            <div style="display:inline-block; margin:2px; text-align:center; vertical-align:bottom;">
              <div style="font-size:9px; color:#888; margin-bottom:2px;">{y_val}</div>
              <div style="
                width:28px; height:{height}px;
                background: linear-gradient(180deg, {self.color_top}, {self.color_bottom});
                border-radius:4px 4px 0 0;
              "></div>
              <div style="font-size:10px; color:#555;">{x_val}</div>
            </div>"""

        return f"""
        <div style="
          display:flex; align-items:flex-end;
          padding:20px; background:#f9f9f9;
          border-radius:8px; flex-wrap:wrap; min-height:260px;
        ">{bars}</div>"""


# ─────────────────────────────────────────
# Shiny UI
# ─────────────────────────────────────────

app_ui = ui.page_fluid(
    ui.h2("📊 Interactive Data Explorer"),
    ui.p("Demonstrates OOP in Python: inheritance, encapsulation, and polymorphism."),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select(
                "generator_type",
                "Data Pattern",
                choices=list(GENERATORS.keys()),
            ),
            ui.input_slider("n_points", "Number of Points", 5, 30, 15),
            ui.input_slider("noise", "Noise Level", 0, 50, 10),
            ui.input_action_button("regenerate", "🔄 Regenerate", class_="btn-primary"),
            ui.hr(),
            ui.p("Each pattern is a subclass of DataGenerator.", style="font-size:12px; color:#888;"),
        ),
        ui.output_ui("chart"),
        ui.output_text("summary"),
        ui.output_text("generator_info"),
    ),
)

# ─────────────────────────────────────────
# Shiny Server
# ─────────────────────────────────────────

def server(input, output, session):

    @reactive.event(input.regenerate, input.generator_type, ignore_none=False)
    def get_data():
        seed = random.randint(0, 9999)
        GeneratorClass = GENERATORS[input.generator_type()]
        generator = GeneratorClass(seed=seed)
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

    @output
    @render.text
    def generator_info():
        GeneratorClass = GENERATORS[input.generator_type()]
        generator = GeneratorClass()
        return f"Active generator: {generator.name()} ({GeneratorClass.__name__})"


app = App(app_ui, server)