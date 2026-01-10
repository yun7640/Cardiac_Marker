# KEQAS hs-TnI 기관별 보고서 및 대시보드

🏥 **2025년 2회차 심장표지자단백검사(High-Sensitivity Cardiac Troponin I) 외부정도관리(KEQAS) 기관별 보고서**

---

## 📊 프로젝트 개요

이 프로젝트는 KEQAS의 hs-TnI 검사 결과를 기관별로 분석하고 시각화한 대시보드와 개별 보고서를 제공합니다.

### 주요 기능
- ✅ **기관별 대시보드**: 194개 기관의 결과를 기준분류별로 필터링
- ✅ **히스토그램**: 전체 및 기준분류별 결과값 분포 (2.5%-97.5% 범위)
- ✅ **Youden Plot**: 검체 간 비교 분석 (기준분류, ±3SD 박스)
- ✅ **Levey-Jennings Chart**: SDI 추세 모니터링
- ✅ **통계 요약**: 기관별, 기준분류별, 세분류별 통계치
- ✅ **GitHub Pages 지원**: 외부 공유 및 온라인 접속

---

## 🌐 접속 방법

### GitHub Pages (온라인)
```
https://{your-github-username}.github.io/keqas-hs-tni/
```

### 로컬 접속 (개발/테스트)
1. 폴더 열기: `G:\내 드라이브\00_KEQAS\Troponin_I\Data`
2. `KEQAS_hs_TnI_Dashboard.html` 또는 `index.html` 더블클릭

---

## 📁 프로젝트 구조

```
keqas-hs-tni/
│
├── 📄 index.html                          # GitHub Pages 메인 페이지 (자동 리다이렉트)
├── 📄 KEQAS_hs_TnI_Dashboard.html         # 기관별 보고서 대시보드
│
├── 📁 reports/
│   └── 📁 institution_reports/            # 194개 기관별 상세 보고서
│       ├── LAB_001.html                   # Abbott Alinity I
│       ├── LAB_002.html                   # Siemens Atellica
│       ├── LAB_003.html
│       └── ... (LAB_194까지)
│
├── 📁 Data/                               # 소스 코드 및 데이터
│   ├── 📋 hs_TnI_input.csv               # 기관별 입력 데이터
│   ├── 📋 hs_TnI_lab_report.csv          # 원본 통계 보고서
│   ├── 📋 hs_TnI_lab_report_generated.csv # 생성된 보고서
│   ├── 🐍 generate_lab_report.py         # 기관별 보고서 생성 스크립트
│   ├── 🐍 create_dashboard.py            # 대시보드 생성 스크립트
│   └── 📄 GITHUB_SETUP.md                # GitHub Pages 설정 가이드
│
├── 📖 README.md                          # 이 파일
└── 📄 GITHUB_SETUP.md                    # 상세 설정 가이드

```

---

## 📊 대시보드 사용법

### 1. 기관 조회
- **기준분류 필터**: 기기 제조사별로 기관 필터링
- **전체 기관**: 194개 기관 정보 표시
- **기관 카드**: 각 기관의 기기회사, 기기명, 시약 정보 표시

### 2. 기관별 보고서 열기
- 기관 카드의 **"📋 보고서 보기"** 버튼 클릭
- 새 창에서 상세 보고서 열림

### 3. 통계 정보
- **총 기관 수**: 194개
- **기준분류 수**: 6개 (Abbott, Siemens, Roche, etc.)
- **검체 수**: 3개 (CCA-25-04, CCA-25-05, CCA-25-06)
- **프로그램 년도**: 2025년 2회차

---

## 📈 기관별 보고서 상세 정보

각 보고서는 다음을 포함합니다:

### 1. 검사 결과 요약 표
| 항목 | 설명 |
|------|------|
| Specimen | 검체명 |
| Your Result | 기관의 검사결과 |
| Group | ALL (전체) / 기준분류 / 세분류 |
| N | 기관 수 |
| Mean | 평균값 |
| SD | 표준편차 |
| CV(%) | 변동계수 |
| Median | 중간값 |
| Min/Max | 최소/최대값 |
| SDI | 표준화지수 |

### 2. 기준분류별 분포 히스토그램 (3개 검체)
- **X축**: 검사결과값 (pg/mL)
- **Y축**: 기관 수 (Frequency)
- **회색 바**: 전체 기관
- **파란 바**: 기준분류 기관
- **빨간 화살표**: Your Result (기관의 결과)
- **범위**: 2.5%-97.5% percentile

### 3. Youden Plot (3개 검체 쌍)
- **X/Y축**: 두 검체의 검사결과
- **회색 점**: 다른 기관
- **파란 점**: 해당 기관
- **검은 박스**: ±3 SD 범위
- **파란 십자**: 기준분류 평균

### 4. Levey-Jennings Chart (SDI 추세)
- **X축**: 3개 검체 (CCA-25-04, 05, 06)
- **Y축**: SDI (표준화지수)
- **기준선**: 0, ±1, ±2, ±3 SD

