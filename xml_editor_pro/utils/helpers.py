"""
Вспомогательные функции для XML редактора 1С
"""
import xml.etree.ElementTree as ET
import re


def clean_tag(tag: str) -> str:
    """Убирает пространство имен из тега"""
    if '}' in tag:
        return tag.split('}')[-1]
    return tag


def get_full_xml_string(element: ET.Element) -> str:
    """Преобразует элемент в строку с форматированием"""
    xml_str = ET.tostring(element, encoding='unicode')
    # Убираем лишние пробелы и нормализуем
    xml_str = re.sub(r'\s+', ' ', xml_str).strip()
    return xml_str


def escape_xml_special_chars(text: str) -> str:
    """Экранирует спецсимволы XML"""
    if not text:
        return ""
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&apos;'
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def unescape_xml_special_chars(text: str) -> str:
    """Декодирует спецсимволы XML"""
    if not text:
        return ""
    replacements = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&apos;': "'"
    }
    for encoded, decoded in replacements.items():
        text = text.replace(encoded, decoded)
    return text


def format_xml_pretty(element: ET.Element, level: int = 0) -> str:
    """Форматирует XML с отступами"""
    indent = "\n" + "  " * level
    if len(element):
        if not element.text or not element.text.strip():
            element.text = indent + "  "
        if not element.tail or not element.tail.strip():
            element.tail = indent
        for child in element:
            format_xml_pretty(child, level + 1)
        if not element.tail or not element.tail.strip():
            element.tail = indent
    else:
        if level and (not element.tail or not element.tail.strip()):
            element.tail = indent
    return ET.tostring(element, encoding='unicode')
