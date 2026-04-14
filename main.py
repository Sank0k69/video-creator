"""
Video Creator — Imperal Cloud Extension
========================================
AI-powered video content creation agent based on Creator Monetize methodology.

Architecture:
- 10 independent modules (microservices pattern)
- Modules don't know about each other
- Pipelines orchestrate modules for complex workflows
- Knowledge stored as JSON data, not hardcoded
- Every module is toggleable per-user
"""
from __future__ import annotations

from imperal_sdk import ChatExtension, Extension
from imperal_sdk.types import ActionResult

from config.defaults import DEFAULTS
from modules import ALL_MODULES
from pipelines import PipelineRegistry
from ui import register_dashboard, register_settings, register_calendar, register_sidebar

# --- Extension setup ---

ext = Extension("video-creator", version="2.0.0", config_defaults=DEFAULTS)

chat = ChatExtension(
    ext,
    tool_name="video_creator",
    description="AI video content creation agent powered by Creator Monetize methodology. "
                "Generates ideas, scripts, hooks, captions, CTAs, VSLs, email sequences, "
                "sales scripts, offer creation, funnel copy, and launch plans.",
    system_prompt="You are Video Creator — an expert AI video content strategist trained on "
                  "the full Creator Monetize methodology. You help creators plan, script, "
                  "and optimize video content for YouTube, Instagram, TikTok, and LinkedIn. "
                  "Use the available functions to generate content. Always be specific, "
                  "actionable, and data-driven. Apply PCM personality types and psychological "
                  "hooks in all content.",
    max_rounds=15,
)

# Fix scopes — ChatExtension defaults to ["*"] but deploy requires dot.notation
ext._tools["video_creator"].scopes = [
    "store.read", "store.write", "ai.complete", "config.read",
    "config.write", "notify.push", "storage.read", "storage.write",
]

# --- DUI Panels ---
# Left slot: navigation sidebar
# Right slot: dashboard workspace + settings (contextual)

register_sidebar(ext)      # slot="left"  — navigation hub
register_dashboard(ext)    # slot="right" — main workspace
register_settings(ext)     # slot="right" — settings (navigated from sidebar)
register_calendar(ext)     # widget       — content calendar


# --- Module registry ---

_modules: dict = {}
_pipelines: PipelineRegistry | None = None


def _get_module(ctx, name: str):
    """Get or create a module instance. Lazy initialization."""
    if name not in _modules:
        if name not in ALL_MODULES:
            return None
        _modules[name] = ALL_MODULES[name](ctx)
    return _modules[name]


def _get_pipelines(ctx) -> PipelineRegistry:
    global _pipelines
    if _pipelines is None:
        _pipelines = PipelineRegistry(ctx, _get_module)
    return _pipelines


# --- Lifecycle ---

@ext.on_install
async def on_install(ctx):
    """Welcome message on first install."""
    return ActionResult.success(summary="Video Creator installed. Configure your niche and platforms in Settings.")


@ext.on_upgrade("1.0.0")
async def on_upgrade_1_0(ctx):
    """Migration for v1.0.0."""
    return ActionResult.success(summary="Upgraded to v1.0.0")


@ext.health_check
async def health(ctx):
    """Health check — verify modules and knowledge base."""
    enabled = [name for name, cls in ALL_MODULES.items() if _get_module(ctx, name).is_enabled()]
    return ActionResult.success(data={
        "version": "2.0.0",
        "modules_enabled": enabled,
        "modules_total": len(ALL_MODULES),
    })


# =====================================================
# CHAT FUNCTIONS — one per module capability
# =====================================================

# --- Ideation ---

@chat.function("generate_ideas", description="Generate video content ideas using Perfect Idea Zone methodology", action_type="read")
async def generate_ideas(ctx, topic: str = "", count: int = 10, method: str = "mixed") -> ActionResult:
    """
    Generate video content ideas using Perfect Idea Zone methodology.

    Args:
        topic: Starting topic or niche area (optional, uses configured niche)
        count: Number of ideas to generate (default 10)
        method: Ideation method — 'commence', 'snatch_twirl', 'audience', 'mixed'
    """
    mod = _get_module(ctx, "ideation")
    result = await mod.execute("generate", {"topic": topic, "count": count, "method": method})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


