import flet as ft
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, tostring
import re
import copy

class XMLEditorApp(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.root_element: Element | None = None
        self.tree_data = []  # Данные для дерева
        self.file_path = ""
        self.unsaved_changes = False
        
        # Кэш элементов для быстрого доступа
        self.element_map = {}  # node_id -> Element
        
        # UI компоненты
        self.tree_view = ft.TreeView(
            expand=True,
            collapse_icon=ft.Icon(ft.icons.CHEVRON_RIGHT),
            expand_icon=ft.Icon(ft.icons.CHEVRON_DOWN),
            leading=ft.Icon(ft.icons.FOLDER_OPEN, size=16),
            on_select=self.on_node_select,
        )
        
        self.detail_text = ft.TextField(
            multiline=True,
            min_lines=15,
            max_lines=20,
            read_only=True,
            text_size=14,
            font_family="Courier New",
            expand=True,
            border_color=ft.colors.TRANSPARENT,
            bgcolor=ft.colors.TRANSPARENT,
        )
        
        self.status_bar = ft.Text("Готов к работе", size=12, color=ft.colors.GREY_600)
        self.title_text = ft.Text("XML Редактор (Flet)", size=16, weight=ft.FontWeight.BOLD)
        
    def build(self):
        return ft.Column([
            # Верхняя панель
            ft.Row([
                self.title_text,
                ft.Container(expand=True),
                ft.ElevatedButton("📂 Открыть", icon=ft.icons.FOLDER_OPEN, on_click=self.load_xml),
                ft.ElevatedButton("💾 Сохранить", icon=ft.icons.SAVE, on_click=self.save_xml),
                ft.ElevatedButton("🎨 Тема", icon=ft.icons.PALETTE, on_click=self.toggle_theme),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, padding=10),
            
            ft.Divider(height=1),
            
            # Основная рабочая область
            ft.Row([
                # Левая панель - Дерево
                ft.Container(
                    content=self.tree_view,
                    expand=2,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=5,
                    padding=5,
                ),
                
                # Правая панель - Детали
                ft.Container(
                    content=ft.Column([
                        ft.Text("Детали элемента", weight=ft.FontWeight.BOLD),
                        self.detail_text,
                        ft.Row([
                            ft.ElevatedButton("✏️ Редактировать", icon=ft.icons.EDIT, on_click=self.edit_selected),
                            ft.ElevatedButton("➕ Добавить", icon=ft.icons.ADD, on_click=self.add_child),
                            ft.ElevatedButton("🗑️ Удалить", icon=ft.icons.DELETE, on_click=self.delete_selected, disabled=True),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                    ]),
                    expand=1,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=5,
                    padding=10,
                    min_width=300,
                ),
            ], expand=True, spacing=10, padding=10),
            
            # Статус бар
            ft.Container(
                content=self.status_bar,
                padding=5,
                bgcolor=ft.colors.SURFACE_VARIANT,
                border_radius=5,
            )
        ], expand=True)

    def load_xml(self, e):
        dialog = ft.FilePicker(on_result=self.on_file_pick)
        self.page.overlay.append(dialog)
        self.page.update()
        dialog.pick_files(allowed_extensions=["xml"])

    def on_file_pick(self, e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            try:
                tree = ET.parse(file_path)
                self.root_element = tree.getroot()
                self.file_path = file_path
                self.unsaved_changes = False
                
                # Построение дерева
                self.build_tree_view()
                
                self.status_bar.value = f"Загружено: {file_path.split('/')[-1]}"
                self.title_text.value = f"XML Редактор - {file_path.split('/')[-1]}"
                self.page.update()
            except Exception as ex:
                self.show_snackbar(f"Ошибка загрузки: {ex}", ft.colors.RED)

    def build_tree_view(self):
        """Рекурсивно строит дерево узлов"""
        self.tree_view.controls.clear()
        self.element_map.clear()
        
        if self.root_element:
            root_node = self.create_tree_node(self.root_element, "root")
            self.tree_view.controls.append(root_node)
        
        self.page.update()

    def create_tree_node(self, element: Element, parent_id: str) -> ft.TreeNode:
        """Создает узел дерева для элемента"""
        tag = element.tag.split('}')[-1]  # Убираем namespace
        node_id = f"{parent_id}_{tag}_{id(element)}"
        
        # Сохраняем ссылку на элемент
        self.element_map[node_id] = element
        
        # Формируем текст узла
        text_content = (element.text or "").strip()
        preview = (text_content[:40] + "...") if len(text_content) > 40 else text_content
        subtitle = f"{len(list(element))} дочерних" if len(list(element)) > 0 else "лист"
        
        children_nodes = []
        for child in element:
            children_nodes.append(self.create_tree_node(child, node_id))
        
        return ft.TreeNode(
            key=node_id,
            leading=ft.Icon(ft.icons.XML, size=16, color=ft.colors.BLUE),
            label=ft.Text(tag, weight=ft.FontWeight.BOLD),
            collapsed_label=ft.Text(tag),
            controls=[ft.Text(subtitle, size=10, color=ft.colors.GREY)],
            expanded=False,
            controls_expanded=children_nodes,
        )

    def on_node_select(self, e: ft.TreeViewSelectionEvent):
        """Обработка выбора узла"""
        if not e.control.selected_node:
            return
            
        node_key = e.control.selected_node.key
        element = self.element_map.get(node_key)
        
        if element:
            xml_str = self.element_to_clean_string(element)
            self.detail_text.value = xml_str
            self.page.update()

    def element_to_clean_string(self, element: Element) -> str:
        """Конвертирует элемент в строку без лишних namespaces"""
        xml_str = tostring(element, encoding='unicode')
        # Упрощение для отображения
        xml_str = re.sub(r'xmlns[^=]*="[^"]*"\s*', '', xml_str)
        xml_str = re.sub(r'\s+', ' ', xml_str).strip()
        return xml_str

    def edit_selected(self, e):
        selected_node = self.tree_view.selected_node
        if not selected_node:
            self.show_snackbar("Выберите элемент для редактирования", ft.colors.ORANGE)
            return
            
        element = self.element_map.get(selected_node.key)
        if not element:
            return

        def save_edit(e):
            new_text = dlg.content.value.strip()
            element.text = new_text if new_text else None
            self.unsaved_changes = True
            self.build_tree_view() # Перестроить дерево
            self.on_node_select(ft.TreeViewSelectionEvent(control=self.tree_view, selected_node=selected_node))
            dlg.open = False
            self.page.update()
            self.show_snackbar("Изменения сохранены", ft.colors.GREEN)

        dlg = ft.AlertDialog(
            title=ft.Text(f"Редактировать: {element.tag}"),
            content=ft.TextField(value=element.text or "", multiline=True, min_lines=10, expand=True),
            actions=[
                ft.TextButton("Отмена", on_click=lambda x: setattr(dlg, 'open', False)),
                ft.TextButton("Сохранить", on_click=save_edit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def add_child(self, e):
        selected_node = self.tree_view.selected_node
        if not selected_node:
            self.show_snackbar("Выберите родительский элемент", ft.colors.ORANGE)
            return
            
        parent_element = self.element_map.get(selected_node.key)
        if not parent_element:
            return

        def confirm_add(e):
            tag_name = name_field.value.strip()
            text_content = text_field.value.strip()
            
            if not tag_name:
                self.show_snackbar("Имя тега обязательно", ft.colors.RED)
                return
                
            new_elem = ET.SubElement(parent_element, tag_name)
            if text_content:
                new_elem.text = text_content
                
            self.unsaved_changes = True
            self.build_tree_view()
            dlg.open = False
            self.page.update()
            self.show_snackbar(f"Элемент <{tag_name}> добавлен", ft.colors.GREEN)

        name_field = ft.TextField(label="Имя тега", autofocus=True)
        text_field = ft.TextField(label="Текст (опционально)", multiline=True, min_lines=3)
        
        dlg = ft.AlertDialog(
            title=ft.Text("Добавить дочерний элемент"),
            content=ft.Column([name_field, text_field], tight=True),
            actions=[
                ft.TextButton("Отмена", on_click=lambda x: setattr(dlg, 'open', False)),
                ft.TextButton("Добавить", on_click=confirm_add),
            ],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def delete_selected(self, e):
        # Реализация удаления потребует доработки логики TreeView Flet
        self.show_snackbar("Функция удаления в разработке", ft.colors.GREY)

    def save_xml(self, e):
        if not self.root_element:
            self.show_snackbar("Нет данных для сохранения", ft.colors.ORANGE)
            return
            
        if not self.file_path:
            # Логика Save As (в браузере сложно, упрощенно)
            self.show_snackbar("Используйте 'Сохранить как' через меню браузера или консоли", ft.colors.BLUE)
            return

        try:
            # Форматирование
            self.indent(self.root_element)
            tree = ET.ElementTree(self.root_element)
            tree.write(self.file_path, encoding='utf-8', xml_declaration=True)
            
            self.unsaved_changes = False
            self.status_bar.value = f"Сохранено: {self.file_path.split('/')[-1]}"
            self.page.update()
            self.show_snackbar("Файл успешно сохранен!", ft.colors.GREEN)
        except Exception as ex:
            self.show_snackbar(f"Ошибка сохранения: {ex}", ft.colors.RED)

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

    def toggle_theme(self, e):
        self.page.theme_mode = (
            ft.ThemeMode.DARK if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        )
        self.page.update()

    def show_snackbar(self, message: str, color: str = ft.colors.BLUE):
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=ft.colors.WHITE),
            bgcolor=color,
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        self.page.snack_bar = snackbar
        snackbar.open = True
        self.page.update()


def main(page: ft.Page):
    page.title = "XML Editor 2026"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.spacing = 20
    
    app = XMLEditorApp(page)
    page.add(app)

if __name__ == "__main__":
    ft.app(target=main)
