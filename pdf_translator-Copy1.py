#!/usr/bin/env python
# coding: utf-8

# In[1]:


font = ImageFont.truetype('Your font.ttf', size=100)
Auth_key = 'Your DeepL Key'



# 번역 api 요청
def DeepL(text, Auth_key, target = 'ko' ):
    import requests
    import json
    url = 'https://api-free.deepl.com/v2/translate'
    headers = {
    'Content-Type': 'application/json; charset = utf-8',
    'Authorization': f'DeepL-Auth-Key {Auth_key}',
    }
    data = {'target_lang': 'ko', 'text': [text]}
    response = requests.post(url, data = json.dumps(data), headers=headers)
    
    return response.json()['translations'][0]['text']

def text_to_fit(image, text, font, container_width, container_height):
    from PIL import ImageDraw, ImageFont

    def compute_text_height(lines, font, padding):
        draw = ImageDraw.Draw(image)
        total_height = -15 #경험적인 오프셋
        for line in lines:
            ascent, _ = font.getmetrics()
            _, (_, offset_y) = font.font.getsize(line)
            line_height = ascent - offset_y
            if total_height == -10:
                total_height += line_height
            else:
                total_height += line_height + padding
        return total_height
    
    # 폰트 크기 조정 최적의 크기
    font_size = font.size
    while font_size > 0:
        font = ImageFont.truetype(font.path, font_size)
        ascent, _ = font.getmetrics()
        _, (_, offset_y) = font.font.getsize(text[0])
        font_h = ascent - offset_y
        padding = int(font_h*1)
        draw = ImageDraw.Draw(image)
        lines = []
        current_line = ''
        current_width = 0
        font_h = ascent - offset_y
        for char in text:
            if char == '\n':
                lines.append(current_line)
                current_line = ''
                current_width = 0
                continue
            char_width, _ = draw.textbbox((0, 0), char, font=font)[2:]
            if current_width + char_width <= container_width:
                current_line += char
                current_width += char_width
            else:
                if char == ' ':
                    continue
                lines.append(current_line)
                current_line = char
                current_width = char_width
        lines.append(current_line)
        
        if compute_text_height(lines, font, padding) <= container_height:
            break  
        font_size -= 1 
    
    return lines, font, padding






def merge_images_vertically(patches, spacing=300):
    images = [patch[0] for patch in patches]
    max_width = max(image.width for image in images)
    total_height = sum(image.height for image in images) + (spacing * (len(images) - 1))
    merged_image = Image.new('RGB', (max_width, total_height), 'white')

    y_offsets = []
    y_offset = 0
    for image in images:
        y_offsets.append(y_offset)
        merged_image.paste(image, (0, y_offset))
        y_offset += image.height + spacing

    return merged_image, y_offsets

def text_processer(text_block, edit_re):
    import re
    tes = ''
    min_x = float("inf")
    min_y = float("inf")
    max_x = 0
    max_y = 0                

    parno = None  # parno를 None으로 초기화

    for te in text_block:
        if te[1]:  # te[1]이 존재하면 (즉, 텍스트가 비어있지 않으면)
            if parno is not None and parno != te[0][1]:
                # parno 값이 변경되었으면 개행 문자를 추가
                tes += "\n    " + te[1]
            else:
                # parno 값이 변경되지 않았으면 공백과 함께 텍스트를 추가
                if len(tes) > 0:
                    tes += " "  # 첫 번째 요소가 아니라면 공백을 추가
                tes += te[1]
            parno = te[0][1]  # parno 값을 현재 te[0][1]으로 업데이트

        min_x = min(min_x, te[2][0])
        min_y = min(min_y, te[2][1])
        max_x = max(max_x, te[2][0]+te[2][2])
        max_y = max(max_y, te[2][1]+te[2][3])
        if edit_re:
            for obj, to in edit_re:
                pattern = re.compile(obj)
                tes = pattern.sub(to, tes)

    if not tes:
        return None
    return [tes, [min_x, min_y, max_x, max_y]]