@chat.function("classify_idea", description="Classify an idea as perfect or sub-optimal using the Perfect Idea Zone framework", action_type="read")
async def classify_idea(ctx, idea: str) -> ActionResult:
    """Classify an idea as 'perfect' or 'sub-optimal' using the Perfect Idea Zone framework."""
    mod = _get_module(ctx, "ideation")
    result = await mod.execute("classify", {"idea": idea})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- Framing ---

@chat.function("frame_video", description="Transform a raw idea into a directed video concept using 4-step framing", action_type="read")
async def frame_video(ctx, idea: str, avatar: str = "") -> ActionResult:
    """
    Transform a raw idea into a directed video concept using 4-step framing.
    Steps: Video Framing → Packaging Framing → Directional Framing → Grand Payoff.
    """
    mod = _get_module(ctx, "framing")
    result = await mod.execute("frame", {"idea": idea, "avatar": avatar})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- Packaging ---

@chat.function("package_video", description="Create title and thumbnail strategy using Want vs Need framework", action_type="read")
async def package_video(ctx, concept: str, style: str = "niched") -> ActionResult:
    """
    Create title + thumbnail strategy using Want vs Need framework.

    Args:
        concept: The framed video concept
        style: 'niched' (search-optimized) or 'shareability' (trend-riding)
    """
    mod = _get_module(ctx, "packaging")
    result = await mod.execute("package", {"concept": concept, "style": style})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- Hooks ---

@chat.function("generate_hooks", description="Generate video hooks from 7 psychological trigger types", action_type="read")
async def generate_hooks(ctx, topic: str, hook_types: list[str] | None = None, count: int = 5) -> ActionResult:
    """
    Generate video hooks from 7 psychological trigger types.
    Types: desirable, social_proof, controversial, secret, negative, quick_solution, lesson.
    """
    mod = _get_module(ctx, "hooks")
    result = await mod.execute("generate", {"topic": topic, "types": hook_types, "count": count})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- Scripting ---

@chat.function("write_script", description="Write a complete video script using Hook-Body-CTA architecture", action_type="write", event="script.created")
async def write_script(ctx, topic: str, hook: str = "", tier: int = 1,
                       format_type: str = "viral", duration: str = "short") -> ActionResult:
    """
    Write a complete video script using Hook-Body-CTA architecture.

    Args:
        topic: What the video is about
        hook: Pre-written hook (optional, generates one if empty)
        tier: Script complexity — 1 (simple) or 2 (setup/stress/payoff)
        format_type: 'viral', 'pitch', or 'false_statement'
        duration: 'short' (60s), 'medium' (3-5min), 'long' (10+min)
    """
    mod = _get_module(ctx, "scripting")
    result = await mod.execute("write", {
        "topic": topic, "hook": hook, "tier": tier,
        "format_type": format_type, "duration": duration,
    })
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- PCM Analysis ---

@chat.function("analyze_pcm", description="Analyze a script for PCM personality type coverage and return coverage score with suggestions", action_type="read")
async def analyze_pcm(ctx, script: str) -> ActionResult:
    """Analyze a script for PCM personality type coverage (6 types). Returns coverage score and suggestions."""
    mod = _get_module(ctx, "pcm")
    result = await mod.execute("analyze", {"script": script})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


@chat.function("enhance_pcm", description="Rewrite a script to cover missing PCM personality types", action_type="read")
async def enhance_pcm(ctx, script: str, target_types: list[str] | None = None) -> ActionResult:
    """Rewrite a script to cover missing PCM personality types."""
    mod = _get_module(ctx, "pcm")
    result = await mod.execute("enhance", {"script": script, "target_types": target_types})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- Captions ---

