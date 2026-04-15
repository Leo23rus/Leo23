"""
Модуль диалоговых окон
"""
import tkinter as tk
from tkinter import ttk, Text, Scrollbar, messagebox, simpledialog
from typing import Optional


class Dialogs:
    """Управляет диалоговыми окнами приложения"""
    
    @staticmethod
    def show_add_from_text(parent) -> Optional[str]:
        """Показывает диалог добавления XML из текста"""
        dialog = tk.Toplevel(parent)
        dialog.title("Добавить XML из текста")
        dialog.geometry("600x400")
        dialog.transient(parent)
        dialog.grab_set()
        
        result = {"xml": None}
        
        tk.Label(
            dialog,
            text="Введите XML для вставки:",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=5, anchor=tk.W, padx=10)
        
        # Текстовое поле
        text_frame = tk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        text_widget = Text(text_frame, wrap=tk.NONE, font=("Consolas", 10))
        v_scroll = Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        h_scroll = Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
        
        text_widget.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Пример
        example = """<calculatedField>
    <dataPath>ПримерПоле</dataPath>
    <expression>Сумма(Поле)</expression>
</calculatedField>"""
        text_widget.insert(tk.END, example)
        
        def on_ok():
            xml_text = text_widget.get("1.0", tk.END).strip()
            if not xml_text:
                messagebox.showwarning("Предупреждение", "Введите XML текст")
                return
            result["xml"] = xml_text
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="✅ Добавить",
            command=on_ok,
            bg="#90EE90",
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="❌ Отмена",
            command=dialog.destroy,
            bg="#FFB6C1",
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        parent.wait_window(dialog)
        return result["xml"]
    
    @staticmethod
    def show_master_1c(parent) -> Optional[dict]:
        """Показывает мастер создания элементов 1С"""
        dialog = tk.Toplevel(parent)
        dialog.title("Мастер 1С - Создание элемента")
        dialog.geometry("500x400")
        dialog.transient(parent)
        dialog.grab_set()
        
        result = {"type": None, "data": {}}
        
        tk.Label(
            dialog,
            text="Выберите тип элемента:",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=10)
        
        element_types = [
            ("calculatedField", "Вычисляемое поле"),
            ("field", "Поле набора данных"),
            ("parameter", "Параметр"),
            ("resource", "Ресурс"),
            ("totalField", "Итоговое поле"),
            ("filter", "Фильтр"),
        ]
        
        selected_type = tk.StringVar(value=element_types[0][0])
        
        for type_id, type_name in element_types:
            tk.Radiobutton(
                dialog,
                text=type_name,
                variable=selected_type,
                value=type_id
            ).pack(anchor=tk.W, padx=20)
        
        tk.Label(
            dialog,
            text="Имя (dataPath):",
            font=("Segoe UI", 9)
        ).pack(pady=(10, 0))
        
        name_entry = tk.Entry(dialog, width=40)
        name_entry.pack()
        
        tk.Label(
            dialog,
            text="Заголовок:",
            font=("Segoe UI", 9)
        ).pack(pady=(10, 0))
        
        title_entry = tk.Entry(dialog, width=40)
        title_entry.pack()
        
        def on_ok():
            result["type"] = selected_type.get()
            result["data"]["name"] = name_entry.get().strip()
            result["data"]["title"] = title_entry.get().strip()
            
            if not result["data"]["name"]:
                messagebox.showwarning("Предупреждение", "Введите имя элемента")
                return
            
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame,
            text="✅ Создать",
            command=on_ok,
            bg="#90EE90",
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="❌ Отмена",
            command=dialog.destroy,
            bg="#FFB6C1",
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        parent.wait_window(dialog)
        return result if result["type"] else None
