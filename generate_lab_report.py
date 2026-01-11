# KEQAS hs_TnI 기관별 보고서 PDF에서 hs_TnI_lab_report.csv 생성하는 코드

import pandas as pd
import numpy as np
import os
from pathlib import Path

# 1. 설정
BASE_PATH = "G:/내 드라이브/00_KEQAS/Troponin_I/Data"
os.chdir(BASE_PATH)

# 2. hs_TnI_input.csv 데이터 로드
input_file = 'hs_TnI_input.csv'
df_input = pd.read_csv(input_file, dtype=str)

print("입력 파일 로드 완료")
print(f"컬럼: {df_input.columns.tolist()}")
print(f"기관 수: {len(df_input)}")

# 3. 데이터 구조 파악
# 샘플 ID (검체명): CCA-25-04, CCA-25-05, CCA-25-06
sample_ids = ['CCA-25-04', 'CCA-25-05', 'CCA-25-06']

# 회차 정보 (하드코딩 - 필요시 수정)
year = 2025
round_num = 2
program_code = '140'
program_name = '심장표지자단백검사(정량)'
test_code = 'T902'
test_name = 'High-Sensitivity Cardiac Troponin I'

# 4. 기존 hs_TnI_lab_report.csv 로드 (통계 값 참고용)
existing_report = 'hs_TnI_lab_report.csv'
if os.path.exists(existing_report):
    df_existing = pd.read_csv(existing_report)
    print(f"\n기존 보고서 로드 완료: {len(df_existing)} 행")
else:
    print(f"\n경고: 기존 {existing_report} 파일을 찾을 수 없습니다.")
    df_existing = None

# 5. 보고서 데이터 생성
report_data = []

# 각 기관별로 처리
for idx, row in df_input.iterrows():
    lab_code = row['기관코드']
    device_company = row['기기회사']
    device_name = row['기기']
    reagent_company = row['시약회사'] if pd.notna(row['시약회사']) and row['시약회사'] != '' else ''
    reagent_name = row['시약'] if pd.notna(row['시약']) and row['시약'] != '' else ''
    test_method = row['검사방법'] if pd.notna(row['검사방법']) and row['검사방법'] != '' else ''
    
    # 각 검체별 결과값 처리
    for sample_id in sample_ids:
        if sample_id in df_input.columns:
            result_value_str = row[sample_id]
            
            # NaN 또는 빈 값 확인
            if pd.isna(result_value_str) or result_value_str == '':
                continue
            
            try:
                result_value = float(result_value_str)
            except:
                print(f"경고: {lab_code} {sample_id} 값 변환 실패: {result_value_str}")
                continue
            
            # 기준분류: 기기회사 기반 분류 (예시)
            reference_class = device_company
            
            # 세분류: 기기명 기반 분류 (예시)
            sub_class = device_name
            
            # 기본 행 데이터
            row_data = {
                '회차년도': year,
                '회차': round_num,
                '프로그램코드': program_code,
                '프로그램명': program_name,
                '기관코드': lab_code,
                '검사코드': test_code,
                '검사명': test_name,
                '검체명': sample_id,
                '검사결과': result_value,
                '기준분류': reference_class,
                '세분류': sub_class,
                '기준분류_sdi (text)': '',
                '세분류_sdi (text)': '',
                '기준분류_sdi (Number)': '',
                '세분류_sdi (Number)': '',
                '기기회사명': device_company,
                '기기명': device_name,
                '시약회사명': reagent_company,
                '시약명': reagent_name,
                '검사방법명': test_method,
            }
            
            # 기존 보고서에서 통계 정보 추출 (있으면)
            if df_existing is not None:
                # 같은 조건의 행 찾기
                matching_rows = df_existing[
                    (df_existing['기관코드'] == lab_code) & 
                    (df_existing['검체명'] == sample_id)
                ]
                
                if not matching_rows.empty:
                    ref_row = matching_rows.iloc[0]
                    
                    # 모든 기관 통계
                    for col in df_existing.columns:
                        if col.startswith('ALL_'):
                            if col in row_data:
                                continue
                            val = ref_row[col]
                            row_data[col] = val if pd.notna(val) else ''
                    
                    # 기준분류 통계
                    for col in df_existing.columns:
                        if col.startswith('기준분류_') and not col.endswith('(text)') and not col.endswith('(Number)'):
                            if col in row_data:
                                continue
                            val = ref_row[col]
                            row_data[col] = val if pd.notna(val) else ''
                    
                    # 세분류 통계
                    for col in df_existing.columns:
                        if col.startswith('세분류_') and not col.endswith('(text)') and not col.endswith('(Number)'):
                            if col in row_data:
                                continue
                            val = ref_row[col]
                            row_data[col] = val if pd.notna(val) else ''
                else:
                    # 매칭되는 행이 없으면 기본값으로 채우기
                    print(f"경고: {lab_code} {sample_id}에 대한 통계 정보를 찾을 수 없습니다.")
            
            report_data.append(row_data)

