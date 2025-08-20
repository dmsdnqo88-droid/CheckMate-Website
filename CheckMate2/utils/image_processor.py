"""
이미지 처리 유틸리티
이 파일은 이미지에서 텍스트를 추출하는 기능을 담당합니다.
"""

import os
from typing import Optional
from PIL import Image
import pytesseract
import io

class ImageProcessor:
    """
    이미지에서 텍스트를 추출하는 클래스
    
    이 클래스는 다음과 같은 기능을 제공합니다:
    1. 이미지 파일에서 텍스트 추출 (OCR)
    2. 다양한 이미지 형식 지원
    3. 텍스트 정리 및 전처리
    """
    
    def __init__(self):
        """ImageProcessor 클래스 초기화"""
        # Windows 환경에서 Tesseract 경로 설정 (필요한 경우)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Tesseract가 설치되어 있는지 확인
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            print(f"Tesseract OCR이 설치되지 않았습니다: {e}")
            print("Tesseract 설치 방법:")
            print("Windows: https://github.com/UB-Mannheim/tesseract/wiki")
            print("Mac: brew install tesseract")
            print("Linux: sudo apt-get install tesseract-ocr")
    
    def extract_text_from_image(self, image_file) -> str:
        """
        업로드된 이미지 파일에서 텍스트를 추출합니다.
        
        Args:
            image_file: Streamlit에서 업로드된 파일 객체
            
        Returns:
            str: 추출된 텍스트
        """
        try:
            # 이미지 파일을 PIL Image 객체로 변환
            image = Image.open(image_file)
            
            # 이미지 전처리 (선택사항)
            # 이미지 품질이 좋지 않은 경우 전처리가 도움될 수 있습니다
            processed_image = self._preprocess_image(image)
            
            # OCR을 사용하여 텍스트 추출
            text = pytesseract.image_to_string(processed_image, lang='kor+eng')
            
            # 텍스트 정리
            cleaned_text = self._clean_text(text)
            
            return cleaned_text
            
        except Exception as e:
            print(f"이미지에서 텍스트 추출 중 오류 발생: {e}")
            return f"이미지 처리 중 오류가 발생했습니다: {str(e)}"
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        OCR 성능 향상을 위한 이미지 전처리
        
        Args:
            image (Image.Image): 원본 이미지
            
        Returns:
            Image.Image: 전처리된 이미지
        """
        # 이미지를 RGB 모드로 변환 (필요한 경우)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 이미지 크기 조정 (너무 크거나 작은 경우)
        width, height = image.size
        
        # 너무 큰 이미지는 축소
        if width > 2000 or height > 2000:
            ratio = min(2000/width, 2000/height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 너무 작은 이미지는 확대
        elif width < 300 or height < 300:
            ratio = max(300/width, 300/height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    def _clean_text(self, text: str) -> str:
        """
        추출된 텍스트를 정리합니다.
        
        Args:
            text (str): 원본 텍스트
            
        Returns:
            str: 정리된 텍스트
        """
        if not text:
            return "이미지에서 텍스트를 추출할 수 없습니다."
        
        # 불필요한 공백 제거
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # 줄 앞뒤 공백 제거
            line = line.strip()
            
            # 빈 줄이 아닌 경우만 추가
            if line:
                cleaned_lines.append(line)
        
        # 줄바꿈으로 다시 결합
        cleaned_text = '\n'.join(cleaned_lines)
        
        return cleaned_text
    
    def is_image_file(self, filename: str) -> bool:
        """
        파일이 이미지 형식인지 확인합니다.
        
        Args:
            filename (str): 파일명
            
        Returns:
            bool: 이미지 파일 여부
        """
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
        file_extension = os.path.splitext(filename.lower())[1]
        return file_extension in image_extensions
