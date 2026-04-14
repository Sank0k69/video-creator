"""
Settings Panel — accessible via SlideOver from sidebar.
Full configuration for Video Creator extension.

Sections: Profile, HeyGen, Figma, Platforms, Module Toggles, Quality Gates.
Renders as a dedicated panel navigated from sidebar Settings button.
"""
from __future__ import annotations

from imperal_sdk.ui import (
    Page, Section,  Stack, Grid,
    Header, Text, Divider, Alert, Badge, Icon,
    Form, Input, TextArea, Toggle, Select, TagInput, Slider, FileUpload,
    Button, Card, Accordion,
    Call,
)


# All extension modules with display names
ALL_MODULE_NAMES = {
    "ideation": {"label": "Ideation", "icon": "lightbulb", "desc": "Generate video ideas using Perfect Idea Zone"},
    "framing": {"label": "Framing", "icon": "frame", "desc": "Transform ideas into directed video concepts"},
    "packaging": {"label": "Packaging", "icon": "package", "desc": "Title + thumbnail strategy"},
    "hooks": {"label": "Hooks", "icon": "anchor", "desc": "Psychological hook generation"},
    "scripting": {"label": "Scripting", "icon": "file-text", "desc": "Full script writing (Hook-Body-CTA)"},
    "pcm": {"label": "PCM Analysis", "icon": "brain", "desc": "Personality type coverage analysis"},
    "captions": {"label": "Captions", "icon": "message-square", "desc": "Social media caption generation"},
    "cta": {"label": "CTA", "icon": "mouse-pointer", "desc": "Call-to-action generation"},
    "publishing": {"label": "Publishing", "icon": "send", "desc": "Pre-publish checklist"},
    "iteration": {"label": "Iteration", "icon": "repeat", "desc": "Performance tracking and optimization"},
    "market_research": {"label": "Market Research", "icon": "bar-chart-2", "desc": "GSB analysis, avatars, trajectory"},
    "funnel_copy": {"label": "Funnel Copy", "icon": "filter", "desc": "VSL, page copy, presentations"},
    "email_sequences": {"label": "Email Sequences", "icon": "mail", "desc": "Promo, nurture, webinar sequences"},
    "sales": {"label": "Sales", "icon": "dollar-sign", "desc": "Sales scripts, objection handling, offers"},
    "launch": {"label": "Launch", "icon": "rocket", "desc": "Pre-launch plans, 28-day roadmaps"},
    "video_production": {"label": "Video Production", "icon": "video", "desc": "HeyGen avatar video creation"},
}


def register_settings(ext):
    """Register the settings panel on the extension."""

    @ext.panel("settings", slot="right")
    async def settings_panel(ctx):
        config = ctx.config

        active_count = sum(1 for m in config.get("modules", {}).values() if m)

        return Page(
            title="Settings",
            subtitle="Configure your Video Creator workspace",
            children=[
                Accordion(
                    sections=[
                        {
                            "title": "Profile",
                            "content": _build_profile_section(config),
                        },
                        {
                            "title": "HeyGen Connection",
                            "content": _build_heygen_section(config),
                        },
                        {
                            "title": "Figma",
                            "content": _build_figma_section(config),
                        },
                        {
                            "title": "Platforms",
                            "content": _build_platforms_section(config),
                        },
                        {
                            "title": f"Modules ({active_count}/{len(ALL_MODULE_NAMES)})",
                            "content": _build_modules_section(config),
                        },
                        {
                            "title": "Quality Gates",
                            "content": _build_quality_section(config),
                        },
                    ],
                    allow_multiple=True,
                ),
            ],
        )

    return settings_panel


# =====================================================
# SECTION BUILDERS
# =====================================================