@chat.function("generate_captions", description="Generate post captions using curiosity loops and personality targeting", action_type="read")
async def generate_captions(ctx, topic: str, style: str = "curiosity", count: int = 5) -> ActionResult:
    """
    Generate post captions.
    Styles: 'curiosity' (curiosity loops), 'pcm' (personality-targeted), 'mixed'.
    """
    mod = _get_module(ctx, "captions")
    result = await mod.execute("generate", {"topic": topic, "style": style, "count": count})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- CTA ---

@chat.function("generate_cta", description="Generate call-to-action for video content", action_type="read")
async def generate_cta(ctx, context: str, goal: str = "engage", platform: str = "youtube") -> ActionResult:
    """
    Generate call-to-action for video content.
    Goals: 'engage' (like/comment/sub), 'redirect' (to another video), 'link' (description link), 'manychat' (comment trigger).
    """
    mod = _get_module(ctx, "cta")
    result = await mod.execute("generate", {"context": context, "goal": goal, "platform": platform})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- Publishing ---

@chat.function("pre_publish_check", description="Run 6-step pre-publishing checklist on content before posting", action_type="read")
async def pre_publish_check(ctx, content: dict) -> ActionResult:
    """Run 6-step pre-publishing checklist on content before posting."""
    mod = _get_module(ctx, "publishing")
    result = await mod.execute("check", {"content": content})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- Iteration ---

@chat.function("track_performance", description="Record performance metrics for published content", action_type="write", event="content.tracked")
async def track_performance(ctx, content_id: str, metrics: dict) -> ActionResult:
    """Record performance metrics for published content (views, retention, CTR, etc.)."""
    mod = _get_module(ctx, "iteration")
    result = await mod.execute("track", {"content_id": content_id, "metrics": metrics})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


@chat.function("analyze_performance", description="Analyze content performance and suggest iterations", action_type="read")
async def analyze_performance(ctx, content_id: str = "", period: str = "week") -> ActionResult:
    """Analyze content performance and suggest iterations."""
    mod = _get_module(ctx, "iteration")
    result = await mod.execute("analyze", {"content_id": content_id, "period": period})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# =====================================================
# PIPELINES — complex multi-module workflows
# =====================================================

@chat.function("create_video", description="Full video creation pipeline from ideation to publish checklist", action_type="write", event="video.created")
async def create_video(ctx, topic: str, tier: int = 1, format_type: str = "viral") -> ActionResult:
    """
    Full video creation pipeline: Ideation → Framing → Packaging → Hooks → Script → PCM → Captions → CTA → Checklist.
    """
    registry = _get_pipelines(ctx)
    pipeline = registry.get("full_video")
    result = await pipeline.run({"topic": topic, "tier": tier, "format_type": format_type})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


@chat.function("quick_script", description="Quick pipeline: Topic to Hook to Script to CTA", action_type="write", event="script.created")
async def quick_script(ctx, topic: str, format_type: str = "viral") -> ActionResult:
    """Quick pipeline: Topic → Hook → Script → CTA. Skip framing/packaging for speed."""
    registry = _get_pipelines(ctx)
    pipeline = registry.get("quick_script")
    result = await pipeline.run({"topic": topic, "format_type": format_type})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


@chat.function("batch_content", description="Batch create scripts for multiple topics at once", action_type="write", event="batch.created")
async def batch_content(ctx, topics: list[str], format_type: str = "viral") -> ActionResult:
    """Batch create scripts for multiple topics at once."""
    registry = _get_pipelines(ctx)
    pipeline = registry.get("batch_content")
    result = await pipeline.run({"topics": topics, "format_type": format_type})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# =====================================================
# NEW MODULES — Market Research, Funnels, Email, Sales, Launch
# =====================================================

# --- Market Research ---

@chat.function("gsb_analyze", description="Run Gold Silver Bronze competitive content analysis for your niche", action_type="read")
async def gsb_analyze(ctx, niche: str = "", platform: str = "youtube") -> ActionResult:
    """Run Gold Silver Bronze competitive content analysis for your niche."""
    mod = _get_module(ctx, "market_research")
    result = await mod.execute("gsb_analyze", {"niche": niche, "platform": platform})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("build_avatar", description="Build a detailed client avatar using 18-question framework", action_type="write", event="avatar.created")
