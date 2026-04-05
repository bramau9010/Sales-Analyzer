import dash
from dash import html, dcc, Input, Output
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# ── Corporate Color Palette ───────────────────────────────────────────────────
BG          = "#464B57"   # Cinza-azulado escuro  (fundo principal)
GOLD        = "#DECF99"   # Amarelo-dourado        (destaque)
WHITE       = "#FFFFFF"   # Branco                 (texto claro)
OFFWHITE    = "#EDECE5"   # Bege / Off-white       (acento claro)
DARK        = "#333333"   # Cinza escuro           (texto escuro)
RED         = "#C00000"   # Vermelho               (alertas / risco)
GREEN       = "#00B050"   # Verde                  (sucesso)
CARD_BG     = "#3D4250"   # Fundo dos cards
SIDEBAR_BG  = "#2E3240"   # Fundo da sidebar

CORP_SEQ = [GOLD, "#8FB4CC", "#5B9BD5", GREEN, OFFWHITE, "#E8A838", "#A8C5DA"]

# ── Data Loading & Enrichment ─────────────────────────────────────────────────
df_raw = pd.read_csv("supermarket_sales.csv")
df_raw["Date"]         = pd.to_datetime(df_raw["Date"])
df_raw["DayOfWeek"]    = df_raw["Date"].dt.day_name()
df_raw["Hour"]         = pd.to_datetime(df_raw["Time"], format="%H:%M").dt.hour

CITIES    = sorted(df_raw["City"].unique())
CUSTOMERS = sorted(df_raw["Customer type"].unique())

# ── App Init ──────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    title="Sales Analyzer"
)
server = app.server

# ── Reusable Plot Theme ───────────────────────────────────────────────────────
def plot_layout(height=260, show_legend=True):
    return dict(
        plot_bgcolor  = CARD_BG,
        paper_bgcolor = "rgba(0,0,0,0)",
        font          = dict(color=OFFWHITE, family="Arial, sans-serif", size=11),
        legend        = dict(
            bgcolor   = "rgba(0,0,0,0)",
            font      = dict(color=OFFWHITE, size=10),
            orientation = "h",
            yanchor   = "bottom", y=1.02,
            xanchor   = "right",  x=1,
        ) if show_legend else dict(visible=False),
        margin        = dict(l=8, r=8, t=8, b=8),
        height        = height,
        xaxis         = dict(gridcolor="#52576A", zerolinecolor="#52576A", tickfont=dict(size=10)),
        yaxis         = dict(gridcolor="#52576A", zerolinecolor="#52576A", tickfont=dict(size=10)),
        colorway      = CORP_SEQ,
        hoverlabel    = dict(bgcolor=SIDEBAR_BG, font_color=WHITE, bordercolor=GOLD),
    )

# ── KPI Card Component ────────────────────────────────────────────────────────
def kpi_card(label, value, subtitle="", value_color=WHITE):
    return dbc.Card(
        dbc.CardBody([
            html.P(label, style={
                "color": GOLD, "fontSize": "10px", "margin": "0",
                "textTransform": "uppercase", "letterSpacing": "1.5px"
            }),
            html.H3(value, style={
                "color": value_color, "margin": "4px 0 2px",
                "fontWeight": "bold", "fontSize": "24px"
            }),
            html.P(subtitle, style={"color": OFFWHITE, "fontSize": "11px", "margin": "0"}),
        ]),
        style={
            "backgroundColor": CARD_BG,
            "border": f"1px solid {GOLD}44",
            "borderRadius": "6px",
            "height": "100%",
        }
    )

# ── Section Header ────────────────────────────────────────────────────────────
def section_header(title, subtitle=""):
    return html.Div([
        html.P(title, style={
            "color": GOLD, "fontSize": "10px", "margin": "0",
            "textTransform": "uppercase", "letterSpacing": "1.5px"
        }),
        html.P(subtitle, style={
            "color": OFFWHITE, "fontSize": "11px", "margin": "0 0 6px"
        }) if subtitle else None,
    ])

# ── Chart Card ────────────────────────────────────────────────────────────────
def chart_card(title, subtitle, graph_id):
    return dbc.Card(
        dbc.CardBody([
            section_header(title, subtitle),
            dcc.Graph(id=graph_id, config={"displayModeBar": False}),
        ]),
        style={
            "backgroundColor": CARD_BG,
            "border": f"1px solid {GOLD}22",
            "borderRadius": "6px",
        }
    )

