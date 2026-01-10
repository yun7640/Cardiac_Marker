# KEQAS hs_TnI 기관별 보고서 조회 대시보드 생성

import pandas as pd
import os
import json
from pathlib import Path

# 설정
BASE_PATH = "G:/내 드라이브/00_KEQAS/Troponin_I/Data"
os.chdir(BASE_PATH)

# ===== GitHub Pages 설정 =====
# GitHub를 통한 외부 공유 설정
GITHUB_USERNAME = "yun7640"  # 본인 GitHub 사용자명으로 변경
GITHUB_REPO = "Cardiac_Marker"  # GitHub 리포지토리 이름
GITHUB_PAGES_URL = f"https://{GITHUB_USERNAME}.github.io/{GITHUB_REPO}"
USE_GITHUB_PAGES = True  # True로 설정하면 GitHub Pages URL 사용

print(f"📋 GitHub Pages 설정:")
print(f"   활성화: {USE_GITHUB_PAGES}")
if USE_GITHUB_PAGES:
    print(f"   URL: {GITHUB_PAGES_URL}")
    print(f"   설정 방법: create_dashboard.py의 GitHub 설정 섹션을 참고하세요.")

# 보고서 데이터 로드 (생성본 우선, 없으면 원본)
report_file = 'hs_TnI_lab_report_generated.csv'
if not os.path.exists(report_file):
    report_file = 'hs_TnI_lab_report.csv'

df = pd.read_csv(report_file)

# 결측을 공백으로 치환해 JSON 직렬화 시 NaN 노출 방지
df[['기준분류', '기기회사명', '기기명', '시약회사명', '시약명']] = df[
    ['기준분류', '기기회사명', '기기명', '시약회사명', '시약명']
].fillna('')

print("기관별 보고서 조회 대시보드 생성 중...")

# 기관별 고유 정보 추출 (기관코드 단위 1건)
institution_data = []
reports_dir = Path(BASE_PATH) / "reports" / "institution_reports"

for lab_code, lab_rows in df.groupby('기관코드'):
    lab_data = lab_rows.iloc[0]
    report_path = reports_dir / f"{lab_code}.html"
    
    # 로컬 또는 GitHub Pages URL 결정
    if USE_GITHUB_PAGES:
        report_url = f"{GITHUB_PAGES_URL}/reports/institution_reports/{lab_code}.html"
    else:
        report_url = f"reports/institution_reports/{lab_code}.html"
    
    institution_data.append({
        'code': lab_code,
        'ref_class': str(lab_data.get('기준분류', '')),
        'device_company': str(lab_data.get('기기회사명', '')),
        'device_name': str(lab_data.get('기기명', '')),
        'reagent_company': str(lab_data.get('시약회사명', '')),
        'reagent_name': str(lab_data.get('시약명', '')),
        'has_report': report_path.exists(),
        'report_url': report_url
    })

# 코드 기준 정렬 (기준분류별 편향 없이 균등 노출)
institution_data.sort(key=lambda x: x['code'])

# 기준분류 목록
ref_classes = sorted(df['기준분류'].unique().tolist())

# JSON 데이터 생성
institutions_json = json.dumps(institution_data, ensure_ascii=False, indent=2)
ref_classes_json = json.dumps(ref_classes, ensure_ascii=False)

