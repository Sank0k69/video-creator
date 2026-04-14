"""
Dashboard Panel — main workspace for Video Creator extension.
Contextual right panel: Create, Library, Idea Generator, Script Writer, etc.
Renders in the right slot of Imperal Cloud OS.
"""
from __future__ import annotations

from imperal_sdk.ui import (
    Page, Section, Row, Column, Stack, Grid, Tabs,
    Header, Text, Stat, Stats, Badge, Divider,
    DataTable, DataColumn, Button, Card, Image, Icon,
    Form, Input, TextArea, Select, Slider, TagInput,
    Timeline, Progress, Alert, Markdown,
    SlideOver, Dialog, Chart, Empty,
    ListItem, List, KeyValue,
    Call, Navigate,
)


def register_dashboard(ext):
    """Register the dashboard panel on the right slot."""

    @ext.panel("dashboard", slot="right")
    async def dashboard_panel(ctx):
        # ------- Load all data -------
        ideas_bank = await ctx.store.get("ideation", "ideas_bank") or []
        scripts = await ctx.store.query("scripting_scripts", {})
        metrics = await ctx.store.query("iteration_metrics", {})
        videos = await ctx.store.get("video_production", "videos") or []
        recent_activity = await ctx.store.get("activity", "recent") or []

        completed = [v for v in videos if v.get("status") == "completed"]
        processing = [v for v in videos if v.get("status") in ("processing", "pending")]
        failed = [v for v in videos if v.get("status") == "failed"]

        return Page(
            title="Video Creator",
            subtitle="AI-powered video content workspace",
            children=[
                Tabs(
                    tabs=[
                        {"label": "Create", "content": _build_create_tab()},
                        {"label": "Library", "content": _build_library_tab(videos, completed, processing, failed)},
                        {"label": "Ideas", "content": _build_ideas_tab(ideas_bank)},
                        {"label": "Scripts", "content": _build_scripts_tab(scripts)},
                        {"label": "Analytics", "content": _build_analytics_tab(videos, completed, metrics, recent_activity)},
                    ],
                ),
            ],
        )

    return dashboard_panel


# =====================================================
# TAB 1: CREATE — the primary workflow
# =====================================================

def _build_create_tab():
    """Create tab — simple brief input, format cards, one-click generate."""

    return Stack(children=[
        # Brief input
        Section(
            title="What is this video about?",
            children=[
                Form(
                    action="create_video_start",
                    submit_label="Generate Script",
                    children=[
                        TextArea(
                            placeholder="Describe your video idea: topic, key points, target audience...",
                            param_name="brief",
                            rows=3,
                        ),

                        Divider(label="Duration"),
                        Row(children=[
                            Button(
                                label="Quick 60s",
                                variant="secondary",
                                icon="zap",
                                on_click=Call(function="write_script", params={"tier": 1, "format_type": "viral", "duration": "short"}),
                            ),
                            Button(
                                label="Detailed 3-5min",
                                variant="secondary",
                                icon="clock",
                                on_click=Call(function="write_script", params={"tier": 2, "format_type": "viral", "duration": "medium"}),
                            ),
                            Button(
                                label="Full 10min+",
                                variant="secondary",
                                icon="film",
                                on_click=Call(function="write_script", params={"tier": 2, "format_type": "viral", "duration": "long"}),
                            ),
                        ]),

                        Divider(label="Style"),
                        Grid(
                            columns=4,
                            gap=8,
                            children=[
                                Card(
                                    title="TikTok Viral",
                                    subtitle="Fast hooks, vertical",
                                    on_click=Call(function="write_script", params={"format_type": "viral", "tier": 1}),
                                    content=Icon(name="zap", size=24),
                                ),
                                Card(
                                    title="YouTube Pro",
                                    subtitle="Retention-optimized",
                                    on_click=Call(function="write_script", params={"format_type": "viral", "tier": 2}),
                                    content=Icon(name="youtube", size=24),
                                ),
                                Card(
                                    title="LinkedIn Corp",
                                    subtitle="Thought leadership",
                                    on_click=Call(function="write_script", params={"format_type": "pitch", "tier": 2}),
                                    content=Icon(name="briefcase", size=24),
                                ),
                                Card(
                                    title="Promo",
                                    subtitle="Product showcase",
                                    on_click=Call(function="write_script", params={"format_type": "pitch", "tier": 1}),
                                    content=Icon(name="megaphone", size=24),
                                ),
                            ],
                        ),

                        Divider(label="Options"),
                        Row(children=[
                            Column(children=[
                                Select(
                                    options=[
                                        {"value": "en", "label": "English"},
                                        {"value": "es", "label": "Spanish"},
                                        {"value": "ru", "label": "Russian"},
                                        {"value": "pt", "label": "Portuguese"},
                                        {"value": "de", "label": "German"},
                                        {"value": "fr", "label": "French"},
                                    ],
                                    value="en",
                                    param_name="language",
                                    placeholder="Language",
                                ),
                            ]),
                            Column(children=[
                                Select(
                                    options=[
                                        {"value": "portrait", "label": "Portrait (9:16)"},
                                        {"value": "landscape", "label": "Landscape (16:9)"},
                                        {"value": "square", "label": "Square (1:1)"},
                                    ],
                                    value="portrait",
                                    param_name="dimension",
                                    placeholder="Aspect Ratio",
                                ),
                            ]),
                        ]),
                    ],
                ),
            ],
        ),

        Divider(),

        # Quick actions
        Section(
            title="Quick Actions",
            collapsible=True,
            children=[
                Row(children=[
                    Button(
                        label="Full Pipeline",
                        variant="primary",
                        icon="play",
                        on_click=Call(function="create_video", params={"tier": 1}),
                    ),
                    Button(
                        label="Quick Script",
                        variant="secondary",
                        icon="zap",
                        on_click=Call(function="quick_script", params={"format_type": "viral"}),
                    ),
                    Button(
                        label="Generate Video",
                        variant="secondary",
                        icon="video",
                        on_click=Call(function="create_video_heygen", params={"dimension": "portrait"}),
                    ),
                ]),
            ],
        ),
    ])


