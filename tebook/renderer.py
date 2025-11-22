import re
from typing import List
from .slide import Slide


def render_html(slides: List[Slide], language: str = "python", doc_type: str = "html-stu", view_mode: str = "slides") -> str:
    """
    Генерує HTML презентацію зі списку слайдів.
    
    Args:
        slides: Список слайдів
        language: Мова програмування для підсвітки коду
        doc_type: Тип документа (html-stu, html-tut, md)
        view_mode: Режим відображення 
            - "slides" - слайди з навігацією
            - "document" - документ з блоків (з'являються по кліку)
            - "full-document" - повний документ (всі слайди відразу)
    """
    if doc_type == "md":
        return render_markdown(slides)
    
    # Режим повного документа - всі слайди відразу
    if view_mode == "full-document":
        return render_html_full_document(slides, language, doc_type)
    
    # Режим документа - всі слайди один за одним (з'являються по кліку)
    if view_mode == "document":
        return render_html_document(slides, language, doc_type)
    
    # Режим слайдів - з навігацією
    return render_html_slides(slides, language, doc_type)


def render_html_slides(slides: List[Slide], language: str = "python", doc_type: str = "html-stu") -> str:
    """Генерує HTML презентацію у режимі слайдів з навігацією"""
    html_parts = []
    html_parts.append("<!DOCTYPE html>")
    html_parts.append("<html lang='uk'>")
    html_parts.append("<head>")
    html_parts.append("    <meta charset='UTF-8'>")
    html_parts.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html_parts.append("    <title>Презентація</title>")
    html_parts.append("    <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css'>")
    html_parts.append("    <style>")
    html_parts.append("        body { position: relative; margin: 0; padding: 0; }")
    html_parts.append("        .slide-container { position: relative; }")
    html_parts.append("        .slide { display: none; padding: 2rem; min-height: 80vh; text-align: center; }")
    html_parts.append("        .slide.active { display: flex; flex-direction: column; justify-content: center; align-items: center; }")
    html_parts.append("        .slide > * { text-align: center; }")
    html_parts.append("        .slide h1 { font-size: 2.5rem; margin-bottom: 1rem; text-align: center; }")
    html_parts.append("        .slide h2 { font-size: 2rem; margin-bottom: 1rem; text-align: center; }")
    html_parts.append("        .slide code { background: #f4f4f4; padding: 0.2rem 0.4rem; border-radius: 0.25rem; }")
    html_parts.append("        .slide pre { background: #f4f4f4; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; }")
    html_parts.append("        .slide .definition { border: 2px solid #333; padding: 1rem; margin: 1rem 0; border-radius: 0.5rem; }")
    html_parts.append("        .slide .task { background: #fff3cd; padding: 1rem; border-left: 4px solid #ffc107; margin: 1rem 0; }")
    html_parts.append("        .slide .table-container { overflow-x: auto; margin: 1rem 0; }")
    html_parts.append("        .slide table { width: 100%; border-collapse: collapse; }")
    html_parts.append("        .slide table th, .slide table td { border: 1px solid #ddd; padding: 0.5rem; }")
    html_parts.append("        .slide table th { background: #f4f4f4; }")
    html_parts.append("        .slide .italic { font-style: italic; }")
    html_parts.append("        .slide .bold { font-weight: bold; }")
    html_parts.append("        .slide img { max-width: 100%; height: auto; }")
    html_parts.append("        .navigation { position: fixed; bottom: 2rem; right: 2rem; z-index: 1000; }")
    html_parts.append("        .navigation button { margin: 0.25rem; }")
    html_parts.append("        .slide-counter { position: fixed; bottom: 2rem; left: 2rem; z-index: 1000; }")
    html_parts.append("        #drawingCanvas { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 500; pointer-events: none; }")
    html_parts.append("        #drawingCanvas.drawing { pointer-events: all; }")
    html_parts.append("        .drawing-toggle-btn { position: fixed; top: 2rem; right: 2rem; z-index: 1001; width: 50px; height: 50px; border-radius: 50%; background: #0066cc; color: white; border: none; cursor: pointer; font-size: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; }")
    html_parts.append("        .drawing-toggle-btn:hover { background: #0052a3; }")
    html_parts.append("        .drawing-controls { position: fixed; top: 6rem; right: 2rem; z-index: 1001; background: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.2); display: none; }")
    html_parts.append("        .drawing-controls.visible { display: block; }")
    html_parts.append("        .drawing-controls button { margin: 0.25rem; display: block; width: 100%; }")
    html_parts.append("        .color-picker { display: flex; gap: 0.5rem; margin: 0.5rem 0; flex-wrap: wrap; }")
    html_parts.append("        .color-btn { width: 30px; height: 30px; border: 2px solid #333; border-radius: 50%; cursor: pointer; }")
    html_parts.append("        .color-btn.active { border-color: #0066cc; border-width: 3px; }")
    html_parts.append("        .eraser-btn { width: 30px; height: 30px; border: 2px solid #333; border-radius: 4px; cursor: pointer; background: white; display: flex; align-items: center; justify-content: center; font-size: 18px; }")
    html_parts.append("        .eraser-btn.active { border-color: #0066cc; border-width: 3px; background: #f0f0f0; }")
    
    # Додаткові стилі для викладацького формату
    if doc_type == "html-tut":
        html_parts.append("        /* Викладацький формат - розширені стилі */")
        html_parts.append("        .slide { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }")
        html_parts.append("        .slide h1 { color: #1a237e; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); }")
        html_parts.append("        .slide h2 { color: #283593; border-bottom: 2px solid #3f51b5; padding-bottom: 0.5rem; }")
        html_parts.append("        .slide .definition { background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #3f51b5; }")
        html_parts.append("        .slide .task { background: linear-gradient(135deg, #fff3cd 0%, #ffe082 100%); box-shadow: 0 2px 4px rgba(0,0,0,0.1); }")
        html_parts.append("        .slide code { background: #263238; color: #aed581; font-weight: bold; }")
        html_parts.append("        .slide pre { background: #263238; color: #aed581; border: 2px solid #37474f; }")
        html_parts.append("        .slide table { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }")
        html_parts.append("        .slide table th { background: linear-gradient(135deg, #3f51b5 0%, #5c6bc0 100%); color: white; font-weight: bold; }")
        html_parts.append("        .slide table tr:nth-child(even) { background: #f5f5f5; }")
        html_parts.append("        .slide table tr:hover { background: #e3f2fd; transition: background 0.3s; }")
    
    html_parts.append("    </style>")
    html_parts.append("</head>")
    html_parts.append("<body>")
    html_parts.append("    <canvas id='drawingCanvas'></canvas>")
    html_parts.append("    <button class='drawing-toggle-btn' id='drawingToggleBtn' title='Малювання'>✏️</button>")
    html_parts.append("    <div class='drawing-controls' id='drawingControls'>")
    html_parts.append("        <button id='clearDrawing'>Очистити</button>")
    html_parts.append("        <div class='color-picker'>")
    html_parts.append("            <div class='color-btn active' data-color='#000000' style='background: #000000;' title='Чорний'></div>")
    html_parts.append("            <div class='color-btn' data-color='#ff0000' style='background: #ff0000;' title='Червоний'></div>")
    html_parts.append("            <div class='color-btn' data-color='#0000ff' style='background: #0000ff;' title='Синій'></div>")
    html_parts.append("            <div class='color-btn' data-color='#00ff00' style='background: #00ff00;' title='Зелений'></div>")
    html_parts.append("            <div class='color-btn' data-color='#ffff00' style='background: #ffff00;' title='Жовтий'></div>")
    html_parts.append("            <div class='color-btn' data-color='#ff00ff' style='background: #ff00ff;' title='Пурпурний'></div>")
    html_parts.append("            <div class='color-btn' data-color='#ffffff' style='background: #ffffff;' title='Білий'></div>")
    html_parts.append("            <div class='eraser-btn' id='eraserBtn' title='Ластик'>🧹</div>")
    html_parts.append("        </div>")
    html_parts.append("    </div>")
    html_parts.append("    <div class='container'>")
    
    # Генеруємо слайди
    for i, slide in enumerate(slides):
        slide_class = "slide" + (" active" if i == 0 else "")
        html_parts.append(f"        <div class='{slide_class}' id='slide-{i}'>")
        html_parts.append(render_slide_content(slide))
        html_parts.append("        </div>")
    
    html_parts.append("    </div>")
    
    # Навігація
    html_parts.append("    <div class='navigation'>")
    html_parts.append("        <button onclick='previousSlide()'>← Попередній</button>")
    html_parts.append("        <button onclick='nextSlide()'>Наступний →</button>")
    html_parts.append("    </div>")
    html_parts.append(f"    <div class='slide-counter' id='counter'>1 / {len(slides)}</div>")
    
    # JS для навігації та малювання
    html_parts.append("    <script>")
    html_parts.append("        let currentSlide = 0;")
    html_parts.append("        const slides = document.querySelectorAll('.slide');")
    html_parts.append("        const totalSlides = slides.length;")
    html_parts.append("")
    html_parts.append("        function showSlide(n) {")
    html_parts.append("            slides.forEach(s => s.classList.remove('active'));")
    html_parts.append("            if (n >= totalSlides) currentSlide = 0;")
    html_parts.append("            if (n < 0) currentSlide = totalSlides - 1;")
    html_parts.append("            if (n >= 0 && n < totalSlides) currentSlide = n;")
    html_parts.append("            slides[currentSlide].classList.add('active');")
    html_parts.append("            document.getElementById('counter').textContent = `${currentSlide + 1} / ${totalSlides}`;")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        function nextSlide() { showSlide(currentSlide + 1); }")
    html_parts.append("        function previousSlide() { showSlide(currentSlide - 1); }")
    html_parts.append("")
    html_parts.append("        document.addEventListener('keydown', (e) => {")
    html_parts.append("            if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();")
    html_parts.append("            if (e.key === 'ArrowLeft') previousSlide();")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        // Малювання")
    html_parts.append("        const canvas = document.getElementById('drawingCanvas');")
    html_parts.append("        const ctx = canvas.getContext('2d');")
    html_parts.append("        let isDrawing = false;")
    html_parts.append("        let currentColor = '#000000';")
    html_parts.append("")
    html_parts.append("        function resizeCanvas() {")
    html_parts.append("            canvas.width = window.innerWidth;")
    html_parts.append("            canvas.height = window.innerHeight;")
    html_parts.append("        }")
    html_parts.append("        resizeCanvas();")
    html_parts.append("        window.addEventListener('resize', resizeCanvas);")
    html_parts.append("")
    html_parts.append("        let isDrawingMode = false;")
    html_parts.append("        let isEraser = false;")
    html_parts.append("        ")
    html_parts.append("        const drawingToggleBtn = document.getElementById('drawingToggleBtn');")
    html_parts.append("        const drawingControls = document.getElementById('drawingControls');")
    html_parts.append("        ")
    html_parts.append("        drawingToggleBtn.addEventListener('click', function() {")
    html_parts.append("            if (drawingControls.classList.contains('visible')) {")
    html_parts.append("                drawingControls.classList.remove('visible');")
    html_parts.append("                canvas.classList.remove('drawing');")
    html_parts.append("                isDrawingMode = false;")
    html_parts.append("            } else {")
    html_parts.append("                drawingControls.classList.add('visible');")
    html_parts.append("                canvas.classList.add('drawing');")
    html_parts.append("                isDrawingMode = true;")
    html_parts.append("            }")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        document.getElementById('clearDrawing').addEventListener('click', function() {")
    html_parts.append("            ctx.clearRect(0, 0, canvas.width, canvas.height);")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        document.querySelectorAll('.color-btn').forEach(btn => {")
    html_parts.append("            btn.addEventListener('click', function() {")
    html_parts.append("                document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));")
    html_parts.append("                if (document.getElementById('eraserBtn')) {")
    html_parts.append("                    document.getElementById('eraserBtn').classList.remove('active');")
    html_parts.append("                }")
    html_parts.append("                this.classList.add('active');")
    html_parts.append("                currentColor = this.getAttribute('data-color');")
    html_parts.append("                isEraser = false;")
    html_parts.append("            });")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        if (document.getElementById('eraserBtn')) {")
    html_parts.append("            document.getElementById('eraserBtn').addEventListener('click', function() {")
    html_parts.append("                document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));")
    html_parts.append("                this.classList.toggle('active');")
    html_parts.append("                isEraser = this.classList.contains('active');")
    html_parts.append("            });")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        canvas.addEventListener('mousedown', function(e) {")
    html_parts.append("            if (!isDrawingMode) return;")
    html_parts.append("            e.stopPropagation();")
    html_parts.append("            isDrawing = true;")
    html_parts.append("            ctx.beginPath();")
    html_parts.append("            ctx.moveTo(e.clientX, e.clientY);")
    html_parts.append("            if (isEraser) {")
    html_parts.append("                ctx.globalCompositeOperation = 'destination-out';")
    html_parts.append("                ctx.lineWidth = 10;")
    html_parts.append("            } else {")
    html_parts.append("                ctx.globalCompositeOperation = 'source-over';")
    html_parts.append("                ctx.strokeStyle = currentColor;")
    html_parts.append("                ctx.lineWidth = 3;")
    html_parts.append("            }")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        canvas.addEventListener('mousemove', function(e) {")
    html_parts.append("            if (!isDrawing) return;")
    html_parts.append("            e.stopPropagation();")
    html_parts.append("            ctx.lineTo(e.clientX, e.clientY);")
    html_parts.append("            ctx.lineCap = 'round';")
    html_parts.append("            ctx.stroke();")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        canvas.addEventListener('mouseup', function() {")
    html_parts.append("            isDrawing = false;")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        canvas.addEventListener('mouseleave', function() {")
    html_parts.append("            isDrawing = false;")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        // Touch events for mobile")
    html_parts.append("        canvas.addEventListener('touchstart', function(e) {")
    html_parts.append("            if (!isDrawing) return;")
    html_parts.append("            e.preventDefault();")
    html_parts.append("            const touch = e.touches[0];")
    html_parts.append("            ctx.beginPath();")
    html_parts.append("            ctx.moveTo(touch.clientX, touch.clientY);")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        canvas.addEventListener('touchmove', function(e) {")
    html_parts.append("            if (!isDrawing) return;")
    html_parts.append("            e.preventDefault();")
    html_parts.append("            const touch = e.touches[0];")
    html_parts.append("            ctx.lineTo(touch.clientX, touch.clientY);")
    html_parts.append("            ctx.strokeStyle = currentColor;")
    html_parts.append("            ctx.lineWidth = 3;")
    html_parts.append("            ctx.lineCap = 'round';")
    html_parts.append("            ctx.stroke();")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        canvas.addEventListener('touchend', function() {")
    html_parts.append("            isDrawing = false;")
    html_parts.append("        });")
    html_parts.append("    </script>")
    html_parts.append("</body>")
    html_parts.append("</html>")
    
    return '\n'.join(html_parts)


def render_slide_content(slide: Slide) -> str:
    """Рендерить вміст одного слайду"""
    content = slide.content.strip() if slide.content else ""

    if slide.slide_type == "@1":
        # Заголовок
        if not content:
            return "            <h1>Заголовок</h1>"
        return f"            <h1>{process_text(content)}</h1>"
    
    elif slide.slide_type == "@2":
        # Підзаголовок
        if not content:
            return "            <h2>Підзаголовок</h2>"
        return f"            <h2>{process_text(content)}</h2>"
    
    elif slide.slide_type == "@3":
        # Основний текст з підтримкою стилів
        if not content:
            return "            <div></div>"
        processed = process_text(content)
        # Латинські слова - курсив
        processed = process_latin_italic(processed)
        return f"            <div>{processed}</div>"
    
    elif slide.slide_type == "@4":
        # Визначення (в рамці)
        if not content:
            return "            <div class='definition'></div>"
        processed = process_text(content)
        return f"            <div class='definition'>{processed}</div>"
    
    elif slide.slide_type == "@5":
        # Багаторядковий код
        code_content = content.strip() if content else ""
        return f"            <pre><code>{escape_html(code_content)}</code></pre>"
    
    elif slide.slide_type == "@6":
        # Задача
        if not content:
            return "            <div class='task'>Задача</div>"
        processed = process_text(content)
        return f"            <div class='task'>{processed}</div>"
    
    elif slide.slide_type == "@7":
        # Таблиця (CSV)
        if not content:
            return "            <div class='table-container'><p>Порожня таблиця</p></div>"
        return render_table(content)
    
    return f"            <div>{process_text(content) if content else ''}</div>"


def process_text(text: str) -> str:
    """
    Обробляє текст слайду @3:
    - {{код}} -> <code>код</code>
    - {виділений} -> <strong>виділений</strong>
    - [[посилання]] -> <img src="посилання" alt="посилання">
    """
    # Подвійні фігурні дужки - код
    text = re.sub(r'\{\{([^}]+)\}\}', r'<code>\1</code>', text)
    
    # Одинарні фігурні дужки - виділений текст
    text = re.sub(r'\{([^}]+)\}', r'<strong>\1</strong>', text)
    
    # Подвійні квадратні дужки - посилання/зображення
    def process_link(match):
        link = match.group(1)
        if link.startswith('http://') or link.startswith('https://'):
            return f'<a href="{link}" target="_blank">{link}</a>'
        return f'<img src="{link}" alt="{link}">'
    
    text = re.sub(r'\[\[([^\]]+)\]\]', process_link, text)
    
    # Замінюємо переноси рядків на <br>
    text = text.replace('\n', '<br>')
    
    return text


def process_latin_italic(text: str) -> str:
    """Перетворює латинські слова на курсив"""
    def italicize_latin(match):
        word = match.group(0)
        return f'<span class="italic">{word}</span>'

    text = re.sub(r'\b[a-zA-Z]{2,}\b', italicize_latin, text)
    return text


def render_table(csv_content: str) -> str:
    """Рендерить таблицю з CSV даних"""
    lines = [line.strip() for line in csv_content.strip().split('\n') if line.strip()]
    if not lines:
        return "            <div>Порожня таблиця</div>"
    
    html_parts = ["            <div class='table-container'>", "                <table>"]
    
    for i, line in enumerate(lines):
        cells = [cell.strip() for cell in line.split(',')]
        tag = 'th' if i == 0 else 'td'
        html_parts.append("                    <tr>")
        for cell in cells:
            html_parts.append(f"                        <{tag}>{escape_html(cell)}</{tag}>")
        html_parts.append("                    </tr>")
    
    html_parts.append("                </table>")
    html_parts.append("            </div>")
    
    return '\n'.join(html_parts)


def render_html_document(slides: List[Slide], language: str = "python", doc_type: str = "html-stu") -> str:
    """
    Генерує HTML документ зі слайдів (всі слайди один за одним, як блоки).
    Спочатку показується перший слайд, далі з'являються наступні при прокрутці.
    """
    html_parts = []
    html_parts.append("<!DOCTYPE html>")
    html_parts.append("<html lang='uk'>")
    html_parts.append("<head>")
    html_parts.append("    <meta charset='UTF-8'>")
    html_parts.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html_parts.append("    <title>Презентація - Документ</title>")
    html_parts.append("    <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css'>")
    html_parts.append("    <style>")
    html_parts.append("        body { position: relative; margin: 0; padding: 0; }")
    html_parts.append("        .document-container { max-width: 900px; margin: 0 auto; padding: 2rem; }")
    html_parts.append("        .slide-block { margin-bottom: 3rem; padding: 2rem; border-left: 4px solid #0066cc; background: #f8f9fa; border-radius: 0.5rem; opacity: 0; transform: translateY(20px); transition: opacity 0.6s ease, transform 0.6s ease; display: none; text-align: center; }")
    html_parts.append("        .slide-block.visible { opacity: 1; transform: translateY(0); display: block; }")
    html_parts.append("        .slide-block h1 { font-size: 2.5rem; margin-bottom: 1rem; color: #0066cc; text-align: center; }")
    html_parts.append("        .slide-block h2 { font-size: 2rem; margin-bottom: 1rem; color: #0066cc; text-align: center; }")
    html_parts.append("        .slide-block code { background: #e9ecef; padding: 0.2rem 0.4rem; border-radius: 0.25rem; }")
    html_parts.append("        .slide-block pre { background: #e9ecef; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; }")
    html_parts.append("        .slide-block .definition { border: 2px solid #333; padding: 1rem; margin: 1rem 0; border-radius: 0.5rem; background: white; }")
    html_parts.append("        .slide-block .task { background: #fff3cd; padding: 1rem; border-left: 4px solid #ffc107; margin: 1rem 0; }")
    html_parts.append("        .slide-block .table-container { overflow-x: auto; margin: 1rem 0; }")
    html_parts.append("        .slide-block table { width: 100%; border-collapse: collapse; }")
    html_parts.append("        .slide-block table th, .slide-block table td { border: 1px solid #ddd; padding: 0.5rem; }")
    html_parts.append("        .slide-block table th { background: #e9ecef; }")
    html_parts.append("        .slide-block .italic { font-style: italic; }")
    html_parts.append("        .slide-block img { max-width: 100%; height: auto; }")
    html_parts.append("        #drawingCanvas { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 500; pointer-events: none; }")
    html_parts.append("        #drawingCanvas.drawing { pointer-events: all; }")
    html_parts.append("        .drawing-toggle-btn { position: fixed; top: 2rem; right: 2rem; z-index: 1001; width: 50px; height: 50px; border-radius: 50%; background: #0066cc; color: white; border: none; cursor: pointer; font-size: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; }")
    html_parts.append("        .drawing-toggle-btn:hover { background: #0052a3; }")
    html_parts.append("        .drawing-controls { position: fixed; top: 6rem; right: 2rem; z-index: 1001; background: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.2); display: none; }")
    html_parts.append("        .drawing-controls.visible { display: block; }")
    html_parts.append("        .drawing-controls button { margin: 0.25rem; display: block; width: 100%; }")
    html_parts.append("        .color-picker { display: flex; gap: 0.5rem; margin: 0.5rem 0; flex-wrap: wrap; }")
    html_parts.append("        .color-btn { width: 30px; height: 30px; border: 2px solid #333; border-radius: 50%; cursor: pointer; }")
    html_parts.append("        .color-btn.active { border-color: #0066cc; border-width: 3px; }")
    html_parts.append("        .eraser-btn { width: 30px; height: 30px; border: 2px solid #333; border-radius: 4px; cursor: pointer; background: white; display: flex; align-items: center; justify-content: center; font-size: 18px; }")
    html_parts.append("        .eraser-btn.active { border-color: #0066cc; border-width: 3px; background: #f0f0f0; }")
    
    # Додаткові стилі для викладацького формату
    if doc_type == "html-tut":
        html_parts.append("        /* Викладацький формат - розширені стилі */")
        html_parts.append("        .slide-block { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-left-color: #3f51b5; }")
        html_parts.append("        .slide-block h1 { color: #1a237e; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); }")
        html_parts.append("        .slide-block h2 { color: #283593; border-bottom: 2px solid #3f51b5; padding-bottom: 0.5rem; }")
        html_parts.append("        .slide-block .definition { background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #3f51b5; }")
        html_parts.append("        .slide-block .task { background: linear-gradient(135deg, #fff3cd 0%, #ffe082 100%); box-shadow: 0 2px 4px rgba(0,0,0,0.1); }")
        html_parts.append("        .slide-block code { background: #263238; color: #aed581; font-weight: bold; }")
        html_parts.append("        .slide-block pre { background: #263238; color: #aed581; border: 2px solid #37474f; }")
        html_parts.append("        .slide-block table { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }")
    html_parts.append("    </style>")
    html_parts.append("</head>")
    html_parts.append("<body>")
    html_parts.append("    <canvas id='drawingCanvas'></canvas>")
    html_parts.append("    <button class='drawing-toggle-btn' id='drawingToggleBtn' title='Малювання'>✏️</button>")
    html_parts.append("    <div class='drawing-controls' id='drawingControls'>")
    html_parts.append("        <button id='clearDrawing'>Очистити</button>")
    html_parts.append("        <div class='color-picker'>")
    html_parts.append("            <div class='color-btn active' data-color='#000000' style='background: #000000;' title='Чорний'></div>")
    html_parts.append("            <div class='color-btn' data-color='#ff0000' style='background: #ff0000;' title='Червоний'></div>")
    html_parts.append("            <div class='color-btn' data-color='#0000ff' style='background: #0000ff;' title='Синій'></div>")
    html_parts.append("            <div class='color-btn' data-color='#00ff00' style='background: #00ff00;' title='Зелений'></div>")
    html_parts.append("            <div class='color-btn' data-color='#ffff00' style='background: #ffff00;' title='Жовтий'></div>")
    html_parts.append("            <div class='color-btn' data-color='#ff00ff' style='background: #ff00ff;' title='Пурпурний'></div>")
    html_parts.append("            <div class='color-btn' data-color='#ffffff' style='background: #ffffff;' title='Білий'></div>")
    html_parts.append("            <div class='eraser-btn' id='eraserBtn' title='Ластик'>🧹</div>")
    html_parts.append("        </div>")
    html_parts.append("    </div>")
    html_parts.append("    <div class='document-container'>")
    
    # Генеруємо слайди як блоки
    for i, slide in enumerate(slides):
        html_parts.append(f"        <div class='slide-block' id='block-{i}'>")
        html_parts.append(render_slide_content(slide))
        html_parts.append("        </div>")
    
    html_parts.append("    </div>")
    
    # JS для показу блоків по кліку
    html_parts.append("    <script>")
    html_parts.append("        const blocks = document.querySelectorAll('.slide-block');")
    html_parts.append("        let currentBlock = 0;")
    html_parts.append("        ")
    html_parts.append("        // Показуємо перший блок одразу")
    html_parts.append("        if (blocks.length > 0) {")
    html_parts.append("            blocks[0].classList.add('visible');")
    html_parts.append("        }")
    html_parts.append("        ")
    html_parts.append("        function showNextBlock() {")
    html_parts.append("            if (currentBlock < blocks.length - 1) {")
    html_parts.append("                currentBlock++;")
    html_parts.append("                blocks[currentBlock].classList.add('visible');")
    html_parts.append("                // Прокручуємо до нового блоку")
    html_parts.append("                setTimeout(() => {")
    html_parts.append("                    blocks[currentBlock].scrollIntoView({ behavior: 'smooth', block: 'start' });")
    html_parts.append("                }, 100);")
    html_parts.append("            }")
    html_parts.append("        }")
    html_parts.append("        ")
    html_parts.append("        // Обробка кліків - тільки на body/document, не на інтерактивних елементах")
    html_parts.append("        document.body.addEventListener('click', (e) => {")
    html_parts.append("            // Не показуємо наступний блок, якщо клікнули на посилання, кнопку, input, textarea, canvas")
    html_parts.append("            const tag = e.target.tagName;")
    html_parts.append("            if (tag === 'A' || tag === 'BUTTON' || tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || tag === 'CANVAS') return;")
    html_parts.append("            // Перевіряємо, чи клікнули на батьківський елемент з посиланням, кнопкою або canvas")
    html_parts.append("            if (e.target.closest('a') || e.target.closest('button') || e.target.closest('canvas')) return;")
    html_parts.append("            showNextBlock();")
    html_parts.append("        });")
    html_parts.append("        ")
    html_parts.append("        // Обробка клавіш")
    html_parts.append("        document.addEventListener('keydown', (e) => {")
    html_parts.append("            if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'Enter') {")
    html_parts.append("                e.preventDefault();")
    html_parts.append("                showNextBlock();")
    html_parts.append("            }")
    html_parts.append("        });")
    html_parts.append("        ")
    html_parts.append("        // Підказка для користувача")
    html_parts.append("        if (blocks.length > 1) {")
    html_parts.append("            const hint = document.createElement('div');")
    html_parts.append("            hint.style.cssText = 'position: fixed; bottom: 2rem; right: 2rem; background: rgba(0,0,0,0.7); color: white; padding: 1rem; border-radius: 0.5rem; z-index: 1000; font-size: 0.9rem; pointer-events: none;';")
    html_parts.append("            hint.textContent = 'Клікніть або натисніть → для наступного слайду';")
    html_parts.append("            document.body.appendChild(hint);")
    html_parts.append("            setTimeout(() => hint.remove(), 5000);")
    html_parts.append("        }")
    html_parts.append("        ")
    html_parts.append("        // Малювання")
    html_parts.append("        const canvas = document.getElementById('drawingCanvas');")
    html_parts.append("        const ctx = canvas.getContext('2d');")
    html_parts.append("        let isDrawing = false;")
    html_parts.append("        let currentColor = '#000000';")
    html_parts.append("")
    html_parts.append("        function resizeCanvas() {")
    html_parts.append("            canvas.width = window.innerWidth;")
    html_parts.append("            canvas.height = window.innerHeight;")
    html_parts.append("        }")
    html_parts.append("        resizeCanvas();")
    html_parts.append("        window.addEventListener('resize', resizeCanvas);")
    html_parts.append("")
    html_parts.append("        let isDrawingMode = false;")
    html_parts.append("        let isEraser = false;")
    html_parts.append("        ")
    html_parts.append("        const drawingToggleBtn = document.getElementById('drawingToggleBtn');")
    html_parts.append("        const drawingControls = document.getElementById('drawingControls');")
    html_parts.append("        ")
    html_parts.append("        drawingToggleBtn.addEventListener('click', function() {")
    html_parts.append("            if (drawingControls.classList.contains('visible')) {")
    html_parts.append("                drawingControls.classList.remove('visible');")
    html_parts.append("                canvas.classList.remove('drawing');")
    html_parts.append("                isDrawingMode = false;")
    html_parts.append("            } else {")
    html_parts.append("                drawingControls.classList.add('visible');")
    html_parts.append("                canvas.classList.add('drawing');")
    html_parts.append("                isDrawingMode = true;")
    html_parts.append("            }")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        document.getElementById('clearDrawing').addEventListener('click', function() {")
    html_parts.append("            ctx.clearRect(0, 0, canvas.width, canvas.height);")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        document.querySelectorAll('.color-btn').forEach(btn => {")
    html_parts.append("            btn.addEventListener('click', function() {")
    html_parts.append("                document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));")
    html_parts.append("                if (document.getElementById('eraserBtn')) {")
    html_parts.append("                    document.getElementById('eraserBtn').classList.remove('active');")
    html_parts.append("                }")
    html_parts.append("                this.classList.add('active');")
    html_parts.append("                currentColor = this.getAttribute('data-color');")
    html_parts.append("                isEraser = false;")
    html_parts.append("            });")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        if (document.getElementById('eraserBtn')) {")
    html_parts.append("            document.getElementById('eraserBtn').addEventListener('click', function() {")
    html_parts.append("                document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));")
    html_parts.append("                this.classList.toggle('active');")
    html_parts.append("                isEraser = this.classList.contains('active');")
    html_parts.append("            });")
    html_parts.append("        }")
    html_parts.append("")
    html_parts.append("        canvas.addEventListener('mousedown', function(e) {")
    html_parts.append("            if (!isDrawingMode) return;")
    html_parts.append("            e.stopPropagation();")
    html_parts.append("            isDrawing = true;")
    html_parts.append("            ctx.beginPath();")
    html_parts.append("            ctx.moveTo(e.clientX, e.clientY);")
    html_parts.append("            if (isEraser) {")
    html_parts.append("                ctx.globalCompositeOperation = 'destination-out';")
    html_parts.append("                ctx.lineWidth = 10;")
    html_parts.append("            } else {")
    html_parts.append("                ctx.globalCompositeOperation = 'source-over';")
    html_parts.append("                ctx.strokeStyle = currentColor;")
    html_parts.append("                ctx.lineWidth = 3;")
    html_parts.append("            }")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        canvas.addEventListener('mousemove', function(e) {")
    html_parts.append("            if (!isDrawing) return;")
    html_parts.append("            e.stopPropagation();")
    html_parts.append("            ctx.lineTo(e.clientX, e.clientY);")
    html_parts.append("            ctx.lineCap = 'round';")
    html_parts.append("            ctx.stroke();")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        canvas.addEventListener('mouseup', function() {")
    html_parts.append("            isDrawing = false;")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        canvas.addEventListener('mouseleave', function() {")
    html_parts.append("            isDrawing = false;")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        // Touch events for mobile")
    html_parts.append("        canvas.addEventListener('touchstart', function(e) {")
    html_parts.append("            if (!isDrawing) return;")
    html_parts.append("            e.preventDefault();")
    html_parts.append("            const touch = e.touches[0];")
    html_parts.append("            ctx.beginPath();")
    html_parts.append("            ctx.moveTo(touch.clientX, touch.clientY);")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        canvas.addEventListener('touchmove', function(e) {")
    html_parts.append("            if (!isDrawing) return;")
    html_parts.append("            e.preventDefault();")
    html_parts.append("            const touch = e.touches[0];")
    html_parts.append("            ctx.lineTo(touch.clientX, touch.clientY);")
    html_parts.append("            ctx.strokeStyle = currentColor;")
    html_parts.append("            ctx.lineWidth = 3;")
    html_parts.append("            ctx.lineCap = 'round';")
    html_parts.append("            ctx.stroke();")
    html_parts.append("        });")
    html_parts.append("")
    html_parts.append("        canvas.addEventListener('touchend', function() {")
    html_parts.append("            isDrawing = false;")
    html_parts.append("        });")
    html_parts.append("    </script>")
    html_parts.append("</body>")
    html_parts.append("</html>")
    
    return '\n'.join(html_parts)


def render_html_full_document(slides: List[Slide], language: str = "python", doc_type: str = "html-stu") -> str:
    """
    Генерує HTML документ зі слайдів (всі слайди відображені одразу один за одним).
    """
    html_parts = []
    html_parts.append("<!DOCTYPE html>")
    html_parts.append("<html lang='uk'>")
    html_parts.append("<head>")
    html_parts.append("    <meta charset='UTF-8'>")
    html_parts.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html_parts.append("    <title>Документ</title>")
    html_parts.append("    <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css'>")
    html_parts.append("    <style>")
    html_parts.append("        .document-container { max-width: 900px; margin: 0 auto; padding: 2rem; }")
    html_parts.append("        .slide-block { margin-bottom: 3rem; padding: 2rem; border-left: 4px solid #0066cc; background: #f8f9fa; border-radius: 0.5rem; }")
    html_parts.append("        .slide-block h1 { font-size: 2.5rem; margin-bottom: 1rem; color: #0066cc; }")
    html_parts.append("        .slide-block h2 { font-size: 2rem; margin-bottom: 1rem; color: #0066cc; }")
    html_parts.append("        .slide-block code { background: #e9ecef; padding: 0.2rem 0.4rem; border-radius: 0.25rem; }")
    html_parts.append("        .slide-block pre { background: #e9ecef; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; }")
    html_parts.append("        .slide-block .definition { border: 2px solid #333; padding: 1rem; margin: 1rem 0; border-radius: 0.5rem; background: white; }")
    html_parts.append("        .slide-block .task { background: #fff3cd; padding: 1rem; border-left: 4px solid #ffc107; margin: 1rem 0; }")
    html_parts.append("        .slide-block .table-container { overflow-x: auto; margin: 1rem 0; }")
    html_parts.append("        .slide-block table { width: 100%; border-collapse: collapse; }")
    html_parts.append("        .slide-block table th, .slide-block table td { border: 1px solid #ddd; padding: 0.5rem; }")
    html_parts.append("        .slide-block table th { background: #e9ecef; }")
    html_parts.append("        .slide-block .italic { font-style: italic; }")
    html_parts.append("        .slide-block img { max-width: 100%; height: auto; }")
    
    # Додаткові стилі для викладацького формату
    if doc_type == "html-tut":
        html_parts.append("        /* Викладацький формат - розширені стилі */")
        html_parts.append("        .slide-block { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-left-color: #3f51b5; }")
        html_parts.append("        .slide-block h1 { color: #1a237e; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); }")
        html_parts.append("        .slide-block h2 { color: #283593; border-bottom: 2px solid #3f51b5; padding-bottom: 0.5rem; }")
        html_parts.append("        .slide-block .definition { background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #3f51b5; }")
        html_parts.append("        .slide-block .task { background: linear-gradient(135deg, #fff3cd 0%, #ffe082 100%); box-shadow: 0 2px 4px rgba(0,0,0,0.1); }")
        html_parts.append("        .slide-block code { background: #263238; color: #aed581; font-weight: bold; }")
        html_parts.append("        .slide-block pre { background: #263238; color: #aed581; border: 2px solid #37474f; }")
        html_parts.append("        .slide-block table { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }")
    
    html_parts.append("    </style>")
    html_parts.append("</head>")
    html_parts.append("<body>")
    html_parts.append("    <div class='document-container'>")
    
    # Генеруємо всі слайди одразу
    for i, slide in enumerate(slides):
        html_parts.append(f"        <div class='slide-block' id='block-{i}'>")
        html_parts.append(render_slide_content(slide))
        html_parts.append("        </div>")
    
    html_parts.append("    </div>")
    html_parts.append("</body>")
    html_parts.append("</html>")
    
    return '\n'.join(html_parts)


def render_markdown(slides: List[Slide]) -> str:
    """Генерує Markdown презентацію"""
    md_parts = []
    
    for slide in slides:
        if slide.slide_type == "@1":
            md_parts.append(f"# {slide.content}\n")
        elif slide.slide_type == "@2":
            md_parts.append(f"## {slide.content}\n")
        elif slide.slide_type == "@3":
            md_parts.append(f"{slide.content}\n")
        elif slide.slide_type == "@4":
            md_parts.append(f"```\n{slide.content}\n```\n")
        elif slide.slide_type == "@5":
            md_parts.append(f"```{slide.content}\n```\n")
        elif slide.slide_type == "@6":
            md_parts.append(f"> **Задача:** {slide.content}\n")
        elif slide.slide_type == "@7":
            md_parts.append(f"{slide.content}\n")
        md_parts.append("\n---\n\n")
    
    return ''.join(md_parts)


def escape_html(text: str) -> str:
    """Екранує HTML символи"""
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))