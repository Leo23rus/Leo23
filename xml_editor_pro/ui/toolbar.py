"""
Модуль панели инструментов и меню
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, Callable


class ToolbarManager:
    """Управляет верхней панелью инструментов"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.setup_ui()
    
    def setup_ui(self):
        """Создает интерфейс панели инструментов"""
        toolbar = tk.Frame(self.parent_frame, bg="#F0F0F0")
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопки
        buttons = [
            ("📂 Открыть", self.on_open),
            ("💾 Сохранить", self.on_save),
            ("💾 Как...", self.on_save_as),
            ("↻ Обновить", self.on_refresh),
        ]
        
        for text, command in buttons:
            btn = tk.Button(
                toolbar,
                text=text,
                command=command,
                bg="#FFFFFF",
                activebackground="#E0E0E0",
                relief=tk.RAISED,
                bd=1
            )
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Разделитель
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        # Кнопки перемещения
        move_buttons = [
            ("⬆️ Вверх", self.on_move_up),
            ("⬇️ Вниз", self.on_move_down),
        ]
        
        for text, command in move_buttons:
            btn = tk.Button(
                toolbar,
                text=text,
                command=command,
                bg="#FFFFFF",
                activebackground="#E0E0E0",
                relief=tk.RAISED,
                bd=1
            )
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Разделитель
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        # Поиск
        search_frame = tk.Frame(toolbar, bg="#F0F0F0")
        search_frame.pack(side=tk.RIGHT, padx=5)
        
        self.search_entry = tk.Entry(search_frame, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=2)
        self.search_entry.insert(0, "Поиск...")
        
        search_btn = tk.Button(
            search_frame,
            text="🔍 Найти",
            command=self.on_search,
            bg="#FFFFFF",
            activebackground="#E0E0E0",
            relief=tk.RAISED,
            bd=1
        )
        search_btn.pack(side=tk.LEFT, padx=2)
        
        reset_btn = tk.Button(
            search_frame,
            text="❌ Сброс",
            command=self.on_reset_search,
            bg="#FFFFFF",
            activebackground="#E0E0E0",
            relief=tk.RAISED,
            bd=1
        )
        reset_btn.pack(side=tk.LEFT, padx=2)
        
        # Мастер 1С
        master_btn = tk.Button(
            toolbar,
            text="➕ Мастер 1С",
            command=self.on_master_1c,
            bg="#90EE90",
            activebackground="#70C070",
            relief=tk.RAISED,
            bd=1
        )
        master_btn.pack(side=tk.LEFT, padx=10, pady=2)
        
        # Записать изменения
        commit_btn = tk.Button(
            toolbar,
            text="✅ Записать",
            command=self.on_commit,
            bg="#87CEEB",
            activebackground="#67A8C8",
            relief=tk.RAISED,
            bd=1
        )
        commit_btn.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Статус изменений
        self.status_label = tk.Label(
            toolbar,
            text="",
            bg="#F0F0F0",
            fg="#FF0000",
            font=("Segoe UI", 9, "bold")
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
    
    # Заглушки для методов (будут переопределены в главном классе)
    def on_open(self): pass
    def on_save(self): pass
    def on_save_as(self): pass
    def on_refresh(self): pass
    def on_move_up(self): pass
    def on_move_down(self): pass
    def on_search(self): pass
    def on_reset_search(self): pass
    def on_master_1c(self): pass
    def on_commit(self): pass
    
    def set_status(self, text: str):
        """Устанавливает статус изменений"""
        self.status_label.config(text=text)
    
    def get_search_text(self) -> str:
        """Получает текст поиска"""
        return self.search_entry.get()
    
    def clear_search(self):
        """Очищает поле поиска"""
        self.search_entry.delete(0, tk.END)
