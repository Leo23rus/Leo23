import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import xml.etree.ElementTree as ET
import os
from typing import Optional, Dict

# === Константы и Настройки ===
NS_1C = "{http://v8.1c.ru/8.1/data-composition-system/schema}"

ICONS = {
    "DataField": "📊",
    "ResourceField": "💰",
    "Parameter": "⚙️",
    "DataSet": "🗄️",
    "Condition": "❓",
    "Group": "📁",
    "Default": "📄"
}

COLORS = {
    "bg_dark": "#1e1e1e",
    "bg_panel": "#252526",
    "bg_input": "#3c3c3c",
    "fg_text": "#d4d4d4",
    "fg_accent": "#4ec9b0",
    "select": "#264f78"
}

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.widget.bind("<Enter>", self.showtip)
        self.widget.bind("<Leave>", self.hidetip)

    def showtip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Segoe UI", "10"))
        label.pack(ipadx=1)

    def hidetip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class XMLEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("1С XML Architect Pro")
        self.root.geometry("1200x800")
        
        # Состояние
        self.tree_data: Optional[ET.ElementTree] = None
        self.root_element: Optional[ET.Element] = None
        self.file_path: str = ""
        self.items_map: Dict[str, ET.Element] = {}
        self.parent_map: Dict[ET.Element, ET.Element] = {}
        self.unsaved_changes: bool = False
        
        self.setup_styles()
        self.create_main_layout()
        self.create_menu()
        self.create_toolbar()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.tree_view.bind("<<TreeviewSelect>>", self.on_selection_change)
        self.tree_view.bind("<Double-1>", self.on_double_click)
        self.tree_view.bind("<Button-3>", self.show_context_menu)
        
        self.update_title()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        self.root.configure(bg=COLORS["bg_dark"])
        
        style.configure("TFrame", background=COLORS["bg_dark"])
        style.configure("TLabel", background=COLORS["bg_dark"], foreground=COLORS["fg_text"], font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"), foreground=COLORS["fg_accent"])
        
        style.configure("TButton", background=COLORS["bg_panel"], foreground=COLORS["fg_text"], 
                        borderwidth=1, focusthickness=0, font=("Segoe UI", 10))
        style.map("TButton", background=[("active", COLORS["select"])])
        
        style.configure("Treeview", background=COLORS["bg_panel"], foreground=COLORS["fg_text"],
                        fieldbackground=COLORS["bg_panel"], borderwidth=0, font=("Consolas", 10))
        style.map("Treeview", background=[("selected", COLORS["select"])])
        
        style.configure("Treeview.Heading", background=COLORS["bg_panel"], foreground=COLORS["fg_accent"],
                        font=("Segoe UI", 10, "bold"))

    def create_main_layout(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая панель (Дерево)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        ttk.Label(left_frame, text="Структура документа", style="Header.TLabel").pack(anchor="w", pady=(0, 5))
        
        tree_container = ttk.Frame(left_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        self.tree_view = ttk.Treeview(tree_container, columns=("type", "name"), selectmode="extended")
        self.tree_view.heading("#0", text="Элемент")
        self.tree_view.heading("type", text="Тип")
        self.tree_view.heading("name", text="Имя/Путь")
        self.tree_view.column("#0", width=250)
        self.tree_view.column("type", width=100)
        self.tree_view.column("name", width=200)
        
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree_view.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree_view.xview)
        self.tree_view.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree_view.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Центральная панель (Свойства)
        center_frame = ttk.Frame(main_frame)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(center_frame, text="Свойства элемента", style="Header.TLabel").pack(anchor="w", pady=(0, 5))
        
        self.props_notebook = ttk.Notebook(center_frame)
        self.props_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка Атрибуты
        attr_frame = ttk.Frame(self.props_notebook)
        self.props_notebook.add(attr_frame, text="Атрибуты")
        
        self.attr_tree = ttk.Treeview(attr_frame, columns=("value",), selectmode="extended")
        self.attr_tree.heading("#0", text="Ключ")
        self.attr_tree.heading("value", text="Значение")
        self.attr_tree.column("#0", width=150)
        self.attr_tree.column("value", width=200)
        
        attr_vsb = ttk.Scrollbar(attr_frame, orient="vertical", command=self.attr_tree.yview)
        self.attr_tree.configure(yscrollcommand=attr_vsb.set)
        self.attr_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        attr_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        attr_btns = ttk.Frame(attr_frame)
        attr_btns.pack(fill=tk.X, pady=5)
        ttk.Button(attr_btns, text="+ Добавить", command=self.add_attribute).pack(side=tk.LEFT, padx=2)
        ttk.Button(attr_btns, text="✏️ Изменить", command=self.edit_attribute).pack(side=tk.LEFT, padx=2)
        ttk.Button(attr_btns, text="🗑️ Удалить", command=self.delete_attribute).pack(side=tk.LEFT, padx=2)
        
        # Вкладка Текст
        text_frame = ttk.Frame(self.props_notebook)
        self.props_notebook.add(text_frame, text="Текст / Значение")
        
        self.text_editor = tk.Text(text_frame, wrap=tk.NONE, bg=COLORS["bg_input"], fg=COLORS["fg_text"], 
                                   insertbackground=COLORS["fg_text"], font=("Consolas", 11), undo=True)
        text_vsb = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_editor.yview)
        text_hsb = ttk.Scrollbar(text_frame, orient="horizontal", command=self.text_editor.xview)
        self.text_editor.configure(yscrollcommand=text_vsb.set, xscrollcommand=text_hsb.set)
        
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        text_hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        ttk.Button(text_frame, text="Сохранить текст", command=self.save_text_content).pack(pady=5)
        
        # Правая панель (Инструменты)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_frame.config(width=250)
        right_frame.pack_propagate(False)
        
        ttk.Label(right_frame, text="Инструменты 1С", style="Header.TLabel").pack(anchor="w", pady=(0, 10))
        ttk.Label(right_frame, text="Добавить элемент:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        
        btn_field = ttk.Button(right_frame, text="📊 Поле данных", command=lambda: self.add_1c_element("DataField"))
        btn_field.pack(fill=tk.X, pady=2)
        ToolTip(btn_field, "Добавляет DataField")
        
        btn_res = ttk.Button(right_frame, text="💰 Поле ресурса", command=lambda: self.add_1c_element("ResourceField"))
        btn_res.pack(fill=tk.X, pady=2)
        ToolTip(btn_res, "Добавляет ResourceField")
        
        btn_param = ttk.Button(right_frame, text="⚙️ Параметр", command=lambda: self.add_1c_element("Parameter"))
        btn_param.pack(fill=tk.X, pady=2)
        ToolTip(btn_param, "Добавляет Parameter")
        
        ttk.Separator(right_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        ttk.Label(right_frame, text="Действия:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        ttk.Button(right_frame, text="📋 Копировать XPath", command=self.copy_xpath).pack(fill=tk.X, pady=2)
        ttk.Button(right_frame, text="🔍 Найти дубликаты", command=self.find_duplicates).pack(fill=tk.X, pady=2)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Открыть...", command=self.load_xml, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить", command=self.save_xml, accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить как...", command=self.save_as_xml)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.on_close)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Добавить потомка", command=self.add_child_simple)
        edit_menu.add_command(label="Удалить элемент", command=self.delete_element)

    def create_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(toolbar, text="📂 Открыть", command=self.load_xml).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="💾 Сохранить", command=self.save_xml).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        ttk.Button(toolbar, text="➕ Потомок", command=self.add_child_simple).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑️ Удалить", command=self.delete_element).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        ttk.Button(toolbar, text="🌲 Развернуть все", command=self.expand_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🌱 Свернуть все", command=self.collapse_all).pack(side=tk.LEFT, padx=2)
        
        self.status_var = tk.StringVar(value="Готов к работе")
        ttk.Label(toolbar, textvariable=self.status_var, anchor=tk.E).pack(side=tk.RIGHT, padx=10)

    # === Логика работы с XML ===
    
    def load_xml(self):
        file_path = filedialog.askopenfilename(title="Выберите XML файл", filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
        if not file_path:
            return
        
        try:
            self.tree_data = ET.parse(file_path)
            self.root_element = self.tree_data.getroot()
            self.file_path = file_path
            self.rebuild_parent_map()
            self.refresh_tree_view()
            self.unsaved_changes = False
            self.update_title()
            self.status_var.set(f"Загружено: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить XML:\n{e}")

    def rebuild_parent_map(self):
        """Строит карту родителей для O(1) доступа"""
        self.parent_map = {child: parent for parent in self.root_element.iter() for child in parent}
        self.parent_map[self.root_element] = None

    def refresh_tree_view(self):
        self.tree_view.delete(*self.tree_view.get_children())
        self.items_map.clear()
        if self.root_element:
            self.populate_tree("", self.root_element)

    def populate_tree(self, parent_id, element: ET.Element):
        tag_name = element.tag.split('}')[-1]
        icon = ICONS.get(tag_name, ICONS["Default"])
        display_tag = f"{icon} {tag_name}"
        
        name_val = element.get('name', element.get('id', ''))
        if len(name_val) > 30:
            name_val = name_val[:27] + "..."
            
        item_id = self.tree_view.insert(parent_id, "end", text=display_tag, values=(tag_name, name_val))
        self.items_map[item_id] = element
        
        for child in element:
            self.populate_tree(item_id, child)

    def on_selection_change(self, event=None):
        selection = self.tree_view.selection()
        if not selection:
            return
            
        item_id = selection[0]
        element = self.items_map.get(item_id)
        if not element:
            return
            
        self.attr_tree.delete(*self.attr_tree.get_children())
        for key, value in element.attrib.items():
            clean_key = key.split('}')[-1]
            self.attr_tree.insert("", "end", text=clean_key, values=(value,))
            
        self.text_editor.delete("1.0", tk.END)
        if element.text:
            self.text_editor.insert("1.0", element.text)
            
        self.props_notebook.select(0)

    def on_double_click(self, event):
        item = self.tree_view.identify_row(event.y)
        if item:
            self.tree_view.item(item, open=not self.tree_view.item(item, "open"))

    # === Редактирование ===
    
    def add_attribute(self):
        selection = self.tree_view.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите элемент в дереве")
            return
            
        element = self.items_map[selection[0]]
        key = simpledialog.askstring("Новый атрибут", "Имя атрибута:")
        if not key:
            return
        value = simpledialog.askstring("Значение", "Значение атрибута:") or ""
        
        element.set(key, value)
        self.on_selection_change()
        self.mark_unsaved()

    def edit_attribute(self):
        selection = self.attr_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        key = self.attr_tree.item(item, "text")
        old_val = self.attr_tree.item(item, "values")[0]
        
        full_key = key
        elem_selection = self.tree_view.selection()
        if elem_selection:
            elem = self.items_map[elem_selection[0]]
            for k in elem.attrib:
                if k.split('}')[-1] == key:
                    full_key = k
                    break
                    
        new_val = simpledialog.askstring("Изменить атрибут", f"Новое значение для {key}:", initialvalue=old_val)
        if new_val is not None:
            self.items_map[elem_selection[0]].set(full_key, new_val)
            self.on_selection_change()
            self.mark_unsaved()

    def delete_attribute(self):
        selection = self.attr_tree.selection()
        if not selection:
            return
        if messagebox.askyesno("Подтверждение", "Удалить выбранные атрибуты?"):
            elem_selection = self.tree_view.selection()
            if not elem_selection: return
            elem = self.items_map[elem_selection[0]]
            
            for item in selection:
                key = self.attr_tree.item(item, "text")
                for k in list(elem.attrib.keys()):
                    if k.split('}')[-1] == key:
                        del elem.attrib[k]
                        
            self.on_selection_change()
            self.mark_unsaved()

    def save_text_content(self):
        selection = self.tree_view.selection()
        if not selection:
            return
        element = self.items_map[selection[0]]
        new_text = self.text_editor.get("1.0", tk.END).strip()
        element.text = new_text if new_text else None
        self.mark_unsaved()
        self.status_var.set("Текст обновлен")

    def add_1c_element(self, elem_type: str):
        selection = self.tree_view.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите родительский элемент")
            return
            
        parent_elem = self.items_map[selection[0]]
        count = len([c for c in parent_elem if c.tag.endswith(elem_type)])
        new_name = f"Поле{count+1}"
        if elem_type == "ResourceField": new_name = f"Ресурс{count+1}"
        if elem_type == "Parameter": new_name = f"Параметр{count+1}"
            
        name = simpledialog.askstring("Имя элемента", "Введите имя поля:", initialvalue=new_name)
        if not name:
            return
            
        tag = f"{NS_1C}{elem_type}"
        new_elem = ET.SubElement(parent_elem, tag)
        new_elem.set("name", name)
        
        if elem_type == "DataField":
            data_path = ET.SubElement(new_elem, f"{NS_1C}dataPath")
            data_path.text = name
            title = ET.SubElement(new_elem, f"{NS_1C}title")
            title.text = name
            
        elif elem_type == "ResourceField":
            expression = ET.SubElement(new_elem, f"{NS_1C}expression")
            expression.text = "0"
            
        self.rebuild_parent_map()
        self.refresh_tree_view()
        self.mark_unsaved()
        self.status_var.set(f"Добавлен {elem_type}: {name}")

    def add_child_simple(self):
        selection = self.tree_view.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите родительский элемент")
            return
        parent = self.items_map[selection[0]]
        tag = simpledialog.askstring("Новый элемент", "Имя тега:")
        if tag:
            ET.SubElement(parent, tag)
            self.rebuild_parent_map()
            self.refresh_tree_view()
            self.mark_unsaved()

    def delete_element(self):
        selection = self.tree_view.selection()
        if not selection:
            return
        item = selection[0]
        if item == "":
            messagebox.showerror("Ошибка", "Нельзя удалить корневой элемент")
            return
            
        element = self.items_map[item]
        parent = self.parent_map.get(element)
        if parent is not None:
            parent.remove(element)
            self.rebuild_parent_map()
            self.refresh_tree_view()
            self.mark_unsaved()

    # === Утилиты ===
    
    def copy_xpath(self):
        selection = self.tree_view.selection()
        if not selection:
            return
        element = self.items_map[selection[0]]
        
        path = []
        current = element
        while current is not None:
            tag = current.tag.split('}')[-1]
            if 'name' in current.attrib:
                path.append(f"{tag}[@name='{current.attrib['name']}']")
            else:
                path.append(tag)
            current = self.parent_map.get(current)
            
        xpath = "/" + "/".join(reversed(path))
        self.root.clipboard_clear()
        self.root.clipboard_append(xpath)
        self.status_var.set("XPath скопирован")

    def find_duplicates(self):
        selection = self.tree_view.selection()
        if not selection:
            messagebox.showinfo("Инфо", "Выберите контейнер для проверки")
            return
            
        container = self.items_map[selection[0]]
        names = {}
        duplicates = []
        
        for child in container:
            name = child.get('name')
            if name:
                if name in names:
                    duplicates.append(name)
                names[name] = child
                
        if duplicates:
            msg = "Найдены дубликаты имен:\n" + "\n".join(set(duplicates))
            messagebox.showwarning("Дубликаты", msg)
        else:
            messagebox.showinfo("Чисто", "Дубликаты не найдены")

    def expand_all(self):
        for item in self.tree_view.get_children():
            self.tree_view.item(item, open=True)
            self._expand_recursive(item)

    def _expand_recursive(self, item):
        for child in self.tree_view.get_children(item):
            self.tree_view.item(child, open=True)
            self._expand_recursive(child)

    def collapse_all(self):
        for item in self.tree_view.get_children():
            self.tree_view.item(item, open=False)

    # === Файловые операции ===
    
    def save_xml(self):
        if not self.root_element:
            return
        if not self.file_path:
            self.save_as_xml()
            return
            
        try:
            self.indent(self.root_element)
            self.tree_data.write(self.file_path, encoding="utf-8", xml_declaration=True)
            self.unsaved_changes = False
            self.update_title()
            self.status_var.set("Файл сохранен")
            messagebox.showinfo("Успех", "XML сохранен!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")

    def save_as_xml(self):
        if not self.root_element:
            return
        path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")])
        if path:
            self.file_path = path
            self.save_xml()

    def indent(self, elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def mark_unsaved(self):
        if not self.unsaved_changes:
            self.unsaved_changes = True
            self.update_title()

    def update_title(self):
        title = "1С XML Architect Pro"
        if self.file_path:
            title += f" - {os.path.basename(self.file_path)}"
        if self.unsaved_changes:
            title += " *"
        self.root.title(title)

    def show_context_menu(self, event):
        item = self.tree_view.identify_row(event.y)
        if item:
            self.tree_view.selection_set(item)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Добавить потомка", command=self.add_child_simple)
            menu.add_command(label="Удалить", command=self.delete_element)
            menu.add_separator()
            menu.add_command(label="Копировать XPath", command=self.copy_xpath)
            menu.post(event.x_root, event.y_root)

    def on_close(self):
        if self.unsaved_changes:
            res = messagebox.askyesnocancel("Выход", "Есть несохраненные изменения. Сохранить?")
            if res is True:
                self.save_xml()
            elif res is None:
                return
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = XMLEditorApp(root)
    root.mainloop()