# OCR 적용, 텍스트 블럭 생성
def ocr_image2blocks(data):
    text_block = []

    # pytesseract에서 얻은 데이터를 순회하며 문장 단위로 추출
    for i in range(len(data['level'])):
        if data['block_num'][i] > 0:
            x, y, width, height = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            text = data['text'][i]
            if text.strip():  # 공백이 아닌 텍스트만
                block_num = data['block_num'][i]
                par_num = data['par_num'][i]

                # 같은 텍스트 블록에 속하는 텍스트들을 하나로
                if (block_num, par_num) not in text_block:
                    text_block.append([[block_num, par_num], text, [x, y, width, height]])
                else:
                    index = next((index for index, item in enumerate(text_block) if item[0] == (block_num, par_num)), None)
                    if index is not None:
                        # 기존 텍스트에 추가
                        _, existing_text, _ = text_blocks[index]
                        text_block[index] = [[block_num, par_num], existing_text + " " + text, [x, y, width, height]]
    return text_block

def image_translator(image, edit_re):
    import pytesseract
    from PIL import Image, ImageDraw, ImageFont
    from pytesseract import Output

    config = ('-l eng --oem 3 --psm 1')
    data = pytesseract.image_to_data(image, config = config, output_type=Output.DICT)

    text_blocks = ocr_image2blocks(data)

    blocks = {}
    block_numbers = []

    estimated_font_sizes = {}


    for block in text_blocks:
        blockno = block[0][0]
        if blockno in blocks:
            blocks[blockno].append(block)
        else:
            block_numbers.append(blockno)
            blocks[blockno] = [block]

    for blockno, block_items in blocks.items():
        max_height = max(item[2][3] for item in block_items)  # item[2][3]는 높이(height)
        estimated_font_sizes[blockno] = max_height

    text_patches = []
    for block_number in block_numbers:
        text_block = blocks[block_number]
        result = text_processer(text_block, edit_re)
        if result is not None:
            text_patches.append(result)

    return text_patches, blocks, text_blocks, estimated_font_sizes

def adjust_patch_coordinates(original_images, patches, y_offsets):
    adjusted_patches = []
    accumulated_height = 0

    for patch in patches:
        text, (min_x, min_y, max_x, max_y) = patch

        # 패치가 속한 이미지와 해당 이미지에서의 좌표
        for i, (img, bbox) in enumerate(original_images):
            original_x1, original_y1, original_x2, original_y2 = bbox
            if y_offsets[i] <= min_y < y_offsets[i] + (original_y2 - original_y1):
                # text_patch가 해당 patch에 속한다고 판단될 때
                adjusted_min_x = min_x + original_x1
                adjusted_max_x = max_x + original_x1
                adjusted_min_y = min_y - y_offsets[i] + original_y1
                adjusted_max_y = max_y - y_offsets[i] + original_y1

                adjusted_patch = (text, (adjusted_min_x, adjusted_min_y, adjusted_max_x, adjusted_max_y))
                adjusted_patches.append(adjusted_patch)
                break  # 해당 패치를 찾았으니 루프 종료

    return adjusted_patches

def translate_module(patches):
    result_patches = []
    for tes, coord in patches:
        success = False
        attempts = 0

        while not success and attempts < 3:
            try:
                tes_translated = DeepL(tes, Auth_key)
                success = True  # 번역 성공
            except Exception as e:
                attempts += 1  # 실패 시 시도 횟수 증가
                if attempts >= 3:
                    # 세 번 시도 후에도 실패하면 루프를 종료하고 오류를 처리
                    print(f"Translation failed after 3 attempts: {e}")
                    break
                else:
                    print(f"Retrying... ({attempts})")
        
        if success:
            result_patches.append((tes_translated, coord))
            result_bool = True
        else:
            result_patches.append((tes, coord))
            result_bool = False

    return result_patches, result_bool


def attach_patches(image, patches, translate = False):
    from PIL import ImageDraw
    work_image = image.copy()
    draw = ImageDraw.Draw(work_image)
    for i, coord in patches: 
        if translate:
            draw.rectangle(coord, fill="white")
        else:
            try:
                draw.rectangle(coord, fill="green")
            except Exception as e:
                print(e)

    for tes, coord in patches:
        current_h = coord[1] -10 # 경험적 오프셋
        text_width = coord[2] - coord[0] +5
        text_height = coord[3] - coord[1]
        
        wrapped_text, result_font, padding = text_to_fit(image, tes, font, text_width, text_height)
        for line in wrapped_text:
            ascent, descent = result_font.getmetrics()
            (width, baseline), (offset_x, offset_y) = font.font.getsize(line)
            draw.text((coord[0], current_h), line, fill="black", font=result_font)
            current_h += ascent - offset_y + padding

    return work_image


