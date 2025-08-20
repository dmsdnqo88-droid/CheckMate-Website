"""
수행평가 검사 웹 앱 (CheckMate)
메인 애플리케이션 파일

이 파일은 Streamlit을 사용하여 웹 인터페이스를 제공하고,
사용자가 수행평가 요구조건과 결과물을 입력받아 AI 분석을 수행합니다.
"""

import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

# 유틸리티 모듈 임포트
from utils.text_processor import TextProcessor
from utils.image_processor import ImageProcessor
from utils.email_sender import EmailSender

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="CheckMate - 수행평가 검사 도구",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 추가
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """메인 애플리케이션 함수"""
    
    # 헤더
    st.markdown("""
    <div class="main-header">
        <h1>📋 CheckMate - 수행평가 검사 도구</h1>
        <p>AI 기반 수행평가 조건 검사 및 개선 제안</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # API 키 확인 및 입력
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            st.error("⚠️ Google API 키가 설정되지 않았습니다.")
            st.info("아래에 API 키를 직접 입력하거나 .env 파일을 설정하세요.")
            
            # API 키 직접 입력
            manual_api_key = st.text_input(
                "Google API 키를 입력하세요:",
                type="password",
                help="Google AI Studio에서 발급받은 API 키를 입력하세요"
            )
            
            if manual_api_key:
                api_key = manual_api_key
                st.success("✅ API 키가 입력되었습니다.")
            else:
                st.info("""
                **설정 방법:**
                1. `.env` 파일을 생성하세요
                2. `GOOGLE_API_KEY=your_api_key_here` 추가
                3. 앱을 다시 시작하세요
                """)
                return
        else:
            st.success("✅ Google API 키가 설정되었습니다.")
        
        # 이메일 설정 확인
        email_sender = EmailSender()
        if not email_sender.sender_email or not email_sender.sender_password:
            st.warning("⚠️ 이메일 전송 기능을 사용하려면 설정이 필요합니다.")
            with st.expander("이메일 설정 방법"):
                st.text(email_sender.get_setup_instructions())
    
    # API 키를 세션 상태에 저장
    st.session_state.api_key = api_key
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["📝 검사하기", "📊 결과 보기", "📧 공유하기"])
    
    with tab1:
        show_analysis_tab()
    
    with tab2:
        show_results_tab()
    
    with tab3:
        show_share_tab()

def show_analysis_tab():
    """검사 탭을 표시합니다."""
    
    st.header("🔍 수행평가 검사")
    
    # 두 개의 컬럼으로 레이아웃 구성
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 요구조건 입력")
        
        # 요구조건 입력 방법 선택
        req_input_method = st.radio(
            "요구조건 입력 방법을 선택하세요:",
            ["직접 입력", "이미지 업로드", "파일 업로드"]
        )
        
        requirements_text = ""
        
        if req_input_method == "직접 입력":
            requirements_text = st.text_area(
                "수행평가 요구조건을 입력하세요:",
                height=300,
                placeholder="예시:\n1. 최소 3페이지 이상 작성\n2. 참고문헌 5개 이상 포함\n3. 표와 그래프 각각 1개 이상 포함\n4. 결론 부분에서 개인적 견해 제시"
            )
        
        elif req_input_method == "이미지 업로드":
            uploaded_image = st.file_uploader(
                "요구조건이 포함된 이미지를 업로드하세요:",
                type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
                key="req_image"
            )
            
            if uploaded_image:
                image_processor = ImageProcessor()
                requirements_text = image_processor.extract_text_from_image(uploaded_image)
                st.text_area("추출된 텍스트:", requirements_text, height=200)
        
        elif req_input_method == "파일 업로드":
            uploaded_file = st.file_uploader(
                "요구조건이 포함된 파일을 업로드하세요:",
                type=['txt', 'docx', 'pdf'],
                key="req_file"
            )
            
            if uploaded_file:
                if uploaded_file.type == "text/plain":
                    requirements_text = str(uploaded_file.read(), "utf-8")
                    st.text_area("파일 내용:", requirements_text, height=200)
                else:
                    st.warning("현재 txt 파일만 지원됩니다. 다른 형식은 추후 업데이트 예정입니다.")
    
    with col2:
        st.subheader("📄 결과물 입력")
        
        # 결과물 입력 방법 선택
        sub_input_method = st.radio(
            "결과물 입력 방법을 선택하세요:",
            ["직접 입력", "이미지 업로드", "파일 업로드"]
        )
        
        submission_text = ""
        
        if sub_input_method == "직접 입력":
            submission_text = st.text_area(
                "수행평가 결과물을 입력하세요:",
                height=300,
                placeholder="여기에 수행평가 결과물을 입력하세요..."
            )
        
        elif sub_input_method == "이미지 업로드":
            uploaded_image = st.file_uploader(
                "결과물이 포함된 이미지를 업로드하세요:",
                type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
                key="sub_image"
            )
            
            if uploaded_image:
                image_processor = ImageProcessor()
                submission_text = image_processor.extract_text_from_image(uploaded_image)
                st.text_area("추출된 텍스트:", submission_text, height=200)
        
        elif sub_input_method == "파일 업로드":
            uploaded_file = st.file_uploader(
                "결과물이 포함된 파일을 업로드하세요:",
                type=['txt', 'docx', 'pdf'],
                key="sub_file"
            )
            
            if uploaded_file:
                if uploaded_file.type == "text/plain":
                    submission_text = str(uploaded_file.read(), "utf-8")
                    st.text_area("파일 내용:", submission_text, height=200)
                else:
                    st.warning("현재 txt 파일만 지원됩니다. 다른 형식은 추후 업데이트 예정입니다.")
    
    # 검사 시작 버튼
    st.markdown("---")
    
    if st.button("🚀 검사 시작", type="primary", use_container_width=True):
        if not requirements_text.strip() or not submission_text.strip():
            st.error("⚠️ 요구조건과 결과물을 모두 입력해주세요.")
            return
        
        # 진행 상황 표시
        with st.spinner("AI가 분석 중입니다..."):
            try:
                # 세션 상태에서 API 키 가져오기
                current_api_key = st.session_state.get('api_key')
                if not current_api_key:
                    st.error("⚠️ API 키가 설정되지 않았습니다. 사이드바에서 API 키를 입력해주세요.")
                    return
                
                # TextProcessor 초기화 (API 키 전달)
                text_processor = TextProcessor(api_key=current_api_key)
                
                # 요구조건 추출
                st.info("📋 요구조건을 분석하고 있습니다...")
                requirements = text_processor.extract_requirements(requirements_text)
                
                if not requirements:
                    st.error("요구조건을 추출할 수 없습니다. 텍스트를 다시 확인해주세요.")
                    return
                
                # 분석 수행
                st.info("🔍 결과물을 분석하고 있습니다...")
                analysis_result = text_processor.analyze_compliance(requirements, submission_text)
                
                # 보고서 생성
                st.info("📊 보고서를 생성하고 있습니다...")
                report = text_processor.generate_report(analysis_result)
                
                # 결과를 세션 상태에 저장
                st.session_state.analysis_result = analysis_result
                st.session_state.report = report
                st.session_state.requirements = requirements
                st.session_state.submission_text = submission_text
                
                st.success("✅ 분석이 완료되었습니다! '결과 보기' 탭에서 확인하세요.")
                
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {str(e)}")

def show_results_tab():
    """결과 탭을 표시합니다."""
    
    st.header("📊 검사 결과")
    
    if 'analysis_result' not in st.session_state:
        st.info("👈 '검사하기' 탭에서 먼저 검사를 실행해주세요.")
        return
    
    # 결과 데이터 가져오기
    analysis_result = st.session_state.analysis_result
    report = st.session_state.report
    requirements = st.session_state.requirements
    
    # 전체 점수 표시
    overall_score = analysis_result.get('overall_score', 0)
    
    # 점수에 따른 색상 결정
    if overall_score >= 80:
        score_color = "🟢"
        score_status = "우수"
    elif overall_score >= 60:
        score_color = "🟡"
        score_status = "보통"
    else:
        score_color = "🔴"
        score_status = "개선 필요"
    
    # 메트릭 카드들
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="전체 만족도",
            value=f"{overall_score}/100",
            delta=f"{score_color} {score_status}"
        )
    
    with col2:
        total_requirements = len(requirements)
        satisfied_requirements = sum(1 for req in analysis_result.get('requirements_analysis', []) 
                                   if req.get('satisfied', False))
        st.metric(
            label="충족된 요구사항",
            value=f"{satisfied_requirements}/{total_requirements}",
            delta=f"{satisfied_requirements/total_requirements*100:.1f}%"
        )
    
    with col3:
        avg_score = sum(req.get('score', 0) for req in analysis_result.get('requirements_analysis', [])) / max(len(analysis_result.get('requirements_analysis', [])), 1)
        st.metric(
            label="평균 점수",
            value=f"{avg_score:.1f}/100",
            delta="항목별 평균"
        )
    
    # 상세 분석 결과
    st.subheader("📋 항목별 분석 결과")
    
    for i, analysis in enumerate(analysis_result.get('requirements_analysis', []), 1):
        with st.expander(f"{i}. {analysis.get('requirement', 'N/A')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                status = "✅ 만족" if analysis.get('satisfied', False) else "❌ 미만족"
                st.write(f"**상태**: {status}")
                st.write(f"**점수**: {analysis.get('score', 0)}/100")
            
            with col2:
                st.write(f"**피드백**: {analysis.get('feedback', 'N/A')}")
            
            st.write("**개선 제안**:")
            for suggestion in analysis.get('suggestions', []):
                st.write(f"• {suggestion}")
    
    # 전체 피드백
    st.subheader("💡 전체 피드백")
    st.markdown(f"""
    <div class="info-box">
        {analysis_result.get('general_feedback', 'N/A')}
    </div>
    """, unsafe_allow_html=True)
    
    # 개선 제안
    st.subheader("🔧 개선 제안")
    improvement_suggestions = analysis_result.get('improvement_suggestions', [])
    if improvement_suggestions:
        for suggestion in improvement_suggestions:
            st.write(f"• {suggestion}")
    else:
        st.info("구체적인 개선 제안이 없습니다.")
    
    # 전체 보고서
    st.subheader("📄 전체 보고서")
    st.markdown(report)

def show_share_tab():
    """공유 탭을 표시합니다."""
    
    st.header("📧 결과 공유")
    
    if 'report' not in st.session_state:
        st.info("👈 '검사하기' 탭에서 먼저 검사를 실행해주세요.")
        return
    
    st.subheader("이메일로 보고서 공유")
    
    # 이메일 입력
    recipient_email = st.text_input(
        "수신자 이메일 주소:",
        placeholder="example@email.com"
    )
    
    # 이메일 제목
    email_subject = st.text_input(
        "이메일 제목:",
        value="수행평가 검사 보고서",
        placeholder="이메일 제목을 입력하세요"
    )
    
    # 이메일 내용 미리보기
    if st.checkbox("이메일 내용 미리보기"):
        st.subheader("📧 이메일 미리보기")
        st.markdown("**제목:** " + email_subject)
        st.markdown("**수신자:** " + recipient_email)
        st.markdown("**내용:**")
        st.markdown(st.session_state.report)
    
    # 이메일 전송
    if st.button("📤 이메일 전송", type="primary"):
        if not recipient_email:
            st.error("수신자 이메일 주소를 입력해주세요.")
            return
        
        # 이메일 형식 검증
        email_sender = EmailSender()
        if not email_sender.validate_email(recipient_email):
            st.error("올바른 이메일 주소 형식이 아닙니다.")
            return
        
        # 이메일 전송
        with st.spinner("이메일을 전송하고 있습니다..."):
            success = email_sender.send_report_email(
                recipient_email,
                st.session_state.report,
                email_subject
            )
            
            if success:
                st.success("✅ 이메일이 성공적으로 전송되었습니다!")
            else:
                st.error("❌ 이메일 전송에 실패했습니다. 설정을 확인해주세요.")

if __name__ == "__main__":
    main()
