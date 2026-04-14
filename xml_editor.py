import xml.etree.ElementTree as ET
from typing import Optional, List, Dict, Any


class XMLEditor:
    """Класс для удобного редактирования XML файлов."""

    def __init__(self, file_path: Optional[str] = None, xml_string: Optional[str] = None):
        """
        Инициализация редактора.
        
        :param file_path: Путь к XML файлу (если нужно загрузить из файла).
        :param xml_string: Строка с XML содержимым (если нужно загрузить из строки).
        """
        self.tree = None
        self.root = None
        self.file_path = file_path

        if file_path:
            self.load(file_path)
        elif xml_string:
            self.load_from_string(xml_string)

    def load(self, file_path: str) -> None:
        """Загрузить XML из файла."""
        self.file_path = file_path
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()

    def load_from_string(self, xml_string: str) -> None:
        """Загрузить XML из строки."""
        self.root = ET.fromstring(xml_string)
        self.tree = ET.ElementTree(self.root)

    def save(self, output_path: Optional[str] = None, encoding: str = "utf-8", xml_declaration: bool = True) -> None:
        """
        Сохранить изменения в файл.
        
        :param output_path: Путь для сохранения. Если не указан, перезапишет исходный файл.
        :param encoding: Кодировка файла.
        :param xml_declaration: Добавлять ли декларацию <?xml version="1.0"?>.
        """
        path = output_path if output_path else self.file_path
        if not path:
            raise ValueError("Не указан путь для сохранения файла.")
        
        self.tree.write(path, encoding=encoding, xml_declaration=xml_declaration)

    def get_root(self) -> ET.Element:
        """Вернуть корневой элемент."""
        return self.root

    def find(self, path: str) -> Optional[ET.Element]:
        """Найти первый элемент по пути (XPath)."""
        return self.root.find(path)

    def find_all(self, path: str) -> List[ET.Element]:
        """Найти все элементы по пути (XPath)."""
        return self.root.findall(path)

    def add_element(self, parent_path: str, tag: str, attributes: Optional[Dict[str, str]] = None, text: Optional[str] = None) -> ET.Element:
        """
        Добавить новый элемент к родителю.
        
        :param parent_path: XPath путь к родителю.
        :param tag: Тег нового элемента.
        :param attributes: Словарь атрибутов.
        :param text: Текстовое содержимое элемента.
        :return: Созданный элемент.
        """
        parent = self.find(parent_path)
        if parent is None:
            raise ValueError(f"Родительский элемент не найден по пути: {parent_path}")

        new_elem = ET.SubElement(parent, tag, attributes or {})
        if text:
            new_elem.text = text
        
        return new_elem

    def set_attribute(self, element_path: str, key: str, value: str) -> None:
        """Установить или обновить атрибут элемента."""
        elem = self.find(element_path)
        if elem is None:
            raise ValueError(f"Элемент не найден по пути: {element_path}")
        elem.set(key, value)

    def remove_element(self, element_path: str) -> bool:
        """
        Удалить элемент. 
        Примечание: В ElementTree нет прямого метода remove для пути, нужно искать родителя.
        Эта реализация работает, если передать точный путь к удаляемому элементу, 
        но для надежного удаления лучше использовать find_all и удалить из родителя вручную.
        Здесь реализован упрощенный вариант для первого найденного.
        """
        # Для надежного удаления нам нужно найти родителя. 
        # XPath в стандартной библиотеке ограничен, поэтому простой вариант:
        # Попытаемся найти элемент, а потом удалить его из родителя, если сможем найти родителя.
        # Однако, стандартный find не дает прямого доступа к родителю.
        # Поэтому мы используем подход: найти всех детей родителя и удалить нужный.
        
        # Разделим путь на часть до последнего элемента и сам последний элемент
        # Это упрощенная логика, работающая для простых путей вида "parent/child"
        parts = element_path.rsplit('/', 1)
        
        if len(parts) == 2:
            parent_path, child_tag = parts
            # Обработка случаев с индексами или условиями в XPath сложна для базовой реализации
            # Поэтому мы найдем родителя и переберем его детей
            
            # Попытка найти родителя
            parent = self.find(parent_path)
            if parent is not None:
                # Ищем ребенка с таким тегом (упрощенно)
                for child in parent:
                    # Простая эвристика: если тег совпадает, считаем что нашли (для сложных путей нужно парсить XPath)
                    if child.tag == child_tag.split('[')[0]: 
                         parent.remove(child)
                         return True
        
        # Альтернатива: если передан просто тег и мы хотим удалить из корня
        if len(parts) == 1:
             tag = parts[0]
             for child in list(self.root):
                 if child.tag == tag:
                     self.root.remove(child)
                     return True

        return False

    def to_string(self, encoding: str = "unicode") -> str:
        """Вернуть XML как строку."""
        return ET.tostring(self.root, encoding=encoding)

    def print_tree(self) -> None:
        """Вывести красивое представление дерева в консоль (упрощенно)."""
        import xml.dom.minidom
        xml_str = ET.tostring(self.root, encoding='utf-8')
        dom = xml.dom.minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")
        # Убрать лишние пустые строки, которые иногда добавляет minidom
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        print('\n'.join(lines))


# Пример использования
if __name__ == "__main__":
    # Создадим пример XML строки
    sample_xml = """
    <library>
        <book id="1">
            <title>Python Programming</title>
            <author>John Doe</author>
        </book>
        <book id="2">
            <title>XML Mastery</title>
            <author>Jane Smith</author>
        </book>
    </library>
    """

    # Инициализируем редактор
    editor = XMLEditor(xml_string=sample_xml)

    print("--- Исходное дерево ---")
    editor.print_tree()

    # Добавим новую книгу
    print("\n--- Добавляем новую книгу ---")
    editor.add_element(
        parent_path=".", 
        tag="book", 
        attributes={"id": "3"}, 
        text="" # Текст обычно внутри дочерних элементов
    )
    # Добавим детали к новой книге (она теперь последняя в списке)
    books = editor.find_all("book")
    new_book = books[-1]
    
    title_elem = ET.SubElement(new_book, "title")
    title_elem.text = "Advanced AI"
    
    author_elem = ET.SubElement(new_book, "author")
    author_elem.text = "Alan Turing"

    # Изменим автора первой книги
    print("\n--- Меняем автора первой книги ---")
    editor.set_attribute("book[@id='1']/author", "verified", "true") # Это не сработает через set_attribute напрямую для текста, см ниже
    
    # Правильный способ изменить текст элемента:
    first_author = editor.find("book[@id='1']/author")
    if first_author is not None:
        first_author.text = "John Updated Doe"
        first_author.set("status", "verified") # Добавим атрибут

    # Удалим вторую книгу
    print("\n--- Удаляем вторую книгу ---")
    # Для удаления найдем родителя (корень) и удалим конкретного ребенка
    book_to_remove = editor.find("book[@id='2']")
    if book_to_remove is not None:
        editor.root.remove(book_to_remove)

    print("\n--- Итоговое дерево ---")
    editor.print_tree()

    # Сохранение в файл (закомментировано, чтобы не создавать файлы при запуске)
    # editor.save("output.xml")