### 5. 확대 토글
- **크게 보기** 버튼: 히스토그램과 Youden 차트 확대
- 읽기 편의성 향상

---

## 🛠 GitHub Pages 배포 (GitHub를 통한 외부 공유)

### 빠른 시작

1. **GitHub 계정 확인**: https://github.com 가입/로그인

2. **리포지토리 생성**:
   - Repository name: `keqas-hs-tni`
   - Public 선택

3. **로컬 Git 설정**:
   ```bash
   cd "G:\내 드라이브\00_KEQAS\Troponin_I\Data"
   git init
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

4. **대시보드 업데이트** (선택사항):
   - `create_dashboard.py` 열기
   - `GITHUB_USERNAME = "your-github-username"` 입력
   - `USE_GITHUB_PAGES = True` 설정
   - `python create_dashboard.py` 실행

5. **GitHub에 업로드**:
   ```bash
   git remote add origin https://github.com/your-username/keqas-hs-tni.git
   git add .
   git commit -m "Initial commit: KEQAS hs-TnI 대시보드"
   git branch -M main
   git push -u origin main
   ```

6. **GitHub Pages 활성화**:
   - GitHub 리포지토리 → Settings → Pages
   - Branch: main 선택 → Save

7. **접속**:
   ```
   https://your-username.github.io/keqas-hs-tni/
   ```

📖 **상세 가이드**: [GITHUB_SETUP.md](GITHUB_SETUP.md) 참조

---

## 🔧 기술 스택

- **언어**: Python, HTML, CSS, JavaScript
- **라이브러리**: pandas, numpy, matplotlib
- **호스팅**: GitHub Pages
- **웹 프레임워크**: 정적 HTML (JavaScript 포함)

---

## 📝 데이터 설명

### hs_TnI_input.csv
기관의 입력 데이터:
```
기관코드, 검사코드, 검사명, 기기회사, 기기, 시약회사, 시약, 검사방법
CCA-25-04, CCA-25-05, CCA-25-06 (3개 검체의 결과값)
```

### hs_TnI_lab_report.csv / hs_TnI_lab_report_generated.csv
생성된 보고서:
- 기관별 통계 (ALL, 기준분류, 세분류)
- SDI 계산 값
- Outlier 판정

---

## 🔍 주요 지표 설명

### SDI (Standardized Difference Index)
```
SDI = (Your Result - Group Mean) / Group SD
```
- **0**: 완벽한 성능
- **±1**: 양호
- **±2**: 주의 필요
- **±3 이상**: 부적절

### CV (Coefficient of Variation)
```
CV = (SD / Mean) × 100 (%)
```
기관 간 정확도 비교

### Percentile 범위
- 2.5%-97.5%: 이상치 제외한 정상 범위
- 전체 데이터의 95%를 포함

---

## 📞 문제 해결

### Q: 대시보드가 로드되지 않는다
**A**: 
- 브라우저 캐시 삭제 후 새로고침
- URL 확인 (대소문자, 하이픈 구분)
- 인터넷 연결 확인

### Q: 보고서 링크가 작동하지 않는다
**A**:
- 로컬 테스트: `reports/institution_reports/LAB_001.html` 파일 존재 확인
- GitHub Pages: `USE_GITHUB_PAGES = True` 설정 확인

### Q: 차트가 표시되지 않는다
**A**:
- 대시보드 재생성: `python create_dashboard.py`
- 기관별 보고서 재생성: `python generate_lab_report.py`

### Q: GitHub에 푸시할 수 없다
**A**:
```bash
git config --global user.email "your.email@example.com"
git config --global user.name "Your Name"
git remote -v  # 원격 설정 확인
git push -u origin main
```

---

## 📚 참고 문서

- [GITHUB_SETUP.md](GITHUB_SETUP.md) - GitHub Pages 상세 설정 가이드
- [generate_lab_report.py](Data/generate_lab_report.py) - 보고서 생성 코드
- [create_dashboard.py](Data/create_dashboard.py) - 대시보드 생성 코드

---

## 📅 업데이트 이력

| 날짜 | 내용 |
|------|------|
| 2025-01-11 | 초기 버전 배포 (194개 기관) |
| 2025-01-11 | GitHub Pages 지원 추가 |
| 2025-01-11 | 히스토그램, Youden, Levey-Jennings 차트 추가 |

---

## 📄 라이선스

이 프로젝트는 KEQAS 외부정도관리 프로그램의 공식 결과 보고용입니다.

---

## 👥 문의 및 피드백

GitHub Issues를 통해 문제를 보고하거나 기능을 제안할 수 있습니다.

**마지막 업데이트**: 2025-01-11  
**프로그램**: KEQAS 2025-2 (심장표지자단백검사)  
**검체 수**: 3개 (CCA-25-04, CCA-25-05, CCA-25-06)  
**기관 수**: 194개
