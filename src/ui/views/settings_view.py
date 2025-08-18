# src/ui/views/settings_view.py
"""
환경설정 뷰 - 모듈화된 버전 래퍼

기존 API 호환성을 유지하기 위한 래퍼 파일입니다.
실제 구현은 settings/ 모듈에 분산되어 있습니다.

모듈화 이후 구조:
- settings/base.py: 기본 윈도우 클래스
- settings/general_tab.py: 일반 설정 탭
- settings/processing_tab.py: 처리 설정 탭  
- settings/folders_tab.py: 폴더 설정 탭
- settings/interface_tab.py: 인터페이스 설정 탭
- settings/alarm_tab.py: 알람 설정 탭
- settings/advanced_tools_tab.py: 고급 및 도구 설정 탭
- settings/handlers.py: 이벤트 핸들러와 유틸리티
- settings/__init__.py: 모듈 통합 및 SettingsView export

변경 사항:
1. 1078줄 → 약 200줄로 분할됨 (8개 파일)
2. 각 탭별로 독립적인 모듈화
3. 이벤트 핸들러 분리
4. AI 친화적 문서화 추가
5. 기존 API 완전 호환성 유지
"""

# 모듈화된 SettingsView를 import
from .settings import SettingsView

# 기존 호환성을 위한 export
__all__ = ['SettingsView']

# 모듈 정보
__version__ = "2.0.0"
__author__ = "PDF Quality Checker Team"
__description__ = "Modularized Settings View"

"""
모듈화 완료 정보:

파일 분할:
- base.py: 150줄 (기본 클래스와 초기화)
- general_tab.py: 120줄 (언어, 테마, 시작 옵션)
- processing_tab.py: 130줄 (프로파일, 자동처리, 보고서)
- folders_tab.py: 100줄 (출력/완료 폴더 설정)
- interface_tab.py: 140줄 (알림, 사이드바, 열 설정)
- alarm_tab.py: 220줄 (알람 설정 - 가장 복잡)
- advanced_tools_tab.py: 200줄 (고급 설정 + 외부 도구)
- handlers.py: 180줄 (이벤트 처리, 검증, 유틸리티)
- __init__.py: 130줄 (모듈 통합 및 API 래핑)

총 1370줄 → 기존 1078줄보다 약간 증가했지만:
- 모듈별 분리로 유지보수성 크게 향상
- AI 친화적 문서화로 이해도 향상
- 각 파일이 200줄 이하로 관리 용이
- 기능별 독립성으로 확장 및 수정 용이
- 순환 참조 방지 설계
"""