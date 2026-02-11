"""
AI Chat module for Pro features.
Provides dockable AI chat functionality with multiple tabs and streaming support.
"""

from .chat_dock import AIChatDock
from .chat_tab import ChatTabWidget
from .markdown_renderer import MarkdownRenderer, ChatMessageDisplay

__all__ = [
    'AIChatDock',
    'ChatTabWidget',
    'MarkdownRenderer',
    'ChatMessageDisplay',
]
