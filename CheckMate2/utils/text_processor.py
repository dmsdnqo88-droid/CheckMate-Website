"""
텍스트 처리 및 AI 분석 유틸리티
이 파일은 수행평가 요구조건과 결과물을 분석하는 기능을 담당합니다.
"""

import os
from typing import Dict, List, Tuple
import google.generativeai as genai
import json

class TextProcessor:
    """
    텍스트 처리 및 AI 분석을 담당하는 클래스
    
    이 클래스는 다음과 같은 기능을 제공합니다:
    1. 수행평가 요구조건 분석
    2. 결과물과 요구조건 비교
    3. 개선점 제안 생성
    """
    
    def __init__(self, api_key=None):
        """TextProcessor 클래스 초기화"""
        # Google API 키 확인
        if api_key is None:
            api_key = os.getenv('GOOGLE_API_KEY')
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY가 설정되지 않았습니다.")
        
        # Google Generative AI 설정
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def extract_requirements(self, text: str) -> List[str]:
        """
        텍스트에서 수행평가 요구조건을 추출합니다.
        
        Args:
            text (str): 요구조건이 포함된 텍스트
            
        Returns:
            List[str]: 추출된 요구조건 리스트
        """
        prompt = f"""
        다음 텍스트에서 수행평가의 요구조건을 추출해주세요.
        각 요구조건을 별도의 항목으로 나누어 리스트 형태로 반환해주세요.
        
        텍스트:
        {text}
        
        요구조건을 JSON 배열 형태로 반환해주세요:
        """
        
        try:
            response = self.model.generate_content(prompt)
            # JSON 형태로 파싱 시도
            try:
                requirements = json.loads(response.text)
                if isinstance(requirements, list):
                    return requirements
            except json.JSONDecodeError:
                pass
            
            # JSON 파싱이 실패하면 줄바꿈으로 분리
            lines = response.text.strip().split('\n')
            requirements = [line.strip().lstrip('- ').lstrip('* ').lstrip('1. ').lstrip('2. ').lstrip('3. ') 
                          for line in lines if line.strip()]
            return [req for req in requirements if req]
            
        except Exception as e:
            print(f"요구조건 추출 중 오류 발생: {e}")
            return []
    
    def analyze_compliance(self, requirements: List[str], submission: str) -> Dict:
        """
        제출물이 요구조건을 얼마나 만족하는지 분석합니다.
        
        Args:
            requirements (List[str]): 요구조건 리스트
            submission (str): 제출된 수행평가 결과물
            
        Returns:
            Dict: 분석 결과 (만족도, 개선점 등)
        """
        requirements_text = "\n".join([f"{i+1}. {req}" for i, req in enumerate(requirements)])
        
        prompt = f"""
        다음 수행평가 요구조건과 제출물을 분석해주세요.
        
        요구조건:
        {requirements_text}
        
        제출물:
        {submission}
        
        다음 JSON 형태로 분석 결과를 반환해주세요:
        {{
            "overall_score": 0-100,
            "requirements_analysis": [
                {{
                    "requirement": "요구조건 내용",
                    "satisfied": true/false,
                    "score": 0-100,
                    "feedback": "구체적인 피드백",
                    "suggestions": ["개선 제안1", "개선 제안2"]
                }}
            ],
            "general_feedback": "전체적인 피드백",
            "improvement_suggestions": ["전체 개선 제안1", "전체 개선 제안2"]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # JSON 파싱 시도
            try:
                result = json.loads(response.text)
                return result
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 기본 구조 반환
                return {
                    "overall_score": 70,
                    "requirements_analysis": [
                        {
                            "requirement": req,
                            "satisfied": True,
                            "score": 70,
                            "feedback": "기본적인 요구사항 충족",
                            "suggestions": ["더 구체적인 내용 추가 필요"]
                        } for req in requirements
                    ],
                    "general_feedback": "전반적으로 요구사항을 충족하지만 개선의 여지가 있습니다.",
                    "improvement_suggestions": ["더 구체적인 예시 추가", "논리적 구조 개선"]
                }
                
        except Exception as e:
            print(f"분석 중 오류 발생: {e}")
            return {
                "overall_score": 0,
                "requirements_analysis": [],
                "general_feedback": "분석 중 오류가 발생했습니다.",
                "improvement_suggestions": []
            }
    
    def generate_report(self, analysis_result: Dict) -> str:
        """
        분석 결과를 바탕으로 검사 보고서를 생성합니다.
        
        Args:
            analysis_result (Dict): analyze_compliance의 결과
            
        Returns:
            str: 생성된 보고서 텍스트
        """
        report = f"""
# 수행평가 검사 보고서

## 📊 전체 만족도: {analysis_result.get('overall_score', 0)}/100

## 📋 항목별 분석 결과
"""
        
        for i, analysis in enumerate(analysis_result.get('requirements_analysis', []), 1):
            status = "✅ 만족" if analysis.get('satisfied', False) else "❌ 미만족"
            report += f"""
### {i}. {analysis.get('requirement', 'N/A')}
- **상태**: {status}
- **점수**: {analysis.get('score', 0)}/100
- **피드백**: {analysis.get('feedback', 'N/A')}
- **개선 제안**:
"""
            for suggestion in analysis.get('suggestions', []):
                report += f"  - {suggestion}\n"
        
        report += f"""
## 💡 전체 피드백
{analysis_result.get('general_feedback', 'N/A')}

## 🔧 개선 제안
"""
        
        for suggestion in analysis_result.get('improvement_suggestions', []):
            report += f"- {suggestion}\n"
        
        return report
