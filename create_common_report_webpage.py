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

# 기준분류별 데이터 미리 준비 (CV 비교 차트용)
all_classification_data = df[
    (df['기준분류명'].notna()) &
    (df['기준분류명'] != '') &
    (df['세분류명'].isna() | (df['세분류명'] == '')) &
    (df['기관수'].notna())
].copy()

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
    """기준분류별 기관 분포 도넛 차트 (첫번째 검체 기준)"""
    if classification_data.empty:
        return None
    
    # 기준분류별 기관수 합산
    dist_data = classification_data.groupby('기준분류명')['기관수'].sum().sort_values(ascending=False)
    
    if dist_data.empty:
        return None
    
    # 차트 생성
    fig, ax = plt.subplots(figsize=(7, 5), facecolor='white')
    
    colors = ['#1e40af', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
    colors = colors[:len(dist_data)]
    
    # 라벨은 표시하지 않고 범례만 사용
    wedges, texts, autotexts = ax.pie(
        dist_data.values,
        labels=None,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 12, 'weight': 'bold'},
        wedgeprops=dict(edgecolor='white', linewidth=3)
    )
    
    # 자동텍스트(퍼센트) 포맷팅
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(11)
        autotext.set_weight('bold')
    
    # 중앙 원 (도넛 모양)
    centre_circle = plt.Circle((0, 0), 0.70, fc='white', edgecolor='white', linewidth=2)
    ax.add_artist(centre_circle)
    
    # 범례 - 기관수만 표시
    legend_labels = [f"{name}: {count}개" for name, count in zip(dist_data.index, dist_data.values)]
    ax.legend(
        legend_labels,
        loc='upper left',
        bbox_to_anchor=(1.05, 1),
        fontsize=12,
        frameon=True,
        fancybox=True,
        shadow=True
    )
    
    ax.set_title('기준분류(제조사)별 참가기관 분포\n(CCA-25-04 기준)', fontsize=16, weight='bold', pad=30)
    
    plt.tight_layout()
    
    # Base64로 변환
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return f"data:image/png;base64,{image_base64}"

