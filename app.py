import sys
import traceback
import yfinance as yf
import pandas as pd
from datetime import datetime, date, timedelta

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QDoubleSpinBox, QDateEdit, QPushButton, 
    QMessageBox, QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDate
from PyQt6.QtGui import QFont, QColor

import matplotlib
matplotlib.use('qtagg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# --- Theme Constants (UI UX Pro Max: Premium Dark Mode OLED) ---
BG_COLOR = "#020617"
CARD_BG = "#0F172A"
PRIMARY_COLOR = "#3B82F6"
SECONDARY_COLOR = "#1D4ED8"
ACCENT_COLOR = "#22C55E"
TEXT_COLOR = "#F8FAFC"
MUTED_TEXT = "#94A3B8"
BORDER_COLOR = "#334155"

STYLESHEET = f"""
QMainWindow, QWidget#MainContent {{
    background-color: {BG_COLOR};
}}

QFrame#Card {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: 8px;
}}

QLabel {{
    color: {TEXT_COLOR};
    font-family: "Segoe UI", "Fira Sans", sans-serif;
}}

QLabel#HeaderTitle {{
    font-size: 24px;
    font-weight: bold;
    color: {PRIMARY_COLOR};
    padding-bottom: 5px;
}}

QLabel#HeaderSubtitle {{
    font-size: 13px;
    color: {MUTED_TEXT};
}}

QLabel#CardTitle {{
    font-size: 16px;
    font-weight: 600;
    color: {PRIMARY_COLOR};
    padding-bottom: 10px;
    border-bottom: 1px solid {BORDER_COLOR};
    margin-bottom: 10px;
}}

QLabel#InputLabel {{
    font-size: 13px;
    font-weight: 500;
}}

QLabel#KpiValue {{
    font-size: 16px;
    font-weight: bold;
    font-family: "Consolas", "Fira Code", monospace;
    color: {TEXT_COLOR};
}}

QLabel#KpiLabel {{
    font-size: 12px;
    color: {MUTED_TEXT};
}}

QLineEdit, QDoubleSpinBox, QDateEdit {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    padding: 6px;
    color: {TEXT_COLOR};
    font-size: 13px;
}}

QLineEdit:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
    border: 2px solid {SECONDARY_COLOR};
}}

QPushButton#RunButton {{
    background-color: {PRIMARY_COLOR};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px;
    font-size: 14px;
    font-weight: bold;
}}

QPushButton#RunButton:hover {{
    background-color: {SECONDARY_COLOR};
}}

QPushButton#RunButton:disabled {{
    background-color: {MUTED_TEXT};
}}
"""

class AnalyzerWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, ticker, capital, tax_rate, start_date, end_date):
        super().__init__()
        self.ticker = ticker
        self.capital = capital
        self.tax_rate = tax_rate
        self.start_date = start_date
        self.end_date = end_date

    def run(self):
        try:
            ticker = self.ticker.strip().upper()
            if not ticker:
                self.error.emit("Please enter a valid ticker.")
                return

            t = yf.Ticker(ticker)
            hist = t.history(start=self.start_date, end=self.end_date)
            
            if hist.empty:
                self.error.emit(f"No data found for ticker {ticker} in the selected date range.")
                return

            divs = t.dividends

            if hist.index.tz is not None:
                hist.index = hist.index.tz_localize(None)

            if not divs.empty:
                if divs.index.tz is not None:
                    divs.index = divs.index.tz_localize(None)
                sd = pd.to_datetime(self.start_date)
                ed = pd.to_datetime(self.end_date)
                divs = divs[(divs.index >= sd) & (divs.index <= ed)]

            df = pd.DataFrame({'close': hist['Close']})
            div_series = pd.Series(dtype=float)
            if not divs.empty:
                divs.index = divs.index.normalize()
                div_series = divs

            df.index = df.index.normalize()
            df = df.groupby(df.index).last()
            
            if not div_series.empty:
                div_series = div_series.groupby(div_series.index).sum()

            df['dividend'] = div_series
            df['dividend'] = df['dividend'].fillna(0.0)
            df = df.sort_index()

            drip_shares = self.capital / df['close'].iloc[0]
            drip_value_history = []
            drip_dividends_total = 0.0
            drip_tax_total = 0.0

            nodrip_shares = self.capital / df['close'].iloc[0]
            nodrip_cash = 0.0
            nodrip_value_history = []
            nodrip_dividends_total = 0.0
            nodrip_tax_total = 0.0

            dates = []

            for dt, row in df.iterrows():
                price = row['close']
                div_per_share = row['dividend']

                if div_per_share > 0:
                    gross_div_drip = drip_shares * div_per_share
                    tax_drip = gross_div_drip * self.tax_rate
                    net_div_drip = gross_div_drip - tax_drip
                    drip_dividends_total += gross_div_drip
                    drip_tax_total += tax_drip
                    drip_shares += net_div_drip / price

                    gross_div_nodrip = nodrip_shares * div_per_share
                    tax_nodrip = gross_div_nodrip * self.tax_rate
                    net_div_nodrip = gross_div_nodrip - tax_nodrip
                    nodrip_dividends_total += gross_div_nodrip
                    nodrip_tax_total += tax_nodrip
                    nodrip_cash += net_div_nodrip

                drip_value = drip_shares * price
                drip_value_history.append(drip_value)

                nodrip_value = nodrip_shares * price + nodrip_cash
                nodrip_value_history.append(nodrip_value)

                dates.append(dt)

            years = (df.index[-1] - df.index[0]).days / 365.25
            if years <= 0: years = 1

            final_drip_value = drip_value_history[-1]
            drip_cagr = ((final_drip_value / self.capital) ** (1 / years)) - 1
            drip_avg_yield = (drip_dividends_total / years) / self.capital

            final_nodrip_value = nodrip_value_history[-1]
            nodrip_cagr = ((final_nodrip_value / self.capital) ** (1 / years)) - 1
            nodrip_avg_yield = (nodrip_dividends_total / years) / self.capital

            result = {
                "ticker": ticker,
                "dates": dates,
                "dripHistory": drip_value_history,
                "nodripHistory": nodrip_value_history,
                "drip_cagr": drip_cagr,
                "nodrip_cagr": nodrip_cagr,
                "drip_final": final_drip_value,
                "nodrip_final": final_nodrip_value,
                "drip_divs": drip_dividends_total,
                "nodrip_divs": nodrip_dividends_total,
                "drip_tax": drip_tax_total,
                "nodrip_tax": nodrip_tax_total,
                "years": years
            }
            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e) + "\n" + traceback.format_exc())

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor=CARD_BG)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(CARD_BG)
        self.ax.tick_params(colors=MUTED_TEXT)
        self.ax.spines['bottom'].set_color(BORDER_COLOR)
        self.ax.spines['top'].set_color(BORDER_COLOR)
        self.ax.spines['right'].set_color(BORDER_COLOR)
        self.ax.spines['left'].set_color(BORDER_COLOR)
        super().__init__(self.fig)
        self.setParent(parent)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ETF Dividend Analyzer - Pro Max")
        self.resize(1100, 750)
        self.setStyleSheet(STYLESHEET)
        
        main_widget = QWidget()
        main_widget.setObjectName("MainContent")
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # --- HEADER ---
        header_layout = QVBoxLayout()
        header_layout.setSpacing(0)
        title = QLabel("ETF Dividend Analyzer")
        title.setObjectName("HeaderTitle")
        subtitle = QLabel("Financial Analytics Dashboard • DRIP Performance Comparison")
        subtitle.setObjectName("HeaderSubtitle")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)
        
        # --- BODY ---
        body_layout = QHBoxLayout()
        body_layout.setSpacing(20)
        
        # Left Panel
        left_panel = QWidget()
        left_panel.setFixedWidth(340)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(20)
        
        # 1. Inputs Card
        input_card = QFrame()
        input_card.setObjectName("Card")
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(20, 20, 20, 20)
        input_layout.setSpacing(15)
        
        card_title = QLabel("Simulation Parameters")
        card_title.setObjectName("CardTitle")
        input_layout.addWidget(card_title)
        
        self.ticker_input = self.create_input("Ticker Symbol:", QLineEdit("SPY"), input_layout)
        self.capital_input = self.create_input("Initial Capital ($):", QDoubleSpinBox(), input_layout)
        self.capital_input.setRange(100, 100000000)
        self.capital_input.setValue(10000)
        
        self.tax_input = self.create_input("Dividend Tax Rate (%):", QDoubleSpinBox(), input_layout)
        self.tax_input.setRange(0, 100)
        self.tax_input.setValue(30.0)
        
        self.start_date_input = self.create_input("Start Date:", QDateEdit(), input_layout)
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate().addYears(-5))
        
        self.end_date_input = self.create_input("End Date:", QDateEdit(), input_layout)
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        
        self.run_btn = QPushButton("Run Analysis")
        self.run_btn.setObjectName("RunButton")
        self.run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_btn.clicked.connect(self.run_analysis)
        input_layout.addWidget(self.run_btn)
        
        left_layout.addWidget(input_card)
        
        # 2. Metrics Card
        self.metrics_card = QFrame()
        self.metrics_card.setObjectName("Card")
        metrics_layout = QVBoxLayout(self.metrics_card)
        metrics_layout.setContentsMargins(20, 20, 20, 20)
        
        metrics_title = QLabel("Performance KPIs")
        metrics_title.setObjectName("CardTitle")
        metrics_layout.addWidget(metrics_title)
        
        self.kpi_grid = QGridLayout()
        self.kpi_grid.setVerticalSpacing(15)
        self.kpi_grid.setHorizontalSpacing(10)
        metrics_layout.addLayout(self.kpi_grid)
        
        # Initialize empty KPIs
        self.kpi_labels = {}
        self.setup_kpis()
        
        left_layout.addWidget(self.metrics_card)
        left_layout.addStretch() # Push everything up
        
        # Right Panel (Chart)
        right_panel = QFrame()
        right_panel.setObjectName("Card")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        
        chart_title = QLabel("Value Growth Projection")
        chart_title.setObjectName("CardTitle")
        right_layout.addWidget(chart_title)
        
        self.canvas = MplCanvas(self, width=6, height=5, dpi=100)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet("background: transparent; border: none;")
        
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)
        
        body_layout.addWidget(left_panel)
        body_layout.addWidget(right_panel, stretch=1)
        
        main_layout.addLayout(body_layout)
        self.worker = None

    def create_input(self, label_text, widget, parent_layout):
        layout = QVBoxLayout()
        layout.setSpacing(5)
        lbl = QLabel(label_text)
        lbl.setObjectName("InputLabel")
        layout.addWidget(lbl)
        layout.addWidget(widget)
        parent_layout.addLayout(layout)
        return widget

    def setup_kpis(self):
        # DRIP Column (0, 1), Non-DRIP Column (2, 3)
        headers = ["DRIP Strategy", "Non-DRIP (Cash)"]
        for col, title in enumerate(headers):
            lbl = QLabel(title)
            lbl.setStyleSheet(f"font-weight: bold; color: {PRIMARY_COLOR if col==0 else ACCENT_COLOR}; font-size: 13px;")
            self.kpi_grid.addWidget(lbl, 0, col, 1, 1)

        kpi_names = ["Final Value", "CAGR", "Gross Divs", "Tax Paid"]
        self.kpi_keys = ["final", "cagr", "divs", "tax"]
        
        for row, name in enumerate(kpi_names, start=1):
            # DRIP
            v_drip = QLabel("-")
            v_drip.setObjectName("KpiValue")
            l_drip = QLabel(name)
            l_drip.setObjectName("KpiLabel")
            
            # Non-DRIP
            v_nodrip = QLabel("-")
            v_nodrip.setObjectName("KpiValue")
            l_nodrip = QLabel(name)
            l_nodrip.setObjectName("KpiLabel")
            
            # Add to grid
            vbox1 = QVBoxLayout()
            vbox1.setSpacing(2)
            vbox1.addWidget(v_drip)
            vbox1.addWidget(l_drip)
            self.kpi_grid.addLayout(vbox1, row, 0)
            
            vbox2 = QVBoxLayout()
            vbox2.setSpacing(2)
            vbox2.addWidget(v_nodrip)
            vbox2.addWidget(l_nodrip)
            self.kpi_grid.addLayout(vbox2, row, 1)
            
            self.kpi_labels[f"drip_{self.kpi_keys[row-1]}"] = v_drip
            self.kpi_labels[f"nodrip_{self.kpi_keys[row-1]}"] = v_nodrip

    def run_analysis(self):
        ticker = self.ticker_input.text()
        capital = self.capital_input.value()
        tax_rate = self.tax_input.value() / 100.0
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.end_date_input.date().toString("yyyy-MM-dd")
        
        self.run_btn.setEnabled(False)
        self.run_btn.setText("Computing...")
        
        # Reset KPIs
        for k, v in self.kpi_labels.items():
            v.setText("...")
            
        self.worker = AnalyzerWorker(ticker, capital, tax_rate, start_date, end_date)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()

    def on_analysis_finished(self, res):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("Run Analysis")
        
        # Update Plot
        self.canvas.ax.clear()
        self.canvas.ax.plot(res["dates"], res["dripHistory"], label="DRIP (Reinvested)", color=PRIMARY_COLOR, linewidth=2.5)
        self.canvas.ax.plot(res["dates"], res["nodripHistory"], label="Non-DRIP (Cash Out)", color=ACCENT_COLOR, linewidth=2)
        
        self.canvas.ax.set_ylabel("Portfolio Value ($)", color=TEXT_COLOR)
        self.canvas.ax.legend(frameon=True, facecolor=CARD_BG, edgecolor=BORDER_COLOR, labelcolor=TEXT_COLOR)
        self.canvas.ax.grid(True, linestyle='--', color=BORDER_COLOR, alpha=0.8)
        self.canvas.fig.tight_layout()
        self.canvas.draw()
        
        # Update Metrics
        self.kpi_labels["drip_final"].setText(f"${res['drip_final']:,.0f}")
        self.kpi_labels["drip_cagr"].setText(f"{res['drip_cagr']*100:.2f}%")
        self.kpi_labels["drip_divs"].setText(f"${res['drip_divs']:,.0f}")
        self.kpi_labels["drip_tax"].setText(f"${res['drip_tax']:,.0f}")
        
        self.kpi_labels["nodrip_final"].setText(f"${res['nodrip_final']:,.0f}")
        self.kpi_labels["nodrip_cagr"].setText(f"{res['nodrip_cagr']*100:.2f}%")
        self.kpi_labels["nodrip_divs"].setText(f"${res['nodrip_divs']:,.0f}")
        self.kpi_labels["nodrip_tax"].setText(f"${res['nodrip_tax']:,.0f}")

    def on_analysis_error(self, err_msg):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("Run Analysis")
        for k, v in self.kpi_labels.items():
            v.setText("-")
        QMessageBox.critical(self, "Error", f"Failed to analyze:\n{err_msg}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