# In[ ]:


import tkinter as tk
from tkinter import filedialog, ttk
import fitz  # PyMuPDF
from PIL import Image, ImageTk, ImageFont
import pytesseract
import io
import re

class PDFTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x400")
        
        # 버튼과 프로그레스바가 배치될 상단 프레임
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)
    
        self.progress = ttk.Progressbar(self.top_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Load PDF 버튼 배치
        self.load_pdf_button = tk.Button(self.top_frame, text="Load PDF", command=self.load_pdf)
        self.load_pdf_button.pack(side=tk.LEFT)
        
        # Next, Previous, Submit 버튼 배치
        self.previous_page_button = tk.Button(self.top_frame, text="Previous", command=self.Previous_page)
        self.next_page_button = tk.Button(self.top_frame, text="Next", command=self.Next_page)
        self.submit_button = tk.Button(self.top_frame, text="Submit", command=self.Submit_button)
        self.edit_button = tk.Button(self.top_frame, text="Edit", command=self.edit)
        self.Translate_button = tk.Button(self.top_frame, text="Translate", command=self.Translate)
        self.Export_button = tk.Button(self.top_frame, text="Export", command=self.save_pdf)
        
        # 캔버스와 텍스트 박스가 배치될 컨테이너
        self.aspect_ratio = 2/1.414
        self.container = tk.Frame(self.root)
        self.canvas = tk.Canvas(self.container, bg='blue')
        
        self.text_box = tk.Text(self.container)
        self.text_menu = tk.Menu(self.text_box, tearoff=0)
        self.text_menu.add_command(label="잘라내기", command=self.cut_text)
        self.text_menu.add_command(label="복사", command=self.copy_text)
        self.text_menu.add_command(label="붙여넣기", command=self.paste_text)
        self.text_box.bind("<Button-2>", self.show_text_menu)
        self.root.bind_all("<Control-x>", lambda event: self.cut_text())
        self.root.bind_all("<Control-c>", lambda event: self.copy_text())
        self.root.bind_all("<Control-v>", lambda event: self.paste_text())

        
        self.root.bind("<Right>", self.Rigth_arrow)
        self.root.bind("<Left>", self.Left_arrow)
        
        self.adjust_container_size()

        # Add menu options
        menu = tk.Menu(root)
        root.config(menu=menu)
        file_menu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open PDF", command=self.load_pdf)
        self.PDF_FILE_PATH = None
        
        self.dpi = 300
        self.pages = []
        self.result_pages = []
        self.doc = None
        self.current_page = tk.IntVar(value=0)
        self.current_page_image = None
        self.total_pages = 0
        self.ratio = None # 원본 이미지와 표시 이미지의 크기 비율
        self.current_page.trace("w", self.change_page_handle)
        self.load_on = False
        self.translated = False
        self.submitted = False
        self._resize_debounce = False
        
        self.width_scale_factor = 0
        self.height_scale_factor = 0

        
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.current_rectangles = []  # 현재 페이지의 사각형
        self.page_rectangles = {} # 전체 페이지의 사각형
        
        # 전체 텍스트, 번역 텍스트
        self.total_page_text = {}
        self.total_page_translated_text = {}
        
        
        
        
        
        # 마우스 이벤트
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<Button-2>", self.right_button_click)
        self.root.bind("<Button-1>", self.on_root_click)
        
        # 창 사이즈 변경
        self.root.bind('<Configure>', self.resize_handle)
        
        # 윈도우 생성 후 이벤트 핸들러를 설정
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        
        self.log_tag = None #디버깅용 깃발
    
    
##################################################### 이벤트 핸들 ###############################################################    

    def change_page_handle(self, *args):
        self.update_buttons()
        self.current_rectangles = []
        self.canvas.delete("all")
        self.show_page()
        
    def resize_handle(self, *args):
        if self.current_page_image:
            self.show_page(quality='low')
        self.adjust_container_size()
        if self._resize_debounce:
            self.root.after_cancel(self._resize_debounce)
        self._resize_debounce = self.root.after(500, self._finalize_resize)

    def _finalize_resize(self):
        # 조절이 완료되면 고품질 리사이징
        if self.current_page_image:
            self.show_page(quality='high')
        self.update_buttons()
        self.adjust_container_size()
        self.resize_debounce = False
        
    def cut_text(self):
        self.text_box.event_generate("<<Cut>>")
    
    def copy_text(self):
        self.text_box.event_generate("<<Copy>>")
    
    def paste_text(self):
        self.text_box.event_generate("<<Paste>>")
    
    # 마우스 우클릭 시 텍스트 메뉴 표시
    def show_text_menu(self, event):
        self.text_menu.post(event.x_root, event.y_root)

##################################################### 버튼 관련 ###############################################################    
    def Next_page(self):
        current_page_number = self.current_page.get()
        self.save_changes()
        if current_page_number < self.total_pages - 1:
            self.current_page.set(current_page_number + 1)

            
    def Previous_page(self):
        self.save_changes()
        current_page_number = self.current_page.get()
        if current_page_number > 0:
            self.current_page.set(current_page_number - 1)
            
            
    def Submit_button(self):
        self.save_changes()
        self.Submit()
        

    def update_buttons(self):
        button_height = 20
        window_height = self.root.winfo_height()
        button_y_position = window_height - button_height
        
        
        current_page_number = self.current_page.get()
        
        if current_page_number <= 0:
            self.previous_page_button.config(state=tk.DISABLED)
        else:
            self.previous_page_button.config(state=tk.NORMAL)
            
        if current_page_number >= self.total_pages - 1:
            self.next_page_button.config(state=tk.DISABLED)
            self.submit_button.config(state=tk.NORMAL)
        else:
            self.next_page_button.config(state=tk.NORMAL)
            self.submit_button.config(state=tk.NORMAL)
        
        if self.load_on:
            self.submit_button.config(state=tk.NORMAL)
        else:
            self.submit_button.config(state=tk.DISABLED)
        if self.submitted:
            self.Translate_button.config(state=tk.NORMAL)
            self.submit_button.config(state=tk.DISABLED)
        else:
            self.Translate_button.config(state=tk.DISABLED)
            
            
    def on_close(self):
        if self.page_rectangles:
            print("프로그램 종료 전 처리...")
            self.save_rectangles(self.PDF_FILE_PATH)
        self.root.destroy()
        
    def Rigth_arrow(self, *args):
        if self.root.focus_get() != self.text_box:
            self.Next_page()
        pass
    
    def Left_arrow(self, *args):
        if self.root.focus_get() != self.text_box:
            self.Previous_page()
            
    
##################################################### 마우스 관련 ###############################################################    
    def on_root_click(self, event):
        # 클릭 이벤트가 텍스트 박스에서 발생했는지 확인합니다.
        if event.widget != self.text_box:
            # 클릭이 텍스트 박스 외부에서 발생했으면, root로 포커스를 이동합니다.
            self.root.focus_set()
            
    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_move_press(self, event):
        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)

        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        # Finalize the rectangle
        if self.rect:
            original_coord_rect = [i//self.ratio for i in self.canvas.coords(self.rect)]
            #self.current_rectangles.append(original_coord_rect)
            self.current_rectangles.append({'coords': original_coord_rect, 'id': self.rect})
            self.page_rectangles[self.current_page.get()] = [rect['coords'] for rect in self.current_rectangles]
        self.rect = None
    
    def right_button_click(self, event):
        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)
        self.delete_rectangle(curX, curY)
    
    def delete_rectangle(self, curX, curY): # 우클릭시 커서를 포함하는 상자 삭제
        if self.current_rectangles:
            curX, curY = curX/self.ratio, curY/self.ratio
            for i, item in enumerate(reversed(self.current_rectangles)):
                actual_index = len(self.current_rectangles) - 1 - i
                if item['coords'][0] <= curX <= item['coords'][2] and item['coords'][1] <= curY <= item['coords'][3]:
                    self.canvas.delete(item['id'])
                    del self.current_rectangles[actual_index]
                    self.page_rectangles[self.current_page.get()] = [rect['coords'] for rect in self.current_rectangles]
                    break
            
            