async def build_avatar(ctx, niche: str = "", product: str = "") -> ActionResult:
    """Build a detailed client avatar using 18-question framework."""
    mod = _get_module(ctx, "market_research")
    result = await mod.execute("build_avatar", {"niche": niche, "product": product})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("classify_trajectory", description="Classify creator into 1 of 8 pathways and get 28-day roadmap", action_type="read")
async def classify_trajectory(ctx, followers_count: int = 0, platform: str = "youtube", has_offer: bool = False, niche_type: str = "high") -> ActionResult:
    """Classify creator into 1 of 8 pathways and get 28-day roadmap."""
    mod = _get_module(ctx, "market_research")
    result = await mod.execute("classify_trajectory", {"followers_count": followers_count, "platform": platform, "has_offer": has_offer, "niche_type": niche_type})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

# --- Funnel Copy ---

@chat.function("write_vsl", description="Write a complete VSL script following the 8-section structure", action_type="write", event="vsl.created")
async def write_vsl(ctx, funnel_type: str = "call", offer: str = "", audience: str = "", tone: str = "casual but confident") -> ActionResult:
    """Write a complete VSL script following the 8-section structure."""
    mod = _get_module(ctx, "funnel_copy")
    result = await mod.execute("write_vsl", {"funnel_type": funnel_type, "offer": offer, "audience": audience, "tone": tone})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("page_copy", description="Generate funnel page copy for opt-in, booking, sales, or post-booking pages", action_type="write", event="page.created")
async def page_copy(ctx, page_type: str = "opt_in", offer: str = "", headline: str = "") -> ActionResult:
    """Generate funnel page copy (opt-in, booking, sales, post-booking)."""
    mod = _get_module(ctx, "funnel_copy")
    result = await mod.execute("page_copy", {"page_type": page_type, "offer": offer, "headline": headline})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("presentation_outline", description="Generate webinar presentation outline using 26-step structure", action_type="write", event="presentation.created")
async def presentation_outline(ctx, topic: str = "", offer: str = "") -> ActionResult:
    """Generate webinar presentation outline using 26-step structure."""
    mod = _get_module(ctx, "funnel_copy")
    result = await mod.execute("presentation_outline", {"topic": topic, "offer": offer})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

# --- Email Sequences ---

@chat.function("promo_sequence", description="Generate 6-email promotional sequence with urgency cascade", action_type="write", event="email.created")
async def promo_sequence(ctx, product_name: str = "", offer: str = "", deadline: str = "") -> ActionResult:
    """Generate 6-email promotional sequence with urgency cascade."""
    mod = _get_module(ctx, "email_sequences")
    result = await mod.execute("promo_sequence", {"product_name": product_name, "offer": offer, "deadline": deadline})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("nurture_sequence", description="Generate 6-email nurture sequence for value video funnel", action_type="write", event="email.created")
async def nurture_sequence(ctx, product: str = "", dream_outcome: str = "") -> ActionResult:
    """Generate 6-email nurture sequence for value video funnel."""
    mod = _get_module(ctx, "email_sequences")
    result = await mod.execute("nurture_sequence", {"product": product, "dream_outcome": dream_outcome})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("webinar_sequence", description="Generate webinar reminder sequence for email, telegram, and sms", action_type="write", event="email.created")
async def webinar_sequence(ctx, webinar_title: str = "", date: str = "", link: str = "", channels: list[str] | None = None) -> ActionResult:
    """Generate webinar reminder sequence (email + telegram + sms)."""
    mod = _get_module(ctx, "email_sequences")
    result = await mod.execute("webinar_sequence", {"webinar_title": webinar_title, "date": date, "link": link, "channels": channels or ["email"]})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("reactivate_list", description="Generate email list reactivation email for dormant subscribers", action_type="write", event="email.created")