# ── Layout ────────────────────────────────────────────────────────────────────
app.layout = dbc.Container([

    # ── Header bar ────────────────────────────────────────────────────────────
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Span("SALES", style={"color": GOLD, "fontWeight": "900", "letterSpacing": "4px", "fontSize": "22px"}),
                html.Span(" ANALYZER", style={"color": WHITE, "fontWeight": "300", "letterSpacing": "4px", "fontSize": "22px"}),
            ]),
            html.P(
                "Supermarket Performance · Business Intelligence Dashboard",
                style={"color": OFFWHITE, "margin": "0", "fontSize": "11px", "letterSpacing": "1px"}
            ),
        ], width=7),
        dbc.Col([
            html.Div([
                html.P("DATA PERIOD", style={"color": GOLD, "fontSize": "10px", "margin": "0", "letterSpacing": "1px"}),
                html.P(
                    f"{df_raw['Date'].min().strftime('%b %d')}  –  {df_raw['Date'].max().strftime('%b %d, %Y')}",
                    style={"color": WHITE, "margin": "0", "fontWeight": "bold", "fontSize": "13px"}
                ),
                html.P(
                    f"{len(df_raw):,} transactions · {df_raw['City'].nunique()} branches",
                    style={"color": OFFWHITE, "margin": "0", "fontSize": "11px"}
                ),
            ], style={"textAlign": "right"})
        ], width=5),
    ], align="center", style={
        "backgroundColor": SIDEBAR_BG,
        "padding": "14px 24px",
        "borderBottom": f"2px solid {GOLD}",
        "marginBottom": "0",
    }),

    # ── Body ──────────────────────────────────────────────────────────────────
    dbc.Row([

        # ── Sidebar ───────────────────────────────────────────────────────────
        dbc.Col([
            html.Div([
                html.P("FILTERS", style={
                    "color": GOLD, "fontSize": "10px",
                    "letterSpacing": "2px", "marginBottom": "16px", "marginTop": "4px"
                }),

                html.Label("Branch / City", style={"color": OFFWHITE, "fontSize": "11px", "marginBottom": "6px", "display": "block"}),
                dcc.Checklist(
                    id="filter_city",
                    options=[{"label": f"  {c}", "value": c} for c in CITIES],
                    value=CITIES,
                    inputStyle={"marginRight": "8px", "accentColor": GOLD},
                    labelStyle={"display": "block", "marginBottom": "6px", "color": WHITE, "fontSize": "13px"},
                ),

                html.Hr(style={"borderColor": f"{GOLD}33", "margin": "14px 0"}),

                html.Label("Metric", style={"color": OFFWHITE, "fontSize": "11px", "marginBottom": "6px", "display": "block"}),
                dcc.RadioItems(
                    id="filter_metric",
                    options=[
                        {"label": "  Gross Income", "value": "gross income"},
                        {"label": "  Total Sales",  "value": "Total"},
                        {"label": "  Rating",       "value": "Rating"},
                    ],
                    value="gross income",
                    inputStyle={"marginRight": "8px", "accentColor": GOLD},
                    labelStyle={"display": "block", "marginBottom": "8px", "color": WHITE, "fontSize": "13px"},
                ),

                html.Hr(style={"borderColor": f"{GOLD}33", "margin": "14px 0"}),

                html.Label("Customer Type", style={"color": OFFWHITE, "fontSize": "11px", "marginBottom": "6px", "display": "block"}),
                dcc.Checklist(
                    id="filter_customer",
                    options=[{"label": f"  {c}", "value": c} for c in CUSTOMERS],
                    value=CUSTOMERS,
                    inputStyle={"marginRight": "8px", "accentColor": GOLD},
                    labelStyle={"display": "block", "marginBottom": "6px", "color": WHITE, "fontSize": "13px"},
                ),

                html.Hr(style={"borderColor": f"{GOLD}33", "margin": "14px 0"}),

                html.Label("Gender", style={"color": OFFWHITE, "fontSize": "11px", "marginBottom": "6px", "display": "block"}),
                dcc.Checklist(
                    id="filter_gender",
                    options=[{"label": f"  {g}", "value": g} for g in sorted(df_raw["Gender"].unique())],
                    value=list(df_raw["Gender"].unique()),
                    inputStyle={"marginRight": "8px", "accentColor": GOLD},
                    labelStyle={"display": "block", "marginBottom": "6px", "color": WHITE, "fontSize": "13px"},
                ),

            ], style={"padding": "16px 14px"})
        ], width=2, style={"backgroundColor": SIDEBAR_BG, "minHeight": "calc(100vh - 68px)", "padding": "0"}),

        # ── Main Content ──────────────────────────────────────────────────────
        dbc.Col([
            html.Div([

                # Row 1 — KPIs
                dbc.Row([
                    dbc.Col(html.Div(id="kpi_income"),      width=3),
                    dbc.Col(html.Div(id="kpi_transactions"), width=3),
                    dbc.Col(html.Div(id="kpi_rating"),       width=3),
                    dbc.Col(html.Div(id="kpi_top_product"),  width=3),
                ], className="g-2", style={"marginBottom": "12px"}),

                # Row 2 — Revenue Trend (full width)
                dbc.Row([
                    dbc.Col(
                        chart_card(
                            "REVENUE TREND",
                            "Daily performance with 7-day moving average · Bar = daily · Line = trend",
                            "chart_trend"
                        ), width=12
                    ),
                ], style={"marginBottom": "12px"}),

                # Row 3 — Product Performance + City Breakdown
                dbc.Row([
                    dbc.Col(
                        chart_card(
                            "PRODUCT LINE PERFORMANCE",
                            "Which categories drive the most revenue?",
                            "chart_product"
                        ), width=6
                    ),
                    dbc.Col(
                        chart_card(
                            "BRANCH COMPARISON",
                            "Stacked contribution by product line per city",
                            "chart_city"
                        ), width=6
                    ),
                ], className="g-2", style={"marginBottom": "12px"}),

                # Row 4 — Payment · Gender · Rating
                dbc.Row([
                    dbc.Col(
                        chart_card(
                            "PAYMENT METHODS",
                            "Transaction share by payment type",
                            "chart_payment"
                        ), width=4
                    ),
                    dbc.Col(
                        chart_card(
                            "GENDER BY CITY",
                            "Revenue split across branches",
                            "chart_gender"
                        ), width=4
                    ),
                    dbc.Col(
                        chart_card(
                            "CUSTOMER SATISFACTION",
                            "Rating distribution with average benchmark",
                            "chart_rating"
                        ), width=4
                    ),
                ], className="g-2", style={"marginBottom": "12px"}),

                # Row 5 — Sales by hour + Day of week
                dbc.Row([
                    dbc.Col(
                        chart_card(
                            "PEAK HOURS",
                            "When do customers shop the most?",
                            "chart_hourly"
                        ), width=6
                    ),
                    dbc.Col(
                        chart_card(
                            "DAY OF WEEK PATTERN",
                            "Revenue distribution across the week",
                            "chart_dow"
                        ), width=6
                    ),
                ], className="g-2"),

            ], style={"padding": "12px 16px"})
        ], width=10),

    ], style={"margin": "0"}, className="g-0"),

    # Footer
    dbc.Row([
        dbc.Col(
            html.P(
                "Sales Analyzer · Powered by Dash & Plotly · Data: Supermarket Sales Dataset",
                style={"color": f"{OFFWHITE}88", "fontSize": "10px", "margin": "0", "textAlign": "center", "padding": "10px"}
            )
        )
    ], style={"backgroundColor": SIDEBAR_BG, "borderTop": f"1px solid {GOLD}33"}),

], fluid=True, style={"backgroundColor": BG, "minHeight": "100vh", "padding": "0"})


