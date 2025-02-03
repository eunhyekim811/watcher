import os
import re
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from datetime import datetime
import matplotlib.cm as cm
import numpy as np

# 엑셀 파일 로드
wb = load_workbook("/home/ubuntu/watcher/outputs/hw12.xlsx")
output_folder = "./graphs_hw12"

# 그래프 출력 폴더 생성
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 데이터 저장용 딕셔너리 (학생 → 코드 → [(시간, 크기)])
data = {}

# 모든 시트(학생)에서 데이터 읽기
for sheet in wb.sheetnames:
    ws = wb[sheet]  # 현재 시트 (학생)
    student = sheet
    
    for row in ws.iter_rows(min_row=2, values_only=True):  # 헤더 제외
        code_dir, snapshot_file, file_size, file_mtime, timestamp = row
        
        # 데이터 저장 구조: {학생: {코드: [(시간, 크기)]}}
        data.setdefault(student, {}).setdefault(code_dir, []).append((timestamp, file_size))

# 그래프 그리기
for student, code_dict in data.items():
    plt.figure(figsize=(15, 8))  # 그래프 크기 조정
    
    # 코드 파일별 색상 지정 (최대 20개 색상)
    cmap = plt.colormaps["tab20"]
    colors = cmap(np.linspace(0, 1, len(code_dict)))
    
    for idx, (code, snapshots) in enumerate(code_dict.items()):
        # 시간 순 정렬
        snapshots.sort()
        times, file_sizes = zip(*snapshots)
        
        # 그래프 플롯 (선 스타일 조정)
        plt.plot(times, file_sizes, marker='o', markersize=6, 
                label=os.path.basename(code), color=colors[idx], 
                linewidth=2, linestyle='-')

    # 그래프 설정
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("File Size (bytes)", fontsize=12)
    plt.title(f"HW12 File Size Changes - {student}", fontsize=14, pad=20)
    plt.xticks(rotation=45, ha='right')
    
    # 범례 설정
    plt.legend(title="Code Files", loc='center left', 
              bbox_to_anchor=(1, 0.5),  # 그래프 오른쪽에 범례 위치
              fontsize=10, title_fontsize=12)
    
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()  # 레이아웃 자동 조정

    # 그래프 저장
    output_filename = os.path.join(output_folder, f"{student}_hw12.png")
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"저장된 그래프: {output_filename}")