# =====================================================
# TAB 2: LIBRARY — browse all videos
# =====================================================

def _build_library_tab(videos, completed, processing, failed):
    """Library tab — video list with status filtering."""

    # Stats bar
    stats_row = Stats(children=[
        Stat(label="Total", value=str(len(videos)), icon="film"),
        Stat(label="Completed", value=str(len(completed)), icon="check-circle"),
        Stat(label="Processing", value=str(len(processing)), icon="loader"),
        Stat(label="Failed", value=str(len(failed)), icon="alert-triangle"),
    ])

    # Video table
    table_rows = []
    for v in videos[:50]:
        table_rows.append({
            "title": v.get("title", v.get("video_id", "Untitled")[:40]),
            "status": v.get("status", "unknown"),
            "duration": _format_duration(v.get("duration", 0)),
            "created": v.get("created_at", v.get("created", "")),
        })

    if not table_rows:
        return Stack(children=[
            stats_row,
            Divider(),
            Empty(
                message="No videos yet. Create your first one!",
                icon="video",
                action=Navigate(path="/video-creator/create"),
            ),
        ])

    videos_table = DataTable(
        rows=table_rows,
        columns=[
            DataColumn(key="title", label="Title"),
            DataColumn(key="status", label="Status"),
            DataColumn(key="duration", label="Duration"),
            DataColumn(key="created", label="Created"),
        ],
    )

    return Stack(children=[
        stats_row,
        Divider(),
        Row(children=[
            Button(
                label="New Video",
                variant="primary",
                icon="plus",
                on_click=Navigate(path="/video-creator/create"),
            ),
            Button(
                label="Refresh",
                variant="secondary",
                icon="refresh-cw",
                on_click=Call(function="list_avatars", params={"limit": 1}),
            ),
        ]),
        videos_table,
    ])


# =====================================================
# TAB 3: IDEAS — idea generator
# =====================================================

