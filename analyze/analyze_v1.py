import pandas as pd
import os

input = "/home/ubuntu/watcher/outputs/hw12.xlsx"

def analyze_snapshots(input_file):
    # 입력 엑셀 파일 읽기
    xls = pd.ExcelFile(input_file)
    
    # 출력 데이터 구조
    summary_data = []
    writer_detail = pd.ExcelWriter('change_rate.xlsx', engine='xlsxwriter')
    writer_summary = pd.ExcelWriter('stats.xlsx', engine='xlsxwriter')
    
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # 필요한 컬럼만 선택 (예제: '디렉터리', '파일 크기', '타임스탬프')
        df = df[['과제 코드 디렉터리 (.c)', '스냅샷 파일명', '파일 크기 (bytes)', '타임스탬프']]
        df.sort_values(by=['과제 코드 디렉터리 (.c)', '타임스탬프'], inplace=True)
        
        # 통계 저장용 데이터프레임
        snapshot_detail = []
        
        for directory, group in df.groupby('과제 코드 디렉터리 (.c)'):
            zero_size_count = (group['파일 크기 (bytes)'] == 0).sum()
            total_count = len(group)
            
            summary_data.append([sheet_name, directory, total_count, zero_size_count])
            
            prev_size = None
            prev_time = None
            for _, row in group.iterrows():
                if prev_size is not None and prev_time is not None:
                    change = '증가' if row['파일 크기 (bytes)'] > prev_size else '감소'
                    time_diff = row['타임스탬프'] - prev_time
                    snapshot_detail.append([directory, change, time_diff])
                prev_size = row['파일 크기 (bytes)']
                prev_time = row['타임스탬프']
        
        # 학생별 상세 데이터 저장
        detail_df = pd.DataFrame(snapshot_detail, columns=['과제 코드 디렉터리 (.c)', '변화', '시간 간격'])
        detail_df.to_excel(writer_detail, sheet_name=sheet_name, index=False)
    
    # 학생별 통계 데이터 저장
    summary_df = pd.DataFrame(summary_data, columns=['학번', '과제 코드 디렉터리 (.c)', '총 스냅샷 개수', '파일 크기 0인 개수'])
    summary_df.to_excel(writer_summary, sheet_name='통계', index=False)
    
    # 엑셀 저장
    writer_detail.close()
    writer_summary.close()
    print("엑셀 파일이 생성되었습니다.")

# 사용 예제
analyze_snapshots(input)
