from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Slide:
    """Модель слайду презентації"""
    slide_type: str  # @1, @2, @3, @4, @5, @6, @7
    content: str
    raw_content: str  # оригінальний вміст для збереження форматування
    
    def __post_init__(self):
        # Видаляємо пробіли на початку і в кінці
        self.content = self.content.strip()
        self.raw_content = self.raw_content.strip()