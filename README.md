# Watcher

## watcher
 코드 파일 스냅샷을 엑셀 파일로 정리하는 코드

- watcher_v1.py : total excel 파일 생성(하나의 엑셀 파일 안에 과제별로 시트 구분)
- watcher_v2.py : 과제별로 엑셀 파일 생성 후 파일마다 시트 구분하여 학생별 스냅샷 정리


## graph
 watcher를 통해 생성된 엑셀 파일을 그래프로 표현하는 코드

- graph_v1.py : 파일 크기 변화 그래프
- graph_v2.py : total excel 파일 크기 변화 그래프
- graph_v3.py : hw12 파일 크기 변화 그래프

## analyze
 watcher를 통해 생성된 엑셀 파일 기반 분석 시도

- analyze_v1.py
    - change_rate.xlsx : 학생별 스냅샷 변화 비율(타임스탬프 간격별 증감)
    - stats.xlsx : 학생별 스냅샷 통계(파일 크기 0인 개수, 총 스냅샷 개수)
