# src/ui/controllers/profile_controller/validator.py
"""
프로파일 유효성 검사 및 규칙 관리

프로파일 설정 검증, 규칙 관리, 품질 기준 업데이트를 담당합니다.
"""

from typing import Dict, List, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import ProfileControllerBase


class ProfileValidator:
    """프로파일 유효성 검사 및 규칙 관리 클래스"""
    
    def __init__(self, parent: 'ProfileControllerBase'):
        self.parent = parent
    
    def get_available_rules(self) -> List[Dict[str, str]]:
        """사용 가능한 규칙 목록 반환"""
        return self.parent.AVAILABLE_RULES.copy()
    
    def get_rule_categories(self) -> List[str]:
        """규칙 카테고리 목록 반환"""
        categories = set()
        for rule in self.parent.AVAILABLE_RULES:
            categories.add(rule['category'])
        return sorted(list(categories))
    
    def get_rules_by_category(self, category: str) -> List[Dict[str, str]]:
        """카테고리별 규칙 목록 반환"""
        return [rule for rule in self.parent.AVAILABLE_RULES 
                if rule['category'] == category]
    
    def validate_profile_name(self, name: str) -> tuple[bool, str]:
        """프로파일 이름 유효성 검사"""
        if not name:
            return False, "프로파일 이름이 비어있습니다."
        
        if len(name) < 2:
            return False, "프로파일 이름이 너무 짧습니다."
        
        if len(name) > 50:
            return False, "프로파일 이름이 너무 깁니다."
        
        # 특수 문자 검사
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            if char in name:
                return False, f"프로파일 이름에 '{char}' 문자를 사용할 수 없습니다."
        
        # 기존 프로파일 이름 중복 검사
        try:
            existing_profiles = self.parent.profile_manager.profiles.values()
            for profile in existing_profiles:
                if profile.name.lower() == name.lower():
                    return False, "이미 존재하는 프로파일 이름입니다."
        except Exception:
            pass
        
        return True, ""
    
    def validate_profile_settings(self, settings: Dict[str, Any]) -> tuple[bool, str]:
        """프로파일 설정 유효성 검사"""
        try:
            # 품질 기준 검사
            if 'quality_standards' in settings:
                is_valid, message = self._validate_quality_standards(settings['quality_standards'])
                if not is_valid:
                    return False, f"품질 기준 오류: {message}"
            
            # 체크 옵션 검사
            if 'check_options' in settings:
                is_valid, message = self._validate_check_options(settings['check_options'])
                if not is_valid:
                    return False, f"체크 옵션 오류: {message}"
            
            # 규칙 설정 검사
            if 'enabled_rules' in settings and settings['enabled_rules'] is not None:
                is_valid, message = self._validate_enabled_rules(settings['enabled_rules'])
                if not is_valid:
                    return False, f"규칙 설정 오류: {message}"
            
            return True, ""
            
        except Exception as e:
            return False, f"설정 검증 중 오류: {str(e)}"
    
    def _validate_quality_standards(self, standards: Dict[str, Any]) -> tuple[bool, str]:
        """품질 기준 유효성 검사"""
        # 필수 키 확인
        required_keys = ['min_image_dpi', 'min_text_size', 'max_ink_coverage']
        for key in required_keys:
            if key not in standards:
                return False, f"필수 설정 '{key}'가 없습니다."
        
        # 값 범위 검사
        validations = [
            ('min_image_dpi', 72, 1200, "이미지 DPI는 72-1200 범위여야 합니다."),
            ('warning_image_dpi', 72, 1200, "경고 이미지 DPI는 72-1200 범위여야 합니다."),
            ('optimal_image_dpi', 72, 1200, "최적 이미지 DPI는 72-1200 범위여야 합니다."),
            ('min_text_size', 1, 100, "최소 텍스트 크기는 1-100pt 범위여야 합니다."),
            ('max_ink_coverage', 200, 500, "최대 잉크 도포량은 200-500% 범위여야 합니다."),
            ('standard_bleed_size', 0, 20, "재단선 크기는 0-20mm 범위여야 합니다.")
        ]
        
        for key, min_val, max_val, message in validations:
            if key in standards:
                value = standards[key]
                if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                    return False, message
        
        return True, ""
    
    def _validate_check_options(self, options: Dict[str, Any]) -> tuple[bool, str]:
        """체크 옵션 유효성 검사"""
        # 스팟 컬러 제한 검사
        if 'spot_color_limit' in options:
            limit = options['spot_color_limit']
            if not isinstance(limit, int) or limit < 0 or limit > 10:
                return False, "스팟 컬러 제한은 0-10 범위의 정수여야 합니다."
        
        # boolean 타입 검사
        bool_keys = ['check_rgb', 'check_spot', 'allow_rgb', 'allow_spot', 'ink_coverage']
        for key in bool_keys:
            if key in options and not isinstance(options[key], bool):
                return False, f"'{key}'는 boolean 값이어야 합니다."
        
        return True, ""
    
    def _validate_enabled_rules(self, rules: List[str]) -> tuple[bool, str]:
        """활성화된 규칙 유효성 검사"""
        available_rule_names = [rule['name'] for rule in self.parent.AVAILABLE_RULES]
        
        for rule_name in rules:
            if rule_name not in available_rule_names:
                return False, f"알 수 없는 규칙: {rule_name}"
        
        return True, ""
    
    def update_rule_settings(self, 
                           profile_name: str,
                           enabled_rules: List[str],
                           rule_severities: Optional[Dict[str, str]] = None) -> bool:
        """
        프로파일의 규칙 설정 업데이트
        
        Args:
            profile_name: 프로파일 이름
            enabled_rules: 활성화할 규칙 목록
            rule_severities: 규칙별 심각도 설정
            
        Returns:
            bool: 성공 여부
        """
        try:
            profile = self.parent.profile_manager.get_profile(profile_name)
            if not profile or profile.is_builtin:
                return False
            
            # 규칙 유효성 검사
            is_valid, message = self._validate_enabled_rules(enabled_rules)
            if not is_valid:
                self.parent.logger.error(f"규칙 설정 오류: {message}")
                return False
            
            # 설정 업데이트
            profile.data['enabled_rules'] = enabled_rules
            if rule_severities:
                profile.data['rule_severities'] = rule_severities
            
            # 프로파일 저장
            if self.parent.profile_manager.update_profile(profile_name, profile.data):
                self.parent.logger.info(f"규칙 설정 업데이트: {profile_name}")
                return True
                
        except Exception as e:
            self.parent.logger.error(f"규칙 설정 업데이트 실패: {e}")
        
        return False
    
    def update_quality_standards(self,
                               profile_name: str,
                               standards: Dict[str, Any]) -> bool:
        """
        프로파일의 품질 기준 업데이트
        
        Args:
            profile_name: 프로파일 이름  
            standards: 새 품질 기준
            
        Returns:
            bool: 성공 여부
        """
        try:
            profile = self.parent.profile_manager.get_profile(profile_name)
            if not profile or profile.is_builtin:
                return False
            
            # 품질 기준 유효성 검사
            is_valid, message = self._validate_quality_standards(standards)
            if not is_valid:
                self.parent.logger.error(f"품질 기준 오류: {message}")
                return False
            
            # 기존 설정과 병합
            if 'quality_standards' not in profile.data:
                profile.data['quality_standards'] = {}
            
            profile.data['quality_standards'].update(standards)
            
            # 프로파일 저장
            if self.parent.profile_manager.update_profile(profile_name, profile.data):
                self.parent.logger.info(f"품질 기준 업데이트: {profile_name}")
                return True
                
        except Exception as e:
            self.parent.logger.error(f"품질 기준 업데이트 실패: {e}")
        
        return False
    
    def get_profile_validation_summary(self, profile_name: str) -> Dict[str, Any]:
        """프로파일 유효성 검사 요약"""
        try:
            profile = self.parent.profile_manager.get_profile(profile_name)
            if not profile:
                return {'valid': False, 'errors': ['프로파일을 찾을 수 없습니다.']}
            
            errors = []
            warnings = []
            
            # 설정 유효성 검사
            is_valid, message = self.validate_profile_settings(profile.data)
            if not is_valid:
                errors.append(message)
            
            # 규칙 설정 확인
            enabled_rules = profile.data.get('enabled_rules', [])
            if enabled_rules is None:
                warnings.append("활성화된 규칙이 설정되지 않았습니다.")
            elif len(enabled_rules) == 0:
                warnings.append("활성화된 규칙이 없습니다.")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'enabled_rules_count': len(enabled_rules) if enabled_rules else 0,
                'total_rules_count': len(self.parent.AVAILABLE_RULES)
            }
            
        except Exception as e:
            return {
                'valid': False, 
                'errors': [f"검증 중 오류: {str(e)}"],
                'warnings': []
            }