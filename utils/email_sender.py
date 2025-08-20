"""
이메일 전송 유틸리티
이 파일은 검사 보고서를 이메일로 전송하는 기능을 담당합니다.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
import streamlit as st

class EmailSender:
    """
    이메일 전송을 담당하는 클래스
    
    이 클래스는 다음과 같은 기능을 제공합니다:
    1. 검사 보고서를 이메일로 전송
    2. Gmail SMTP 서버 사용
    3. HTML 형식의 이메일 지원
    """
    
    def __init__(self):
        """EmailSender 클래스 초기화"""
        # Gmail SMTP 설정
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # 환경 변수에서 이메일 설정 가져오기
        self.sender_email = os.getenv('EMAIL_ADDRESS')
        self.sender_password = os.getenv('EMAIL_PASSWORD')
        
        # 이메일 설정이 없는 경우 경고
        if not self.sender_email or not self.sender_password:
            print("이메일 전송을 위해서는 EMAIL_ADDRESS와 EMAIL_PASSWORD 환경 변수를 설정해야 합니다.")
    
    def send_report_email(self, recipient_email: str, report_content: str, 
                         subject: str = "수행평가 검사 보고서") -> bool:
        """
        검사 보고서를 이메일로 전송합니다.
        
        Args:
            recipient_email (str): 수신자 이메일 주소
            report_content (str): 전송할 보고서 내용
            subject (str): 이메일 제목
            
        Returns:
            bool: 전송 성공 여부
        """
        if not self.sender_email or not self.sender_password:
            st.error("이메일 전송을 위한 설정이 완료되지 않았습니다.")
            return False
        
        try:
            # 이메일 메시지 생성
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # HTML 형식의 이메일 본문 생성
            html_content = self._create_html_email(report_content)
            
            # HTML 부분 추가
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)
            
            # SMTP 서버 연결 및 이메일 전송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # TLS 암호화 시작
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            return True
            
        except Exception as e:
            print(f"이메일 전송 중 오류 발생: {e}")
            return False
    
    def _create_html_email(self, report_content: str) -> str:
        """
        보고서 내용을 HTML 형식의 이메일로 변환합니다.
        
        Args:
            report_content (str): 마크다운 형식의 보고서 내용
            
        Returns:
            str: HTML 형식의 이메일 내용
        """
        # 간단한 마크다운을 HTML로 변환
        html_content = report_content
        
        # 제목 변환
        html_content = html_content.replace("# ", "<h1>").replace("\n", "</h1>\n")
        html_content = html_content.replace("## ", "<h2>").replace("\n", "</h2>\n")
        html_content = html_content.replace("### ", "<h3>").replace("\n", "</h3>\n")
        
        # 굵은 글씨 변환
        html_content = html_content.replace("**", "<strong>").replace("**", "</strong>")
        
        # 줄바꿈 변환
        html_content = html_content.replace("\n", "<br>\n")
        
        # HTML 템플릿 적용
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }}
                .score {{
                    background-color: #ecf0f1;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
                .feedback {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-left: 4px solid #3498db;
                    margin: 10px 0;
                }}
                .suggestion {{
                    background-color: #fff3cd;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 5px 0;
                }}
            </style>
        </head>
        <body>
            <h1>📋 수행평가 검사 보고서</h1>
            {html_content}
            <hr>
            <p style="color: #7f8c8d; font-size: 12px;">
                이 보고서는 CheckMate 웹 앱을 통해 자동으로 생성되었습니다.
            </p>
        </body>
        </html>
        """
        
        return html_template
    
    def validate_email(self, email: str) -> bool:
        """
        이메일 주소 형식이 올바른지 검증합니다.
        
        Args:
            email (str): 검증할 이메일 주소
            
        Returns:
            bool: 유효한 이메일 주소 여부
        """
        import re
        
        # 간단한 이메일 형식 검증
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def get_setup_instructions(self) -> str:
        """
        이메일 설정 방법을 반환합니다.
        
        Returns:
            str: 설정 방법 안내
        """
        return """
        이메일 전송 기능을 사용하려면 다음 설정이 필요합니다:
        
        1. Gmail 계정에서 2단계 인증을 활성화하세요.
        2. 앱 비밀번호를 생성하세요:
           - Gmail 설정 → 보안 → 2단계 인증 → 앱 비밀번호
        3. .env 파일에 다음을 추가하세요:
           EMAIL_ADDRESS=your_email@gmail.com
           EMAIL_PASSWORD=your_app_password
        
        또는 Streamlit의 secrets.toml 파일에 추가할 수도 있습니다.
        """