# 6. DataFrame 생성
df_report = pd.DataFrame(report_data)

print(f"\n생성된 보고서: {len(df_report)} 행")
print(f"컬럼: {df_report.columns.tolist()}")

# 7. 컬럼 순서 정렬 (기존 파일과 동일하게)
if df_existing is not None:
    existing_cols = df_existing.columns.tolist()
    # 기존 컬럼 순서대로 정렬, 없는 컬럼은 뒤에 추가
    cols_to_keep = [col for col in existing_cols if col in df_report.columns]
    cols_to_add = [col for col in df_report.columns if col not in existing_cols]
    df_report = df_report[cols_to_keep + cols_to_add]
    print(f"\n컬럼 순서 정렬 완료")

# 8. CSV 저장
output_file = 'hs_TnI_lab_report_generated.csv'
df_report.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n보고서 저장 완료: {output_file}")
print(f"저장 경로: {os.path.abspath(output_file)}")

# 9. 샘플 데이터 출력
print("\n생성된 데이터 샘플 (처음 5행):")
print(df_report.head())

# 10. 통계 검증
print("\n통계 검증:")
print(f"기관 수: {df_report['기관코드'].nunique()}")
print(f"검체 수: {df_report['검체명'].nunique()}")
print(f"총 행 수: {len(df_report)}")
print(f"검사결과 범위: {df_report['검사결과'].min():.2f} ~ {df_report['검사결과'].max():.2f}")

print("\n완료!")
 
# === 기관별 보고서(HTML + PNG) 생성 ===
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

OUT_DIR = Path('reports') / 'institution_reports'
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"\n기관별 보고서 생성 시작. 출력 폴더: {OUT_DIR}")

src_file = 'hs_TnI_lab_report.csv'
if not os.path.exists(src_file):
    print(f"원본 {src_file}이 없어 기관별 리포트 생성을 건너뜁니다.")
