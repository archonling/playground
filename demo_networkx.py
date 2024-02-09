import networkx as nx
import plotly.graph_objects as go
import random

# List of Greek gods' names
greek_gods = [
    'Zeus', 'Hera', 'Poseidon', 'Demeter', 'Athena', 'Apollo', 'Artemis', 'Ares', 'Aphrodite', 'Hephaestus',
    'Hermes', 'Hestia', 'Dionysus', 'Hades', 'Persephone', 'Hecate', 'Helios', 'Selene', 'Eros', 'Nike'
]

# Define the relationships
relationships = [
    (random.choice(greek_gods), random.choice(greek_gods)),
    (random.choice(greek_gods), random.choice(greek_gods)),
    (random.choice(greek_gods), random.choice(greek_gods)),
    (random.choice(greek_gods), random.choice(greek_gods)),
    (random.choice(greek_gods), random.choice(greek_gods)),
    (random.choice(greek_gods), random.choice(greek_gods)),
    (random.choice(greek_gods), random.choice(greek_gods)),
    (random.choice(greek_gods), random.choice(greek_gods)),
    (random.choice(greek_gods), random.choice(greek_gods)),
    (random.choice(greek_gods), random.choice(greek_gods)),
    (random.choice(greek_gods), random.choice(greek_gods)),
    (random.choice(greek_gods), random.choice(greek_gods))
]

# Create a directed graph
G = nx.DiGraph()

# Add edges to the graph
G.add_edges_from(relationships)

# Compute node positions using spring layout
pos = nx.spring_layout(G)

# Create edge traces
edge_x = []
edge_y = []
edge_text = []  # List to hold edge text
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])
    edge_text.append(f"Connections: {len(G.adj[edge[1]])}")  # Append number of connections to edge text

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='text',
    text=edge_text,  # Assign edge text
    mode='lines')

# Create node traces
node_x = []
node_y = []
node_names = []  # List to hold node names
node_text = []  # List to hold node text
node_colors = []  # List to hold node colors
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_names.append(f"{node}: {len(G.adj[node])}")  # Append node name with number of connections
    node_colors.append(len(G.adj[node]))  # Append node degree to colors list

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    hoverinfo='text',
    text=node_names,  # Assign node names
    textposition="top center",
    marker=dict(
        showscale=True,
        colorscale='YlGnBu',
        size=10,
        color=node_colors,  # Assign node colors
        line_width=2))

# Create figure
fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='Relationships Knowledge Graph',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    height=800  # Set the height of the plot
                    ))

# Show interactive plot
fig.show()
