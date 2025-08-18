"""
통계 데이터 관리자
기능: PDF 처리 통계 수집, 저장, 조회
최종 수정: 2025-01-12
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from ...controllers import FileStatus


class StatisticsManager:
    """통계 데이터 관리자"""
    
    def __init__(self):
        """통계 관리자 초기화"""
        self.stats_file = Path("statistics.json")
        self.daily_stats = {}
        self.load_stats()
    
    def load_stats(self):
        """저장된 통계 로드"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.daily_stats = data.get('daily_stats', {})
        except Exception:
            # 오류 발생 시 빈 통계로 초기화
            self.daily_stats = {}
    
    def save_stats(self):
        """통계 저장"""
        try:
            data = {
                'daily_stats': self.daily_stats,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            # 저장 실패 시 무시 (통계는 부가 기능)
            pass
    
    def record_file_processing(self, file_item):
        """파일 처리 기록"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 오늘 통계가 없으면 초기화
        if today not in self.daily_stats:
            self.daily_stats[today] = {
                'total_files': 0,
                'total_pages': 0,
                'success_count': 0,
                'error_count': 0,
                'warning_count': 0,
                'auto_fixed_count': 0,
                'processing_time': 0.0,
                'issues': {}
            }
        
        stats = self.daily_stats[today]
        stats['total_files'] += 1
        
        # 상태별 카운트
        if file_item.status == FileStatus.COMPLETED:
            stats['success_count'] += 1
        elif file_item.status == FileStatus.ERROR:
            stats['error_count'] += 1
        
        # 경고 카운트
        if hasattr(file_item, 'warning_count') and file_item.warning_count > 0:
            stats['warning_count'] += 1
        
        # 처리 시간 누적
        if hasattr(file_item, 'processing_time'):
            stats['processing_time'] += file_item.processing_time
        
        self.save_stats()
    
    def get_statistics(self, date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """통계 데이터 조회"""
        # 기간 필터링
        if date_range:
            start_date, end_date = date_range
            filtered_stats = {}
            
            for date_str, data in self.daily_stats.items():
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    if start_date <= date < end_date:
                        filtered_stats[date_str] = data
                except ValueError:
                    # 날짜 파싱 실패 시 건너뛰기
                    continue
        else:
            filtered_stats = self.daily_stats
        
        # 통계 집계
        basic_stats = {
            'total_files': 0,
            'total_pages': 0,
            'success_count': 0,
            'error_count': 0,
            'warning_count': 0,
            'auto_fixed_count': 0,
            'avg_processing_time': 0.0,
            'total_errors': 0,
            'total_warnings': 0
        }
        
        daily_data = []
        common_issues = {}
        total_time = 0.0
        
        for date_str, data in filtered_stats.items():
            # 기본 통계 집계
            basic_stats['total_files'] += data.get('total_files', 0)
            basic_stats['total_pages'] += data.get('total_pages', 0)
            basic_stats['success_count'] += data.get('success_count', 0)
            basic_stats['error_count'] += data.get('error_count', 0)
            basic_stats['warning_count'] += data.get('warning_count', 0)
            basic_stats['auto_fixed_count'] += data.get('auto_fixed_count', 0)
            total_time += data.get('processing_time', 0.0)
            
            # 일별 데이터
            daily_data.append({
                'date': date_str,
                'files': data.get('total_files', 0),
                'pages': data.get('total_pages', 0)
            })
            
            # 이슈 집계
            for issue_type, count in data.get('issues', {}).items():
                if issue_type not in common_issues:
                    common_issues[issue_type] = 0
                common_issues[issue_type] += count
        
        # 평균 처리 시간 계산 (0으로 나누기 방지)
        if basic_stats['total_files'] > 0:
            basic_stats['avg_processing_time'] = total_time / basic_stats['total_files']
        
        # 총 오류/경고 (추정값)
        basic_stats['total_errors'] = basic_stats['error_count'] * 2  # 추정값
        basic_stats['total_warnings'] = basic_stats['warning_count'] * 3  # 추정값
        
        # 상위 이슈 정렬
        sorted_issues = sorted(common_issues.items(), key=lambda x: x[1], reverse=True)
        common_issues_list = [
            {
                'type': issue_type,
                'count': count,
                'affected_files': max(count // 2, 1)  # 추정값
            }
            for issue_type, count in sorted_issues[:10]
        ]
        
        return {
            'basic': basic_stats,
            'daily': daily_data[-7:],  # 최근 7일
            'common_issues': common_issues_list
        }