def create_cv_comparison_chart(all_classification_data):
    """기준분류별 변동계수(CV%) 비교 바차트 (3개 검체 평균)"""
    if all_classification_data.empty:
        return None
    
    # 3개 검체별로 변동계수(CV%) 데이터 추출
    cv_data_list = []
    for specimen in all_classification_data['검체명'].unique():
        specimen_data = all_classification_data[all_classification_data['검체명'] == specimen]
        cv_filtered = specimen_data[specimen_data['변동계수'].notna()].copy()
        if not cv_filtered.empty:
            cv_data_list.append(cv_filtered)
    
    if not cv_data_list:
        return None
    
    # 기준분류별 CV 평균값 계산 (변동계수가 낮은 것이 맨 위에 오도록 역순 정렬)
    combined_cv = pd.concat(cv_data_list, ignore_index=True)
    cv_avg = combined_cv.groupby('기준분류명')['변동계수'].mean().sort_values(ascending=False)
    
    if cv_avg.empty:
        return None
    
    # 차트 생성 - 50% 크기
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor='white')
    
    # 색상: CV값에 따라 달라짐
    colors = []
    for cv in cv_avg.values:
        if cv <= 5:
            colors.append('#10b981')  # 초록색 (우수)
        elif cv <= 10:
            colors.append('#3b82f6')  # 파랑색 (양호)
        elif cv <= 20:
            colors.append('#f59e0b')  # 주황색 (주의)
        else:
            colors.append('#ef4444')  # 빨강색 (부주의)
    
    bars = ax.barh(cv_avg.index, cv_avg.values, color=colors, edgecolor='black', linewidth=2, height=0.6)
    
    # 값 표시 - 바 오른쪽에 배치
    for i, (bar, val) in enumerate(zip(bars, cv_avg.values)):
        ax.text(val + 1.5, i, f'{val:.2f}%', va='center', fontsize=14, weight='bold', fontfamily='monospace')
    
    # 축 레이블 폰트 사이즈 증가
    ax.set_xlabel('변동계수(CV%)', fontsize=15, weight='bold')
    ax.set_ylabel('기준분류(제조사)', fontsize=15, weight='bold')
    ax.set_xticklabels(ax.get_xticklabels(), fontsize=13)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=13)
    
    ax.set_title('기준분류별 변동계수(CV%) 비교\n(CCA-25-04, CCA-25-05, CCA-25-06 평균)', 
                 fontsize=16, weight='bold', pad=30)
    
    # 참조선 추가 및 범례 (차트 밖으로 배치)
    ax.axvline(x=5, color='#10b981', linestyle='--', linewidth=2.5, alpha=0.7, label='우수 (≤5%)')
    ax.axvline(x=10, color='#3b82f6', linestyle='--', linewidth=2.5, alpha=0.7, label='양호 (≤10%)')
    ax.axvline(x=20, color='#f59e0b', linestyle='--', linewidth=2.5, alpha=0.7, label='주의 (≤20%)')
    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=13, frameon=True, fancybox=True, shadow=True)
    
    ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=1)
    ax.set_xlim(0, max(cv_avg.values) * 1.2)
    
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
            margin: 20px 0 40px 0;
            padding: 15px;
            background-color: #f9fafb;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 15px;
        }}
        
        .chart-container {{
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            width: 100%;
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
        }}
        
        .chart-title {{
            font-size: 13px;
            font-weight: bold;
            color: #1e40af;
            margin-bottom: 8px;
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
    
    for specimen_idx, specimen in enumerate(specimens):
        specimen_data = overall_data[overall_data['검체명'] == specimen]
        
        if specimen_data.empty:
            continue
        
        row = specimen_data.iloc[0]
        is_first_specimen = (specimen_idx == 0)
        is_last_specimen = (specimen_idx == len(specimens) - 1)
        
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
                            <div class="stat-item-label">변동계수(CV%)</div>
                            <div class="stat-item-value">{format_number(row['변동계수'])}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">신뢰구간 범위</div>
                            <div class="stat-item-value">{format_number(row['하한치'])} ~ {format_number(row['상한치'])}</div>
                        </div>
                    </div>
                </div>
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
                            <th>변동계수(CV%)</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # 해당 검체의 기준분류 데이터 (기관 수 많은 순으로 정렬)
        specimen_classification = classification_data[classification_data['검체명'] == specimen].sort_values('기관수', ascending=False)
        
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
    
    # 하단 차트 섹션 추가
    html_content += """        <div class="section">
            <div class="section-title">📊 기준분류별 분석</div>
            
            <div class="charts-section">
                <div class="charts-grid">
"""
    
    # 하단에 표시할 차트들 생성
    dist_chart = create_distribution_chart(all_classification_data[all_classification_data['검체명'].isin(specimens)])
    if dist_chart:
        # 제조사별 분포 비율 계산
        first_specimen_data = overall_data[overall_data['검체명'] == specimens[0]].iloc[0] if len(specimens) > 0 else None
        dist_classification = all_classification_data[all_classification_data['검체명'] == specimens[0]].groupby('기준분류명')['기관수'].sum().sort_values(ascending=False) if len(specimens) > 0 else None
        
        distribution_info = ""
        if dist_classification is not None:
            total = dist_classification.sum()
            distribution_info = "<div style='margin-left: 20px; font-size: 12px;'><strong>분포 비율:</strong><br>"
            for name, count in dist_classification.items():
                percentage = (count / total) * 100
                distribution_info += f"{name}: {percentage:.1f}%<br>"
            distribution_info += "</div>"
        
        html_content += f"""                    <div class="chart-container" style="display: flex; align-items: flex-start; gap: 20px;">
                        <div style="flex: 1;">
                            <div class="chart-title">🥧 제조사별 참가기관 분포 (CCA-25-04 기준)</div>
                            <img src="{dist_chart}" alt="기관 분포" style="max-width: 100%; height: auto;">
                        </div>
                        {distribution_info}
                    </div>
"""
    
    cv_chart = create_cv_comparison_chart(all_classification_data)
    if cv_chart:
        html_content += f"""                    <div class="chart-container">
                        <div class="chart-title">📈 제조사별 변동계수(CV%) 비교 (3개 검체 평균)</div>
                        <img src="{cv_chart}" alt="변동계수(CV%) 비교">
                    </div>
"""
    
    html_content += """                </div>
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
