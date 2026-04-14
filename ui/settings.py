"""
Settings Panel -- full configuration for Video Creator extension.
Renders in the left slot of Imperal Cloud OS.

Sections: Profile, HeyGen, Figma, Platforms, Module Toggles, Quality Gates.
"""
from __future__ import annotations

from imperal_sdk.ui import (
    Page, Section, Row, Column, Stack,
    Header, Text, Divider, Alert, Badge, Icon,
    Form, Input, TextArea, Toggle, Select, TagInput, Slider, FileUpload,
    Button, Card,
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

    @ext.panel("settings", slot="left")
    async def settings_panel(ctx):
        config = ctx.config

        return Page(
            title="Settings",
            children=[
                # --- Profile ---
                _build_profile_section(config),
                Divider(),

                # --- HeyGen Connection ---
                _build_heygen_section(config),
                Divider(),

                # --- Figma ---
                _build_figma_section(config),
                Divider(),

                # --- Platforms ---
                _build_platforms_section(config),
                Divider(),

                # --- Module Toggles ---
                _build_modules_section(config),
                Divider(),

                # --- Quality Gates ---
                _build_quality_section(config),
            ],
        )

    return settings_panel


# =====================================================
# SECTION BUILDERS
# =====================================================

def _build_profile_section(config):
    """Profile: niche, audience, brand voice, language."""
    return Section(
        title="Profile",
        description="Your content niche and target audience",
        icon="user",
        children=[
            Form(
                id="profile_form",
                on_submit=Call(function="_save_profile"),
                children=[
                    Input(
                        name="niche",
                        label="Your Niche",
                        placeholder="e.g., Web hosting, SaaS, fitness coaching",
                        value=config.get("niche", ""),
                    ),
                    TextArea(
                        name="target_audience",
                        label="Target Audience",
                        placeholder="Describe your ideal viewer -- demographics, pain points, aspirations...",
                        value=config.get("target_audience", ""),
                        rows=3,
                    ),
                    TagInput(
                        name="brand_voice",
                        label="Brand Voice",
                        placeholder="Add voice keywords (e.g., confident, casual, data-driven)...",
                        value=config.get("brand_voice", []),
                    ),
                    Select(
                        name="language",
                        label="Content Language",
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
                    ),
                    Button(label="Save Profile", type="submit", variant="primary", icon="save"),
                ],
            ),
        ],
    )


def _build_heygen_section(config):
    """HeyGen: connection method, API key, status."""
    heygen_key = config.get("heygen_api_key", "")
    is_connected = bool(heygen_key)

    return Section(
        title="HeyGen",
        description="Video generation service connection",
        icon="video",
        children=[
            Row(children=[
                Badge(
                    text="Connected" if is_connected else "Not Connected",
                    color="green" if is_connected else "red",
                ),
                Text(text="API key is set" if is_connected else "Add your HeyGen API key to enable video generation"),
            ]),
            Form(
                id="heygen_form",
                on_submit=Call(function="_save_profile"),
                children=[
                    Select(
                        name="heygen_method",
                        label="Connection Method",
                        options=[
                            {"value": "api_key", "label": "API Key (direct)"},
                            {"value": "mcp", "label": "MCP Server (OAuth)"},
                        ],
                        value="api_key" if heygen_key else "mcp",
                    ),
                    Input(
                        name="heygen_api_key",
                        label="HeyGen API Key",
                        placeholder="Enter your HeyGen API key...",
                        value=heygen_key,
                        type="password",
                    ),
                    Button(label="Save HeyGen Settings", type="submit", variant="primary", icon="save"),
                ],
            ),
            Alert(
                type="info",
                message="HeyGen API key is used for avatar video generation. Get yours at app.heygen.com/settings.",
            ),
        ],
    )


def _build_figma_section(config):
    """Figma: token, file key."""
    figma_token = config.get("figma_token", "")
    figma_file_key = config.get("figma_file_key", "")
    is_connected = bool(figma_token)

    return Section(
        title="Figma",
        description="Design asset integration",
        icon="figma",
        children=[
            Row(children=[
                Badge(
                    text="Connected" if is_connected else "Not Connected",
                    color="green" if is_connected else "gray",
                ),
                Text(text="Figma token is configured" if is_connected else "Add your Figma personal access token"),
            ]),
            Form(
                id="figma_form",
                on_submit=Call(function="_save_profile"),
                children=[
                    Input(
                        name="figma_token",
                        label="Figma Access Token",
                        placeholder="Enter your Figma personal access token...",
                        value=figma_token,
                        type="password",
                    ),
                    Input(
                        name="figma_file_key",
                        label="Default File Key",
                        placeholder="e.g., abc123xyz (from Figma URL)",
                        value=figma_file_key,
                    ),
                    Button(label="Save Figma Settings", type="submit", variant="primary", icon="save"),
                ],
            ),
        ],
    )


def _build_platforms_section(config):
    """Social platforms: YouTube, TikTok, Instagram, LinkedIn."""
    platforms_cfg = config.get("platforms", {})

    platform_defs = [
        ("youtube", "YouTube", "youtube"),
        ("tiktok", "TikTok", "music"),
        ("instagram", "Instagram", "instagram"),
        ("linkedin", "LinkedIn", "linkedin"),
    ]

    platform_forms = []
    for platform_id, platform_name, icon_name in platform_defs:
        pcfg = platforms_cfg.get(platform_id, {})
        is_enabled = pcfg.get("enabled", False)
        has_key = bool(pcfg.get("api_key", ""))

        platform_forms.append(
            Card(
                title=platform_name,
                children=[
                    Row(children=[
                        Icon(name=icon_name, size=20),
                        Badge(
                            text="Active" if is_enabled and has_key else "Inactive",
                            color="green" if is_enabled and has_key else "gray",
                        ),
                    ]),
                    Toggle(
                        name=f"platform_{platform_id}_enabled",
                        label="Enable",
                        value=is_enabled,
                    ),
                    Input(
                        name=f"platform_{platform_id}_api_key",
                        label="API Key",
                        placeholder=f"Enter {platform_name} API key...",
                        value=pcfg.get("api_key", ""),
                        type="password",
                    ),
                ],
            )
        )

    return Section(
        title="Platforms",
        description="Connect your social media accounts for publishing",
        icon="share-2",
        children=[
            Stack(children=platform_forms),
            Divider(),
            Alert(
                type="info",
                message="API keys are stored securely in your personal token wallet. Never shared with other users or extensions.",
            ),
            FileUpload(
                name="credentials_file",
                label="Or upload a credentials JSON file",
                accept=".json",
                on_upload=Call(function="_import_credentials"),
            ),
        ],
    )


def _build_modules_section(config):
    """Module toggles -- enable/disable individual modules."""
    modules_cfg = config.get("modules", {})

    module_cards = []
    for mod_id, mod_info in ALL_MODULE_NAMES.items():
        is_enabled = modules_cfg.get(mod_id, True)
        module_cards.append(
            Card(
                title=mod_info["label"],
                children=[
                    Row(children=[
                        Icon(name=mod_info["icon"], size=16),
                        Text(text=mod_info["desc"]),
                    ]),
                    Toggle(
                        name=f"module_{mod_id}",
                        label="Enabled",
                        value=is_enabled,
                    ),
                ],
            )
        )

    return Section(
        title="Modules",
        description="Enable or disable individual modules to customize your workflow",
        icon="puzzle",
        children=[
            Alert(
                type="info",
                message=f"{sum(1 for m in modules_cfg.values() if m)} of {len(ALL_MODULE_NAMES)} modules active",
            ),
            Grid(
                columns=2,
                gap=12,
                children=module_cards,
            ),
        ],
    )


def _build_quality_section(config):
    """Quality gates -- PCM min types, title length, hook timing."""
    quality = config.get("quality", {})

    return Section(
        title="Quality Gates",
        description="Set minimum quality thresholds for generated content",
        icon="shield-check",
        children=[
            Form(
                id="quality_form",
                on_submit=Call(function="_save_quality_settings"),
                children=[
                    Row(children=[
                        Column(children=[
                            Select(
                                name="pcm_min_types",
                                label="Min PCM Types per Script",
                                options=[
                                    {"value": "2", "label": "2 -- Lenient"},
                                    {"value": "3", "label": "3 -- Recommended"},
                                    {"value": "4", "label": "4 -- Strict"},
                                    {"value": "5", "label": "5 -- Very Strict"},
                                    {"value": "6", "label": "6 -- All Types"},
                                ],
                                value=str(quality.get("pcm_min_types", 3)),
                            ),
                        ], width="50%"),
                        Column(children=[
                            Input(
                                name="title_max_chars",
                                label="Max Title Length (chars)",
                                value=str(quality.get("title_max_chars", 55)),
                            ),
                        ], width="50%"),
                    ]),
                    Row(children=[
                        Column(children=[
                            Input(
                                name="hook_max_seconds",
                                label="Max Hook Duration (seconds)",
                                value=str(quality.get("hook_max_seconds", 3)),
                            ),
                        ], width="50%"),
                        Column(children=[
                            Input(
                                name="thumbnail_max_words",
                                label="Max Thumbnail Words",
                                value=str(quality.get("thumbnail_max_words", 4)),
                            ),
                        ], width="50%"),
                    ]),
                    Row(children=[
                        Column(children=[
                            Input(
                                name="min_word_count",
                                label="Min Script Word Count",
                                value=str(config.get("content", {}).get("min_word_count", 150)),
                            ),
                        ], width="50%"),
                        Column(children=[
                            Input(
                                name="max_hashtags",
                                label="Max Hashtags per Post",
                                value=str(config.get("content", {}).get("max_hashtags", 4)),
                            ),
                        ], width="50%"),
                    ]),
                    Button(label="Save Quality Gates", type="submit", variant="primary", icon="save"),
                ],
            ),
        ],
    )
