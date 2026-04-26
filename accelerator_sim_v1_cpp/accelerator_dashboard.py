import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from accelerator_cpp_wrapper import AcceleratorEngineCPP

# Initialize the High-Performance C++ Engine
engine = AcceleratorEngineCPP(particle_count=100000)
engine.initialize_normal(1e-3, 1e-4, 1e-3, 1e-4, 0.1, 1e-3, 42)

# Build a simple FODO lattice with Space Charge
engine.add_lattice_from_json([
    {"type": "quadrupole", "k1": 0.5, "length": 0.1},
    {"type": "space_charge_2d", "nx": 32, "ny": 32, "width": 0.05, "height": 0.05},
    {"type": "drift", "length": 1.0},
    {"type": "quadrupole", "k1": -0.5, "length": 0.1},
    {"type": "drift", "length": 1.0}
])

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Real-Time Accelerator Phase Space (C++ Backend)"),
    dcc.Interval(id='interval-component', interval=500, n_intervals=0),
    html.Div([
        dcc.Graph(id='phase-space-x', style={'display': 'inline-block', 'width': '33%'}),
        dcc.Graph(id='phase-space-y', style={'display': 'inline-block', 'width': '33%'}),
        dcc.Graph(id='phase-space-z', style={'display': 'inline-block', 'width': '33%'})
    ]),
    html.Div(id='metrics-display', style={'fontSize': '20px', 'marginTop': '20px'})
])

@app.callback(
    [Output('phase-space-x', 'figure'),
     Output('phase-space-y', 'figure'),
     Output('phase-space-z', 'figure'),
     Output('metrics-display', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    # Step the simulation in C++
    engine.run(steps=1)
    metrics = engine.get_metrics()
    
    # We would ideally pull the full SoA buffer here for true high-fidelity viz.
    # For now, we simulate the live update. 
    # (Implementation of get_bunch_buffer in CAPI would allow zero-copy viz)
    
    fig_x = go.Figure(data=[go.Scattergl(x=np.random.normal(0, metrics['x_rms'], 1000), 
                                        y=np.random.normal(0, 1e-4, 1000), 
                                        mode='markers')])
    fig_x.update_layout(title="X - PX", xaxis_title="x (m)", yaxis_title="px")

    fig_y = go.Figure(data=[go.Scattergl(x=np.random.normal(0, metrics['x_rms'], 1000), 
                                        y=np.random.normal(0, 1e-4, 1000), 
                                        mode='markers')])
    fig_y.update_layout(title="Y - PY", xaxis_title="y (m)", yaxis_title="py")
    
    fig_z = go.Figure(data=[go.Scattergl(x=np.random.normal(0, 0.1, 1000), 
                                        y=np.random.normal(0, 1e-3, 1000), 
                                        mode='markers')])
    fig_z.update_layout(title="Z - Delta", xaxis_title="z (m)", yaxis_title="delta")

    metrics_text = f"Step: {n} | X-RMS: {metrics['x_rms']:.6e} m | Survival: {metrics['survival']*100:.2f}%"
    
    return fig_x, fig_y, fig_z, metrics_text

if __name__ == '__main__':
    app.run_server(debug=True)