def _build_profile_section(config):
    """Profile: niche, audience, brand voice, language."""
    return Stack(children=[
        Form(
            action="_save_profile",
            submit_label="Save Profile",
            children=[
                Input(
                    placeholder="e.g., Web hosting, SaaS, fitness coaching",
                    value=config.get("niche", ""),
                    param_name="niche",
                ),
                TextArea(
                    placeholder="Describe your ideal viewer -- demographics, pain points, aspirations...",
                    value=config.get("target_audience", ""),
                    rows=3,
                    param_name="target_audience",
                ),
                TagInput(
                    placeholder="Add voice keywords (e.g., confident, casual, data-driven)...",
                    values=config.get("brand_voice", []),
                    param_name="brand_voice",
                ),
                Select(
                    options=[
                        {"value": "en", "label": "English"},
                        {"value": "es", "label": "Spanish"},
                        {"value": "ru", "label": "Russian"},
                        {"value": "pt", "label": "Portuguese"},
                        {"value": "de", "label": "German"},
                        {"value": "fr", "label": "French"},
                        {"value": "zh", "label": "Chinese"},
                        {"value": "ja", "label": "Japanese"},
                        {"value": "ko", "label": "Korean"},
                        {"value": "ar", "label": "Arabic"},
                    ],
                    value=config.get("language", "en"),
                    param_name="language",
                    placeholder="Content Language",
                ),
            ],
        ),
    ])


def _build_heygen_section(config):
    """HeyGen: connection method, API key, status."""
    heygen_key = config.get("heygen_api_key", "")
    is_connected = bool(heygen_key)

    return Stack(children=[
        Stack(direction="h", children=[
            Badge(
                label="Connected" if is_connected else "Not Connected",
                color="green" if is_connected else "red",
            ),
            Text(content="API key is set" if is_connected else "Add your HeyGen API key to enable video generation"),
        ]),
        Form(
            action="_save_profile",
            submit_label="Save HeyGen Settings",
            children=[
                Select(
                    options=[
                        {"value": "api_key", "label": "API Key (direct)"},
                        {"value": "mcp", "label": "MCP Server (OAuth)"},
                    ],
                    value="api_key" if heygen_key else "mcp",
                    param_name="heygen_method",
                    placeholder="Connection Method",
                ),
                Input(
                    placeholder="Enter your HeyGen API key...",
                    value=heygen_key,
                    param_name="heygen_api_key",
                ),
            ],
        ),
        Alert(
            type="info",
            message="HeyGen API key is used for avatar video generation. Get yours at app.heygen.com/settings.",
        ),
    ])


def _build_figma_section(config):
    """Figma: token, file key."""
    figma_token = config.get("figma_token", "")
    figma_file_key = config.get("figma_file_key", "")
    is_connected = bool(figma_token)

    return Stack(children=[
        Stack(direction="h", children=[
            Badge(
                label="Connected" if is_connected else "Not Connected",
                color="green" if is_connected else "gray",
            ),
            Text(content="Figma token is configured" if is_connected else "Add your Figma personal access token"),
        ]),
        Form(
            action="_save_profile",
            submit_label="Save Figma Settings",
            children=[
                Input(
                    placeholder="Enter your Figma personal access token...",
                    value=figma_token,
                    param_name="figma_token",
                ),
                Input(
                    placeholder="e.g., abc123xyz (from Figma URL)",
                    value=figma_file_key,
                    param_name="figma_file_key",
                ),
            ],
        ),
    ])


