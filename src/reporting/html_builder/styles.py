# src/reporting/html_builder/styles.py
"""
HTML 보고서 스타일 관리
"""


class StyleManager:
    """CSS 스타일 관리자"""
    
    @staticmethod
    def get_main_styles() -> str:
        """메인 CSS 스타일"""
        return """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* 헤더 */
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        /* 섹션 공통 */
        .section {
            background: white;
            padding: 30px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .section-title {
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #2c3e50;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }
        
        /* 요약 카드 */
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e9ecef;
            transition: transform 0.3s ease;
        }
        
        .summary-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .summary-card .value {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .summary-card .label {
            color: #6c757d;
            font-size: 0.9em;
            text-transform: uppercase;
        }
        
        /* 품질 점수 */
        .quality-score {
            text-align: center;
            padding: 40px;
        }
        
        .score-circle {
            width: 200px;
            height: 200px;
            margin: 0 auto 20px;
            position: relative;
        }
        
        .score-value {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 3em;
            font-weight: bold;
        }
        
        .score-label {
            font-size: 1.2em;
            color: #6c757d;
        }
        
        /* 이슈 목록 */
        .issue-group {
            margin-bottom: 30px;
        }
        
        .issue-group-title {
            font-size: 1.3em;
            margin-bottom: 15px;
            color: #495057;
        }
        
        .issue-item {
            background: #f8f9fa;
            padding: 15px 20px;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 4px solid #dee2e6;
            transition: all 0.3s ease;
        }
        
        .issue-item:hover {
            background: #e9ecef;
        }
        
        .issue-item.error {
            border-left-color: #dc3545;
        }
        
        .issue-item.warning {
            border-left-color: #ffc107;
        }
        
        .issue-item.info {
            border-left-color: #17a2b8;
        }
        
        .issue-header {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .issue-severity {
            font-size: 1.5em;
            margin-right: 10px;
        }
        
        .issue-title {
            font-weight: 600;
            flex: 1;
        }
        
        .issue-pages {
            color: #6c757d;
            font-size: 0.9em;
        }
        
        .issue-description {
            color: #6c757d;
            margin-bottom: 8px;
        }
        
        .issue-suggestions {
            margin-top: 10px;
            padding: 10px;
            background: #e7f3ff;
            border-radius: 4px;
            font-size: 0.9em;
        }
        
        /* 상세 정보 */
        .details-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }
        
        .detail-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
        }
        
        .detail-card h3 {
            margin-bottom: 15px;
            color: #495057;
        }
        
        .detail-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .detail-row:last-child {
            border-bottom: none;
        }
        
        .detail-label {
            color: #6c757d;
        }
        
        .detail-value {
            font-weight: 500;
        }
        
        /* 태그 */
        .tag {
            display: inline-block;
            padding: 4px 12px;
            background: #e9ecef;
            color: #495057;
            border-radius: 20px;
            font-size: 0.85em;
            margin-right: 8px;
        }
        
        .tag.error {
            background: #f8d7da;
            color: #721c24;
        }
        
        .tag.warning {
            background: #fff3cd;
            color: #856404;
        }
        
        .tag.info {
            background: #d1ecf1;
            color: #0c5460;
        }
        
        /* 버튼 */
        .button {
            display: inline-block;
            padding: 10px 20px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s ease;
        }
        
        .button:hover {
            background: #0056b3;
        }
        
        /* 차트 컨테이너 */
        .chart-container {
            width: 100%;
            max-width: 400px;
            margin: 20px auto;
        }
        
        /* 반응형 */
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2em;
            }
            
            .summary-cards {
                grid-template-columns: 1fr;
            }
            
            .details-grid {
                grid-template-columns: 1fr;
            }
        }
        
        @media print {
            body {
                background: white;
            }
            
            .section {
                box-shadow: none;
                break-inside: avoid;
            }
            
            .button {
                display: none;
            }
        }
    </style>
        """
    
    @staticmethod
    def get_color_by_score(score: float) -> tuple:
        """
        점수에 따른 색상 반환
        
        Args:
            score: 품질 점수
            
        Returns:
            (color, grade) 튜플
        """
        if score >= 90:
            return '#28a745', '우수'
        elif score >= 70:
            return '#ffc107', '양호'
        elif score >= 50:
            return '#fd7e14', '주의'
        else:
            return '#dc3545', '불량'