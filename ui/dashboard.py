"""
Dashboard Panel — main workspace for Video Creator extension.
Pure DUI components, no iframe. SDK 1.5.4 with native Video() player.

Tabs: Create | My Videos | Ideas | Scripts | Analytics
Renders in slot="main" (center panel).
"""
from __future__ import annotations

from imperal_sdk.ui import (
    Page, Section, Stack, Grid, Tabs,
    Header, Text, Stat, Stats, Badge, Divider,
    DataTable, DataColumn, Button, Card, Image, Icon,
    Form, Input, TextArea, Select,
    Timeline, Progress, Alert, Markdown, Chart,
    List, ListItem, Empty, KeyValue, Video,
    Call, Open, Link,
)


def register_dashboard(ext):
    """Register the dashboard panel on the center slot (like Mail Client)."""

    @ext.panel("workspace", slot="center", title="Video Creator", icon="Film")
    async def workspace_panel(ctx):
        # Load data from store
        # Use get() only — query() causes 307 redirect on Imperal
        try:
            videos = await ctx.store.get("video_production", "videos") or []
        except Exception:
            videos = []
        try:
            ideas_bank = await ctx.store.get("ideation", "ideas_bank") or []
        except Exception:
            ideas_bank = []
        try:
            scripts = await ctx.store.get("scripting", "scripts") or []
        except Exception:
            scripts = []
        try:
            metrics = await ctx.store.get("iteration", "metrics") or []
        except Exception:
            metrics = []
        try:
            recent_activity = await ctx.store.get("activity", "log") or []
        except Exception:
            recent_activity = []

        completed = [v for v in videos if v.get("status") == "completed"]
        processing = [v for v in videos if v.get("status") in ("processing", "pending")]
        failed = [v for v in videos if v.get("status") == "failed"]

        return Page(
            title="Video Creator",
            subtitle="AI-powered video content workspace",
            children=[
                Tabs(
                    tabs=[
                        {
                            "label": "Create",
                            "icon": "sparkles",
                            "content": _build_create_tab(),
                        },
                        {
                            "label": "My Videos",
                            "icon": "film",
                            "content": _build_library_tab(videos, completed, processing, failed),
                        },
                        {
                            "label": "Ideas",
                            "icon": "lightbulb",
                            "content": _build_ideas_tab(ideas_bank),
                        },
                        {
                            "label": "Scripts",
                            "icon": "file-text",
                            "content": _build_scripts_tab(scripts),
                        },
                        {
                            "label": "Analytics",
                            "icon": "bar-chart-2",
                            "content": _build_analytics_tab(videos, completed, metrics, recent_activity),
                        },
                    ],
                    default_tab=0,
                ),
            ],
        )

    return workspace_panel


# =====================================================
# TAB 1: CREATE — the main workflow
# =====================================================

