"""
Left Sidebar — navigation hub for Video Creator.
Compact navigation, library filters, tools, queue status, quick stats.
Renders in the left slot of Imperal Cloud OS.
"""
from __future__ import annotations

from imperal_sdk.ui import (
    Page, Section,  Stack,
    Header, Text, Stat, Stats, Badge, Divider, Icon,
    Button, Card, ListItem, List,
    Progress,
    Call, Navigate,
)


def register_sidebar(ext):
    """Register the left sidebar panel on the extension."""

    @ext.panel("sidebar", slot="left")
    async def sidebar_panel(ctx):
        # ------- Load data for counts -------
        videos = await ctx.store.get("video_production", "videos") or []
        ideas_bank = await ctx.store.get("ideation", "ideas_bank") or []
        scripts = await ctx.store.query("scripting_scripts", {})

        completed = [v for v in videos if v.get("status") == "completed"]
        processing = [v for v in videos if v.get("status") in ("processing", "pending")]
        drafts = [v for v in videos if v.get("status") == "draft"]

        queue_size = len(processing)
        queue_pct = 50 if queue_size > 0 else 0  # approximate

        # ------- Build page -------
        return Page(
            title="Video Creator",
            children=[
                # ── Primary CTA ──
                Button(
                    label="New Video",
                    variant="primary",
                    icon="plus",
                    full_width=True,
                    size="md",
                    on_click=Navigate(path="/video-creator/create"),
                ),

                Divider(),

                # ── LIBRARY ──
                Section(
                    title="Library",
                    collapsible=True,
                    children=[
                        List(
                            items=[
                                ListItem(
                                    id="lib-all",
                                    title="All Videos",
                                    icon="film",
                                    meta=str(len(videos)),
                                    on_click=Navigate(path="/video-creator/library"),
                                ),
                                ListItem(
                                    id="lib-completed",
                                    title="Completed",
                                    icon="check-circle",
                                    meta=str(len(completed)),
                                    on_click=Navigate(path="/video-creator/library?filter=completed"),
                                ),
                                ListItem(
                                    id="lib-processing",
                                    title="Processing",
                                    icon="loader",
                                    meta=str(len(processing)),
                                    on_click=Navigate(path="/video-creator/library?filter=processing"),
                                ),
                                ListItem(
                                    id="lib-drafts",
                                    title="Drafts",
                                    icon="file-text",
                                    meta=str(len(drafts)),
                                    on_click=Navigate(path="/video-creator/library?filter=draft"),
                                ),
                            ],
                        ),
                    ],
                ),

                # ── TOOLS ──
                Section(
                    title="Tools",
                    collapsible=True,
                    children=[
                        List(
                            items=[
                                ListItem(
                                    id="tool-ideas",
                                    title="Idea Generator",
                                    icon="lightbulb",
                                    on_click=Navigate(path="/video-creator/ideas"),
                                ),
                                ListItem(
                                    id="tool-scripts",
                                    title="Script Writer",
                                    icon="file-text",
                                    on_click=Navigate(path="/video-creator/scripts"),
                                ),
                                ListItem(
                                    id="tool-hooks",
                                    title="Hook Builder",
                                    icon="anchor",
                                    on_click=Navigate(path="/video-creator/hooks"),
                                ),
                                ListItem(
                                    id="tool-designer",
                                    title="Designer",
                                    icon="image",
                                    on_click=Navigate(path="/video-creator/designer"),
                                ),
                            ],
                        ),
                    ],
                ),

                Divider(),

                # ── QUEUE STATUS ──
                *(
                    [
                        Section(
                            title="Queue",
                            children=[
                                Progress(
                                    value=queue_pct,
                                    label=f"{queue_size} video{'s' if queue_size != 1 else ''} generating",
                                    variant="bar",
                                ),
                            ],
                        ),
                        Divider(),
                    ]
                    if queue_size > 0 else []
                ),

                # ── QUICK STATS ──
                Section(
                    title="Stats",
                    collapsible=True,
                    children=[
                        Stats(
                            children=[
                                Stat(
                                    label="Videos",
                                    value=str(len(completed)),
                                    icon="check-circle",
                                ),
                                Stat(
                                    label="Ideas",
                                    value=str(len(ideas_bank)),
                                    icon="lightbulb",
                                ),
                                Stat(
                                    label="Scripts",
                                    value=str(len(scripts)),
                                    icon="file-text",
                                ),
                            ],
                        ),
                    ],
                ),

                Divider(),

                # ── Settings link ──
                Button(
                    label="Settings",
                    variant="secondary",
                    icon="settings",
                    full_width=True,
                    on_click=Navigate(path="/video-creator/settings"),
                ),
            ],
        )

    return sidebar_panel
