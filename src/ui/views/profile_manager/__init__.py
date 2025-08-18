"""
Profile Manager View 모듈 - 모듈화된 프로파일 관리 시스템

AI 친화적 문서화:
- 기능: PDF 검사 프로파일 관리 (생성, 수정, 삭제, 가져오기/내보내기)
- 아키텍처: 헬퍼 패턴 + 이벤트 위임 패턴
- 주요 컴포넌트:
  * base.py: 메인 뷰 클래스와 전체 레이아웃
  * profile_list.py: 좌측 프로파일 목록 UI
  * info_tab.py: 기본 정보 탭 헬퍼
  * standards_tab.py: 품질 기준 탭 헬퍼
  * rules_tab.py: 검사 규칙 탭 헬퍼
  * color_tab.py: 색상 설정 탭 헬퍼
  * dialogs.py: 각종 대화상자 클래스들
  * handlers.py: 모든 CRUD 이벤트 처리

설계 원칙:
- 단일 책임 원칙: 각 모듈은 하나의 명확한 책임
- 개방 폐쇄 원칙: 확장에 열려있고 수정에 닫혀있음
- 의존성 역전: 구체적 구현이 아닌 인터페이스에 의존
- 결합도 최소화: 콜백과 이벤트 위임을 통한 느슨한 결합

확장성:
- 새로운 탭 추가 시: 헬퍼 클래스 생성 후 base.py에 등록
- 새로운 기능 추가 시: handlers.py에 메서드 추가
- UI 변경 시: 해당 헬퍼 클래스만 수정

최종 수정: 2025-01-11
"""

# 메인 클래스들 (외부 인터페이스)
from .base import ProfileManagerView
from .dialogs import ProfileCreateDialog

# 헬퍼 클래스들 (내부 사용)
from .profile_list import ProfileListWidget
from .info_tab import InfoTabHelper
from .standards_tab import StandardsTabHelper
from .rules_tab import RulesTabHelper
from .color_tab import ColorTabHelper
from .handlers import ProfileEventHandler

__all__ = [
    # 외부 인터페이스
    'ProfileManagerView',
    'ProfileCreateDialog',
    
    # 헬퍼 클래스들 (고급 사용자용)
    'ProfileListWidget',
    'InfoTabHelper', 
    'StandardsTabHelper',
    'RulesTabHelper',
    'ColorTabHelper',
    'ProfileEventHandler'
]