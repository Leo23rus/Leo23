"""
Модуль работы с XML для 1С СКД
"""
import xml.etree.ElementTree as ET
from typing import Optional, List, Dict, Any
from utils.helpers import clean_tag, format_xml_pretty


class XMLEngine:
    """Движок для работы с XML схемами 1С"""
    
    def __init__(self):
        self.tree: Optional[ET.ElementTree] = None
        self.root_element: Optional[ET.Element] = None
        self.parent_map: Dict[ET.Element, ET.Element] = {}
        self.file_path: str = ""
        
    def load_file(self, file_path: str) -> bool:
        """Загружает XML файл"""
        try:
            self.tree = ET.parse(file_path)
            self.root_element = self.tree.getroot()
            self.file_path = file_path
            self._build_parent_map()
            return True
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return False
    
    def _build_parent_map(self):
        """Строит карту родителей для быстрого поиска"""
        self.parent_map = {child: parent for parent in self.root_element.iter() for child in parent}
    
    def get_parent(self, element: ET.Element) -> Optional[ET.Element]:
        """Получает родителя элемента за O(1)"""
        if element == self.root_element:
            return None
        return self.parent_map.get(element)
    
    def get_path_to_element(self, element: ET.Element) -> List[str]:
        """Возвращает путь к элементу от корня"""
        path = []
        current = element
        while current is not None:
            path.insert(0, clean_tag(current.tag))
            current = self.parent_map.get(current)
        return path
    
    def find_elements_by_filter(self, search_text: str) -> List[ET.Element]:
        """Ищет элементы по тексту в теге, тексте или атрибутах"""
        if not self.root_element or not search_text:
            return []
        
        results = []
        search_lower = search_text.lower()
        
        for elem in self.root_element.iter():
            # Проверка тега
            if search_lower in clean_tag(elem.tag).lower():
                results.append(elem)
                continue
            
            # Проверка текста
            if elem.text and search_lower in elem.text.lower():
                results.append(elem)
                continue
            
            # Проверка атрибутов
            for attr_name, attr_value in elem.attrib.items():
                if search_lower in attr_name.lower() or search_lower in attr_value.lower():
                    results.append(elem)
                    break
        
        return results
    
    def move_element_up(self, element: ET.Element) -> bool:
        """Перемещает элемент вверх средиsiblings"""
        parent = self.get_parent(element)
        if parent is None:
            return False
        
        siblings = list(parent)
        index = siblings.index(element)
        if index > 0:
            parent.remove(element)
            parent.insert(index - 1, element)
            self._build_parent_map()
            return True
        return False
    
    def move_element_down(self, element: ET.Element) -> bool:
        """Перемещает элемент вниз среди siblings"""
        parent = self.get_parent(element)
        if parent is None:
            return False
        
        siblings = list(parent)
        index = siblings.index(element)
        if index < len(siblings) - 1:
            parent.remove(element)
            parent.insert(index + 1, element)
            self._build_parent_map()
            return True
        return False
    
    def add_child_from_text(self, parent: ET.Element, xml_text: str) -> bool:
        """Добавляет дочерний элемент из XML текста"""
        try:
            # Оборачиваем в временный корень для парсинга нескольких элементов
            wrapper = f"<root>{xml_text.strip()}</root>"
            temp_root = ET.fromstring(wrapper)
            
            for child in temp_root:
                # Клонируем элемент
                import copy
                new_child = copy.deepcopy(child)
                parent.append(new_child)
            
            self._build_parent_map()
            return True
        except ET.ParseError as e:
            print(f"Ошибка парсинга XML: {e}")
            return False
    
    def save_file(self, file_path: Optional[str] = None) -> bool:
        """Сохраняет XML файл"""
        if not self.root_element:
            return False
        
        target_path = file_path or self.file_path
        if not target_path:
            return False
        
        try:
            # Форматируем перед сохранением
            format_xml_pretty(self.root_element)
            self.tree.write(target_path, encoding='utf-8', xml_declaration=True)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False
    
    def get_element_string(self, element: ET.Element) -> str:
        """Возвращает строковое представление элемента"""
        return format_xml_pretty(element)