def _build_ideas_tab(ideas_bank):
    """Ideas tab — generate and browse ideas."""

    return Stack(children=[
        Section(
            title="Idea Generator",
            children=[
                Form(
                    action="generate_ideas_form",
                    submit_label="Generate Ideas",
                    children=[
                        Input(
                            placeholder="Topic or niche (e.g., NVMe hosting, website speed)...",
                            param_name="topic",
                        ),
                        Row(children=[
                            Column(children=[
                                Select(
                                    options=[
                                        {"value": "5", "label": "5 ideas"},
                                        {"value": "10", "label": "10 ideas"},
                                        {"value": "20", "label": "20 ideas"},
                                    ],
                                    value="10",
                                    param_name="count",
                                    placeholder="How many",
                                ),
                            ]),
                            Column(children=[
                                Select(
                                    options=[
                                        {"value": "mixed", "label": "Mixed methods"},
                                        {"value": "commence", "label": "Commence"},
                                        {"value": "snatch_twirl", "label": "Snatch & Twirl"},
                                        {"value": "audience", "label": "Audience-first"},
                                    ],
                                    value="mixed",
                                    param_name="method",
                                    placeholder="Method",
                                ),
                            ]),
                        ]),
                    ],
                ),
                Row(children=[
                    Button(
                        label="Generate Ideas",
                        variant="primary",
                        icon="lightbulb",
                        on_click=Call(function="generate_ideas", params={"count": 10, "method": "mixed"}),
                    ),
                    Button(
                        label="Generate Hooks",
                        variant="secondary",
                        icon="anchor",
                        on_click=Call(function="generate_hooks", params={"count": 5}),
                    ),
                ]),
            ],
        ),

        Divider(),

        # Ideas bank
        Section(
            title=f"Ideas Bank ({len(ideas_bank)})",
            collapsible=True,
            children=[
                DataTable(
                    rows=ideas_bank[:20],
                    columns=[
                        DataColumn(key="title", label="Idea"),
                        DataColumn(key="classification", label="Zone"),
                        DataColumn(key="hook_potential", label="Hook Type"),
                    ],
                ) if ideas_bank else Empty(
                    message="No ideas yet. Generate some above!",
                    icon="lightbulb",
                ),
            ],
        ),
    ])


# =====================================================
# TAB 4: SCRIPTS — script workspace
# =====================================================

def _build_scripts_tab(scripts):
    """Scripts tab — write and manage scripts."""

    return Stack(children=[
        Section(
            title="Script Writer",
            children=[
                Form(
                    action="write_script_form",
                    submit_label="Write Script",
                    children=[
                        Input(
                            placeholder="Topic (e.g., Why NVMe hosting is 10x faster)",
                            param_name="topic",
                        ),
                        Row(children=[
                            Column(children=[
                                Select(
                                    options=[
                                        {"value": "1", "label": "Tier 1 -- Simple (hook-body-CTA)"},
                                        {"value": "2", "label": "Tier 2 -- Advanced (setup-stress-payoff)"},
                                    ],
                                    value="1",
                                    param_name="tier",
                                ),
                            ]),
                            Column(children=[
                                Select(
                                    options=[
                                        {"value": "viral", "label": "Viral"},
                                        {"value": "pitch", "label": "Pitch"},
                                        {"value": "false_statement", "label": "False Statement"},
                                    ],
                                    value="viral",
                                    param_name="format_type",
                                ),
                            ]),
                            Column(children=[
                                Select(
                                    options=[
                                        {"value": "short", "label": "Short (60s)"},
                                        {"value": "medium", "label": "Medium (3-5 min)"},
                                        {"value": "long", "label": "Long (10+ min)"},
                                    ],
                                    value="short",
                                    param_name="duration",
                                ),
                            ]),
                        ]),
                    ],
                ),
                Row(children=[
                    Button(
                        label="Write Script",
                        variant="primary",
                        icon="file-text",
                        on_click=Call(function="write_script", params={"tier": 1, "format_type": "viral"}),
                    ),
                    Button(
                        label="Quick Script",
                        variant="secondary",
                        icon="zap",
                        on_click=Call(function="quick_script", params={"format_type": "viral"}),
                    ),
                ]),
            ],
        ),

        Divider(),

        # Script output
        Section(
            title="Script Preview",
            collapsible=True,
            children=[
                Card(
                    title="Output",
                    content=Markdown(content="_No script generated yet. Use the form above to create one._"),
                ),
                Divider(),
                Row(children=[
                    Input(
                        placeholder="Rewrite instructions (e.g., make it more casual, add humor)...",
                        param_name="rewrite_prompt",
                    ),
                    Button(
                        label="Rewrite",
                        variant="secondary",
                        icon="refresh-cw",
                        on_click=Call(function="write_script", params={"tier": 1}),
                    ),
                ]),
            ],
        ),

        Divider(),

        # Video generation from script
        Section(
            title="Render Video",
            collapsible=True,
            children=[
                Row(children=[
                    Column(children=[
                        Select(
                            options=[
                                {"value": "portrait", "label": "Portrait (9:16)"},
                                {"value": "landscape", "label": "Landscape (16:9)"},
                                {"value": "square", "label": "Square (1:1)"},
                            ],
                            value="portrait",
                            param_name="dimension",
                            placeholder="Video Dimension",
                        ),
                    ]),
                    Column(children=[
                        Select(
                            options=[
                                {"value": "en", "label": "English"},
                                {"value": "es", "label": "Spanish"},
                                {"value": "ru", "label": "Russian"},
                            ],
                            value="en",
                            param_name="voice_language",
                            placeholder="Voice Language",
                        ),
                    ]),
                ]),
                Row(children=[
                    Button(
                        label="Generate Video",
                        variant="primary",
                        icon="video",
                        on_click=Call(function="create_video_heygen", params={"dimension": "portrait"}),
                    ),
                    Button(
                        label="List Avatars",
                        variant="secondary",
                        icon="users",
                        on_click=Call(function="list_avatars", params={"limit": 20}),
                    ),
                    Button(
                        label="List Voices",
                        variant="secondary",
                        icon="mic",
                        on_click=Call(function="list_voices", params={"language": "en"}),
                    ),
                ]),
                Progress(
                    value=0,
                    label="Waiting for generation...",
                    variant="bar",
                ),
            ],
        ),

        Divider(),

        # Scripts list
        Section(
            title=f"Recent Scripts ({len(scripts)})",
            collapsible=True,
            children=[
                DataTable(
                    rows=[
                        {"script_id": sid, "status": "completed"}
                        for sid in scripts[:10]
                    ] if scripts else [],
                    columns=[
                        DataColumn(key="script_id", label="Script"),
                        DataColumn(key="status", label="Status"),
                    ],
                ) if scripts else Empty(
                    message="No scripts yet. Write one above!",
                    icon="file-text",
                ),
            ],
        ),
    ])


