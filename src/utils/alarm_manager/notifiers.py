# src/utils/alarm_manager/notifiers.py
"""
알림 발송 구현체들
"""

import logging
import winsound
import threading
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from tkinter import messagebox

# 알림 라이브러리 우선순위별로 시도
NOTIFICATION_AVAILABLE = False
NOTIFICATION_METHOD = None

# 1순위: plyer (가장 안정적)
try:
    from plyer import notification as plyer_notification
    NOTIFICATION_AVAILABLE = True
    NOTIFICATION_METHOD = 'plyer'
except ImportError:
    pass

# 2순위: win10toast (기존 방식)
if not NOTIFICATION_AVAILABLE:
    try:
        from win10toast import ToastNotifier
        NOTIFICATION_AVAILABLE = True
        NOTIFICATION_METHOD = 'win10toast'
    except ImportError:
        pass

# 3순위: Windows 네이티브 (ctypes)
if not NOTIFICATION_AVAILABLE:
    try:
        import ctypes
        from ctypes import wintypes
        NOTIFICATION_AVAILABLE = True
        NOTIFICATION_METHOD = 'ctypes'
    except ImportError:
        pass

# 소리 재생 라이브러리
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from ...config.alarm_config import AlarmConditionType


class BaseNotifier:
    """알림 발송 기본 클래스"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        
    def send(self, title: str, message: str, **kwargs) -> bool:
        """
        알림 발송 (서브클래스에서 구현)
        
        Args:
            title: 제목
            message: 메시지
            **kwargs: 추가 옵션
            
        Returns:
            성공 여부
        """
        raise NotImplementedError


class SystemNotifier(BaseNotifier):
    """시스템 알림 발송"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            logger: 로거
        """
        super().__init__(logger)
        self.method = NOTIFICATION_METHOD
        self.toast_notifier = None
        
        if NOTIFICATION_METHOD == 'win10toast':
            try:
                self.toast_notifier = ToastNotifier()
                self.logger.info("win10toast 초기화 성공")
            except Exception as e:
                self.logger.warning(f"win10toast 초기화 실패: {e}")
                
    def send(self, title: str, message: str, **kwargs) -> bool:
        """
        시스템 알림 발송
        
        Args:
            title: 제목
            message: 메시지
            **kwargs: 추가 옵션
            
        Returns:
            성공 여부
        """
        success = False
        
        # 1. plyer 사용 (가장 안정적)
        if self.method == 'plyer':
            try:
                plyer_notification.notify(
                    title=title,
                    message=message,
                    app_name='PDF Quality Checker',
                    timeout=kwargs.get('timeout', 10)
                )
                success = True
                self.logger.debug("plyer 알림 성공")
            except Exception as e:
                self.logger.warning(f"plyer 알림 실패: {e}")
                
        # 2. win10toast 사용 (기존 방식)
        elif self.method == 'win10toast' and self.toast_notifier:
            try:
                # 별도 스레드에서 실행하여 WNDPROC 에러 방지
                def show_toast():
                    try:
                        self.toast_notifier.show_toast(
                            title, 
                            message,
                            duration=kwargs.get('timeout', 10),
                            threaded=False  # 스레드 내에서는 False
                        )
                    except Exception as inner_e:
                        self.logger.error(f"win10toast 스레드 내 오류: {inner_e}")
                
                thread = threading.Thread(target=show_toast, daemon=True)
                thread.start()
                success = True
                self.logger.debug("win10toast 알림 시작")
            except Exception as e:
                self.logger.warning(f"win10toast 알림 실패: {e}")
                
        # 3. Windows 네이티브 알림 (ctypes)
        elif self.method == 'ctypes':
            try:
                # Windows MessageBox API 사용
                ctypes.windll.user32.MessageBoxW(
                    0, 
                    message, 
                    title, 
                    0x40 | 0x1000  # MB_ICONINFORMATION | MB_SYSTEMMODAL
                )
                success = True
                self.logger.debug("ctypes 알림 성공")
            except Exception as e:
                self.logger.warning(f"ctypes 알림 실패: {e}")
                
        # 4. 대체 방법: Windows 시스템 소리
        if not success:
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                self.logger.info(f"알림 (소리만): {title} - {message}")
            except Exception as e:
                self.logger.error(f"시스템 소리도 실패: {e}")
                
        return success


class SoundNotifier(BaseNotifier):
    """소리 알림 발송"""
    
    def __init__(self, 
                 sound_dir: Path,
                 logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            sound_dir: 소리 파일 디렉토리
            logger: 로거
        """
        super().__init__(logger)
        self.sound_dir = sound_dir
        self.sound_enabled = False
        
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                self.sound_enabled = True
            except Exception as e:
                self.logger.warning(f"pygame 초기화 실패: {e}")
                
    def send(self, title: str, message: str, **kwargs) -> bool:
        """
        소리 알림 발송
        
        Args:
            title: 제목 (미사용)
            message: 메시지 (미사용)
            **kwargs: sound_file, volume, condition_type 등
            
        Returns:
            성공 여부
        """
        if not self.sound_enabled:
            return False
            
        sound_file = kwargs.get('sound_file')
        volume = kwargs.get('volume', 100)
        condition_type = kwargs.get('condition_type')
        
        # 사운드 파일 경로 결정
        if sound_file:
            sound_path = self.sound_dir / sound_file
        else:
            # 기본 사운드 사용
            sound_path = None
            
        # 파일이 있으면 재생
        if sound_path and sound_path.exists():
            if PYGAME_AVAILABLE:
                try:
                    pygame.mixer.music.load(str(sound_path))
                    pygame.mixer.music.set_volume(volume / 100)
                    pygame.mixer.music.play()
                    return True
                except Exception as e:
                    self.logger.error(f"pygame 소리 재생 실패: {e}")
                    
        # 시스템 소리로 대체
        try:
            if condition_type in [AlarmConditionType.ERROR_LEVEL, 
                                 AlarmConditionType.PROCESSING_FAILED]:
                winsound.MessageBeep(winsound.MB_ICONHAND)  # 오류 소리
            else:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)  # 경고 소리
            return True
        except Exception as e:
            self.logger.error(f"시스템 소리 재생 실패: {e}")
            
        return False