def _build_platforms_section(config):
    """Social platforms: YouTube, TikTok, Instagram, LinkedIn."""
    platforms_cfg = config.get("platforms", {})

    platform_defs = [
        ("youtube", "YouTube", "youtube"),
        ("tiktok", "TikTok", "music"),
        ("instagram", "Instagram", "instagram"),
        ("linkedin", "LinkedIn", "linkedin"),
    ]

    platform_cards = []
    for platform_id, platform_name, icon_name in platform_defs:
        pcfg = platforms_cfg.get(platform_id, {})
        is_enabled = pcfg.get("enabled", False)
        has_key = bool(pcfg.get("api_key", ""))

        platform_cards.append(
            Card(
                title=platform_name,
                content=Stack(children=[
                    Stack(direction="h", children=[
                        Icon(name=icon_name, size=20),
                        Badge(
                            label="Active" if is_enabled and has_key else "Inactive",
                            color="green" if is_enabled and has_key else "gray",
                        ),
                    ]),
                    Toggle(
                        label="Enable",
                        value=is_enabled,
                        param_name=f"platform_{platform_id}_enabled",
                    ),
                    Input(
                        placeholder=f"Enter {platform_name} API key...",
                        value=pcfg.get("api_key", ""),
                        param_name=f"platform_{platform_id}_api_key",
                    ),
                ]),
            )
        )

    return Stack(children=[
        Grid(
            columns=2,
            gap=12,
            children=platform_cards,
        ),
        Alert(
            type="info",
            message="API keys are stored securely in your personal token wallet. Never shared with other users or extensions.",
        ),
        FileUpload(
            accept=".json",
            on_upload=Call(function="_import_credentials"),
            param_name="credentials_file",
        ),
    ])


def _build_modules_section(config):
    """Module toggles -- enable/disable individual modules."""
    modules_cfg = config.get("modules", {})

    module_cards = []
    for mod_id, mod_info in ALL_MODULE_NAMES.items():
        is_enabled = modules_cfg.get(mod_id, True)
        module_cards.append(
            Card(
                title=mod_info["label"],
                content=Stack(children=[
                    Stack(direction="h", children=[
                        Icon(name=mod_info["icon"], size=16),
                        Text(content=mod_info["desc"]),
                    ]),
                    Toggle(
                        label="Enabled",
                        value=is_enabled,
                        param_name=f"module_{mod_id}",
                    ),
                ]),
            )
        )

    return Stack(children=[
        Grid(
            columns=2,
            gap=12,
            children=module_cards,
        ),
    ])


def _build_quality_section(config):
    """Quality gates -- PCM min types, title length, hook timing."""
    quality = config.get("quality", {})

    return Stack(children=[
        Form(
            action="_save_quality_settings",
            submit_label="Save Quality Gates",
            children=[
                Stack(direction="h", children=[
                    Stack(children=[
                        Select(
                            options=[
                                {"value": "2", "label": "2 -- Lenient"},
                                {"value": "3", "label": "3 -- Recommended"},
                                {"value": "4", "label": "4 -- Strict"},
                                {"value": "5", "label": "5 -- Very Strict"},
                                {"value": "6", "label": "6 -- All Types"},
                            ],
                            value=str(quality.get("pcm_min_types", 3)),
                            param_name="pcm_min_types",
                            placeholder="Min PCM Types per Script",
                        ),
                    ]),
                    Stack(children=[
                        Input(
                            placeholder="Max Title Length (chars)",
                            value=str(quality.get("title_max_chars", 55)),
                            param_name="title_max_chars",
                        ),
                    ]),
                ]),
                Stack(direction="h", children=[
                    Stack(children=[
                        Input(
                            placeholder="Max Hook Duration (seconds)",
                            value=str(quality.get("hook_max_seconds", 3)),
                            param_name="hook_max_seconds",
                        ),
                    ]),
                    Stack(children=[
                        Input(
                            placeholder="Max Thumbnail Words",
                            value=str(quality.get("thumbnail_max_words", 4)),
                            param_name="thumbnail_max_words",
                        ),
                    ]),
                ]),
                Stack(direction="h", children=[
                    Stack(children=[
                        Input(
                            placeholder="Min Script Word Count",
                            value=str(config.get("content", {}).get("min_word_count", 150)),
                            param_name="min_word_count",
                        ),
                    ]),
                    Stack(children=[
                        Input(
                            placeholder="Max Hashtags per Post",
                            value=str(config.get("content", {}).get("max_hashtags", 4)),
                            param_name="max_hashtags",
                        ),
                    ]),
                ]),
            ],
        ),
    ])