##################################################### 문서 로드 ###############################################################    

    def load_pdf(self):
        self.PDF_FILE_PATH = tk.filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not self.PDF_FILE_PATH:
            return

        self.doc = fitz.open(self.PDF_FILE_PATH)
        dpi = self.dpi
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)

        for i, page in enumerate(self.doc):
            self.update_progress((i + 1) / len(self.doc) * 50)  # 업데이트 진행 상태
            page.set_cropbox(page.mediabox)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.pil_tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            self.pages.append(image)
        
        self.total_pages = len(self.pages)
        self.load_rectangles(self.PDF_FILE_PATH)
        print("Load complete")
        self.update_progress(50)
        self.load_pdf_button.pack_forget()
        self.next_page_button.pack(side=tk.RIGHT)
        self.previous_page_button.pack(side=tk.RIGHT)
        self.submit_button.pack(side=tk.RIGHT)
        self.edit_button.pack(side=tk.RIGHT)
        self.Translate_button.pack(side=tk.RIGHT)
        self.Export_button.pack(side=tk.LEFT)
        self.update_buttons()
        self.show_page()
        self.load_on = True


    def update_progress(self, progress):
        self.progress['value'] = progress
        self.root.update_idletasks()



##################################################### 리사이징 작업 ###############################################################    
# 모든 좌표 저장은 원본 크기로, 그릴땐 현재 비율로

    def adjust_container_size(self):
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height() - self.top_frame.winfo_reqheight()

        # 컨테이너의 너비와 높이 계산
        container_width = root_width
        container_height = int(container_width * self.aspect_ratio)

        if container_height > root_height:
            container_height = root_height
            container_width = int(container_height * self.aspect_ratio)

        # 캔버스와 텍스트 박스의 너비를 컨테이너의 너비와 동일하게 설정
        widget_width = container_width // 2

        # 컨테이너와 내부 위젯의 크기 및 위치 조정
        x = (root_width - container_width) // 2
        y = self.top_frame.winfo_reqheight()
        self.container.place(x=x, y=y, width=container_width, height=container_height)
        self.canvas.place(x=0, y=0, width=widget_width, height=container_height)
        self.text_box.place(x=widget_width, y=0, width=widget_width, height=container_height)


    def canvas_resize(self):
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        # 종횡비 유지
        container_width = window_width
        container_height = window_width / (self.aspect_ratio)

        if container_height > window_height:
            container_width = window_height * (self.aspect_ratio)
            container_height = window_height

        self.canvas.config(width=int(container_width // 2), height=int(container_height))
        self.text_box.config(width=int(container_width // 2), height=int(container_height))

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            
            
    def resize_paint_rectangles(self, current_page_number):
        if not self.translated:
            if self.page_rectangles.get(current_page_number, False):
                current_rects = self.page_rectangles[current_page_number]
                self.current_rectangles =[]
                for rect in current_rects:
                    scaled_rect = [int(j*self.ratio) for j in rect]
                    self.rect = self.canvas.create_rectangle(scaled_rect)

                    self.current_rectangles.append({'coords': rect, 'id': self.rect})
                    self.rect = None
        
    def resize_image(self, image, resample_filter):
        win_width, win_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        original_width, original_height = image.size
        self.ratio = win_height/original_height
        resized_image = image.resize((win_width, win_height), resample_filter)
        
        return resized_image
        
        
##################################################### 이미지 처리 ###############################################################    


    def crop_page(self, page_num):
        if not self.doc or page_num not in self.page_rectangles:
            return
        patches =[]
        page = self.pages[page_num]
        crop_area = self.page_rectangles[page_num] # 존재확인후 연산 작업할것
        for rect in crop_area:
            x1, y1, x2, y2 = map(int, rect)
            cropped_image = page.crop((x1, y1, x2, y2))
            patches.append((cropped_image, (x1, y1, x2, y2))) 
        return patches
    
    def save_pdf(self):
            # 새 PDF 문서 생성
        pdf_document = fitz.open()

        for img in self.result_pages:
            original_width, original_height = img.size
            # DPI 변경을 역산하여 원본 크기 계산
            original_width = int(original_width * (72 / self.dpi)*2)
            original_height = int(original_height * (72 / self.dpi)*2)
            img = img.resize((original_width, original_height), Image.LANCZOS)
            # PIL 이미지를 bytes로 변환
            img_byte_arr = io.BytesIO()
            #img.save(img_byte_arr, format='PNG')
            img.save(img_byte_arr, format='JPEG', quality=90)
            img_byte_arr = img_byte_arr.getvalue()

            # 새 페이지 생성 및 이미지 삽입
            pdf_page = pdf_document.new_page(width=img.size[0], height=img.size[1])
            xref = pdf_page.insert_image(pdf_page.rect, stream=img_byte_arr)
        
        path = 'Exported_'+self.PDF_FILE_PATH.rsplit('/', 1)[1]
        # PDF 문서 저장
        pdf_document.save(path)
        pdf_document.close()



        
        
##################################################### 저장, 불러오기 ###############################################################    


    def save_rectangles(self, filename):
        import pickle
        # 파일 이름에서 확장자를 제거하고 .rectangles 확장자를 추가합니다.
        save_file = filename.rsplit('.', 1)[0] + '.rectangles'

        # 저장할 정보를 딕셔너리에 담습니다.
        save_data = {
            'page_rectangles': self.page_rectangles,
            'translated': self.translated,
            'total_page_text': self.total_page_text,
            'total_page_translated_text': self.total_page_translated_text,
            'Submitted': self.submitted
        }

        with open(save_file, 'wb') as f:
            pickle.dump(save_data, f)



    def load_rectangles(self, filename):
        import pickle
        save_file = filename.rsplit('.', 1)[0] + '.rectangles'

        try:
            with open(save_file, 'rb') as f:
                load_data = pickle.load(f)
                
                if isinstance(load_data, dict):
                    # 새로운 데이터 구조
                    self.page_rectangles = load_data.get('page_rectangles', {})
                    self.translated = load_data.get('translated', False)
                    self.total_page_text = load_data.get('total_page_text', {})
                    self.total_page_translated_text = load_data.get('total_page_translated_text', {})
                    self.submitted = load_data.get('Submitted',False)
                else:
                    # 기존 데이터 구조 (오직 page_rectangles 정보만 포함)
                    self.page_rectangles = load_data
                    # 나머지는 기본값으로 설정
                    self.translated = False
                    self.total_page_text = {}
                    self.total_page_translated_text = {}

        except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
            # 로드 실패 시 기본값으로 초기화
            self.page_rectangles = {}
            self.translated = False
            self.total_page_text = {}
            self.total_page_translated_text = {}
            
        if self.submitted:
             for page_num in range(self.total_pages):
                 self.update_progress((page_num + 1) / self.total_pages * 50 +50)
                 adjusted_patches = self.total_page_translated_text.get(page_num, []) if self.translated else self.total_page_text.get(page_num, [])
                 #adjusted_patches = self.total_page_translated_text[page_num] if self.translated else self.total_page_text[page_num] 
                 result_page = attach_patches(self.pages[page_num], adjusted_patches, translate = self.translated)
                 self.result_pages.append(result_page)
                
                
        
        self.update_progress(100)
        self.progress.pack_forget()

            
            
##################################################### 메인 플로우 ###############################################################    
            
            
    def update_text_box(self):
        # 현재 페이지 번호의 데이터를 텍스트 박스에 표시
        page_data = self.total_page_text.get(self.current_page.get(), []) if not self.translated else self.total_page_translated_text.get(self.current_page.get(), [])
        self.text_box.delete('1.0', tk.END)  # 텍스트 박스 내용을 지움
        for item in page_data:
            self.text_box.insert(tk.END, f"{item[0]} : {item[1]}\n")  # 텍스트 박스에 내용을 추가함

    def save_changes(self):
        # 텍스트 박스의 데이터를 가져와서 딕셔너리에 저장
        content = self.text_box.get('1.0', tk.END).strip()
        new_data = []
        pattern = r': \((\d+, \d+, \d+, \d+)\)(?:\n|$)'

        # 패턴을 기준으로 내용을 나눕니다.
        # 캡처 그룹을 사용하여 좌표도 포함시키는 방식입니다.
        parts = re.split(pattern, content)

        # parts 배열에서 텍스트와 좌표 데이터를 추출하여 new_data에 저장합니다.
        i = 0
        while i < len(parts) - 1:
            text = parts[i].rstrip()  # 오른쪽 끝의 공백 제거
            # 마지막 좌표 데이터인 경우 뒤에 오는 텍스트 부분이 없으므로 조건 추가
            if i + 1 < len(parts) and parts[i + 1]:
                coords_text = parts[i + 1]
                coords = tuple(map(int, coords_text.split(', ')))
                new_data.append([text, coords])
                i += 2  # 텍스트와 좌표 데이터를 모두 처리했으므로, 인덱스 2 증가
            else:
                # 좌표 데이터 없이 텍스트만 남은 경우
                new_data.append([text, None])
                break

                
        if not self.translated:
            self.total_page_text[self.current_page.get()] = new_data
        else:
            self.total_page_translated_text[self.current_page.get()] = new_data

        
    
##################################################### 메인 플로우 ###############################################################    

        
    def show_page(self, opt='Edit', quality = 'high', *args):
        current_page_number = self.current_page.get()
        if self.submitted == True: opt = 'temp'
        img = self.pages[current_page_number] if opt == 'Edit' else self.result_pages[current_page_number]

        original_width, original_height = img.size
        self.aspect_ratio =original_width/original_height*2
        
        resample_filter = Image.NEAREST if quality == 'low' else Image.LANCZOS
        img = self.resize_image(img, resample_filter)
        
        # 캔버스에서 이전에 표시된 이미지 삭제
        if self.current_page_image:
            self.canvas.delete(self.current_page_image)
    
        canvas_center_x = self.canvas.winfo_width() / 2
        canvas_center_y = self.canvas.winfo_height() / 2
        self.tk_image = ImageTk.PhotoImage(img)
        self.current_page_image = self.canvas.create_image(canvas_center_x, canvas_center_y, anchor='center', image=self.tk_image)
            
        self.resize_paint_rectangles(current_page_number)
        self.update_text_box()

        
    def Submit(self, opt = 'new'):
        edit_re=[]
        self.result_pages = []
        self.progress.pack(side=tk.LEFT)
        for page_num in range(self.total_pages):
            self.update_progress(page_num / self.total_pages * 100) 
            patches = self.crop_page(page_num)
            
            if patches:
                img, y_offsets = merge_images_vertically(patches)
                text_patches, blocks, text_blocks, estimated_font_sizes = image_translator(img,edit_re)
                adjusted_patches = adjust_patch_coordinates(patches, text_patches, y_offsets)
                self.total_page_text[page_num] = adjusted_patches
                result_page = attach_patches(self.pages[page_num], adjusted_patches, translate = False)
                self.result_pages.append(result_page)
                    
            else:
                result_page = self.pages[page_num]
                self.result_pages.append(result_page)
                
        self.update_progress(100)
        self.show_page(opt='temp')
        self.progress.pack_forget()
        self.submitted = True
        self.update_buttons()
        
        
    def Translate(self):
        self.current_page.set(0)
        self.save_changes()
        self.next_page_button.config(state=tk.DISABLED)
        self.previous_page_button.config(state=tk.DISABLED)
        self.submit_button.config(state=tk.DISABLED) 
        self.edit_button.config(state=tk.DISABLED) 
        self.Translate_button.config(state=tk.DISABLED)
        self.progress.pack(side=tk.LEFT)
        self.update_progress(0) 
        
        self.result_pages = []
        
        for page_num in range(self.total_pages):
            self.update_progress(page_num / self.total_pages * 100) 
            if self.total_page_text.get(page_num, False):
                adjusted_patches = self.total_page_text[page_num]
                adjusted_patches, self.translated = translate_module(adjusted_patches)
                self.total_page_translated_text[page_num] = adjusted_patches
                result_page = attach_patches(self.pages[page_num], adjusted_patches, translate = True)
                self.result_pages.append(result_page)
            else:
                result_page = self.pages[page_num]
                self.result_pages.append(result_page)
                
        self.update_progress(100)
        self.show_page(opt='temp')
        self.progress.pack_forget()
        self.next_page_button.config(state=tk.NORMAL)
        self.previous_page_button.config(state=tk.NORMAL)
        self.edit_button.config(state=tk.NORMAL)
        
        
    def edit(self):
        page_num = self.current_page.get()
        self.save_changes()
        adjusted_patches = self.total_page_translated_text[page_num] if self.translated else self.total_page_text[page_num] 
        result_page = attach_patches(self.pages[page_num], adjusted_patches, translate = self.translated)
        self.result_pages[page_num] = result_page
        self.show_page()
        
#     def Export_doc(self)
#         for page_num in range(self.total_pages):

        
        
            
root = tk.Tk()
root.title('PDF translator')
app = PDFTranslatorApp(root)
root.mainloop()


# In[ ]:




