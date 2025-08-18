"""
폴더별 설정 테스트
"""

from pathlib import Path
import time

# UTF-8 인코딩 설정
from _utf8_setup import setup_utf8_encoding

from src.processing.folder_watcher import FolderWatcher, FolderConfig

# 테스트 폴더 생성
# 테스트 폴더 경로 설정
fixtures_dir = Path(__file__).parent.parent / 'fixtures'

test_folders = {
    str(fixtures_dir / 'test_rgb_fix'): {
        'profile': 'default',
        'check_settings': {
            'check_color': True,
            'check_font': False,
            'check_image': False,
            'check_bleed': False,
            'check_metadata': False
        },
        'auto_fix_settings': {
            'fix_rgb': True,
            'fix_fonts': False,
            'fix_images': False
        },
        'generate_report': True,
        'report_formats': ['html']
    },
    str(fixtures_dir / 'test_font_check'): {
        'profile': 'default',
        'check_settings': {
            'check_color': False,
            'check_font': True,
            'check_image': False,
            'check_bleed': False,
            'check_metadata': False
        },
        'auto_fix_settings': {
            'fix_rgb': False,
            'fix_fonts': True,
            'fix_images': False
        },
        'generate_report': True,
        'report_formats': ['json']
    },
    str(fixtures_dir / 'test_no_auto'): {
        'profile': 'default',
        'check_settings': {
            'check_color': True,
            'check_font': True,
            'check_image': True,
            'check_bleed': True,
            'check_metadata': True
        },
        'auto_fix_settings': {},  # 자동 수정 없음
        'auto_process': False,  # 자동 처리 비활성화
        'generate_report': False
    }
}

def setup_test_folders():
    """테스트 폴더 설정"""
    watcher = FolderWatcher()
    
    for folder_name, settings in test_folders.items():
        folder_path = Path(folder_name)
        folder_path.mkdir(exist_ok=True)
        
        # 폴더 추가
        config = FolderConfig(
            path=folder_path,
            profile=settings['profile'],
            check_settings=settings['check_settings'],
            auto_fix_settings=settings['auto_fix_settings'],
            auto_process=settings.get('auto_process', True),
            generate_report=settings.get('generate_report', True),
            report_formats=settings.get('report_formats', ['html'])
        )
        
        watcher.folder_configs[str(folder_path.absolute())] = config
        print(f"[OK] 폴더 설정 추가: {folder_name}")
        print(f"   - 검사 항목: {list(k for k, v in settings['check_settings'].items() if v)}")
        print(f"   - 자동 수정: {list(k for k, v in settings['auto_fix_settings'].items() if v)}")
        print(f"   - 자동 처리: {settings.get('auto_process', True)}")
        print(f"   - 보고서: {settings.get('generate_report', True)}")
        print()
    
    # 설정 저장
    watcher._save_config()
    print("[SAVE] 설정 파일 저장 완료: data/watch_folders.json")
    
    return watcher

def test_folder_processing():
    """폴더별 처리 테스트"""
    print("=" * 60)
    print("폴더별 설정 테스트")
    print("=" * 60)
    print()
    
    # 1. 테스트 폴더 설정
    watcher = setup_test_folders()
    
    # 2. 폴더 감시 시작
    print("\n[START] 폴더 감시 시작...")
    watcher.start_watching()
    
    # 3. 각 폴더에 테스트 파일 복사
    test_file = Path(__file__).parent.parent / "fixtures" / "test_sample.pdf"
    if not test_file.exists():
        print(f"[WARNING] {test_file} 파일이 없습니다.")
        return
    
    import shutil
    for folder_name in test_folders.keys():
        folder_path = Path(folder_name)
        target_file = folder_path / f"test_{folder_name}.pdf"
        shutil.copy(test_file, target_file)
        print(f"[COPY] 파일 복사: {target_file}")
    
    # 4. 처리 대기
    print("\n[WAIT] 처리 대기 중...")
    time.sleep(10)
    
    # 5. 결과 확인
    print("\n[RESULT] 처리 결과:")
    for folder_name in test_folders.keys():
        folder_path = Path(folder_name)
        config = watcher.folder_configs.get(str(folder_path.absolute()))
        if config:
            print(f"\n{folder_name}:")
            print(f"  - 처리된 파일 수: {config.files_processed}")
            print(f"  - 마지막 처리: {config.last_processed}")
            
            # 보고서 확인
            if config.generate_report:
                reports = list(Path("reports").glob(f"*{folder_name}*"))
                if reports:
                    print(f"  - 생성된 보고서: {len(reports)}개")
                    for report in reports[:3]:
                        print(f"    * {report.name}")
    
    # 6. 감시 중지
    print("\n[STOP] 폴더 감시 중지...")
    watcher.stop_watching()
    
    print("\n[COMPLETE] 테스트 완료!")

if __name__ == "__main__":
    test_folder_processing()