async def reactivate_list(ctx, brand: str = "", niche: str = "", time_away: str = "") -> ActionResult:
    """Generate email list reactivation email for dormant subscribers."""
    mod = _get_module(ctx, "email_sequences")
    result = await mod.execute("reactivation", {"brand": brand, "niche": niche, "time_away": time_away})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

# --- Sales ---

@chat.function("sales_script", description="Generate customized 12-stage sales call script", action_type="write", event="script.created")
async def sales_script(ctx, product: str = "", price: str = "", niche: str = "") -> ActionResult:
    """Generate customized 12-stage sales call script."""
    mod = _get_module(ctx, "sales")
    result = await mod.execute("sales_script", {"product": product, "price": price, "niche": niche})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("handle_objection", description="Handle a sales objection using DECPC formula", action_type="read")
async def handle_objection(ctx, objection: str = "", context: str = "") -> ActionResult:
    """Handle a sales objection using DECPC formula."""
    mod = _get_module(ctx, "sales")
    result = await mod.execute("handle_objection", {"objection": objection, "context": context})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("create_offer", description="Build complete offer using 8-step Elixir Genesis methodology", action_type="write", event="offer.created")
async def create_offer(ctx, dream_outcome: str = "", target_audience: str = "", product_type: str = "course") -> ActionResult:
    """Build complete offer using 8-step Elixir Genesis methodology."""
    mod = _get_module(ctx, "sales")
    result = await mod.execute("create_offer", {"dream_outcome": dream_outcome, "target_audience": target_audience, "product_type": product_type})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

# --- Launch ---

@chat.function("pre_launch_plan", description="Generate pre-launch plan with timeline, tasks, and discount strategy", action_type="write", event="launch.planned")
async def pre_launch_plan(ctx, product: str = "", launch_date: str = "", launch_type: str = "loud") -> ActionResult:
    """Generate pre-launch plan with timeline, tasks, and discount strategy."""
    mod = _get_module(ctx, "launch")
    result = await mod.execute("pre_launch_plan", {"product": product, "launch_date": launch_date, "launch_type": launch_type})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("launch_roadmap", description="Generate full 28-day launch roadmap based on trajectory pathway", action_type="write", event="launch.planned")
async def launch_roadmap(ctx, pathway_number: int = 1, niche: str = "", product: str = "") -> ActionResult:
    """Generate full 28-day launch roadmap based on trajectory pathway."""
    mod = _get_module(ctx, "launch")
    result = await mod.execute("launch_28_day", {"pathway_number": pathway_number, "niche": niche, "product": product})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# --- Video Production (HeyGen) ---

@chat.function("create_video_heygen", description="Create an actual video from a script using HeyGen avatar", action_type="write", event="video.rendered")
async def create_video_heygen(ctx, script: str = "", avatar_id: str = "", voice_id: str = "", dimension: str = "portrait") -> ActionResult:
    """Create a real video from script via HeyGen. Auto-selects avatar and voice if not specified."""
    mod = _get_module(ctx, "video_production")
    # First clean the script for voice synthesis
    clean = await mod.execute("clean_script", {"script": script})
    clean_text = clean.get("data", {}).get("clean_script", script)
    result = await mod.execute("create_video", {"script": clean_text, "avatar_id": avatar_id, "voice_id": voice_id, "dimension": dimension})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("video_status", description="Check HeyGen video generation status and get download URL", action_type="read")
async def video_status(ctx, video_id: str = "") -> ActionResult:
    """Check video rendering status. Returns download URL when complete."""
    mod = _get_module(ctx, "video_production")
    result = await mod.execute("check_status", {"video_id": video_id})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("list_avatars", description="List available HeyGen avatars for video creation", action_type="read")
async def list_avatars(ctx, limit: int = 20) -> ActionResult:
    """List available HeyGen avatars."""
    mod = _get_module(ctx, "video_production")
    result = await mod.execute("list_avatars", {"limit": limit})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))

@chat.function("list_voices", description="List available HeyGen voices filtered by language", action_type="read")
async def list_voices(ctx, language: str = "en") -> ActionResult:
    """List available HeyGen voices for a given language."""
    mod = _get_module(ctx, "video_production")
    result = await mod.execute("list_voices", {"language": language})
    return ActionResult.success(data=result["data"], summary=result.get("summary", ""))


