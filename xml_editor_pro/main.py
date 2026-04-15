"""
1С XML Architect Pro - Главный файл запуска
Современный редактор XML схем 1С СКД
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import os

# Импорт наших модулей
from core.engine import XMLEngine
from core.cache import ChangeCache
from ui.tree_view import TreeViewManager
from ui.details_panel import DetailsPanel
from ui.toolbar import ToolbarManager
from ui.dialogs import Dialogs
from ui.styles import COLORS, FONTS


class XMLArchitectApp:
    """Главный класс приложения"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("1С XML Architect Pro")
        self.root.geometry("1400x800")
        
        # Инициализация компонентов
        self.engine = XMLEngine()
        self.cache = ChangeCache()
        
        # Создание интерфейса
        self.setup_ui()
        
        # Привязка событий
        self.bind_events()
    
    def setup_ui(self):
        """Создает основной интерфейс"""
        # Верхняя панель
        self.toolbar = ToolbarManager(self.root)
        # Переопределяем методы toolbar
        self.toolbar.on_open = self.load_file
        self.toolbar.on_save = self.save_file
        self.toolbar.on_save_as = self.save_file_as
        self.toolbar.on_refresh = self.refresh_tree
        self.toolbar.on_move_up = self.move_element_up
        self.toolbar.on_move_down = self.move_element_down
        self.toolbar.on_search = self.perform_search
        self.toolbar.on_reset_search = self.reset_search
        self.toolbar.on_master_1c = self.open_master_1c
        self.toolbar.on_commit = self.commit_changes
        
        # Основная область
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая панель - дерево
        left_frame = tk.Frame(main_paned, bg=COLORS['bg_main'])
        main_paned.add(left_frame, weight=3)
        
        tree_container = tk.Frame(left_frame, bg=COLORS['bg_tree'])
        tree_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview
        columns = ("text", "attrib")
        self.tree_widget = ttk.Treeview(
            tree_container,
            columns=columns,
            displaycolumns=columns,
            selectmode="browse"
        )
        
        self.tree_widget.heading("#0", text="Тег")
        self.tree_widget.heading("text", text="Текст/Значение")
        self.tree_widget.heading("attrib", text="Атрибуты")
        
        self.tree_widget.column("#0", width=200, minwidth=100)
        self.tree_widget.column("text", width=300, minwidth=150)
        self.tree_widget.column("attrib", width=250, minwidth=100)
        
        # Скроллы
        v_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree_widget.yview)
        h_scroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree_widget.xview)
        self.tree_widget.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.tree_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Менеджер дерева
        self.tree_manager = TreeViewManager(self.tree_widget)
        
        # Правая панель - детали
        right_frame = tk.Frame(main_paned, bg=COLORS['bg_panel'], width=500)
        right_frame.pack_propagate(False)
        main_paned.add(right_frame, weight=1)
        
        self.details_panel = DetailsPanel(right_frame)
        
        # Нижняя панель - статус
        self.status_bar = tk.Label(
            self.root,
            text="Готов к работе",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg=COLORS['status_bar']
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Контекстное меню
        self.create_context_menu()
    
    def create_context_menu(self):
        """Создает контекстное меню"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="✏️ Редактировать", command=self.edit_element)
        self.context_menu.add_command(label="➕ Добавить потомка (текст)", command=self.add_child_from_text)
        self.context_menu.add_command(label="🗑️ Удалить элемент", command=self.delete_element)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Копировать XPath", command=self.copy_xpath)
        
        # Привязка ПКМ
        self.tree_widget.bind("<Button-3>", self.show_context_menu)
    
    def bind_events(self):
        """Привязывает события"""
        self.tree_widget.bind("<<TreeviewSelect>>", self.on_selection_change)
        
        # Закрытие с проверкой сохранений
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def load_file(self):
        """Загружает XML файл"""
        file_path = filedialog.askopenfilename(
            title="Открыть XML файл",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        if self.engine.load_file(file_path):
            self.cache.set_original(self.engine.root_element)
            self.tree_manager.build_tree(self.engine.root_element)
            self.update_status(f"Открыт: {os.path.basename(file_path)}")
            self.toolbar.set_status("")
            self.update_title()
        else:
            messagebox.showerror("Ошибка", "Не удалось загрузить файл")
    
    def save_file(self):
        """Сохраняет текущий файл"""
        if not self.engine.root_element:
            messagebox.showwarning("Предупреждение", "Нет открытых данных")
            return
        
        if self.engine.save_file():
            self.cache.save_snapshot(self.engine.root_element)
            self.update_status(f"Сохранено: {os.path.basename(self.engine.file_path)}")
            self.toolbar.set_status("")
            self.update_title()
            messagebox.showinfo("Успех", "Файл успешно сохранён!")
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить файл")
    
    def save_file_as(self):
        """Сохраняет как новый файл"""
        if not self.engine.root_element:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.engine.save_file(file_path):
                self.cache.save_snapshot(self.engine.root_element)
                self.update_status(f"Сохранено как: {os.path.basename(file_path)}")
                self.toolbar.set_status("")
                self.update_title()
    
    def commit_changes(self):
        """Применяет накопленные изменения и обновляет дерево"""
        if not self.cache.has_unsaved_changes:
            messagebox.showinfo("Информация", "Нет несохранённых изменений")
            return
        
        # Обновляем дерево из кэша
        self.tree_manager.build_tree(self.engine.root_element)
        self.toolbar.set_status("")
        self.update_status("Изменения применены")
    
    def refresh_tree(self):
        """Обновляет дерево"""
        if self.engine.root_element:
            self.tree_manager.build_tree(self.engine.root_element)
    
    def move_element_up(self):
        """Перемещает элемент вверх"""
        selected = self.tree_widget.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите элемент")
            return
        
        item_id = selected[0]
        element = self.tree_manager.get_element_by_item(item_id)
        
        if element and self.engine.move_element_up(element):
            self.cache.update_current(self.engine.root_element)
            self.toolbar.set_status("● Изменения не записаны")
            # Не перестраиваем дерево сразу, только по кнопке "Записать"
    
    def move_element_down(self):
        """Перемещает элемент вниз"""
        selected = self.tree_widget.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите элемент")
            return
        
        item_id = selected[0]
        element = self.tree_manager.get_element_by_item(item_id)
        
        if element and self.engine.move_element_down(element):
            self.cache.update_current(self.engine.root_element)
            self.toolbar.set_status("● Изменения не записаны")
    
    def perform_search(self):
        """Выполняет поиск"""
        search_text = self.toolbar.get_search_text()
        
        if not search_text or search_text == "Поиск...":
            messagebox.showinfo("Информация", "Введите текст для поиска")
            return
        
        # Сворачиваем всё перед поиском
        self.tree_manager.collapse_all()
        
        results = self.engine.find_elements_by_filter(search_text)
        
        if not results:
            messagebox.showinfo("Результат", f"Ничего не найдено по запросу '{search_text}'")
            return
        
        self.tree_manager.filter_tree(results)
        self.update_status(f"Найдено элементов: {len(results)}")
    
    def reset_search(self):
        """Сбрасывает поиск"""
        self.toolbar.clear_search()
        self.tree_manager.reset_filter()
        self.update_status("Поиск сброшен")
    
    def open_master_1c(self):
        """Открывает мастер 1С"""
        result = Dialogs.show_master_1c(self.root)
        
        if not result:
            return
        
        selected = self.tree_widget.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите родительский элемент")
            return
        
        parent_item = selected[0]
        parent_element = self.tree_manager.get_element_by_item(parent_item)
        
        if not parent_element:
            return
        
        # Создаём XML элемента
        elem_type = result["type"]
        name = result["data"]["name"]
        title = result["data"]["title"]
        
        # Формируем базовую структуру
        import xml.etree.ElementTree as ET
        
        new_elem = ET.Element(elem_type)
        
        if elem_type in ["calculatedField", "field", "parameter", "resource", "totalField"]:
            data_path = ET.SubElement(new_elem, "dataPath")
            data_path.text = name
            
            title_elem = ET.SubElement(new_elem, "title")
            title_elem.set("xsi:type", "v8:LocalStringType")
            
            # Добавляем структуру LocalStringType
            v8_item = ET.SubElement(title_elem, "{http://v8.1c.ru/8.1/data-core}item")
            v8_lang = ET.SubElement(v8_item, "{http://v8.1c.ru/8.1/data-core}lang")
            v8_lang.text = "ru"
            v8_content = ET.SubElement(v8_item, "{http://v8.1c.ru/8.1/data-core}content")
            v8_content.text = title
        
        parent_element.append(new_elem)
        self.cache.update_current(self.engine.root_element)
        self.toolbar.set_status("● Изменения не записаны")
        self.refresh_tree()
    
    def edit_element(self):
        """Редактирует выбранный элемент"""
        self.details_panel.open_editor()
    
    def add_child_from_text(self):
        """Добавляет потомка из текста"""
        xml_text = Dialogs.show_add_from_text(self.root)
        
        if not xml_text:
            return
        
        selected = self.tree_widget.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите родительский элемент")
            return
        
        parent_item = selected[0]
        parent_element = self.tree_manager.get_element_by_item(parent_item)
        
        if not parent_element:
            return
        
        if self.engine.add_child_from_text(parent_element, xml_text):
            self.cache.update_current(self.engine.root_element)
            self.toolbar.set_status("● Изменения не записаны")
            self.refresh_tree()
        else:
            messagebox.showerror("Ошибка", "Неверный формат XML")
    
    def delete_element(self):
        """Удаляет выбранный элемент"""
        selected = self.tree_widget.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите элемент")
            return
        
        item_id = selected[0]
        element = self.tree_manager.get_element_by_item(item_id)
        
        if not element:
            return
        
        if element == self.engine.root_element:
            messagebox.showwarning("Предупреждение", "Нельзя удалить корневой элемент")
            return
        
        parent = self.engine.get_parent(element)
        if parent is not None:
            parent.remove(element)
            self.cache.update_current(self.engine.root_element)
            self.toolbar.set_status("● Изменения не записаны")
            self.refresh_tree()
    
    def copy_xpath(self):
        """Копирует XPath в буфер обмена"""
        selected = self.tree_widget.selection()
        if not selected:
            return
        
        item_id = selected[0]
        element = self.tree_manager.get_element_by_item(item_id)
        
        if element:
            path = self.engine.get_path_to_element(element)
            xpath = "/" + "/".join(path)
            self.root.clipboard_clear()
            self.root.clipboard_append(xpath)
            self.update_status(f"XPath скопирован: {xpath}")
    
    def on_selection_change(self, event=None):
        """Обрабатывает изменение выделения"""
        selected = self.tree_widget.selection()
        
        if not selected:
            self.details_panel.update_display(None)
            return
        
        item_id = selected[0]
        element = self.tree_manager.get_element_by_item(item_id)
        
        if element:
            path = self.engine.get_path_to_element(element)
            self.details_panel.update_display(element, path)
    
    def show_context_menu(self, event):
        """Показывает контекстное меню"""
        item = self.tree_widget.identify_row(event.y)
        if item:
            self.tree_widget.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def update_status(self, text: str):
        """Обновляет строку статуса"""
        self.status_bar.config(text=text)
    
    def update_title(self):
        """Обновляет заголовок окна"""
        title = "1С XML Architect Pro"
        if self.engine.file_path:
            title += f" - {os.path.basename(self.engine.file_path)}"
        if self.cache.has_unsaved_changes:
            title += " *"
        self.root.title(title)
    
    def on_close(self):
        """Обрабатывает закрытие приложения"""
        if self.cache.has_unsaved_changes:
            response = messagebox.askyesnocancel(
                "Несохранённые изменения",
                "Есть несохранённые изменения. Сохранить?"
            )
            
            if response is True:
                self.save_file()
            elif response is False:
                pass
            else:
                return
        
        self.root.destroy()


def main():
    """Точка входа"""
    root = tk.Tk()
    app = XMLArchitectApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
