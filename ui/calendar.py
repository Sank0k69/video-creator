"""
Content Calendar Widget — schedule and visualize content production.
Shows: planned content, posted content, 30-day streak progress.
"""
from __future__ import annotations
from imperal_sdk.ui import (
    Stack, Row, Column,
    Header, Text, Stat, Stats, Badge, Divider,
    Button, Card,
    Timeline, Progress,
    Call,
)


def register_calendar(ext):
    """Register the content calendar widget."""

    @ext.widget("content_calendar")
    async def calendar_widget(ctx):
        # Load content history
        scripts = await ctx.store.query("scripting_scripts", {})
        metrics = await ctx.store.query("iteration_metrics", {})

        # Calculate streak (simplified)
        total_created = len(scripts)
        streak_progress = min(total_created / 30 * 100, 100) if total_created else 0

        return Stack(children=[
            Header(text="Content Calendar", level=3),

            # 30-day challenge progress
            Card(
                title="30-Day Content Challenge",
                content=Stack(children=[
                    Progress(
                        value=int(streak_progress),
                        label=f"{total_created}/30 pieces created",
                        variant="bar",
                    ),
                    Text(
                        content="Protocol: 1 piece per day, 30 days straight, no breaks."
                        if streak_progress < 100
                        else "Challenge complete! Keep the momentum going.",
                    ),
                ]),
            ),

            Divider(),

            # Content timeline
            Timeline(
                items=[
                    {"label": script_id, "status": "completed"}
                    for script_id in scripts[:5]
                ] if scripts else [
                    {"label": "No content created yet", "status": "pending"}
                ],
            ),

            # Stats
            Stats(children=[
                Stat(label="Created", value=str(total_created)),
                Stat(label="Tracked", value=str(len(metrics))),
                Stat(label="Streak", value=f"{min(total_created, 30)}d"),
            ]),

            # Quick create
            Button(
                label="Create Today's Content",
                variant="primary",
                full_width=True,
                on_click=Call(function="quick_script"),
            ),
        ])

    return calendar_widget
