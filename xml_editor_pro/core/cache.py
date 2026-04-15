"""
Модуль управления кэшем и историей изменений
"""
import copy
import xml.etree.ElementTree as ET
from typing import Optional, List


class ChangeCache:
    """Управляет кэшем изменений XML"""
    
    def __init__(self):
        self.original_root: Optional[ET.Element] = None
        self.current_root: Optional[ET.Element] = None
        self.has_unsaved_changes: bool = False
        self.history: List[ET.Element] = []
        self.history_index: int = -1
    
    def set_original(self, root: ET.Element):
        """Сохраняет оригинальное состояние"""
        self.original_root = copy.deepcopy(root)
        self.current_root = copy.deepcopy(root)
        self.has_unsaved_changes = False
        self.history = [copy.deepcopy(root)]
        self.history_index = 0
    
    def update_current(self, root: ET.Element):
        """Обновляет текущее состояние после изменений"""
        self.current_root = copy.deepcopy(root)
        self.has_unsaved_changes = True
        
        # Добавляем в историю
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        self.history.append(copy.deepcopy(root))
        self.history_index += 1
        
        # Ограничиваем историю 50 шагами
        if len(self.history) > 50:
            self.history.pop(0)
            self.history_index -= 1
    
    def apply_changes_to_tree(self, tree: ET.ElementTree):
        """Применяет изменения из кэша к дереву"""
        if self.current_root is not None:
            # Очищаем текущее дерево и заменяем корнем из кэша
            tree._root = copy.deepcopy(self.current_root)
    
    def save_snapshot(self, root: ET.Element):
        """Сохраняет снимок после успешного сохранения"""
        self.original_root = copy.deepcopy(root)
        self.has_unsaved_changes = False
