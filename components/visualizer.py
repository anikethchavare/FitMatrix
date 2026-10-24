# FitMatrix - components/visualizer.py

# Imports
from typing import List
import plotly.graph_objects as go
from core.models import AllocationResult, Block

# Function 1: render_memory_strip
def render_memory_strip(result: AllocationResult) -> go.Figure:
    fig = go.Figure()
    
    for block in result.blocks:
        label = f"Block {block.bid}"
        
        if block.is_allocated:
            fig.add_trace(go.Bar(
                y=[label],
                x=[block.allocated_size],
                orientation='h',
                name='Allocated',
                marker=dict(color=block.process_color or '#3B82F6', line=dict(color='#1E293B', width=1.5)),
                showlegend=False
            ))
            
            if block.internal_fragmentation > 0:
                fig.add_trace(go.Bar(
                    y=[label],
                    x=[block.internal_fragmentation],
                    orientation='h',
                    name='Internal Frag',
                    marker=dict(color='rgba(239, 68, 68, 0.45)', line=dict(color='#EF4444', width=1.5)),
                    showlegend=False
                ))
        else:
            fig.add_trace(go.Bar(
                y=[label],
                x=[block.capacity],
                orientation='h',
                name='Free Partition',
                marker=dict(color='rgba(16, 185, 129, 0.25)', line=dict(color='#10B981', width=1.5)),
                showlegend=False
            ))

    fig.add_trace(go.Bar(x=[None], y=[None], name='Allocated Space', marker=dict(color='#3B82F6')))
    fig.add_trace(go.Bar(x=[None], y=[None], name='Internal Frag', marker=dict(color='rgba(239, 68, 68, 0.45)')))
    fig.add_trace(go.Bar(x=[None], y=[None], name='Free Partition', marker=dict(color='rgba(16, 185, 129, 0.25)')))

    fig.update_layout(
        barmode='stack',
        height=max(240, len(result.blocks) * 55 + 80),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=20, t=10, b=30),
        xaxis=dict(
            title=dict(text='Physical Memory Offset (KB)', font=dict(size=12, color='#94A3B8')),
            gridcolor='#334155'
        ),
        yaxis=dict(
            autorange='reversed',
            tickfont=dict(size=12, color='#CBD5E1'),
            showgrid=False
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.03,
            xanchor='center',
            x=0.5,
            font=dict(size=11, color='#CBD5E1')
        )
    )
    
    return fig

# Function 2: render_partition_cards_html
def render_partition_cards_html(blocks: List[Block]) -> str:
    return ""