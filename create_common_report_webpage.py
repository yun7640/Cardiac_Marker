#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KEQAS hs-TnI 공통보고서 웹페이지 생성 스크립트
PDF 형식의 공통보고서를 HTML 웹페이지로 변환
"""

import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt
import matplotlib
import base64
from io import BytesIO
import numpy as np

# 한글 폰트 설정
matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

# CSV 파일 로드
csv_file = "hs_TnI_common_report.csv"
df = pd.read_csv(csv_file, encoding='utf-8')

# 프로그램 정보 추출
program_year = df['회차년도'].iloc[0]
program_round = df['회차'].iloc[0]
program_code = df['프로그램코드'].iloc[0]
program_name = df['프로그램명'].iloc[0]
test_code = df['검사코드'].iloc[0]
test_name = df['상위검사명'].iloc[0]

# 전체(세분류 없음) 데이터만 필터링
overall_data = df[
    (df['기준분류명'].isna() | (df['기준분류명'] == '')) &
    (df['세분류명'].isna() | (df['세분류명'] == '')) &
    (df['기관수'].notna())
].copy()

# 기준분류별 데이터 필터링 (세분류 없음)
classification_data = df[
    (df['기준분류명'].notna()) &
    (df['기준분류명'] != '') &
    (df['세분류명'].isna() | (df['세분류명'] == '')) &
    (df['기관수'].notna())
].copy()

# 검체별 정보 추출
specimens = df[
    (df['기준분류명'].isna() | (df['기준분류명'] == '')) &
    (df['세분류명'].isna() | (df['세분류명'] == ''))
]['검체명'].unique()

def format_number(value):
    """숫자 포맷팅"""
    if pd.isna(value):
        return '-'
    try:
        val = float(value)
        if val == int(val):
            return f"{int(val):,}"
        else:
            return f"{val:,.2f}"
    except:
        return str(value)

def create_distribution_chart(classification_data):
    """기준분류별 기관 분포 도넛 차트"""
    if classification_data.empty:
        return None
    
    # 기준분류별 기관수 합산
    dist_data = classification_data.groupby('기준분류명')['기관수'].sum().sort_values(ascending=False)
    
    if dist_data.empty:
        return None
    
    # 차트 생성
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')
    
    colors = ['#1e40af', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
    colors = colors[:len(dist_data)]
    
    wedges, texts, autotexts = ax.pie(
        dist_data.values,
        labels=dist_data.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 11, 'weight': 'bold'},
        wedgeprops=dict(edgecolor='white', linewidth=2)
    )
    
    # 중앙 원 (도넛 모양)
    centre_circle = plt.Circle((0, 0), 0.70, fc='white', edgecolor='white', linewidth=2)
    ax.add_artist(centre_circle)
    
    # 범례
    ax.legend(
        [(f"{name}: {count}") for name, count in zip(dist_data.index, dist_data.values)],
        loc='center left',
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=10
    )
    
    ax.set_title('기준분류별 참가기관 분포', fontsize=14, weight='bold', pad=20)
    
    plt.tight_layout()
    
    # Base64로 변환
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return f"data:image/png;base64,{image_base64}"

def create_cv_comparison_chart(classification_data):
    """기준분류별 변동계수 비교 바차트"""
    if classification_data.empty:
        return None
    
    # 변동계수가 있는 데이터만 필터링
    cv_data = classification_data[classification_data['변동계수'].notna()].copy()
    cv_data = cv_data.sort_values('변동계수', ascending=True)
    
    if cv_data.empty:
        return None
    
    # 차트 생성
    fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')
    
    # 색상: CV값에 따라 달라짐
    colors = []
    for cv in cv_data['변동계수'].values:
        if cv <= 10:
            colors.append('#10b981')  # 초록색 (우수)
        elif cv <= 20:
            colors.append('#3b82f6')  # 파랑색 (양호)
        elif cv <= 30:
            colors.append('#f59e0b')  # 주황색 (주의)
        else:
            colors.append('#ef4444')  # 빨강색 (부주의)
    
    bars = ax.barh(cv_data['기준분류명'], cv_data['변동계수'], color=colors, edgecolor='black', linewidth=1.5)
    
    # 값 표시
    for i, (bar, val) in enumerate(zip(bars, cv_data['변동계수'].values)):
        ax.text(val + 1, i, f'{val:.1f}%', va='center', fontsize=10, weight='bold')
    
    ax.set_xlabel('변동계수 (%)', fontsize=12, weight='bold')
    ax.set_title('기준분류별 변동계수(CV) 비교', fontsize=14, weight='bold', pad=20)
    ax.set_xlim(0, max(cv_data['변동계수'].values) * 1.15)
    
    # 참조선 추가
    ax.axvline(x=10, color='#10b981', linestyle='--', linewidth=1, alpha=0.5, label='우수 (≤10%)')
    ax.axvline(x=20, color='#f59e0b', linestyle='--', linewidth=1, alpha=0.5, label='양호 (≤20%)')
    ax.legend(loc='lower right', fontsize=9)
    
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    # Base64로 변환
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return f"data:image/png;base64,{image_base64}"

def create_html():
    """HTML 보고서 생성"""
    
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KEQAS hs-TnI 공통보고서</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 20px auto;
            background-color: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        
        /* 헤더 */
        .header {{
            text-align: center;
            border-bottom: 3px solid #1e40af;
            padding-bottom: 30px;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 32px;
            color: #1e40af;
            margin-bottom: 10px;
            font-weight: bold;
        }}
        
        .header p {{
            font-size: 14px;
            color: #666;
            margin: 5px 0;
        }}
        
        .program-info {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
            text-align: center;
        }}
        
        .info-box {{
            background-color: #f0f9ff;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #1e40af;
        }}
        
        .info-box .label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        
        .info-box .value {{
            font-size: 16px;
            font-weight: bold;
            color: #1e40af;
        }}
        
        /* 섹션 */
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            font-size: 22px;
            font-weight: bold;
            color: #1e40af;
            border-bottom: 2px solid #1e40af;
            padding-bottom: 10px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }}
        
        .section-title::before {{
            content: "";
            display: inline-block;
            width: 6px;
            height: 22px;
            background-color: #1e40af;
            border-radius: 2px;
            margin-right: 10px;
        }}
        
        .specimen-subsection {{
            margin-bottom: 30px;
        }}
        
        .specimen-title {{
            font-size: 16px;
            font-weight: bold;
            color: #1e40af;
            background-color: #f0f9ff;
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 15px;
        }}
        
        /* 테이블 */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        
        table thead {{
            background-color: #1e40af;
            color: white;
        }}
        
        table thead th {{
            padding: 12px;
            text-align: right;
            font-weight: bold;
            border: 1px solid #1e40af;
        }}
        
        table thead th:first-child {{
            text-align: left;
        }}
        
        table tbody td {{
            padding: 10px 12px;
            border: 1px solid #ddd;
            text-align: right;
        }}
        
        table tbody td:first-child {{
            text-align: left;
            font-weight: 500;
            background-color: #f9fafb;
        }}
        
        table tbody tr:nth-child(even) {{
            background-color: #f9fafb;
        }}
        
        table tbody tr:hover {{
            background-color: #f0f9ff;
        }}
        
        /* 통계 정보 */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background-color: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }}
        
        .stat-card.high {{
            border-left-color: #10b981;
        }}
        
        .stat-card.low {{
            border-left-color: #f59e0b;
        }}
        
        .stat-card.range {{
            border-left-color: #8b5cf6;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
            text-transform: uppercase;
        }}
        
        .stat-value {{
            font-size: 18px;
            font-weight: bold;
            color: #1e40af;
        }}
        
        /* 기술통계 */
        .technical-stats {{
            background-color: #f9fafb;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        
        .stats-row {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 10px;
            background-color: white;
            border-radius: 4px;
            border: 1px solid #e5e7eb;
        }}
        
        .stat-item-label {{
            font-size: 12px;
            color: #666;
            margin-bottom: 8px;
        }}
        
        .stat-item-value {{
            font-size: 16px;
            font-weight: bold;
            color: #1e40af;
        }}
        
        /* 차트 섹션 */
        .charts-section {{
            margin: 30px 0;
            padding: 20px;
            background-color: #f9fafb;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .chart-container {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
        }}
        
        .chart-title {{
            font-size: 14px;
            font-weight: bold;
            color: #1e40af;
            margin-bottom: 10px;
            text-align: center;
        }}
        
        /* 하단 정보 */
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
        
        .footer-note {{
            background-color: #fef3c7;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 15px;
            border-left: 4px solid #f59e0b;
        }}
        
        /* 반응형 */
        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}
            
            .program-info {{
                grid-template-columns: 1fr 1fr;
            }}
            
            .header h1 {{
                font-size: 24px;
            }}
            
            .stats-row {{
                grid-template-columns: repeat(3, 1fr);
            }}
            
            table {{
                font-size: 12px;
            }}
            
            table thead th, table tbody td {{
                padding: 8px 6px;
            }}
        }}
        
        .print-button {{
            background-color: #1e40af;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            margin-bottom: 20px;
        }}
        
        .print-button:hover {{
            background-color: #1e3a8a;
        }}
        
        @media print {{
            .print-button {{
                display: none;
            }}
            
            body {{
                background-color: white;
            }}
            
            .container {{
                box-shadow: none;
                margin: 0;
                padding: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 헤더 -->
        <div class="header">
            <h1>KEQAS 공통보고서</h1>
            <p>심장표지자단백검사(정량) - High-Sensitivity Cardiac Troponin I (hs-TnI)</p>
            
            <div class="program-info">
                <div class="info-box">
                    <div class="label">회차연도</div>
                    <div class="value">{program_year}년</div>
                </div>
                <div class="info-box">
                    <div class="label">회차</div>
                    <div class="value">제{program_round}회</div>
                </div>
                <div class="info-box">
                    <div class="label">프로그램코드</div>
                    <div class="value">{program_code}</div>
                </div>
                <div class="info-box">
                    <div class="label">검사코드</div>
                    <div class="value">{test_code}</div>
                </div>
            </div>
        </div>
        
        <button class="print-button" onclick="window.print()">📄 인쇄 / PDF 저장</button>
        
        <!-- 검체별 보고서 -->
"""
    
    for specimen in specimens:
        specimen_data = overall_data[overall_data['검체명'] == specimen]
        
        if specimen_data.empty:
            continue
        
        row = specimen_data.iloc[0]
        
        html_content += f"""        <div class="section">
            <div class="section-title">{specimen}</div>
            
            <div class="specimen-subsection">
                <div class="specimen-title">참여기관 및 결과</div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">참여기관 수</div>
                        <div class="stat-value">{format_number(row['기관수'])}</div>
                    </div>
                    <div class="stat-card high">
                        <div class="stat-label">결과제출 기관</div>
                        <div class="stat-value">{format_number(row['기관수_OUT'])}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">중간값</div>
                        <div class="stat-value">{format_number(row['중간값'])}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">평균</div>
                        <div class="stat-value">{format_number(row['평균'])}</div>
                    </div>
                </div>
                
                <div class="technical-stats">
                    <div class="stats-row">
                        <div class="stat-item">
                            <div class="stat-item-label">최소값</div>
                            <div class="stat-item-value">{format_number(row['최소값'])}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">최대값</div>
                            <div class="stat-item-value">{format_number(row['최대값'])}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">표준편차</div>
                            <div class="stat-item-value">{format_number(row['표준편차'])}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">변동계수 (%)</div>
                            <div class="stat-item-value">{format_number(row['변동계수'])}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">신뢰구간 범위</div>
                            <div class="stat-item-value">{format_number(row['하한치'])} ~ {format_number(row['상한치'])}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 차트 섹션 -->
            <div class="charts-section">
                <div style="font-size: 16px; font-weight: bold; color: #1e40af; margin-bottom: 20px;">📊 기준분류별 분석</div>
                <div class="charts-grid">
"""
        
        # 해당 검체의 기준분류 데이터
        specimen_classification = classification_data[classification_data['검체명'] == specimen]
        
        # 분포도 차트
        dist_chart = create_distribution_chart(specimen_classification)
        if dist_chart:
            html_content += f"""                    <div class="chart-container">
                        <div class="chart-title">🥧 기준분류별 기관 분포</div>
                        <img src="{dist_chart}" alt="기관 분포">
                    </div>
"""
        
        # CV 비교 차트
        cv_chart = create_cv_comparison_chart(specimen_classification)
        if cv_chart:
            html_content += f"""                    <div class="chart-container">
                        <div class="chart-title">📈 기준분류별 변동계수(CV) 비교</div>
                        <img src="{cv_chart}" alt="변동계수 비교">
                    </div>
"""
        
        html_content += """                </div>
            </div>
            
            <!-- 기준분류별 결과 -->
            <div class="specimen-subsection">
                <div class="specimen-title">기준분류(의료기관 유형)별 결과</div>
                
                <table>
                    <thead>
                        <tr>
                            <th>기준분류</th>
                            <th>기관 수</th>
                            <th>결과 제출</th>
                            <th>중간값</th>
                            <th>평균</th>
                            <th>표준편차</th>
                            <th>신뢰하한치</th>
                            <th>신뢰상한치</th>
                            <th>변동계수 (%)</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # 해당 검체의 기준분류 데이터
        specimen_classification = classification_data[classification_data['검체명'] == specimen]
        
        for idx, cls_row in specimen_classification.iterrows():
            html_content += f"""                        <tr>
                            <td>{cls_row['기준분류명'] if pd.notna(cls_row['기준분류명']) else '-'}</td>
                            <td>{format_number(cls_row['기관수'])}</td>
                            <td>{format_number(cls_row['기관수_OUT'])}</td>
                            <td>{format_number(cls_row['중간값'])}</td>
                            <td>{format_number(cls_row['평균'])}</td>
                            <td>{format_number(cls_row['표준편차'])}</td>
                            <td>{format_number(cls_row['하한치'])}</td>
                            <td>{format_number(cls_row['상한치'])}</td>
                            <td>{format_number(cls_row['변동계수'])}</td>
                        </tr>
"""
        
        html_content += """                    </tbody>
                </table>
            </div>
        </div>
        
"""
    
    # 하단 정보
    html_content += """        <div class="footer">
            <div class="footer-note">
                <strong>주의:</strong> 본 보고서는 KEQAS(신빙도조사)의 정량 검사 결과를 요약한 공통보고서입니다. 
                개별 기관의 성적 평가는 각 기관에서 수신한 성적표를 참조하시기 바랍니다.
            </div>
            <p>보고서 생성일: """ + datetime.now().strftime("%Y년 %m월 %d일") + """</p>
            <p>한국의료인정제 - KEQAS (Korean External Quality Assessment Service)</p>
            <p>www.keqas.org</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html_content

def main():
    """메인 함수"""
    print("KEQAS hs-TnI 공통보고서 웹페이지 생성 중...")
    
    # HTML 생성
    html = create_html()
    
    # 파일 저장
    output_file = "KEQAS_hs_TnI_Common_Report.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ 보고서 생성 완료: {output_file}")
    
    # 파일 크기 확인
    file_size = os.path.getsize(output_file)
    print(f"  파일 크기: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    return output_file

if __name__ == "__main__":
    main()
