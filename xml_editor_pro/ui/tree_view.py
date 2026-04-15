"""
Модуль управления деревом элементов
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, List
import xml.etree.ElementTree as ET
from utils.helpers import clean_tag


class TreeViewManager:
    """Управляет отображением дерева XML"""
    
    def __init__(self, tree_widget: ttk.Treeview):
        self.tree_widget = tree_widget
        self.items_map: Dict[str, ET.Element] = {}  # item_id -> element
        self.element_to_item: Dict[int, str] = {}   # id(element) -> item_id
    
    def clear(self):
        """Очищает дерево"""
        for item in self.tree_widget.get_children():
            self.tree_widget.delete(item)
        self.items_map.clear()
        self.element_to_item.clear()
    
    def build_tree(self, root_element: ET.Element):
        """Строит дерево из корневого элемента"""
        self.clear()
        self._populate_tree("", root_element)
    
    def _populate_tree(self, parent_id: str, element: ET.Element):
        """Рекурсивно заполняет дерево"""
        tag = clean_tag(element.tag)
        
        # Формируем текст для отображения
        text_content = ""
        if element.text and element.text.strip():
            text_content = element.text.strip()
            if len(text_content) > 80:
                text_content = text_content[:80] + "..."
        elif len(element) > 0:
            text_content = "[Структура]"
        else:
            text_content = "[Пусто]"
        
        # Формируем строку атрибутов
        attrib_str = ""
        if element.attrib:
            attribs = [f"{k}={v}" for k, v in element.attrib.items()]
            attrib_str = " | ".join(attribs)
            if len(attrib_str) > 100:
                attrib_str = attrib_str[:100] + "..."
        
        # Вставляем элемент
        item_id = self.tree_widget.insert(
            parent_id, 
            "end", 
            text=tag, 
            values=(text_content, attrib_str),
            open=False
        )
        
        # Сохраняем映射
        self.items_map[item_id] = element
        self.element_to_item[id(element)] = item_id
        
        # Рекурсивно добавляем детей
        for child in element:
            self._populate_tree(item_id, child)
    
    def get_element_by_item(self, item_id: str) -> Optional[ET.Element]:
        """Получает элемент по ID узла дерева"""
        return self.items_map.get(item_id)
    
    def get_item_by_element(self, element: ET.Element) -> Optional[str]:
        """Получает ID узла по элементу"""
        return self.element_to_item.get(id(element))
    
    def refresh_node(self, item_id: str, element: ET.Element):
        """Обновляет конкретный узел"""
        tag = clean_tag(element.tag)
        
        text_content = ""
        if element.text and element.text.strip():
            text_content = element.text.strip()
            if len(text_content) > 80:
                text_content = text_content[:80] + "..."
        elif len(element) > 0:
            text_content = "[Структура]"
        else:
            text_content = "[Пусто]"
        
        attrib_str = ""
        if element.attrib:
            attribs = [f"{k}={v}" for k, v in element.attrib.items()]
            attrib_str = " | ".join(attribs)
            if len(attrib_str) > 100:
                attrib_str = attrib_str[:100] + "..."
        
        self.tree_widget.item(item_id, text=tag, values=(text_content, attrib_str))
    
    def filter_tree(self, elements: List[ET.Element]):
        """Фильтрует дерево, показывая только указанные элементы"""
        # Сохраняем текущее состояние
        current_selection = self.tree_widget.selection()
        
        # Скрываем все элементы
        for item in self.tree_widget.get_children():
            self._hide_item(item)
        
        # Показываем найденные элементы и их родителей
        shown_items = set()
        for elem in elements:
            item_id = self.get_item_by_element(elem)
            if item_id:
                self._show_path_to_item(item_id, shown_items)
        
        # Разворачиваем найденные элементы
        for elem in elements:
            item_id = self.get_item_by_element(elem)
            if item_id:
                self.tree_widget.item(item_id, open=True)
    
    def _hide_item(self, item_id: str):
        """Скрывает элемент (детально можно реализовать через detach)"""
        # В ttk нет прямого скрытия, поэтому просто сворачиваем
        self.tree_widget.item(item_id, open=False)
    
    def _show_path_to_item(self, item_id: str, shown_items: set):
        """Показывает путь к элементу"""
        if item_id in shown_items:
            return
        
        shown_items.add(item_id)
        self.tree_widget.see(item_id)
        
        # Получаем родителя
        parent_id = self.tree_widget.parent(item_id)
        if parent_id:
            self.tree_widget.item(parent_id, open=True)
            self._show_path_to_item(parent_id, shown_items)
    
    def reset_filter(self):
        """Сбрасывает фильтр и показывает всё дерево"""
        for item in self.tree_widget.get_children():
            self._expand_all(item)
    
    def _expand_all(self, item_id: str):
        """Рекурсивно разворачивает все элементы"""
        self.tree_widget.item(item_id, open=True)
        for child in self.tree_widget.get_children(item_id):
            self._expand_all(child)
    
    def collapse_all(self):
        """Сворачивает всё дерево"""
        for item in self.tree_widget.get_children():
            self._collapse_all(item)
    
    def _collapse_all(self, item_id: str):
        """Рекурсивно сворачивает элементы"""
        self.tree_widget.item(item_id, open=False)
        for child in self.tree_widget.get_children(item_id):
            self._collapse_all(child)
