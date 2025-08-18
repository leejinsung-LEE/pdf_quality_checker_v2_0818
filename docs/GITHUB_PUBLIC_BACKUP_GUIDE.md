# GitHub 퍼블릭 저장소 백업 가이드

## 저장소 정보
- **퍼블릭 저장소**: https://github.com/leejinsung-LEE/pdf_quality_checker_v2_0818
- **프라이빗 저장소**: https://github.com/leejinsung-LEE/pdf_quality_checker_v2
- **현재 퍼블릭 브랜치**: clean-backup

## 백업 전략

### 1. 이중 저장소 운영 목적
- **프라이빗**: 전체 개발 히스토리, 민감한 정보 포함, 실제 개발용
- **퍼블릭**: 오픈소스 공유, 포트폴리오, 민감한 정보 제외

### 2. 민감한 정보 관리
퍼블릭 저장소에서 제외해야 할 항목:
- API 키, 토큰, 비밀번호
- 개인 정보가 포함된 데이터베이스
- 내부 문서 및 기밀 정보
- 라이선스가 있는 상용 코드

## 백업 방법

### 방법 1: 클린 히스토리로 새 브랜치 생성 (권장)
```bash
# 1. 히스토리 없는 새 브랜치 생성
git checkout --orphan public-backup

# 2. 모든 파일 스테이징
git add -A

# 3. 초기 커밋 생성
git commit -m "Initial public release: PDF Quality Checker v2"

# 4. 퍼블릭 저장소 추가 (이미 있다면 생략)
git remote add public https://github.com/leejinsung-LEE/pdf_quality_checker_v2_0818.git

# 5. 퍼블릭 저장소에 푸시
git push public public-backup --force
```

### 방법 2: 기존 브랜치에서 민감한 정보 제거
```bash
# 1. 새 브랜치 생성
git checkout -b public-release

# 2. 민감한 파일 제거
git rm --cached sensitive_file.txt
echo "sensitive_file.txt" >> .gitignore

# 3. 변경사항 커밋
git commit -m "Remove sensitive information for public release"

# 4. 퍼블릭 저장소에 푸시
git push public public-release
```

### 방법 3: 자동화 스크립트 사용
```bash
# backup_to_public.sh 스크립트 생성
#!/bin/bash

# 현재 브랜치 저장
CURRENT_BRANCH=$(git branch --show-current)

# 클린 브랜치 생성
git checkout --orphan temp-public

# 민감한 파일 제외하고 추가
git add -A
git reset -- .env
git reset -- config/secrets.json
git reset -- data/database/*.db

# 커밋
git commit -m "Public backup: $(date +%Y%m%d_%H%M%S)"

# 퍼블릭에 푸시
git push public temp-public:main --force

# 원래 브랜치로 복귀
git checkout $CURRENT_BRANCH
git branch -D temp-public
```

## 정기 백업 워크플로우

### 일일 백업
1. **프라이빗 저장소**: 모든 변경사항 즉시 푸시
2. **퍼블릭 저장소**: 주요 기능 완성 시 클린 버전 푸시

### 주간 백업
```bash
# 주간 백업 스크립트
# 매주 금요일 실행

# 프라이빗 백업
git push origin main

# 퍼블릭 백업 (클린 버전)
git checkout --orphan weekly-public
git add -A
git commit -m "Weekly public backup: Week $(date +%U)"
git push public weekly-public:main --force
```

## 민감한 정보 체크리스트

### 반드시 제외할 파일
- [ ] `.env` 파일
- [ ] `config/secrets.json`
- [ ] `data/database/*.db` (실제 사용자 데이터)
- [ ] `logs/*.log` (민감한 로그 정보)
- [ ] `backups/` 디렉토리
- [ ] API 키가 포함된 설정 파일

### 검토가 필요한 파일
- [ ] `config.yaml` (API 엔드포인트 확인)
- [ ] 테스트 파일 (하드코딩된 인증 정보)
- [ ] 문서 파일 (내부 URL, 이메일 주소)

## GitHub Actions 자동화

### .github/workflows/public-backup.yml
```yaml
name: Public Repository Backup

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 5'  # 매주 금요일 자정

jobs:
  backup:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
      with:
        fetch-depth: 0
    
    - name: Create clean branch
      run: |
        git config user.name "GitHub Actions"
        git config user.email "actions@github.com"
        git checkout --orphan public-clean
        
    - name: Remove sensitive files
      run: |
        rm -f .env
        rm -rf data/database/
        rm -rf backups/
        
    - name: Commit clean version
      run: |
        git add -A
        git commit -m "Automated public backup: ${{ github.run_number }}"
        
    - name: Push to public repo
      env:
        PUBLIC_REPO_TOKEN: ${{ secrets.PUBLIC_REPO_TOKEN }}
      run: |
        git remote add public https://${PUBLIC_REPO_TOKEN}@github.com/leejinsung-LEE/pdf_quality_checker_v2_0818.git
        git push public public-clean:main --force
```

## 보안 고려사항

### Git 히스토리 정리
민감한 정보가 커밋 히스토리에 남아있는 경우:

```bash
# BFG Repo-Cleaner 사용
java -jar bfg.jar --delete-files "*.env" --no-blob-protection
git reflog expire --expire=now --all && git gc --prune=now --aggressive

# 또는 git filter-branch 사용
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/sensitive-file" \
  --prune-empty --tag-name-filter cat -- --all
```

### GitHub Secret Scanning
- GitHub의 Secret Scanning 기능 활성화
- Push Protection 설정으로 실수 방지
- 정기적인 보안 알림 확인

## 문제 해결

### 토큰 감지 오류
```
error: GH013: Repository rule violations found
```
해결 방법:
1. 감지된 파일 확인: `git rev-list --objects --all | grep <blob-id>`
2. 파일에서 토큰 제거
3. 클린 브랜치로 다시 시작

### 대용량 파일 경고
```
warning: File is XX MB; this is larger than GitHub's recommended maximum
```
해결 방법:
1. Git LFS 사용 고려
2. 불필요한 대용량 파일 제외
3. `.gitignore`에 추가

## 유용한 명령어

### 원격 저장소 관리
```bash
# 원격 저장소 목록 확인
git remote -v

# 원격 저장소 추가
git remote add public https://github.com/username/public-repo.git

# 원격 저장소 URL 변경
git remote set-url public https://github.com/username/new-repo.git

# 원격 저장소 제거
git remote remove public
```

### 브랜치 관리
```bash
# 로컬 브랜치 목록
git branch

# 원격 브랜치 목록
git branch -r

# 브랜치 삭제
git branch -d branch-name

# 원격 브랜치 삭제
git push origin --delete branch-name
```

## 베스트 프랙티스

1. **정기적인 백업**: 주 1회 이상 퍼블릭 저장소 업데이트
2. **자동화**: GitHub Actions나 스크립트로 백업 자동화
3. **검증**: 푸시 전 민감한 정보 재확인
4. **문서화**: 변경사항과 백업 일정 기록
5. **테스트**: 퍼블릭 저장소 클론 후 정상 작동 확인

## 연락처 및 지원
- 프로젝트 관리자: [이메일 주소]
- 이슈 트래커: https://github.com/leejinsung-LEE/pdf_quality_checker_v2_0818/issues
- 위키: https://github.com/leejinsung-LEE/pdf_quality_checker_v2_0818/wiki

---
*최종 업데이트: 2025-01-18*