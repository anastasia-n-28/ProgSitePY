import re
from typing import List
from .slide import Slide


def parse_draft(content: str) -> List[Slide]:
    """
    Парсить чернетку презентації і повертає список слайдів.
    
    Коментарі (рядки, що починаються з @@) ігноруються.
    """
    slides = []
    lines = content.split('\n')
    
    current_slide_type = None
    current_content = []
    current_raw = []
    
    for line in lines:
        if line.strip().startswith('@@'):
            continue

        marker_match = re.match(r'^@([1-7])(?:\s+(.*))?$', line)
        if marker_match:
            if current_slide_type is not None:
                slides.append(Slide(
                    slide_type=f"@{current_slide_type}",
                    content='\n'.join(current_content),
                    raw_content='\n'.join(current_raw)
                ))

            current_slide_type = marker_match.group(1)
            current_content = []
            current_raw = []
            remaining = marker_match.group(2) if marker_match.group(2) else ""
            remaining = remaining.strip()
            if remaining:
                current_content.append(remaining)
                current_raw.append(line)
        else:
            if current_slide_type is not None:
                current_content.append(line)
                current_raw.append(line)

    if current_slide_type is not None:
        slides.append(Slide(
            slide_type=f"@{current_slide_type}",
            content='\n'.join(current_content),
            raw_content='\n'.join(current_raw)
        ))
    
    return slides