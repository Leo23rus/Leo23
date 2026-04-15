"""
Стили и настройки интерфейса
"""

# Цветовая схема (светлая тема по умолчанию)
COLORS = {
    'bg_main': '#FFFFFF',
    'bg_panel': '#F5F5F5',
    'bg_tree': '#FFFFFF',
    'bg_selected': '#0078D7',
    'fg_text': '#000000',
    'fg_selected': '#FFFFFF',
    'border': '#CCCCCC',
    'highlight': '#E5F3FF',
    'status_bar': '#ECECEC',
    'toolbar': '#F0F0F0',
}

# Шрифты
FONTS = {
    'default': ('Segoe UI', 10),
    'bold': ('Segoe UI', 10, 'bold'),
    'tree': ('Consolas', 9),
    'code': ('Consolas', 10),
    'title': ('Segoe UI', 12, 'bold'),
}

# Настройки TreeView
TREE_CONFIG = {
    'show_names': True,
    'show_attributes': True,
    'show_text_preview': True,
    'max_text_length': 80,
}