else:
    df_src = pd.read_csv(src_file, encoding='utf-8-sig')
    
    def safe_get(row, col):
        return row[col] if col in row.index else ''
    
    def create_levey_jennings_chart(df_lab):
        """Levey-Jennings chart 생성 (기준분류_SDI 기반)"""
        try:
            plt.rcParams['font.family'] = 'Malgun Gothic'
            plt.rcParams['axes.unicode_minus'] = False
            
            specimens = ['CCA-25-04', 'CCA-25-05', 'CCA-25-06']
            sdi_values = []
            
            for specimen in specimens:
                specimen_data = df_lab[df_lab['검체명'] == specimen]
                if not specimen_data.empty:
                    sdi = specimen_data.iloc[0].get('기준분류_sdi (Number)', None)
                    if pd.notna(sdi):
                        try:
                            sdi_values.append(float(sdi))
                        except:
                            sdi_values.append(0)
                    else:
                        sdi_values.append(0)
                else:
                    sdi_values.append(0)
            
            if len(sdi_values) == 0:
                return None
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            x_positions = list(range(len(specimens)))
            
            # SDI 기준선 그리기
            ax.axhline(y=0, color='green', linestyle='-', linewidth=2, alpha=0.7, label='Mean (0 SD)')
            ax.axhline(y=1, color='yellow', linestyle='--', linewidth=1.5, alpha=0.6, label='±1 SD')
            ax.axhline(y=-1, color='yellow', linestyle='--', linewidth=1.5, alpha=0.6)
            ax.axhline(y=2, color='orange', linestyle='--', linewidth=1.5, alpha=0.6, label='±2 SD')
            ax.axhline(y=-2, color='orange', linestyle='--', linewidth=1.5, alpha=0.6)
            ax.axhline(y=3, color='red', linestyle='--', linewidth=1.5, alpha=0.6, label='±3 SD')
            ax.axhline(y=-3, color='red', linestyle='--', linewidth=1.5, alpha=0.6)
            
            # 데이터 포인트 그리기
            ax.plot(x_positions, sdi_values, marker='o', markersize=10, 
                   color='black', linewidth=2, label='SDI 값')
            
            # 포인트에 값 표시
            for i, (x, y) in enumerate(zip(x_positions, sdi_values)):
                ax.text(x, y + 0.2, f'{y:.2f}', ha='center', va='bottom', 
                       fontsize=16, fontweight='bold')
            
            ax.set_xlim(-0.5, len(specimens) - 0.5)
            ax.set_ylim(-4, 4)
            ax.set_xticks(x_positions)
            ax.set_xticklabels(specimens, rotation=45, ha='right')
            ax.set_ylabel('SDI', fontsize=20, fontweight='bold')
            ax.set_xlabel('검체명', fontsize=20, fontweight='bold')
            ax.set_title('SDI : 기준 분류의 SDI', fontsize=22, fontweight='bold', pad=20)
            ax.tick_params(axis='both', labelsize=16, width=1.2)
            ax.grid(axis='y', linestyle=':', alpha=0.5)
            ax.legend(loc='upper right', fontsize=14)
            
            # Base64 인코딩
            buffer = BytesIO()
            fig.tight_layout()
            fig.savefig(buffer, format='png', dpi=120, bbox_inches='tight')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)
            
            return img_base64
        except Exception as e:
            print(f"Levey-Jennings chart 생성 오류: {e}")
            return None
    
    def create_youden_plot(df, specimen_x, specimen_y, group_type, group_value, lab_code):
        """Youden Plot 생성 (2개 검체 비교) - 박스는 ±3 SD 범위"""
        try:
            plt.rcParams['font.family'] = 'Malgun Gothic'
            plt.rcParams['axes.unicode_minus'] = False
            
            # 그룹 필터링 (기준분류 또는 세분류)
            if group_type == '기준분류':
                group_data = df[df['기준분류'] == group_value].copy()
            else:  # 세분류
                group_data = df[df['세분류'] == group_value].copy()
            
            # 검체별 데이터 추출
            data_x = group_data[group_data['검체명'] == specimen_x].copy()
            data_y = group_data[group_data['검체명'] == specimen_y].copy()
            
            # 기관코드 기준으로 병합
            merged = pd.merge(
                data_x[['기관코드', '검사결과']], 
                data_y[['기관코드', '검사결과']], 
                on='기관코드', 
                suffixes=('_x', '_y')
            )
            
            if merged.empty:
                return None
            
            # 수치 변환
            merged['결과_x'] = pd.to_numeric(merged['검사결과_x'], errors='coerce')
            merged['결과_y'] = pd.to_numeric(merged['검사결과_y'], errors='coerce')
            merged = merged.dropna(subset=['결과_x', '결과_y'])
            
            if len(merged) == 0:
                return None
            
            # 통계값 계산
            mean_x = merged['결과_x'].mean()
            mean_y = merged['결과_y'].mean()
            sd_x = merged['결과_x'].std()
            sd_y = merged['결과_y'].std()
            
            # 해당 기관 데이터
            lab_data = merged[merged['기관코드'] == lab_code]
            
            fig, ax = plt.subplots(figsize=(8, 8))
            
            # 전체 기관 데이터 (회색)
            ax.scatter(merged['결과_x'], merged['결과_y'], 
                      color='lightgray', s=50, alpha=0.6, label='다른 기관')
            
            # 해당 기관 데이터 (파란색)
            if not lab_data.empty:
                ax.scatter(lab_data['결과_x'].iloc[0], lab_data['결과_y'].iloc[0], 
                          color='blue', s=150, marker='o', 
                          edgecolors='darkblue', linewidths=2, 
                          label='해당 기관', zorder=5)
            
            # 평균값 십자선
            ax.axhline(y=mean_y, color='blue', linestyle='-', linewidth=2, alpha=0.7)
            ax.axvline(x=mean_x, color='blue', linestyle='-', linewidth=2, alpha=0.7)
            
            # ±2SD 사각형 박스
            rect_x = mean_x - 3*sd_x
            rect_y = mean_y - 3*sd_y
            rect_width = 6*sd_x
            rect_height = 6*sd_y
            
            from matplotlib.patches import Rectangle
            rect = Rectangle((rect_x, rect_y), rect_width, rect_height,
                           linewidth=2, edgecolor='black', facecolor='none', 
                           linestyle='--', label='±3 SD')
            ax.add_patch(rect)

            # 축 스케일 자동 조정: 데이터와 박스를 모두 포함하도록 패딩
            x_candidates = [merged['결과_x'].min(), merged['결과_x'].max(), rect_x, rect_x + rect_width]
            y_candidates = [merged['결과_y'].min(), merged['결과_y'].max(), rect_y, rect_y + rect_height]

            x_min, x_max = min(x_candidates), max(x_candidates)
            y_min, y_max = min(y_candidates), max(y_candidates)

            x_range = x_max - x_min if x_max > x_min else 1.0
            y_range = y_max - y_min if y_max > y_min else 1.0

            pad_x = x_range * 0.1
            pad_y = y_range * 0.1

            ax.set_xlim(x_min - pad_x, x_max + pad_x)
            ax.set_ylim(y_min - pad_y, y_max + pad_y)
            
            ax.set_xlabel(f'{specimen_x}', fontsize=20, fontweight='bold')
            ax.set_ylabel(f'{specimen_y}', fontsize=20, fontweight='bold')
            ax.set_title(f'Youden Plot - {group_type}: {group_value}\n({specimen_x} vs {specimen_y})', 
                        fontsize=22, fontweight='bold', pad=20)
            ax.tick_params(axis='both', labelsize=16, width=1.2)
            ax.legend(loc='upper left', fontsize=14)
            ax.grid(True, linestyle=':', alpha=0.5)
            
            # Base64 인코딩
            buffer = BytesIO()
            fig.tight_layout()
            fig.savefig(buffer, format='png', dpi=120, bbox_inches='tight')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)
            
            return img_base64
        except Exception as e:
            print(f"Youden Plot 생성 오류: {e}")
            return None
    
    def create_histogram_base64(df, specimen_name, lab_code):
        """검체별 전체 histogram과 기관의 기준분류별 데이터 겹침"""
        try:
            plt.rcParams['font.family'] = 'Malgun Gothic'
            plt.rcParams['axes.unicode_minus'] = False
            
            # 1단계: 전체 데이터 필터링 (ALL_Outlier='YES' 제외)
            specimen_df_all = df[df['검체명'] == specimen_name].copy()
            
            if 'ALL_Outlier' in specimen_df_all.columns:
                specimen_df_all = specimen_df_all[specimen_df_all['ALL_Outlier'] != 'YES'].copy()
            
            if specimen_df_all.empty:
                return None
            
            specimen_series_all = pd.to_numeric(specimen_df_all['검사결과'], errors='coerce').dropna()
            
            if len(specimen_series_all) == 0:
                return None
            
            # 2단계: 해당 기관의 기준분류 파악
            lab_ref_class_data = df[df['기관코드'] == lab_code]['기준분류']
            if lab_ref_class_data.empty:
                return None
            
            lab_ref_class = lab_ref_class_data.iloc[0]
            
            # 3단계: 해당 기준분류에 속한 모든 기관의 데이터 필터링
            specimen_df_lab = df[(df['검체명'] == specimen_name) & (df['기준분류'] == lab_ref_class)].copy()
            
            if 'ALL_Outlier' in specimen_df_lab.columns:
                specimen_df_lab = specimen_df_lab[specimen_df_lab['ALL_Outlier'] != 'YES'].copy()
            
            specimen_series_lab = pd.to_numeric(specimen_df_lab['검사결과'], errors='coerce').dropna()
            
            if len(specimen_series_lab) == 0:
                return None
            
            # 전체 데이터의 2.5%-97.5% percentile 범위 계산
            p_low = specimen_series_all.quantile(0.025)
            p_high = specimen_series_all.quantile(0.975)
            
            total_count = len(specimen_series_all)
            lab_count = len(specimen_series_lab)
            in_count = total_count - int((specimen_series_all < p_low).sum()) - int((specimen_series_all > p_high).sum())
            
            # 히스토그램 생성
            fig, ax = plt.subplots(figsize=(12, 9))
            
            # 20개 bin의 경계값 계산
            bins_edges = np.linspace(p_low, p_high, 21)
            
            # 범위 외 값을 첫/마지막 bar에 포함하도록 클리핑
            clipped_all = specimen_series_all.clip(lower=p_low, upper=p_high)
            clipped_lab = specimen_series_lab.clip(lower=p_low, upper=p_high)
            
            # 1단계: 전체 데이터로 histogram (회색 배경)
            ax.hist(clipped_all, bins=bins_edges, color='lightgray', edgecolor='black', 
                   linewidth=0.5, alpha=0.7, label=f'전체(n={total_count})')
            
            # 2단계: 해당 기준분류의 데이터를 겹쳐서 표시 (파란색)
            ax.hist(clipped_lab, bins=bins_edges, color='steelblue', edgecolor='darkblue', 
                   linewidth=0.5, alpha=0.7, label=f'{lab_ref_class}(n={lab_count})')
            
            ax.set_xlim(p_low, p_high)
            
            # 통계치 계산
            mean_all = specimen_series_all.mean()
            median_all = specimen_series_all.median()
            mean_lab = specimen_series_lab.mean()
            median_lab = specimen_series_lab.median()
            
            # 해당 기관의 검사 결과값 가져오기
            lab_result_data = df[(df['검체명'] == specimen_name) & (df['기관코드'] == lab_code)]
            lab_result = None
            if not lab_result_data.empty:
                lab_result = pd.to_numeric(lab_result_data['검사결과'].iloc[0], errors='coerce')
            
            # 수직선 표시 (전체: 점선, 기준분류: 실선)
            ax.axvline(mean_all, color='red', linestyle=':', linewidth=1.5, alpha=0.5, label=f'전체 평균: {mean_all:.2f}')
            ax.axvline(median_all, color='green', linestyle=':', linewidth=1.5, alpha=0.5, label=f'전체 중간값: {median_all:.2f}')
            ax.axvline(mean_lab, color='red', linestyle='--', linewidth=2, label=f'{lab_ref_class} 평균: {mean_lab:.2f}')
            ax.axvline(median_lab, color='green', linestyle='-', linewidth=2, label=f'{lab_ref_class} 중간값: {median_lab:.2f}')
            
            # 해당 기관의 결과값을 X축 하단에 붉은색 화살표로 표시
            if lab_result is not None and not pd.isna(lab_result):
                y_min = ax.get_ylim()[0]
                arrow_height = (ax.get_ylim()[1] - y_min) * 0.05  # 그래프 높이의 5%
                ax.arrow(lab_result, y_min - arrow_height*0.5, 0, arrow_height*0.4, 
                        head_width=(p_high-p_low)*0.02, head_length=arrow_height*0.3,
                        fc='red', ec='red', linewidth=3, alpha=0.8)
                ax.text(lab_result, y_min - arrow_height*1.2, f'Your Result\n{lab_result:.2f}', 
                       ha='center', va='top', fontsize=16, color='red', fontweight='bold')
            
            # 제목 및 축 설정
            ax.set_title(f'[{specimen_name}] hs-TnI 기관별 결과값 분포 - 2.5%-97.5% 범위내\n(전체: {total_count}개, {lab_ref_class}: {lab_count}개)', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('검사결과값 (pg/mL)', fontsize=18, fontweight='bold')
            ax.set_ylabel('기관 수 (Frequency)', fontsize=18, fontweight='bold')
            ax.tick_params(axis='both', labelsize=16, width=1.1)
            ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=14, framealpha=0.95, borderaxespad=0)
            ax.grid(axis='y', linestyle=':', alpha=0.7)
            
            # Base64 인코딩
            buffer = BytesIO()
            fig.tight_layout()
            fig.savefig(buffer, format='png', dpi=120, bbox_inches='tight')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)
            
            return img_base64
        except Exception as e:
            print(f"히스토그램 생성 오류 ({specimen_name}, {lab_code}): {e}")
            return None

    # 상위 N개 기관에 대해서만 샘플 리포트 생성
    MAX_REPORTS = 5
    unique_labs = df_src['기관코드'].unique().tolist()
    target_labs = unique_labs[:MAX_REPORTS]

    for lab_code in target_labs:
        df_lab = df_src[df_src['기관코드'] == lab_code]
        html_lines = []
        html_lines.append(f"<html><head><meta charset='utf-8'><title>{lab_code} 보고서</title>")
        html_lines.append(
            "<style>"
            "body {font-family: Arial, sans-serif; margin: 20px;} "
            "table {border-collapse: collapse; width: 100%;} "
            "th, td {border: 1px solid #ccc; padding: 8px; text-align: left;} "
            "th {background-color: #333; color: white;} "
            ".charts-header {display: flex; align-items: center; gap: 10px; flex-wrap: wrap;} "
            "#toggle-enlarge {padding: 6px 12px; border: 1px solid #444; background: #f5f5f5; cursor: pointer;} "
            "#toggle-enlarge:hover {background: #e0e0e0;} "
            ".histogram {margin: 12px 0; text-align: center;} "
            ".histogram img {max-width: 630px; width: 100%; height: auto; border: 1px solid #ddd;} "
            ".grid-row {display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0;} "
            ".grid-item {flex: 1 1 32%; max-width: 34%; text-align: center;} "
            ".grid-item img {width: 100%; max-width: 420px; height: auto; border: 1px solid #ddd;} "
            "#charts-wrapper.enlarge .grid-item {flex: 1 1 48%; max-width: 48%;} "
            "#charts-wrapper.enlarge .grid-item img {max-width: 640px;} "
            "</style>"
        )
        html_lines.append(f"</head><body>")
        html_lines.append(f"<h2>{lab_code} 기관별 보고서 (예시 5개 기관 중)</h2>")

        first = df_lab.iloc[0]
        device = safe_get(first, '기기명')
        device_co = safe_get(first, '기기회사명')
        reagent_co = safe_get(first, '시약회사명')
        html_lines.append('<p>')
        html_lines.append(f"<strong>기기회사:</strong> {device_co} &nbsp; <strong>기기명:</strong> {device} <br>")
        html_lines.append(f"<strong>시약회사:</strong> {reagent_co} <br>")
        html_lines.append('</p>')

        # 표 스타일 및 헤더 (이미지의 표 구성 참고)
        html_lines.append('<h3>검사 결과 요약</h3>')
        html_lines.append('<table border="1" cellpadding="6" cellspacing="0">')
        html_lines.append('<tr><th>Specimen</th><th>Your Result</th><th>Group</th><th>N</th><th>Mean</th><th>SD</th><th>CV(%)</th><th>Median</th><th>Min</th><th>Max</th><th>SDI</th><th>Remark</th></tr>')

        for _, r in df_lab.iterrows():
            specimen = r.get('검체명', '')
            your_result = r.get('검사결과', '')

            # Your Result row
            html_lines.append(f"<tr><td rowspan=3>{specimen}</td><td rowspan=3>{your_result}</td>")

            # ALL row
            all_n = r.get('ALL_기관수', '')
            all_mean = r.get('ALL_평균값', '')
            all_sd = r.get('ALL_표준편차', '')
            all_cv = r.get('ALL_변동계수', '')
            all_med = r.get('ALL_중간값', '')
            all_min = r.get('ALL_최소값', '')
            all_max = r.get('ALL_최대값', '')
            all_rem = r.get('ALL_Outlier', '') if 'ALL_Outlier' in r.index else ''
            html_lines.append(f"<td>All</td><td>{all_n}</td><td>{all_mean}</td><td>{all_sd}</td><td>{all_cv}</td><td>{all_med}</td><td>{all_min}</td><td>{all_max}</td><td></td><td>{all_rem}</td></tr>")

            # 기준분류 row
            g_n = r.get('기준분류_기관수', '')
            g_mean = r.get('기준분류_평균값', '')
            g_sd = r.get('기준분류_표준편차', '')
            g_cv = r.get('기준분류_변동계수', '')
            g_med = r.get('기준분류_중간값', '')
            g_min = r.get('기준분류_최소값', '')
            g_max = r.get('기준분류_최대값', '')
            g_sdi = r.get('기준분류_sdi (Number)', '')
            g_rem = r.get('기준분류_Outlier', '') if '기준분류_Outlier' in r.index else ''
            html_lines.append(f"<tr><td>{r.get('기준분류','')}</td><td>{g_n}</td><td>{g_mean}</td><td>{g_sd}</td><td>{g_cv}</td><td>{g_med}</td><td>{g_min}</td><td>{g_max}</td><td>{g_sdi}</td><td>{g_rem}</td></tr>")

            # 세분류 row
            s_n = r.get('세분류_기관수', '')
            s_mean = r.get('세분류_평균값', '')
            s_sd = r.get('세분류_표준편차', '')
            s_cv = r.get('세분류_변동계수', '')
            s_med = r.get('세분류_중간값', '')
            s_min = r.get('세분류_최소값', '')
            s_max = r.get('세분류_최대값', '')
            s_sdi = r.get('세분류_sdi (Number)', '')
            s_rem = r.get('세분류_Outlier', '') if '세분류_Outlier' in r.index else ''
            html_lines.append(f"<tr><td>{r.get('세분류','')}</td><td>{s_n}</td><td>{s_mean}</td><td>{s_sd}</td><td>{s_cv}</td><td>{s_med}</td><td>{s_min}</td><td>{s_max}</td><td>{s_sdi}</td><td>{s_rem}</td></tr>")

        html_lines.append('</table>')

        # 히스토그램/Youden 묶음 + 확대 토글
        html_lines.append("<div class='charts-header'><h3 style='margin:0;'>그래프</h3><button id='toggle-enlarge' type='button'>크게 보기</button></div>")
        html_lines.append("<div id='charts-wrapper'>")

        # 히스토그램 섹션 추가 (1행 3개)
        html_lines.append('<h4>기준분류별 분포 히스토그램</h4>')
        specimens = ['CCA-25-04', 'CCA-25-05', 'CCA-25-06']
        hist_items = []
        for specimen in specimens:
            specimen_data = df_lab[df_lab['검체명'] == specimen]
            if not specimen_data.empty:
                img_base64 = create_histogram_base64(df_src, specimen, lab_code)
                if img_base64:
                    hist_items.append(
                        f"<div class='grid-item'><h4>{specimen}</h4>"
                        f"<img src='data:image/png;base64,{img_base64}' alt='{specimen} 히스토그램'></div>"
                    )
        if hist_items:
            html_lines.append("<div class='grid-row'>" + ''.join(hist_items) + "</div>")

        html_lines.append("</div>")

        # Levey-Jennings chart 추가 (두 번째 줄)
        html_lines.append('<h3>SDI 추세 (Levey-Jennings Chart)</h3>')
        lj_chart = create_levey_jennings_chart(df_lab)
        if lj_chart:
            html_lines.append('<div class="histogram">')
            html_lines.append(f'<img src="data:image/png;base64,{lj_chart}" alt="Levey-Jennings Chart">')
            html_lines.append('</div>')

        # Youden Plot 섹션 (세 번째 줄, 기준분류만, 1행 3개)
        html_lines.append('<h3>Youden Plot (검체 간 비교, 기준분류)</h3>')
        ref_class = first.get('기준분류', '')
        specimen_pairs = [
            ('CCA-25-04', 'CCA-25-05'),  # 검체 1-2
            ('CCA-25-05', 'CCA-25-06'),  # 검체 2-3
            ('CCA-25-04', 'CCA-25-06')   # 검체 1-3
        ]
        youden_items = []
        if ref_class:
            for spec_x, spec_y in specimen_pairs:
                youden_img = create_youden_plot(df_src, spec_x, spec_y, '기준분류', ref_class, lab_code)
                if youden_img:
                    youden_items.append(
                        f"<div class='grid-item'><h4>{spec_x} vs {spec_y}</h4>"
                        f"<img src='data:image/png;base64,{youden_img}' alt='Youden Plot {spec_x} vs {spec_y}'></div>"
                    )
        if youden_items:
            html_lines.append("<div class='grid-row'>" + ''.join(youden_items) + "</div>")

        # 확대 토글 스크립트
        html_lines.append(
            "<script>"
            "const toggleBtn = document.getElementById('toggle-enlarge');"
            "const chartsWrapper = document.getElementById('charts-wrapper');"
            "if (toggleBtn && chartsWrapper) {"
            "  toggleBtn.addEventListener('click', () => {"
            "    chartsWrapper.classList.toggle('enlarge');"
            "    toggleBtn.textContent = chartsWrapper.classList.contains('enlarge') ? '원래 크기' : '크게 보기';"
            "  });"
            "}"
            "</script>"
        )

        html_lines.append('</body></html>')

        out_html = OUT_DIR / f"{lab_code}.html"
        with open(out_html, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(html_lines))

        print(f"작성됨: {out_html}")

print('\n기관별 리포트 생성 완료')
