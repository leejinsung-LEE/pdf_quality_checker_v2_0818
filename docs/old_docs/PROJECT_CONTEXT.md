# PDF Quality Checker v2.0 - 프로젝트 컨텍스트

> 이 문서는 프로젝트의 현재 상태와 향후 작업을 위한 핵심 정보만을 담고 있습니다.

## 🎯 프로젝트 상태: 100% 완료

### 현재 작동 상태
- ✅ **모든 핵심 기능 정상 작동**
- ✅ **프로덕션 사용 가능**
- ✅ **테스트 완료**

---

## 📁 핵심 파일 위치

### 메인 진입점
- `main.py` - GUI 애플리케이션 시작
- `test_worker.py` - 워커 시스템 테스트
- `test_complete_pipeline.py` - 전체 파이프라인 테스트

### 핵심 모듈
```
src/
├── core/           # 분석, 검사, 수정 로직
├── processing/     # 파이프라인, 워커, 큐 시스템  
├── ui/            # GUI (MVC 패턴)
├── reporting/     # 보고서 생성
└── external/      # 외부 도구 연동
```

### 설정 파일
- `CLAUDE.md` - AI 작업 지침
- `PROMPTS.md` - 품질 관리 체크리스트
- `src/config/constants.py` - 품질 기준 상수
- `data/profiles/` - 검사 프로파일

---

## 🔧 주요 컴포넌트 관계

```
사용자 → GUI → FileController → QueueManager → WorkerPool
                                      ↓
                              ProcessingPipeline
                                      ↓
                    [Analyzer → Checker → Fixer → Reporter]
```

---

## 💡 핵심 기능 요약

### 1. PDF 분석 및 검사
- **5개 분석기**: 메타데이터, 페이지, 폰트, 색상, 이미지
- **5개 체커**: 색상, 폰트, 이미지, 재단선, 메타데이터
- **품질 점수**: 0-100점 자동 계산

### 2. 자동 수정
- **RGB→CMYK 변환**: `ColorFixer` + Ghostscript
- **폰트 처리**: `FontFixer` - 임베딩 또는 아웃라인
- **이미지 최적화**: `ImageFixer` - 해상도 조정

### 3. 자동화
- **폴더 감시**: `FolderWatcher` - 실시간 감지
- **배치 처리**: `BatchProcessor` - 대량 처리
- **워커 풀**: `WorkerPool` - 멀티스레드

### 4. 보고서
- HTML, JSON, PDF, TXT 형식 지원
- 상세 분석 결과 및 개선 제안

---

## ⚙️ 기술 의존성

### 필수 Python 패키지
```
customtkinter     # GUI
pikepdf          # PDF 처리
PyMuPDF          # PDF 분석
watchdog         # 폴더 감시
reportlab        # PDF 생성
jinja2           # 템플릿
```

### 외부 도구 (포함됨)
- `gs/` - Ghostscript (RGB→CMYK 변환)
- `poppler/` - PDF 도구 (폰트 분석 등)

---

## 📝 작업 시 주의사항

### 1. 워커 시스템
- QueueManager가 자동으로 워커를 시작함
- `auto_start_workers=True`가 기본값
- 2개 워커가 동시 처리

### 2. 파일 처리 플로우
```python
# FileController에서 작업 추가
controller.add_files(files, profile="default")
# → QueueManager가 워커에 분배
# → ProcessingWorker가 실제 처리
# → 콜백으로 UI 업데이트
```

### 3. 자동 수정 옵션
```python
fix_options = {
    'fix_rgb': True,     # RGB→CMYK 변환
    'fix_fonts': True,   # 폰트 임베딩/아웃라인
    'fix_images': False  # 이미지 최적화
}
```

---

## 🐛 알려진 이슈 및 해결

### ✅ 해결된 이슈
1. **ColorInfo 속성 문제** → 호환성 속성 추가
2. **워커 미연결** → 이미 연결되어 있었음
3. **UI 업데이트** → 콜백 메커니즘 수정

### ⚠️ 제한사항
- 암호화된 PDF 처리 불가
- 500MB 이상 파일은 느림
- 일부 특수 CJK 폰트 제한

---

## 🚀 빠른 시작

### GUI 실행
```bash
python main.py
```

### 테스트
```bash
# 워커 테스트
python test_worker.py

# 전체 파이프라인 테스트  
python test_complete_pipeline.py
```

### 코드에서 사용
```python
from src.processing.pipeline import process_pdf

result = process_pdf(
    "input.pdf", 
    profile="default",
    auto_fix=True
)
```

---

## 📊 성능 지표
- 단일 파일: ~0.04초 (1페이지)
- RGB→CMYK 변환: ~0.8초
- 메모리: 파일 크기의 2-3배
- 동시 처리: 2개 워커 기본

---

## 🔄 향후 확장 (Phase 6)
- [ ] 판짜기(Imposition) 기능
- [ ] 클라우드 연동
- [ ] 웹 인터페이스
- [ ] API 서버

---

## 📚 참고 문서
- `docs/PDF_Quality_Checker_v2.0_최종설계명세서.md` - 전체 설계
- `PROMPTS.md` - 코드 품질 체크리스트
- `requirements.txt` - 의존성 목록

---

**마지막 업데이트**: 2025-08-07  
**상태**: ✅ 완료  
**다음 작업**: 사용자 피드백 반영