# HTML 대시보드 생성
html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KEQAS 2025-2 심장표지자단백검사(hs-TnI) 기관별 보고서</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            padding: 40px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
        }}
        
        .header h1 {{
            font-size: 28px;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #666;
            font-size: 14px;
        }}
        
        .filter-section {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .filter-section label {{
            font-weight: bold;
            color: #333;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .filter-section select {{
            padding: 10px 15px;
            border: 2px solid #667eea;
            border-radius: 5px;
            font-size: 14px;
            font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
            cursor: pointer;
            background: white;
        }}
        
        .filter-section select:focus {{
            outline: none;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        
        .info-section {{
            background: #e7f3ff;
            padding: 15px;
            border-left: 4px solid #667eea;
            margin-bottom: 20px;
            border-radius: 5px;
            color: #333;
        }}
        
        .info-section strong {{
            color: #667eea;
        }}
        
        .institutions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 12px;
        }}
        
        .institution-card {{
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            padding: 12px;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .institution-card:hover {{
            border-color: #667eea;
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.2);
            transform: translateY(-2px);
        }}
        
        .institution-card.hidden {{
            display: none;
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            padding-bottom: 6px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .card-code {{
            font-weight: bold;
            font-size: 14px;
            color: #667eea;
        }}
        
        .card-ref-class {{
            background: #667eea;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: bold;
        }}
        
        .card-info {{
            font-size: 11px;
            color: #666;
            line-height: 1.6;
        }}
        
        .card-info-label {{
            font-weight: bold;
            color: #333;
            display: inline-block;
            width: 65px;
        }}
        
        .card-button {{
            margin-top: 10px;
            width: 100%;
            padding: 8px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
            font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
            transition: background 0.3s ease;
        }}
        
        .card-button.disabled {{
            background: #cccccc;
            color: #666;
            cursor: not-allowed;
        }}
        
        .card-button:hover {{
            background: #764ba2;
        }}
        
        .stats {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
        
        .no-results {{
            grid-column: 1 / -1;
            text-align: center;
            padding: 40px;
            color: #999;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #999;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 KEQAS 2025-2 심장표지자단백검사(hs-TnI)</h1>
            <p>기관별 보고서 조회 대시보드</p>
        </div>
        
        <div class="filter-section">
            <label for="refClassFilter">
                🔍 기준분류 선택:
            </label>
            <select id="refClassFilter">
                <option value="">전체 보기</option>
            </select>
            <button onclick="resetFilter()" style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;">초기화</button>
        </div>
        
        <div class="info-section" id="infoSection">
            <strong>📊 전체 기관:</strong> <span id="totalCount">0</span>개 | 
            <strong>✓ 표시된 기관:</strong> <span id="displayCount">0</span>개
        </div>
        
        <div class="institutions-grid" id="institutionsGrid">
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number" id="statTotal">0</div>
                <div class="stat-label">총 기관 수</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="statRefClass">0</div>
                <div class="stat-label">기준분류 수</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="statSpecimens">3</div>
                <div class="stat-label">검체 수</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="statYear">2025</div>
                <div class="stat-label">프로그램 년도</div>
            </div>
        </div>
        
        <div class="footer">
            <p>KEQAS (외부정도관리) 기관별 보고서 - 각 기관의 개별 보고서를 확인하려면 기관 카드의 "보고서 보기" 버튼을 클릭하세요.</p>
            <p style="margin-top: 10px; font-size: 11px; color: #999;">
                📋 이 대시보드는 GitHub Pages를 통해 외부와 공유됩니다. 더 자세한 정보는 GitHub 리포지토리를 참조하세요.
            </p>
        </div>
    </div>
    
    <script>
        // 데이터 로드
        const institutions = {institutions_json};
        const refClasses = {ref_classes_json};
        
        // 초기화
        function initializeDashboard() {{
            // 기준분류 필터 채우기
            const filterSelect = document.getElementById('refClassFilter');
            refClasses.forEach(refClass => {{
                const option = document.createElement('option');
                option.value = refClass;
                option.textContent = refClass;
                filterSelect.appendChild(option);
            }});
            
            // 통계 업데이트
            document.getElementById('statTotal').textContent = institutions.length;
            document.getElementById('statRefClass').textContent = refClasses.length;
            
            // 기관 카드 렌더링
            renderInstitutions();
            
            // 필터 이벤트 리스너
            filterSelect.addEventListener('change', filterInstitutions);
        }}
        
        // 기관 카드 렌더링
        function renderInstitutions() {{
            const grid = document.getElementById('institutionsGrid');
            grid.innerHTML = '';
            
            institutions.forEach(inst => {{
                const card = document.createElement('div');
                card.className = 'institution-card';
                card.id = `card-${{inst.code}}`;
                const btnClass = inst.has_report ? 'card-button' : 'card-button disabled';
                const btnLabel = inst.has_report ? '📋 보고서 보기' : '보고서 없음';
                const btnAttr = inst.has_report ? `onclick="openReport('${{inst.code}}', '${{inst.report_url}}')"` : 'disabled';
                card.innerHTML = `
                    <div class="card-header">
                        <span class="card-code">${{inst.code}}</span>
                        <span class="card-ref-class">${{inst.ref_class}}</span>
                    </div>
                    <div class="card-info">
                        <div><span class="card-info-label">기기회사:</span> ${{inst.device_company}}</div>
                        <div><span class="card-info-label">기기명:</span> ${{inst.device_name}}</div>
                        <div><span class="card-info-label">시약회사:</span> ${{inst.reagent_company || '미입력'}}</div>
                        <div><span class="card-info-label">시약명:</span> ${{inst.reagent_name || '미입력'}}</div>
                    </div>
                    <button class="${{btnClass}}" ${{btnAttr}}>${{btnLabel}}</button>
                `;
                grid.appendChild(card);
            }});
            
            updateCounts();
        }}
        
        // 기관 필터링
        function filterInstitutions() {{
            const filterValue = document.getElementById('refClassFilter').value;
            const cards = document.querySelectorAll('.institution-card');
            
            cards.forEach(card => {{
                const code = card.id.replace('card-', '');
                const inst = institutions.find(i => i.code === code);
                
                if (filterValue === '' || inst.ref_class === filterValue) {{
                    card.classList.remove('hidden');
                }} else {{
                    card.classList.add('hidden');
                }}
            }});
            
            updateCounts();
        }}
        
        // 카운트 업데이트
        function updateCounts() {{
            const total = institutions.length;
            const displayed = document.querySelectorAll('.institution-card:not(.hidden)').length;
            document.getElementById('totalCount').textContent = total;
            document.getElementById('displayCount').textContent = displayed;
        }}
        
        // 보고서 열기
        function openReport(labCode, reportUrl) {{
            if (reportUrl) {{
                window.open(reportUrl, "_blank");
            }} else {{
                alert("보고서를 찾을 수 없습니다.");
            }}
        }}
        
        // 필터 초기화
        function resetFilter() {{
            document.getElementById('refClassFilter').value = '';
            filterInstitutions();
        }}
        
        // 페이지 로드 시 초기화
        window.addEventListener('load', initializeDashboard);
    </script>
</body>
</html>
"""

# 대시보드 저장
output_path = 'KEQAS_hs_TnI_Dashboard.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ 대시보드 생성 완료: {output_path}")
print(f"📊 총 기관 수: {len(institution_data)}")
print(f"📋 기준분류: {len(ref_classes)}개")
print(f"\n대시보드 특징:")
print("  - 기준분류별 필터링 기능")
print("  - 기관 카드 형식의 레이아웃")
print("  - 기관별 기기회사, 기기명, 시약정보 표시")
print("  - 각 기관의 개별 보고서 링크")
print(f"\n생성된 파일: {os.path.abspath(output_path)}")