# ── Callback ──────────────────────────────────────────────────────────────────
@app.callback(
    [
        Output("kpi_income",       "children"),
        Output("kpi_transactions", "children"),
        Output("kpi_rating",       "children"),
        Output("kpi_top_product",  "children"),
        Output("chart_trend",      "figure"),
        Output("chart_product",    "figure"),
        Output("chart_city",       "figure"),
        Output("chart_payment",    "figure"),
        Output("chart_gender",     "figure"),
        Output("chart_rating",     "figure"),
        Output("chart_hourly",     "figure"),
        Output("chart_dow",        "figure"),
    ],
    [
        Input("filter_city",     "value"),
        Input("filter_metric",   "value"),
        Input("filter_customer", "value"),
        Input("filter_gender",   "value"),
    ]
)
def update_dashboard(cities, metric, customers, genders):
    df = df_raw.copy()
    if cities:    df = df[df["City"].isin(cities)]
    if customers: df = df[df["Customer type"].isin(customers)]
    if genders:   df = df[df["Gender"].isin(genders)]

    empty_fig = go.Figure().update_layout(**plot_layout())
    no_data   = html.P("No data", style={"color": RED, "padding": "8px"})

    if df.empty:
        return (no_data,)*4 + (empty_fig,)*8

    op = np.sum if metric != "Rating" else np.mean

    # ── KPIs ─────────────────────────────────────────────────────────────────
    total_income = df["gross income"].sum()
    n_trans      = len(df)
    avg_rating   = df["Rating"].mean()
    top_product  = df.groupby("Product line")["gross income"].sum().idxmax()

    all_income   = df_raw["gross income"].sum()
    pct_income   = (total_income / all_income * 100) if all_income else 0

    rating_color = GREEN if avg_rating >= 7 else (GOLD if avg_rating >= 5 else RED)

    kpi1 = kpi_card("Gross Income",   f"${total_income:,.0f}", f"{pct_income:.0f}% of total period", GOLD)
    kpi2 = kpi_card("Transactions",   f"{n_trans:,}",          f"avg ${df['Total'].mean():,.1f} / sale")
    kpi3 = kpi_card("Avg Rating",     f"{avg_rating:.2f}",     "out of 10.0", rating_color)
    kpi4 = kpi_card("Top Category",   top_product,             "by gross income", OFFWHITE)

    # ── Trend Chart ──────────────────────────────────────────────────────────
    df_trend      = df.groupby("Date")[metric].apply(op).reset_index()
    df_trend["MA7"] = df_trend[metric].rolling(7, min_periods=1).mean()

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Bar(
        x=df_trend["Date"], y=df_trend[metric],
        name="Daily", marker_color="rgba(222,207,153,0.4)", hovertemplate="%{x|%b %d}<br>%{y:,.1f}<extra></extra>",
    ))
    fig_trend.add_trace(go.Scatter(
        x=df_trend["Date"], y=df_trend["MA7"],
        name="7-day avg", line=dict(color=GOLD, width=2.5),
        hovertemplate="%{x|%b %d}<br>MA7: %{y:,.1f}<extra></extra>",
    ))
    fig_trend.update_layout(**plot_layout(height=230))

    # ── Product Performance ───────────────────────────────────────────────────
    df_prod = df.groupby("Product line")[metric].apply(op).sort_values().reset_index()
    label_fmt = "${:,.0f}" if metric != "Rating" else "{:.2f}"
    fig_product = go.Figure(go.Bar(
        x=df_prod[metric],
        y=df_prod["Product line"],
        orientation="h",
        marker=dict(
            color=df_prod[metric],
            colorscale=[[0, "#3D4250"], [0.5, "#8E7D4A"], [1, GOLD]],
            showscale=False,
        ),
        text=[label_fmt.format(v) for v in df_prod[metric]],
        textposition="outside",
        textfont=dict(color=OFFWHITE, size=10),
        hovertemplate="%{y}<br>" + ("%{x:,.1f}" if metric != "Rating" else "%{x:.2f}") + "<extra></extra>",
    ))
    fig_product.update_layout(**plot_layout(height=280, show_legend=False))
    fig_product.update_xaxes(showgrid=True)

    # ── City Stacked ─────────────────────────────────────────────────────────
    df_city = df.groupby(["City", "Product line"])[metric].apply(op).reset_index()
    fig_city = px.bar(
        df_city, x="City", y=metric, color="Product line",
        barmode="stack", color_discrete_sequence=CORP_SEQ,
        text_auto=".2s",
    )
    fig_city.update_traces(textfont_size=9, textposition="inside")
    fig_city.update_layout(**plot_layout(height=280))

    # ── Payment Donut ─────────────────────────────────────────────────────────
    df_pay = df.groupby("Payment")[metric].apply(op).reset_index()
    fig_payment = go.Figure(go.Pie(
        labels=df_pay["Payment"], values=df_pay[metric],
        hole=0.58,
        marker=dict(colors=[GOLD, "#8FB4CC", GREEN], line=dict(color=BG, width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color=WHITE),
        hovertemplate="%{label}<br>%{value:,.1f}<br>%{percent}<extra></extra>",
    ))
    fig_payment.add_annotation(
        text=f"${df_pay[metric].sum():,.0f}" if metric != "Rating" else f"{df_pay[metric].mean():.2f}",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=14, color=GOLD, family="Arial"),
    )
    fig_payment.update_layout(**plot_layout(height=260, show_legend=False))

    # ── Gender Grouped ────────────────────────────────────────────────────────
    df_gen = df.groupby(["City", "Gender"])[metric].apply(op).reset_index()
    fig_gender = px.bar(
        df_gen, x="City", y=metric, color="Gender",
        barmode="group", color_discrete_map={"Female": GOLD, "Male": "#8FB4CC"},
        text_auto=".2s",
    )
    fig_gender.update_traces(textfont_size=9, textposition="outside")
    fig_gender.update_layout(**plot_layout(height=260))

    # ── Rating Histogram ──────────────────────────────────────────────────────
    avg_r = df["Rating"].mean()
    fig_rating = px.histogram(
        df, x="Rating", nbins=18,
        color_discrete_sequence=[GOLD],
        opacity=0.85,
    )
    fig_rating.add_vline(
        x=avg_r, line_dash="dash", line_color=GREEN, line_width=2,
        annotation_text=f" Avg {avg_r:.1f}",
        annotation_font=dict(color=GREEN, size=11),
        annotation_position="top right",
    )
    fig_rating.update_layout(**plot_layout(height=260, show_legend=False))

    # ── Hourly Pattern ────────────────────────────────────────────────────────
    df_hour = df.groupby("Hour")[metric].apply(op).reset_index()
    peak_hour = df_hour.loc[df_hour[metric].idxmax(), "Hour"]
    fig_hourly = go.Figure(go.Scatter(
        x=df_hour["Hour"], y=df_hour[metric],
        mode="lines+markers",
        line=dict(color=GOLD, width=2.5),
        marker=dict(
            color=[RED if h == peak_hour else GOLD for h in df_hour["Hour"]],
            size=[10 if h == peak_hour else 5 for h in df_hour["Hour"]],
        ),
        fill="tozeroy", fillcolor="rgba(222,207,153,0.1)",
        hovertemplate="Hour %{x}:00<br>%{y:,.1f}<extra></extra>",
    ))
    fig_hourly.add_annotation(
        x=peak_hour, y=df_hour[df_hour["Hour"] == peak_hour][metric].values[0],
        text=f"Peak: {peak_hour}:00h", showarrow=True, arrowhead=2,
        arrowcolor=RED, font=dict(color=RED, size=10), ax=20, ay=-30,
    )
    fig_hourly.update_xaxes(tickvals=list(range(6, 22)), ticktext=[f"{h}h" for h in range(6, 22)])
    fig_hourly.update_layout(**plot_layout(height=240, show_legend=False))

    # ── Day of Week ───────────────────────────────────────────────────────────
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df_dow    = df.groupby("DayOfWeek")[metric].apply(op).reindex(dow_order).reset_index()
    df_dow.columns = ["Day", metric]
    best_day  = df_dow.loc[df_dow[metric].idxmax(), "Day"]

    fig_dow = go.Figure(go.Bar(
        x=df_dow["Day"], y=df_dow[metric],
        marker_color=[GOLD if d == best_day else "rgba(222,207,153,0.33)" for d in df_dow["Day"]],
        text=[f"${v:,.0f}" if metric != "Rating" else f"{v:.1f}" for v in df_dow[metric]],
        textposition="outside", textfont=dict(size=10, color=OFFWHITE),
        hovertemplate="%{x}<br>%{y:,.1f}<extra></extra>",
    ))
    fig_dow.add_annotation(
        x=best_day, y=df_dow[df_dow["Day"] == best_day][metric].values[0],
        text="Best day", showarrow=False, yshift=18,
        font=dict(color=GOLD, size=10),
    )
    fig_dow.update_layout(**plot_layout(height=240, show_legend=False))

    return (
        kpi1, kpi2, kpi3, kpi4,
        fig_trend, fig_product, fig_city,
        fig_payment, fig_gender, fig_rating,
        fig_hourly, fig_dow,
    )


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run_server(debug=True, port=8080, host="0.0.0.0")