class PopupNotifier(BaseNotifier):
    """팝업 대화상자 알림"""
    
    def send(self, title: str, message: str, **kwargs) -> bool:
        """
        팝업 알림 발송
        
        Args:
            title: 제목
            message: 메시지
            **kwargs: 추가 옵션
            
        Returns:
            성공 여부
        """
        # 별도 스레드에서 실행
        def show():
            try:
                messagebox.showinfo(title, message)
                return True
            except Exception as e:
                self.logger.error(f"팝업 표시 실패: {e}")
                return False
                
        thread = threading.Thread(target=show, daemon=True)
        thread.start()
        return True


class TrayNotifier(BaseNotifier):
    """트레이 아이콘 알림"""
    
    def __init__(self, 
                 on_tray_update: Optional[Callable[[str, str], None]] = None,
                 logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            on_tray_update: 트레이 업데이트 콜백
            logger: 로거
        """
        super().__init__(logger)
        self.on_tray_update = on_tray_update
        
    def send(self, title: str, message: str, **kwargs) -> bool:
        """
        트레이 알림 발송
        
        Args:
            title: 제목
            message: 메시지
            **kwargs: 추가 옵션
            
        Returns:
            성공 여부
        """
        if self.on_tray_update:
            try:
                self.on_tray_update(title, message)
                return True
            except Exception as e:
                self.logger.error(f"트레이 업데이트 실패: {e}")
                
        return False


class LogNotifier(BaseNotifier):
    """로그 알림"""
    
    def send(self, title: str, message: str, **kwargs) -> bool:
        """
        로그 알림 발송
        
        Args:
            title: 제목
            message: 메시지
            **kwargs: level (로그 레벨)
            
        Returns:
            성공 여부
        """
        level = kwargs.get('level', 'info')
        
        try:
            if level == 'debug':
                self.logger.debug(f"알람: {title} - {message}")
            elif level == 'warning':
                self.logger.warning(f"알람: {title} - {message}")
            elif level == 'error':
                self.logger.error(f"알람: {title} - {message}")
            else:
                self.logger.info(f"알람: {title} - {message}")
            return True
        except Exception as e:
            print(f"로그 알림 실패: {e}")
            return False


class NotifierFactory:
    """알림 발송자 팩토리"""
    
    @staticmethod
    def create_notifier(notifier_type: str, **kwargs) -> Optional[BaseNotifier]:
        """
        알림 발송자 생성
        
        Args:
            notifier_type: 알림 타입
            **kwargs: 추가 옵션
            
        Returns:
            알림 발송자 인스턴스
        """
        logger = kwargs.get('logger')
        
        if notifier_type == 'system':
            return SystemNotifier(logger)
        elif notifier_type == 'sound':
            sound_dir = kwargs.get('sound_dir', Path("data/sounds"))
            return SoundNotifier(sound_dir, logger)
        elif notifier_type == 'popup':
            return PopupNotifier(logger)
        elif notifier_type == 'tray':
            on_tray_update = kwargs.get('on_tray_update')
            return TrayNotifier(on_tray_update, logger)
        elif notifier_type == 'log':
            return LogNotifier(logger)
        else:
            return None