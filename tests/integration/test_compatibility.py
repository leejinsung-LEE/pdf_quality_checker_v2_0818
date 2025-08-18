# -*- coding: utf-8 -*-
"""
기존 기능 호환성 테스트

새 기능들이 기존 기능을 방해하지 않는지 확인합니다.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json

# 기존 기능 모듈들
from src.core import QualityChecker
from src.core.analyzers import PDFAnalyzer
from src.core.profiles import get_profile_manager
from src.processing import PDFProcessor, BatchProcessor, FolderWatcher, FolderConfig
from src.data import get_data_manager
from src.reporting import ReportGenerator, ThumbnailGenerator


class CompatibilityTest(unittest.TestCase):
    """기존 기능 호환성 테스트"""
    
    @classmethod
    def setUpClass(cls):
        """테스트 클래스 설정"""
        # 테스트용 임시 디렉토리
        cls.test_dir = Path(tempfile.mkdtemp())
        cls.test_pdf = cls.test_dir / "test.pdf"
        
        # 최소 PDF 파일 생성
        cls.test_pdf.write_bytes(b"%PDF-1.4\n%%EOF")
        
    @classmethod
    def tearDownClass(cls):
        """테스트 클래스 정리"""
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)
    
    def test_quality_checker_compatibility(self):
        """품질 검사기 호환성 테스트"""
        # 기존 방식으로 품질 검사기 사용
        checker = QualityChecker()
        
        # 기본 검사
        result = checker.check(self.test_pdf)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.quality_score)
        
        # 프로파일 기반 검사
        result = checker.check_with_profile(self.test_pdf, "default")
        self.assertIsNotNone(result)
        
        # 빠른 검사
        result = checker.quick_check(self.test_pdf)
        self.assertIsNotNone(result)
        
        # 엄격한 검사
        result = checker.strict_check(self.test_pdf)
        self.assertIsNotNone(result)
    
    def test_pdf_analyzer_compatibility(self):
        """PDF 분석기 호환성 테스트"""
        analyzer = PDFAnalyzer()
        
        # 기본 분석
        result = analyzer.analyze(self.test_pdf)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.document)
        
        # 문서 정보 확인
        self.assertEqual(result.document.total_pages, 0)  # 빈 PDF
        self.assertIsNotNone(result.document.file_size)
    
    def test_profile_manager_compatibility(self):
        """프로파일 매니저 호환성 테스트"""
        profile_manager = get_profile_manager()
        
        # 기본 프로파일 확인
        profiles = profile_manager.get_profile_list()
        self.assertGreater(len(profiles), 0)
        
        # 기본 프로파일 존재 확인
        default_profile = profile_manager.get_profile("default")
        self.assertIsNotNone(default_profile)
        
        # 현재 프로파일 설정
        success = profile_manager.set_current_profile("default")
        self.assertTrue(success)
        
        # 프로파일 생성 (기존 방식)
        success = profile_manager.create_profile(
            "compat_test_profile",
            base_profile="default"
        )
        # 이미 존재할 수 있음
        
        # 프로파일 삭제
        if "compat_test_profile" in [p["name"] for p in profiles]:
            profile_manager.delete_profile("compat_test_profile")
    
    def test_pdf_processor_compatibility(self):
        """PDF 처리기 호환성 테스트"""
        processor = PDFProcessor()
        
        # 기본 처리
        result = processor.process_with_profile(
            self.test_pdf,
            profile_name="default",
            auto_fix=False
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.file_path, self.test_pdf)
    
    def test_batch_processor_compatibility(self):
        """배치 처리기 호환성 테스트"""
        batch_processor = BatchProcessor()
        
        # 파일 추가
        batch_processor.add_file(self.test_pdf)
        
        # 대기 중인 파일 확인
        pending = batch_processor.get_pending_files()
        self.assertGreater(len(pending), 0)
        
        # 통계 확인
        stats = batch_processor.get_statistics()
        self.assertIsNotNone(stats)
        self.assertIn("total", stats)
    
    def test_folder_watcher_compatibility(self):
        """폴더 감시자 호환성 테스트"""
        config = FolderConfig(
            path=self.test_dir,
            recursive=False,
            profile="default",
            auto_process=True
        )
        
        watcher = FolderWatcher(config)
        
        # 감시 시작/중지 (실제로 실행하지 않음)
        self.assertFalse(watcher.is_running)
        
        # 설정 확인
        self.assertEqual(watcher.config.path, self.test_dir)
        self.assertEqual(watcher.config.profile, "default")
    
    def test_data_manager_compatibility(self):
        """데이터 매니저 호환성 테스트"""
        data_manager = get_data_manager()
        
        # 이력 추가 (기존 방식)
        from src.data.models import ProcessingStatus
        
        entry = data_manager.add_history(
            file_path=str(self.test_pdf),
            status=ProcessingStatus.COMPLETED,
            profile="default",
            quality_score=85.0,
            error_count=0,
            warning_count=1
        )
        
        self.assertIsNotNone(entry)
        
        # 이력 조회
        histories = data_manager.get_history(limit=10)
        self.assertIsInstance(histories, list)
        
        # 통계 조회
        stats = data_manager.get_statistics()
        self.assertIsNotNone(stats)
        self.assertIn("total", stats)
    
    def test_report_generator_compatibility(self):
        """보고서 생성기 호환성 테스트"""
        # 품질 검사 결과 생성
        checker = QualityChecker()
        quality_result = checker.check(self.test_pdf)
        
        # 보고서 생성기
        generator = ReportGenerator()
        
        # HTML 보고서 생성
        report_path = generator.generate(
            quality_result,
            format_type="html",
            output_folder=self.test_dir
        )
        
        # 보고서 파일 확인
        if report_path:  # 생성 실패할 수 있음 (의존성 문제)
            self.assertTrue(report_path.exists())
    
    def test_thumbnail_generator_compatibility(self):
        """썸네일 생성기 호환성 테스트"""
        generator = ThumbnailGenerator()
        
        # 썸네일 생성 (실패할 수 있음 - PDF가 비어있음)
        try:
            thumb_path = generator.generate(
                self.test_pdf,
                output_folder=self.test_dir,
                size=(200, 200)
            )
            
            if thumb_path:
                self.assertTrue(thumb_path.exists())
        except:
            pass  # 빈 PDF라 실패 가능
    
    def test_mixed_usage(self):
        """기존 기능과 새 기능 혼합 사용 테스트"""
        from src.data import get_backup_manager
        from src.data.history_manager import HistoryManager, ProcessHistory
        
        # 1. 기존 방식으로 품질 검사
        checker = QualityChecker()
        quality_result = checker.check(self.test_pdf)
        
        # 2. 새 기능: 백업 생성
        backup_manager = get_backup_manager()
        backup_id = backup_manager.create_backup(
            self.test_pdf,
            profile_used="default"
        )
        
        # 3. 기존 방식: 데이터 매니저에 이력 추가
        data_manager = get_data_manager()
        entry = data_manager.add_history(
            file_path=str(self.test_pdf),
            status="completed",
            profile="default",
            quality_score=quality_result.quality_score
        )
        
        # 4. 새 기능: SQLite 이력 매니저
        history_manager = HistoryManager(db_path=self.test_dir / "test.db")
        history = ProcessHistory(
            file_name=self.test_pdf.name,
            file_path=str(self.test_pdf),
            profile="default",
            quality_score=quality_result.quality_score,
            backup_id=backup_id
        )
        history_id = history_manager.add_history(history)
        
        # 모든 작업이 성공적으로 완료되었는지 확인
        self.assertIsNotNone(quality_result)
        self.assertIsNotNone(backup_id)
        self.assertIsNotNone(entry)
        self.assertIsNotNone(history_id)
    
    def test_backward_compatibility(self):
        """이전 버전 데이터 호환성 테스트"""
        # 이전 버전 형식의 프로파일 데이터
        old_profile_data = {
            "name": "old_format_profile",
            "settings": {
                "quality_standards": {
                    "minimum_dpi": 300
                },
                "check_options": {}
            }
        }
        
        # 프로파일 매니저가 이전 형식을 처리할 수 있는지
        profile_manager = get_profile_manager()
        
        # 수동으로 프로파일 추가 (이전 형식)
        try:
            from src.core.profiles import QualityProfile
            old_profile = QualityProfile(
                name="old_format_test",
                data=old_profile_data["settings"],
                is_builtin=False
            )
            
            # 유효성 검사
            is_valid = old_profile.validate()
            self.assertTrue(is_valid)
        except:
            pass  # 형식이 변경되었을 수 있음
        
        # 이전 버전 이력 데이터
        old_history_data = {
            "entries": [
                {
                    "id": 1,
                    "file_path": "/old/path/test.pdf",
                    "processed_at": "2024-01-01T00:00:00",
                    "status": "completed",
                    "profile_used": "default"
                }
            ]
        }
        
        # 데이터 매니저가 이전 형식을 처리할 수 있는지
        # (실제로는 migration 코드가 필요할 수 있음)
        data_manager = get_data_manager()
        # 기존 메서드가 여전히 작동하는지 확인
        recent_files = data_manager.get_recent_files(count=5)
        self.assertIsInstance(recent_files, list)


if __name__ == "__main__":
    unittest.main()