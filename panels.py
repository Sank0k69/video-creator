"""
Panels registration — root level module like Mail Client pattern.
"""
from app_ext import ext
from ui.dashboard import register_dashboard
from ui.sidebar import register_sidebar

register_sidebar(ext)
register_dashboard(ext)