# =====================================================
# EXPOSED API — for Daria and other extensions (IPC)
# =====================================================

@ext.expose("generate_ideas")
async def api_generate_ideas(ctx, topic: str = "", count: int = 5) -> ActionResult:
    """IPC: Generate video ideas. Callable by Daria and other extensions."""
    mod = _get_module(ctx, "ideation")
    result = await mod.execute("generate", {"topic": topic, "count": count, "method": "mixed"})
    return ActionResult.success(data=result["data"])


@ext.expose("write_script")
async def api_write_script(ctx, topic: str, tier: int = 1, format_type: str = "viral") -> ActionResult:
    """IPC: Write a video script. Callable by Daria and other extensions."""
    mod = _get_module(ctx, "scripting")
    result = await mod.execute("write", {
        "topic": topic, "tier": tier, "format_type": format_type, "duration": "short",
    })
    return ActionResult.success(data=result["data"])


@ext.expose("full_pipeline")
async def api_full_pipeline(ctx, topic: str, tier: int = 1) -> ActionResult:
    """IPC: Run full video creation pipeline. Callable by Daria."""
    registry = _get_pipelines(ctx)
    pipeline = registry.get("full_video")
    result = await pipeline.run({"topic": topic, "tier": tier, "format_type": "viral"})
    return ActionResult.success(data=result["data"])


# --- New IPC Methods ---

@ext.expose("write_vsl")
async def api_write_vsl(ctx, funnel_type: str = "call", offer: str = "", audience: str = "") -> ActionResult:
    """IPC: Write a VSL script. Callable by other extensions."""
    mod = _get_module(ctx, "funnel_copy")
    result = await mod.execute("write_vsl", {"funnel_type": funnel_type, "offer": offer, "audience": audience, "tone": "casual but confident"})
    return ActionResult.success(data=result["data"])

@ext.expose("create_offer")
async def api_create_offer(ctx, dream_outcome: str = "", target_audience: str = "") -> ActionResult:
    """IPC: Create an offer using Elixir Genesis. Callable by other extensions."""
    mod = _get_module(ctx, "sales")
    result = await mod.execute("create_offer", {"dream_outcome": dream_outcome, "target_audience": target_audience, "product_type": "course"})
    return ActionResult.success(data=result["data"])

@ext.expose("promo_sequence")
async def api_promo_sequence(ctx, product_name: str = "", offer: str = "", deadline: str = "") -> ActionResult:
    """IPC: Generate promo email sequence. Callable by other extensions."""
    mod = _get_module(ctx, "email_sequences")
    result = await mod.execute("promo_sequence", {"product_name": product_name, "offer": offer, "deadline": deadline})
    return ActionResult.success(data=result["data"])


@ext.expose("create_video", action_type="write")
async def api_create_video(ctx, script: str = "", avatar_id: str = "", voice_id: str = "") -> ActionResult:
    """IPC: Create video from script via HeyGen. Callable by Daria."""
    mod = _get_module(ctx, "video_production")
    clean = await mod.execute("clean_script", {"script": script})
    clean_text = clean.get("data", {}).get("clean_script", script)
    result = await mod.execute("create_video", {"script": clean_text, "avatar_id": avatar_id, "voice_id": voice_id, "dimension": "portrait"})
    return ActionResult.success(data=result["data"])


# =====================================================
# SCHEDULED TASKS
# =====================================================

@ext.schedule("content_reminder", cron="0 9 * * *")
async def daily_content_reminder(ctx):
    """Daily reminder to create content. Checks pending ideas and suggests today's topic."""
    mod = _get_module(ctx, "ideation")
    ideas = await mod.load("ideas_bank", [])
    if ideas:
        top_idea = ideas[0]
        await ctx.notify.push(
            title="Time to create content",
            body=f"Top idea: {top_idea.get('title', 'Check your ideas bank')}",
        )
    return ActionResult.success(summary="Daily reminder sent")