# =====================================================
# TAB 5: ANALYTICS — performance overview
# =====================================================

def _build_analytics_tab(videos, completed, metrics, recent_activity):
    """Analytics tab — performance charts, activity timeline."""

    # Performance chart
    chart_data = [
        {"name": "Mon", "videos": 0},
        {"name": "Tue", "videos": 0},
        {"name": "Wed", "videos": 0},
        {"name": "Thu", "videos": 0},
        {"name": "Fri", "videos": 0},
        {"name": "Sat", "videos": 0},
        {"name": "Sun", "videos": 0},
    ]

    # Activity timeline
    activity_items = []
    for act in (recent_activity or [])[:8]:
        activity_items.append({
            "label": act.get("label", "Activity"),
            "description": act.get("description", ""),
            "status": act.get("status", "completed"),
            "time": act.get("time", ""),
        })
    if not activity_items:
        activity_items = [{"label": "No activity yet", "status": "pending"}]

    return Stack(children=[
        Stats(children=[
            Stat(label="Total Videos", value=str(len(videos)), icon="film"),
            Stat(label="Completed", value=str(len(completed)), icon="check-circle", trend="up" if completed else ""),
            Stat(label="Tracked", value=str(len(metrics)), icon="bar-chart-2"),
        ]),

        Divider(),

        Row(children=[
            Column(children=[
                Section(
                    title="Videos Created (This Week)",
                    children=[
                        Chart(
                            type="line",
                            data=chart_data,
                            x_key="name",
                            height=200,
                        ),
                    ],
                ),
            ]),
            Column(children=[
                Section(
                    title="Recent Activity",
                    children=[
                        Timeline(items=activity_items),
                    ],
                ),
            ]),
        ]),
    ])


# =====================================================
# HELPERS
# =====================================================

def _format_duration(seconds) -> str:
    """Format seconds into human-readable duration."""
    if not seconds:
        return "--"
    try:
        seconds = int(float(seconds))
    except (ValueError, TypeError):
        return "--"
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    secs = seconds % 60
    if minutes < 60:
        return f"{minutes}m {secs}s"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m"
