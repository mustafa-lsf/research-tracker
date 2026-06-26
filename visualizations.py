import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from config import STATUS_COLORS, PUBLICATION_STATUSES

def create_status_pie_chart(stats):
    """Create pie chart of publication statuses"""
    if not stats or not stats.get('status_counts'):
        return create_empty_chart("No publication data available")
    
    status_counts = stats['status_counts']
    
    # Filter out zero counts
    labels = []
    values = []
    colors = []
    
    for status, count in status_counts.items():
        if count > 0:
            labels.append(status)
            values.append(count)
            colors.append(STATUS_COLORS.get(status, '#BDBDBD'))
    
    if not values:
        return create_empty_chart("No publications to display")
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent+value',
        textposition='outside',
        hovertemplate="<b>%{label}</b><br>" +
                      "Count: %{value}<br>" +
                      "Percentage: %{percent}<br>" +
                      "<extra></extra>"
    )])
    
    fig.update_layout(
        title={
            'text': "Publication Status Distribution",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333'}
        },
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        height=450,
        margin=dict(t=60, b=80)
    )
    
    return fig

def create_group_comparison_chart(all_groups_data):
    """Create bar chart comparing multiple groups"""
    if not all_groups_data:
        return create_empty_chart("No group data available")
    
    groups = []
    accepted = []
    in_progress = []
    rejected = []
    
    for group_name, stats in all_groups_data.items():
        if stats:
            groups.append(group_name)
            accepted.append(stats.get('accepted', 0))
            in_progress.append(stats.get('in_progress', 0))
            rejected.append(stats.get('rejected', 0))
    
    if not groups:
        return create_empty_chart("No data to compare")
    
    fig = go.Figure(data=[
        go.Bar(name='Accepted', x=groups, y=accepted, 
               marker_color=STATUS_COLORS['Accepted'],
               text=accepted, textposition='auto'),
        go.Bar(name='In Progress', x=groups, y=in_progress, 
               marker_color=STATUS_COLORS['In Preparation'],
               text=in_progress, textposition='auto'),
        go.Bar(name='Rejected', x=groups, y=rejected, 
               marker_color=STATUS_COLORS['Rejected'],
               text=rejected, textposition='auto')
    ])
    
    fig.update_layout(
        title={
            'text': "Group Publication Comparison",
            'x': 0.5,
            'font': {'size': 16, 'color': '#333'}
        },
        barmode='group',
        xaxis_title="Research Groups",
        yaxis_title="Number of Publications",
        legend_title="Status",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_monthly_trend_chart(monthly_data):
    """Create line chart showing monthly publication trends"""
    if not monthly_data:
        return create_empty_chart("No trend data available")
    
    # Prepare data
    months = []
    total_counts = []
    accepted_counts = []
    
    # This would need actual data processing based on your database structure
    for month_data in monthly_data:
        months.append(month_data['month'])
        total_counts.append(month_data['count'])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months, 
        y=total_counts,
        mode='lines+markers',
        name='Total Submissions',
        line=dict(color='#42A5F5', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title={
            'text': "Publication Trends (Last 12 Months)",
            'x': 0.5,
            'font': {'size': 16, 'color': '#333'}
        },
        xaxis_title="Month",
        yaxis_title="Number of Publications",
        height=400,
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_publication_type_chart(type_distribution):
    """Create chart showing distribution of publication types"""
    if not type_distribution:
        return create_empty_chart("No publication type data available")
    
    types = [t['publication_type'] for t in type_distribution]
    counts = [t['count'] for t in type_distribution]
    
    fig = go.Figure(data=[go.Bar(
        y=types,
        x=counts,
        orientation='h',
        marker=dict(
            color=counts,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Count")
        ),
        text=counts,
        textposition='auto'
    )])
    
    fig.update_layout(
        title={
            'text': "Publications by Type",
            'x': 0.5,
            'font': {'size': 16, 'color': '#333'}
        },
        xaxis_title="Number of Publications",
        yaxis_title="Publication Type",
        height=350,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

def create_acceptance_gauge(acceptance_rate):
    """Create gauge chart for acceptance rate"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=acceptance_rate,
        title={'text': "Acceptance Rate", 'font': {'size': 16}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': "#66BB6A"},
            'steps': [
                {'range': [0, 25], 'color': "#FFB6C1"},
                {'range': [25, 50], 'color': "#FFF176"},
                {'range': [50, 75], 'color': "#81C784"},
                {'range': [75, 100], 'color': "#4CAF50"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 2},
                'thickness': 0.75,
                'value': 50
            }
        },
        number={'suffix': "%", 'font': {'size': 20}}
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(t=30, b=0)
    )
    
    return fig

def create_publication_timeline(publications_df):
    """Create timeline of publications"""
    if publications_df.empty:
        return create_empty_chart("No publication data available")
    
    fig = go.Figure()
    
    for status in PUBLICATION_STATUSES:
        status_df = publications_df[publications_df['status'] == status]
        if not status_df.empty:
            fig.add_trace(go.Scatter(
                x=status_df['date_submitted'],
                y=[status] * len(status_df),
                mode='markers',
                name=status,
                marker=dict(
                    size=12,
                    color=STATUS_COLORS.get(status, '#BDBDBD'),
                    symbol='circle'
                ),
                text=status_df['paper_title'],
                hovertemplate="<b>%{text}</b><br>" +
                              "Status: %{y}<br>" +
                              "Date: %{x}<br>" +
                              "<extra></extra>"
            ))
    
    fig.update_layout(
        title={
            'text': "Publication Timeline",
            'x': 0.5,
            'font': {'size': 16, 'color': '#333'}
        },
        xaxis_title="Date",
        yaxis_title="Status",
        height=400,
        hovermode='closest',
        showlegend=True
    )
    
    return fig

def create_empty_chart(message="No data available"):
    """Create empty chart with message"""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=14, color="#999")
    )
    fig.update_layout(
        height=300,
        xaxis={'visible': False},
        yaxis={'visible': False}
    )
    return fig

def create_summary_metrics(stats):
    """Create summary metrics display"""
    if not stats:
        return None
    
    metrics = [
        {"label": "Total Publications", "value": stats.get('total', 0), "delta": None},
        {"label": "In Progress", "value": stats.get('in_progress', 0), "delta": None},
        {"label": "Accepted", "value": stats.get('accepted', 0), 
         "delta": f"+{stats.get('accepted', 0) - stats.get('rejected', 0)}"},
        {"label": "Acceptance Rate", "value": f"{stats.get('acceptance_rate', 0)}%", "delta": None}
    ]
    
    return metrics