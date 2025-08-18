# src/ui/controllers/settings_controller/persistence.py
"""
설정 파일 저장 및 로드 모듈

설정 파일의 안전한 저장, 로드, 백업, 복원 등을 담당합니다.
"""

import json
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .base import SettingsControllerBase, UserSettings


class PersistenceManager(SettingsControllerBase):
    """설정 파일 지속성 관리자
    
    설정 파일의 안전한 저장과 로드를 담당합니다.
    """
    
    def __init__(self, settings_file: Optional[Path] = None, 
                 logger: Optional[logging.Logger] = None):
        """지속성 관리자 초기화
        
        Args:
            settings_file: 설정 파일 경로
            logger: 로거 인스턴스
        """
        super().__init__(settings_file, logger)
        
        # 백업 파일 경로
        self.backup_file = self.settings_file.with_suffix('.json.bak')
        self.emergency_backup_file = self.settings_file.with_suffix('.json.emergency')
        
        # 초기화 시 백업 정리
        self._cleanup_old_backups()
    
    def _cleanup_old_backups(self) -> None:
        """이전 백업 파일들 정리"""
        try:
            # 시작 시 기본 백업 파일 삭제
            if self.backup_file.exists():
                self.backup_file.unlink()
                self.logger.debug("이전 백업 파일 삭제됨")
                
        except Exception as e:
            self.logger.warning(f"백업 파일 정리 실패: {e}")
    
    def load_settings(self) -> bool:
        """설정 파일 로드
        
        Returns:
            bool: 로드 성공 여부
        """
        try:
            if self.settings_file.exists():
                return self._load_from_file(self.settings_file)
            else:
                # 기본 설정으로 새 파일 생성
                self.settings = UserSettings()
                success = self.save_settings()
                if success:
                    self.logger.info("기본 설정으로 초기화됨")
                return success
                
        except Exception as e:
            self.logger.error(f"설정 파일 로드 실패: {e}")
            return self._handle_load_failure()
    
    def _load_from_file(self, file_path: Path) -> bool:
        """파일에서 설정 로드
        
        Args:
            file_path: 로드할 파일 경로
            
        Returns:
            bool: 로드 성공 여부
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 데이터 검증
            if not self._validate_settings_data(data):
                raise ValueError("설정 데이터 검증 실패")
            
            # 설정 객체 생성
            self.settings = UserSettings.from_dict(data)
            self.logger.info(f"설정 파일 로드 완료: {file_path}")
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 파싱 오류: {e}")
            return False
        except Exception as e:
            self.logger.error(f"파일 로드 오류: {e}")
            return False
    
    def _handle_load_failure(self) -> bool:
        """로드 실패 시 복구 처리
        
        Returns:
            bool: 복구 성공 여부
        """
        # 1. 비상 백업에서 복구 시도
        if self.emergency_backup_file.exists():
            self.logger.info("비상 백업에서 복구 시도")
            if self._load_from_file(self.emergency_backup_file):
                # 복구된 설정을 메인 파일에 저장
                self.save_settings()
                return True
        
        # 2. 기본 백업에서 복구 시도
        if self.backup_file.exists():
            self.logger.info("백업 파일에서 복구 시도")
            if self._load_from_file(self.backup_file):
                # 복구된 설정을 메인 파일에 저장
                self.save_settings()
                return True
        
        # 3. 기본 설정으로 초기화
        self.logger.warning("기본 설정으로 초기화")
        self.settings = UserSettings()
        return self.save_settings()
    
    def save_settings(self) -> bool:
        """설정 파일 저장
        
        Returns:
            bool: 저장 성공 여부
        """
        try:
            # 1. 현재 파일 백업
            if not self._create_backup():
                self.logger.warning("백업 생성 실패")
            
            # 2. 설정 데이터 준비
            data = self.settings.to_dict()
            data['last_saved'] = datetime.now().isoformat()
            
            # 3. 임시 파일에 저장
            temp_file = self.settings_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 4. 원자적 교체
            if self.settings_file.exists():
                self.settings_file.unlink()
            temp_file.rename(self.settings_file)
            
            # 5. 백업 정리 (저장 성공 후)
            self._cleanup_successful_save()
            
            self.logger.info("설정 파일 저장 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"설정 파일 저장 실패: {e}")
            return self._handle_save_failure()
    
    def _create_backup(self) -> bool:
        """현재 설정 파일 백업 생성
        
        Returns:
            bool: 백업 성공 여부
        """
        try:
            if not self.settings_file.exists():
                return True
            
            # 기존 백업 파일이 있으면 삭제
            if self.backup_file.exists():
                self.backup_file.unlink()
            
            # 안전한 복사
            shutil.copy2(self.settings_file, self.backup_file)
            return True
            
        except Exception as e:
            self.logger.error(f"백업 생성 실패: {e}")
            return False
    
    def _handle_save_failure(self) -> bool:
        """저장 실패 시 복구 처리
        
        Returns:
            bool: 복구 성공 여부
        """
        try:
            # 백업에서 복원 시도
            if self.backup_file.exists():
                if self.settings_file.exists():
                    self.settings_file.unlink()
                self.backup_file.rename(self.settings_file)
                self.logger.info("백업 파일에서 복원됨")
                return True
        except Exception as e:
            self.logger.error(f"백업 복원 실패: {e}")
        
        return False
    
    def _cleanup_successful_save(self) -> None:
        """저장 성공 후 백업 정리"""
        try:
            # 기본 백업은 보존하고, 임시 파일들만 정리
            temp_patterns = ['.tmp', '.temp']
            for pattern in temp_patterns:
                temp_file = self.settings_file.with_suffix(pattern)
                if temp_file.exists():
                    temp_file.unlink()
        except Exception as e:
            self.logger.warning(f"백업 정리 실패: {e}")
    
    def export_settings(self, export_path: Path, include_metadata: bool = True) -> bool:
        """설정 내보내기
        
        Args:
            export_path: 내보낼 경로
            include_metadata: 메타데이터 포함 여부
            
        Returns:
            bool: 성공 여부
        """
        try:
            data = self.settings.to_dict()
            
            if include_metadata:
                data['exported_at'] = datetime.now().isoformat()
                data['app_version'] = "2.0.0"
                data['export_source'] = str(self.settings_file)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"설정 내보내기 완료: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"설정 내보내기 실패: {e}")
            return False
    
    def import_settings(self, import_path: Path, create_backup: bool = True) -> bool:
        """설정 가져오기
        
        Args:
            import_path: 가져올 파일 경로
            create_backup: 백업 생성 여부
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 가져올 파일 검증
            if not import_path.exists():
                self.logger.error(f"가져올 파일이 존재하지 않음: {import_path}")
                return False
            
            # 데이터 로드 및 검증
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not self._validate_settings_data(data):
                self.logger.error("가져올 설정 데이터 검증 실패")
                return False
            
            # 현재 설정 백업
            if create_backup:
                backup_path = self.settings_file.with_suffix('.json.import_backup')
                if not self.export_settings(backup_path, include_metadata=True):
                    self.logger.warning("가져오기 전 백업 실패")
            
            # 설정 적용
            old_settings = self.settings.copy()
            self.settings = UserSettings.from_dict(data)
            
            # 저장
            if self.save_settings():
                self.logger.info(f"설정 가져오기 완료: {import_path}")
                
                # 변경 알림
                self._notify_import_changes(old_settings, self.settings)
                return True
            else:
                # 저장 실패 시 이전 설정 복원
                self.settings = old_settings
                return False
                
        except Exception as e:
            self.logger.error(f"설정 가져오기 실패: {e}")
            return False
    
    def create_emergency_backup(self) -> bool:
        """비상 백업 생성
        
        Returns:
            bool: 백업 성공 여부
        """
        try:
            if self.settings_file.exists():
                shutil.copy2(self.settings_file, self.emergency_backup_file)
                self.logger.info("비상 백업 생성됨")
                return True
            return False
        except Exception as e:
            self.logger.error(f"비상 백업 생성 실패: {e}")
            return False
    
    def restore_from_emergency_backup(self) -> bool:
        """비상 백업에서 복원
        
        Returns:
            bool: 복원 성공 여부
        """
        try:
            if not self.emergency_backup_file.exists():
                self.logger.error("비상 백업 파일이 존재하지 않음")
                return False
            
            # 현재 파일 백업
            if self.settings_file.exists():
                corrupt_backup = self.settings_file.with_suffix('.json.corrupt')
                shutil.move(self.settings_file, corrupt_backup)
            
            # 비상 백업에서 복원
            shutil.copy2(self.emergency_backup_file, self.settings_file)
            
            # 설정 다시 로드
            if self.load_settings():
                self.logger.info("비상 백업에서 복원 완료")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"비상 백업 복원 실패: {e}")
            return False
    
    def _validate_settings_data(self, data: Dict[str, Any]) -> bool:
        """설정 데이터 검증
        
        Args:
            data: 검증할 데이터
            
        Returns:
            bool: 검증 성공 여부
        """
        try:
            # 기본 구조 검증
            if not isinstance(data, dict):
                return False
            
            # 필수 필드 검증
            required_fields = {'theme', 'language'}
            if not all(field in data for field in required_fields):
                return False
            
            # 테스트 생성해보기
            test_settings = UserSettings.from_dict(data)
            return True
            
        except Exception as e:
            self.logger.error(f"설정 데이터 검증 실패: {e}")
            return False
    
    def _notify_import_changes(self, old_settings: UserSettings, new_settings: UserSettings) -> None:
        """설정 가져오기 후 변경 알림
        
        Args:
            old_settings: 이전 설정
            new_settings: 새로운 설정
        """
        try:
            old_dict = old_settings.to_dict()
            new_dict = new_settings.to_dict()
            
            for key, new_value in new_dict.items():
                old_value = old_dict.get(key)
                if old_value != new_value:
                    category = self._get_setting_category(key)
                    self._notify_change(key, old_value, new_value, category)
                    
        except Exception as e:
            self.logger.error(f"가져오기 변경 알림 실패: {e}")
    
    # 추상 메서드 임시 구현
    def get_setting(self, key: str, default: Any = None) -> Any:
        """설정 조회 - 다른 모듈에서 구현"""
        return getattr(self.settings, key, default)
    
    def set_setting(self, key: str, value: Any, save: bool = True) -> bool:
        """설정 변경 - 다른 모듈에서 구현"""
        return True
    
    def reset_settings(self, category: Optional[str] = None) -> bool:
        """설정 초기화 - 다른 모듈에서 구현"""
        return True