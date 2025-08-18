# -*- coding: utf-8 -*-
"""
백업 압축 관리

백업 파일의 압축 및 압축 해제 기능을 제공합니다.
"""

import zipfile
import shutil
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime


class BackupCompressor:
    """백업 압축 관리자"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        
    def compress_backup(self, source_path: Path, backup_id: str, 
                       backup_dir: Path) -> Optional[Path]:
        """
        백업 파일 압축
        
        Args:
            source_path: 원본 파일 경로
            backup_id: 백업 ID
            backup_dir: 백업 디렉토리
            
        Returns:
            Optional[Path]: 압축된 백업 파일 경로
        """
        try:
            # 백업 서브디렉토리 생성
            backup_subdir = backup_dir / source_path.name
            backup_subdir.mkdir(exist_ok=True)
            
            # ZIP 파일 경로
            zip_path = backup_subdir / f"{backup_id}.zip"
            
            # ZIP으로 압축
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # 파일 추가 시 원본 파일명 유지
                zf.write(source_path, source_path.name)
                
                # 메타데이터 추가
                info = zipfile.ZipInfo('backup_info.txt')
                info.date_time = datetime.now().timetuple()[:6]
                metadata = f"Backup ID: {backup_id}\n"
                metadata += f"Original: {source_path}\n"
                metadata += f"Created: {datetime.now().isoformat()}\n"
                zf.writestr(info, metadata)
                
            self.logger.debug(f"백업 압축 완료: {zip_path}")
            return zip_path
            
        except Exception as e:
            self.logger.error(f"백업 압축 실패: {e}")
            return None
            
    def decompress_backup(self, zip_path: Path, 
                         target_path: Path) -> bool:
        """
        백업 파일 압축 해제 및 복원
        
        Args:
            zip_path: 압축 파일 경로
            target_path: 복원 대상 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            if not zip_path.exists():
                self.logger.error(f"압축 파일을 찾을 수 없습니다: {zip_path}")
                return False
                
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # 임시 디렉토리에 압축 해제
                temp_dir = zip_path.parent / f"temp_{zip_path.stem}"
                temp_dir.mkdir(exist_ok=True)
                
                try:
                    # 파일 추출
                    zf.extractall(temp_dir)
                    
                    # 원본 파일 찾기 (backup_info.txt 제외)
                    extracted_files = list(temp_dir.glob("*"))
                    pdf_files = [f for f in extracted_files 
                                if f.suffix.lower() == '.pdf']
                    
                    if pdf_files:
                        # PDF 파일 복원
                        shutil.copy2(pdf_files[0], target_path)
                        self.logger.debug(f"백업 복원 완료: {target_path}")
                        return True
                    else:
                        # PDF가 아닌 경우 첫 번째 파일 복원
                        source_files = [f for f in extracted_files 
                                      if f.name != 'backup_info.txt']
                        if source_files:
                            shutil.copy2(source_files[0], target_path)
                            return True
                            
                    self.logger.error("복원할 파일을 찾을 수 없습니다")
                    return False
                    
                finally:
                    # 임시 디렉토리 정리
                    if temp_dir.exists():
                        shutil.rmtree(temp_dir)
                        
        except Exception as e:
            self.logger.error(f"백업 압축 해제 실패: {e}")
            return False
            
    def get_compressed_size(self, zip_path: Path) -> int:
        """
        압축된 백업 파일 크기 조회
        
        Args:
            zip_path: 압축 파일 경로
            
        Returns:
            int: 파일 크기 (바이트)
        """
        try:
            if zip_path.exists():
                return zip_path.stat().st_size
            return 0
        except (OSError, PermissionError) as e:
            self.logger.error(f"압축 파일 크기 조회 실패: {e}")
            return 0
            
    def verify_compressed_backup(self, zip_path: Path) -> bool:
        """
        압축된 백업 파일 무결성 검증
        
        Args:
            zip_path: 압축 파일 경로
            
        Returns:
            bool: 유효 여부
        """
        try:
            if not zip_path.exists():
                return False
                
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # ZIP 파일 테스트
                result = zf.testzip()
                if result is not None:
                    self.logger.error(f"손상된 파일: {result}")
                    return False
                    
                # 최소 1개 이상의 파일 확인
                if len(zf.namelist()) == 0:
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"백업 검증 실패: {e}")
            return False
            
    def list_compressed_contents(self, zip_path: Path) -> List[str]:
        """
        압축 파일 내용 목록 조회
        
        Args:
            zip_path: 압축 파일 경로
            
        Returns:
            List[str]: 파일 목록
        """
        try:
            if not zip_path.exists():
                return []
                
            with zipfile.ZipFile(zip_path, 'r') as zf:
                return zf.namelist()
                
        except Exception as e:
            self.logger.error(f"압축 파일 목록 조회 실패: {e}")
            return []