"""
Модуль панели деталей и редактирования
"""
import tkinter as tk
from tkinter import ttk, Text, Scrollbar, messagebox
from typing import Optional
import xml.etree.ElementTree as ET
from utils.helpers import clean_tag, format_xml_pretty


class DetailsPanel:
    """Правая панель с деталями элемента и редактором"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.current_element: Optional[ET.Element] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Создает интерфейс панели"""
        # Заголовок
        header_frame = tk.Frame(self.parent_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(
            header_frame, 
            text="Детали элемента", 
            font=("Segoe UI", 12, "bold")
        ).pack(side=tk.LEFT)
        
        self.path_label = tk.Label(
            header_frame, 
            text="", 
            font=("Consolas", 8),
            fg="#666666"
        )
        self.path_label.pack(side=tk.RIGHT, padx=5)
        
        # Панель с кнопками
        btn_frame = tk.Frame(self.parent_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.edit_btn = tk.Button(
            btn_frame,
            text="✏️ Редактировать",
            command=self.open_editor,
            bg="#E0E0E0",
            activebackground="#D0D0D0"
        )
        self.edit_btn.pack(side=tk.LEFT, padx=2)
        
        # Текстовая область для отображения XML
        text_frame = tk.Frame(self.parent_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text_widget = Text(
            text_frame,
            wrap=tk.NONE,
            font=("Consolas", 10),
            bg="#FFFFFF",
            fg="#000000",
            state=tk.DISABLED
        )
        
        v_scroll = Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        h_scroll = Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.text_widget.xview)
        
        self.text_widget.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_display(self, element: Optional[ET.Element], path: list = None):
        """Обновляет отображение элемента"""
        self.current_element = element
        
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        
        if element is None:
            self.text_widget.insert(tk.END, "Элемент не выбран")
            self.path_label.config(text="")
        else:
            # Отображаем полный XML элемента
            try:
                xml_str = format_xml_pretty(element)
                self.text_widget.insert(tk.END, xml_str)
            except Exception as e:
                self.text_widget.insert(tk.END, f"Ошибка отображения: {e}")
            
            # Обновляем путь
            if path:
                path_str = " / ".join(path)
                self.path_label.config(text=path_str)
            else:
                self.path_label.config(text=clean_tag(element.tag))
        
        self.text_widget.config(state=tk.DISABLED)
    
    def open_editor(self):
        """Открывает окно редактора XML"""
        if self.current_element is None:
            messagebox.showwarning("Предупреждение", "Выберите элемент для редактирования")
            return
        
        editor_window = tk.Toplevel(self.parent_frame)
        editor_window.title(f"Редактировать: {clean_tag(self.current_element.tag)}")
        editor_window.geometry("700x500")
        editor_window.transient(self.parent_frame)
        editor_window.grab_set()
        
        # Заголовок
        tk.Label(
            editor_window,
            text=f"Редактирование: {clean_tag(self.current_element.tag)}",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor=tk.W, padx=10, pady=10)
        
        # Текстовое поле
        text_frame = tk.Frame(editor_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        edit_widget = Text(
            text_frame,
            wrap=tk.NONE,
            font=("Consolas", 10),
            undo=True
        )
        
        v_scroll = Scrollbar(text_frame, orient=tk.VERTICAL, command=edit_widget.yview)
        h_scroll = Scrollbar(text_frame, orient=tk.HORIZONTAL, command=edit_widget.xview)
        
        edit_widget.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        edit_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Вставляем текущий XML
        try:
            current_xml = format_xml_pretty(self.current_element)
            edit_widget.insert(tk.END, current_xml)
        except Exception as e:
            edit_widget.insert(tk.END, f"Ошибка загрузки: {e}")
        
        # Кнопки
        btn_frame = tk.Frame(editor_window)
        btn_frame.pack(pady=10)
        
        def save_changes():
            new_xml = edit_widget.get("1.0", tk.END).strip()
            # Логика сохранения будет вызвана из главного окна
            editor_window.destroy()
            # Возвращаем новый XML через callback (будет реализовано в главном классе)
            if hasattr(self, 'on_save_callback'):
                self.on_save_callback(new_xml)
        
        tk.Button(
            btn_frame,
            text="✅ Сохранить",
            command=save_changes,
            bg="#90EE90",
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="❌ Отмена",
            command=editor_window.destroy,
            bg="#FFB6C1",
            width=12
        ).pack(side=tk.LEFT, padx=5)