def _build_create_tab():
    """Create tab -- brief input, duration/style cards, generate button."""

    return Stack(children=[
        # Brief
        Section(
            title="What is this video about?",
            children=[
                TextArea(
                    placeholder="Describe your video idea: topic, key points, target audience...",
                    param_name="brief",
                    rows=3,
                ),
            ],
        ),

        # Duration selection
        Section(
            title="Duration",
            children=[
                Stack(direction="h", gap=4, children=[
                    Card(
                        title="Quick 60s",
                        subtitle="Fast hook, single point",
                        content=Icon(name="zap", size=28, color="orange"),
                        on_click=Call(function="write_script", tier=1, format_type="viral", duration="short"),
                    ),
                    Card(
                        title="Detailed 3-5min",
                        subtitle="Deep dive, multi-point",
                        content=Icon(name="clock", size=28, color="blue"),
                        on_click=Call(function="write_script", tier=2, format_type="viral", duration="medium"),
                    ),
                    Card(
                        title="Full 10min+",
                        subtitle="Complete breakdown",
                        content=Icon(name="film", size=28, color="purple"),
                        on_click=Call(function="write_script", tier=2, format_type="viral", duration="long"),
                    ),
                ]),
            ],
        ),

        # Style presets
        Section(
            title="Style Preset",
            children=[
                Grid(columns=2, gap=4, children=[
                    Card(
                        title="TikTok Viral",
                        subtitle="Fast hooks, vertical, trending",
                        content=Stack(direction="h", gap=2, children=[
                            Icon(name="zap", size=20),
                            Badge(label="Short-form", color="orange"),
                        ]),
                        on_click=Call(function="write_script", format_type="viral", tier=1, duration="short"),
                    ),
                    Card(
                        title="YouTube Pro",
                        subtitle="Retention-optimized, long-form",
                        content=Stack(direction="h", gap=2, children=[
                            Icon(name="play", size=20),
                            Badge(label="Long-form", color="red"),
                        ]),
                        on_click=Call(function="write_script", format_type="viral", tier=2, duration="medium"),
                    ),
                    Card(
                        title="LinkedIn Corp",
                        subtitle="Thought leadership, professional",
                        content=Stack(direction="h", gap=2, children=[
                            Icon(name="briefcase", size=20),
                            Badge(label="B2B", color="blue"),
                        ]),
                        on_click=Call(function="write_script", format_type="pitch", tier=2, duration="medium"),
                    ),
                    Card(
                        title="Promo",
                        subtitle="Product showcase, no avatar",
                        content=Stack(direction="h", gap=2, children=[
                            Icon(name="megaphone", size=20),
                            Badge(label="Sales", color="green"),
                        ]),
                        on_click=Call(function="write_script", format_type="pitch", tier=1, duration="short"),
                    ),
                ]),
            ],
        ),

        # Language + Format row
        Section(
            title="Options",
            collapsible=True,
            children=[
                Stack(direction="h", gap=4, children=[
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
            ],
        ),

        Divider(),

        # BIG Generate button
        Button(
            label="Generate Script",
            variant="primary",
            icon="sparkles",
            size="md",
            full_width=True,
            on_click=Call(function="write_script", tier=1, format_type="viral", duration="short"),
        ),

        Divider(),

        # Quick actions
        Section(
            title="Quick Actions",
            collapsible=True,
            children=[
                Stack(direction="h", gap=3, children=[
                    Button(
                        label="Full Pipeline",
                        variant="primary",
                        icon="play",
                        on_click=Call(function="create_video", tier=1),
                    ),
                    Button(
                        label="Quick Script",
                        variant="secondary",
                        icon="zap",
                        on_click=Call(function="quick_script", format_type="viral"),
                    ),
                    Button(
                        label="Generate Video",
                        variant="secondary",
                        icon="video",
                        on_click=Call(function="create_video_heygen", dimension="portrait"),
                    ),
                ]),
            ],
        ),
    ])


# =====================================================
# TAB 2: MY VIDEOS — video library with native Video()
# =====================================================

def _build_library_tab(videos, completed, processing, failed):
    """Library tab -- stats, video cards with native player, data table."""

    # Stats row
    stats_row = Stats(children=[
        Stat(label="Total", value=str(len(videos)), icon="film", color="blue"),
        Stat(label="Completed", value=str(len(completed)), icon="check-circle", color="green"),
        Stat(label="Processing", value=str(len(processing)), icon="loader", color="yellow"),
        Stat(label="Failed", value=str(len(failed)), icon="alert-triangle", color="red"),
    ])

    # Empty state
    if not videos:
        return Stack(children=[
            stats_row,
            Divider(),
            Empty(
                message="No videos yet. Create your first one!",
                icon="film",
                action=Call(function="write_script", topic="", tier=1),
            ),
        ])

    # Video cards for completed videos with native Video() player
    video_cards = []
    for v in completed[:6]:
        title = v.get("title", "Untitled")[:40]
        video_url = v.get("video_url", "")
        thumb = v.get("thumbnail_url", "")
        duration = _format_duration(v.get("duration", 0))
        status = v.get("status", "completed")

        card_content_items = []

        # Native video player
        if video_url:
            card_content_items.append(
                Video(
                    src=video_url,
                    poster=thumb,
                    controls=True,
                    width="100%",
                    title=title,
                )
            )
        elif thumb:
            card_content_items.append(
                Image(src=thumb, alt=title, width="100%", object_fit="cover")
            )

        # Meta info
        card_content_items.append(
            Stack(direction="h", gap=2, children=[
                Badge(label=status, color="green"),
                Text(content=duration, variant="caption"),
            ])
        )

        video_cards.append(Card(
            title=title,
            subtitle=duration,
            content=Stack(children=card_content_items),
        ))

    # Data table for all videos
    table_rows = []
    for v in videos[:50]:
        status = v.get("status", "unknown")
        table_rows.append({
            "title": v.get("title", v.get("video_id", "Untitled"))[:40],
            "status": status,
            "duration": _format_duration(v.get("duration", 0)),
            "created": v.get("created_at", v.get("created", "")),
        })

    videos_table = DataTable(
        rows=table_rows,
        columns=[
            DataColumn(key="title", label="Title"),
            DataColumn(key="status", label="Status"),
            DataColumn(key="duration", label="Duration"),
            DataColumn(key="created", label="Created"),
        ],
        on_row_click=Call(function="video_status", video_id=""),
    )

    children = [
        stats_row,
        Divider(),
    ]

    # Video preview grid
    if video_cards:
        children.append(
            Section(
                title="Recent Videos",
                children=[
                    Grid(columns=2, gap=4, children=video_cards),
                ],
            )
        )
        children.append(Divider())

    # Action buttons + table
    children.append(
        Stack(direction="h", gap=3, children=[
            Button(
                label="New Video",
                variant="primary",
                icon="plus",
                on_click=Call(function="write_script", topic="", tier=1),
            ),
            Button(
                label="Refresh",
                variant="secondary",
                icon="refresh-cw",
                on_click=Call(function="video_status", video_id="all"),
            ),
        ])
    )
    children.append(videos_table)

    return Stack(children=children)


# =====================================================
# TAB 3: IDEAS — idea generator
# =====================================================

def _build_ideas_tab(ideas_bank):
    """Ideas tab -- generate ideas and browse bank."""

    # Idea items as clickable list
    idea_items = []
    for i, idea in enumerate(ideas_bank[:20]):
        idea_title = idea.get("title", f"Idea {i+1}")
        zone = idea.get("classification", "")
        hook_type = idea.get("hook_potential", "")

        idea_items.append(
            ListItem(
                id=f"idea-{i}",
                title=idea_title,
                subtitle=f"{zone} -- {hook_type}" if zone else "",
                icon="lightbulb",
                badge=Badge(label=zone, color="blue") if zone else None,
                on_click=Call(function="write_script", topic=idea_title, tier=1),
                actions=[
                    {
                        "label": "Use this idea",
                        "icon": "arrow-right",
                        "on_click": Call(function="write_script", topic=idea_title, tier=1),
                    },
                ],
            )
        )

    return Stack(children=[
        Section(
            title="Idea Generator",
            children=[
                Stack(children=[
                    Input(
                        placeholder="Topic or niche (e.g., NVMe hosting, website speed)...",
                        param_name="topic",
                    ),
                    Stack(direction="h", gap=3, children=[
                        Select(
                            options=[
                                {"value": "5", "label": "5 ideas"},
                                {"value": "10", "label": "10 ideas"},
                                {"value": "20", "label": "20 ideas"},
                            ],
                            value="5",
                            param_name="count",
                            placeholder="How many",
                        ),
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
                Divider(),
                Stack(direction="h", gap=3, children=[
                    Button(
                        label="Generate 5 Ideas",
                        variant="primary",
                        icon="sparkles",
                        on_click=Call(function="generate_ideas", count=5, method="mixed"),
                    ),
                    Button(
                        label="Generate Hooks",
                        variant="secondary",
                        icon="anchor",
                        on_click=Call(function="generate_hooks", count=5),
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
                List(items=idea_items) if idea_items else Empty(
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
    """Scripts tab -- write new, browse recent, preview with Markdown."""

    # Recent script cards
    script_cards = []
    for s in (scripts[:6] if isinstance(scripts, list) else []):
        sid = s.get("script_id", s.get("id", ""))
        title = s.get("title", s.get("topic", f"Script {sid}"))[:40]
        preview = s.get("preview", s.get("content", ""))[:120]
        status = s.get("status", "completed")

        script_cards.append(Card(
            title=title,
            subtitle=status,
            content=Stack(children=[
                Markdown(content=preview + "..." if len(preview) >= 120 else preview) if preview else Text(content="No preview available", variant="caption"),
                Badge(label=status, color="green" if status == "completed" else "gray"),
            ]),
            on_click=Call(function="video_status", video_id=sid),
        ))

    return Stack(children=[
        # Script writer form
        Section(
            title="Write New Script",
            children=[
                Input(
                    placeholder="Topic (e.g., Why NVMe hosting is 10x faster)",
                    param_name="topic",
                ),
                Stack(direction="h", gap=3, children=[
                    Select(
                        options=[
                            {"value": "1", "label": "Tier 1 -- Simple (hook-body-CTA)"},
                            {"value": "2", "label": "Tier 2 -- Advanced (setup-stress-payoff)"},
                        ],
                        value="1",
                        param_name="tier",
                    ),
                    Select(
                        options=[
                            {"value": "viral", "label": "Viral"},
                            {"value": "pitch", "label": "Pitch"},
                            {"value": "false_statement", "label": "False Statement"},
                        ],
                        value="viral",
                        param_name="format_type",
                    ),
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
                Divider(),
                Stack(direction="h", gap=3, children=[
                    Button(
                        label="Write Script",
                        variant="primary",
                        icon="file-text",
                        on_click=Call(function="write_script", tier=1, format_type="viral"),
                    ),
                    Button(
                        label="Quick Script",
                        variant="secondary",
                        icon="zap",
                        on_click=Call(function="quick_script", format_type="viral"),
                    ),
                ]),
            ],
        ),

        Divider(),

        # Render video section
        Section(
            title="Render Video",
            collapsible=True,
            children=[
                Stack(direction="h", gap=3, children=[
                    Select(
                        options=[
                            {"value": "portrait", "label": "Portrait (9:16)"},
                            {"value": "landscape", "label": "Landscape (16:9)"},
                            {"value": "square", "label": "Square (1:1)"},
                        ],
                        value="portrait",
                        param_name="dimension",
                        placeholder="Dimension",
                    ),
                    Select(
                        options=[
                            {"value": "en", "label": "English"},
                            {"value": "es", "label": "Spanish"},
                            {"value": "ru", "label": "Russian"},
                        ],
                        value="en",
                        param_name="voice_language",
                        placeholder="Voice",
                    ),
                ]),
                Stack(direction="h", gap=3, children=[
                    Button(
                        label="Generate Video",
                        variant="primary",
                        icon="video",
                        on_click=Call(function="create_video_heygen", dimension="portrait"),
                    ),
                    Button(
                        label="List Avatars",
                        variant="secondary",
                        icon="users",
                        on_click=Call(function="list_avatars", limit=20),
                    ),
                    Button(
                        label="List Voices",
                        variant="secondary",
                        icon="mic",
                        on_click=Call(function="list_voices", language="en"),
                    ),
                ]),
            ],
        ),

        Divider(),

        # Recent scripts
        Section(
            title=f"Recent Scripts ({len(scripts) if isinstance(scripts, list) else 0})",
            collapsible=True,
            children=[
                Grid(columns=2, gap=3, children=script_cards) if script_cards else Empty(
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
    """Analytics tab -- stats, chart, activity timeline."""

    metrics_list = metrics if isinstance(metrics, list) else []
    activity_list = recent_activity if isinstance(recent_activity, list) else []

    # Calculate totals
    total_words = 0
    total_duration = 0
    for v in completed:
        total_words += v.get("word_count", 0)
        total_duration += v.get("duration", 0)
    avg_duration = _format_duration(total_duration // len(completed)) if completed else "--"

    # Chart data
    chart_data = [
        {"name": "Mon", "videos": 0},
        {"name": "Tue", "videos": 0},
        {"name": "Wed", "videos": 0},
        {"name": "Thu", "videos": 0},
        {"name": "Fri", "videos": 0},
        {"name": "Sat", "videos": 0},
        {"name": "Sun", "videos": 0},
    ]

    # Activity timeline items
    activity_items = []
    for act in activity_list[:8]:
        activity_items.append({
            "label": act.get("label", "Activity"),
            "description": act.get("description", ""),
            "status": act.get("status", "completed"),
            "time": act.get("time", ""),
        })
    if not activity_items:
        activity_items = [{"label": "No activity yet", "status": "pending"}]

    return Stack(children=[
        # Stats overview
        Stats(children=[
            Stat(label="Videos Created", value=str(len(videos)), icon="film", color="blue"),
            Stat(
                label="Completed",
                value=str(len(completed)),
                icon="check-circle",
                color="green",
                trend="up" if completed else "",
            ),
            Stat(label="Total Words", value=str(total_words), icon="type", color="purple"),
            Stat(label="Avg Duration", value=avg_duration, icon="clock", color="orange"),
        ]),

        Divider(),

        # Chart + Timeline side by side
        Grid(columns=2, gap=4, children=[
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
            Section(
                title="Recent Activity",
                children=[
                    Timeline(items=activity_items),
                ],
            ),
        ]),

        Divider(),

        # Metrics table
        Section(
            title=f"Performance Metrics ({len(metrics_list)})",
            collapsible=True,
            children=[
                DataTable(
                    rows=[
                        {
                            "content": m.get("content_id", ""),
                            "views": str(m.get("views", 0)),
                            "retention": f"{m.get('retention', 0)}%",
                            "ctr": f"{m.get('ctr', 0)}%",
                        }
                        for m in metrics_list[:20]
                    ],
                    columns=[
                        DataColumn(key="content", label="Content"),
                        DataColumn(key="views", label="Views"),
                        DataColumn(key="retention", label="Retention"),
                        DataColumn(key="ctr", label="CTR"),
                    ],
                ) if metrics_list else Empty(
                    message="No metrics tracked yet. Publish a video and track its performance.",
                    icon="bar-chart-2",
                ),
            ],
        ),
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
