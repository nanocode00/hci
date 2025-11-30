import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import FinanceDataReader as fdr
import re
import numpy as np
from get_pdf import download_pdfs

stocks = fdr.StockListing('KRX') # 코스피, 코스닥, 코넥스 전체

stocks['Symbol'] = stocks['Code'].astype(str)
def remove_noise_and_split_title(title):
    in_code = ''
    in_name = ''

    for code, name in stocks[['Symbol', 'Name']].values:
        if code in title and name in title:
            in_code = code
            in_name = name

    # 한글, 영어, 숫자 외 노이즈 제거
    clean_title = re.sub('[^A-Za-z0-9가-힣]', ' ', title)

    # 기업명 코드 수정
    clean_title = clean_title.replace(in_code, ' ')
    clean_title = clean_title.replace(in_name, ' ')
    while ' ' * 2 in clean_title:
        clean_title = clean_title.replace(' ' * 2, ' ')

    if in_name == '': # 기업명이 없는 제목이라면, 데이터에 추가하지 않음
        return [None]
    else:
        return [in_name, in_code, clean_title]

# 수정
base_url = "https://consensus.hankyung.com/analysis/list?sdate=2025-08-20&edate=2025-11-20&now_page={}&search_value=&report_type=CO&pagenum=20&search_text=&business_code="
data = []
print("l")
max_page = 36
for page_no in range(1, max_page):
    while True:
        try:
            url = base_url.format(page_no)
            html = requests.get(url, headers={'User-Agent':'Gils'}).content
            soup = BeautifulSoup(html, 'lxml')
            print("{}/{}".format(page_no, max_page))
            break
        except:
            time.sleep(15 * 60)

    table = soup.find("div", {"class":"table_style01"}).find('table')
    for tr in table.find_all("tr")[1:]: # 1번째 행부터 순회
        record = []
        all_tds = tr.find_all("td") # 한 행의 모든 셀을 저장
        indices = [0, 1, 2, 3, 4, 5, 6, 8] # 기업정보 열과 차트 열을 제외한 나머지 셀의 인덱스

        for i, td in enumerate(all_tds): # 한 행 순회
            if i in indices: # 해당하는 열인 경우
                if i == 1:
                    record += remove_noise_and_split_title(td.text) # remove_noise_title의 출력과 이어 붙임
                elif i == 3: # 노이즈가 껴있는 세번째 셀만 따로 처리
                    record.append(td.text.replace(" ", "").replace("\r","").replace("\n",""))
                elif i == 6: # 기업정보 링크가 있는 열
                    a_tag = td.find('a')

                    if a_tag and a_tag.has_attr('href'):
                        raw_href = a_tag['href']

                        # 정규표현식을 사용하여 'http...' 로 시작하는 주소만 추출
                        # 패턴 설명: '(http 로 시작하고, ' 가 나오기 전까지의 문자열)' 을 찾음
                        match = re.search(r"'(https?://[^']+)'", raw_href)

                        if match:
                            # 찾은 URL을 record에 추가 (이미지상 절대경로이므로 앞에 주소 붙일 필요 없음)
                            extracted_url = match.group(1)
                            record.append(extracted_url)
                        else:
                            # URL 패턴을 못 찾았을 경우 (혹은 상대경로일 경우 로직 추가 필요)
                            record.append(None)

                elif i == 8: # 9번째 셀
                    # 9번째 셀 안의 <a> 태그를 찾습니다.
                    a_tag = td.find('a')
                    # <a> 태그가 존재하고 href 속성이 있는지 확인합니다.
                    if a_tag and a_tag.has_attr('href'):
                        # href 속성 값을 record에 추가합니다.
                        record.append("https://consensus.hankyung.com" + a_tag['href'])
                    else:
                        # 링크가 없는 경우를 대비해 None을 추가합니다.
                        record.append(None)
                else: # 1번째 셀이 아니면:
                    record.append(td.text) # 셀의 텍스트 값 그대로 입력

        if None not in record: # 레코드에 None이 없으면
            data.append(record)

    time.sleep(0.3) # 연결 끊김 방지를 위해
data = pd.DataFrame(data, columns = ["작성일", "종목명", "종목코드", "제목", "적정가격", "평가의견", "작성자", "작성기관", "기업정보", "첨부파일"])

# PDF 다운로드 실행
print("PDF 다운로드를 시작합니다...")
pdf_urls = data['첨부파일'].dropna().tolist()
download_pdfs(pdf_urls)
print("PDF 다운로드 완료.")

from datetime import datetime, timedelta

# 1. 중복 제거된 종목 코드 리스트 추출
unique_codes = data['종목코드'].astype(str).unique()

print(f"전체 데이터 개수: {len(data)}개")
print(f"조회할 고유 종목 개수: {len(unique_codes)}개")

# 2. 각 종목별 최신 종가 가져오기 (딕셔너리에 저장)
price_map = {}

# 최근 데이터 조회를 위한 시작 날짜 설정 (안전하게 일주일 전)
start_date = datetime.now() - timedelta(days=7)

for code in unique_codes:
    # 데이터 조회
    df_price = fdr.DataReader(code, start_date)
    
    if not df_price.empty:
        # 가장 최근 날짜의 종가 가져오기
        latest_price = df_price['Close'].iloc[-1]
        price_map[code] = latest_price
    else:
        # 데이터가 없는 경우 (상장폐지, 코드오류 등)
        price_map[code] = None 

# 3. 원본 데이터프레임에 '현재가격' 컬럼 추가 (Mapping)
data['현재가격'] = data['종목코드'].map(price_map)

# 1. 종목코드별 레포트 개수 계산
report_counts = data['종목코드'].value_counts()

# 2. 단 하나의 레포트만 가진 종목의 개수 출력
single_report_count = (report_counts == 1).sum() 
double_report_count = (report_counts == 2).sum()
print(f"단 하나의 레포트만 가진 종목(기업) 개수: {single_report_count}개") # 180
print(f"레포트 두개 가진 종목(기업) 개수 : {double_report_count}개") # 83

# 3. 단 하나의 레포트만 가진 기업들을 제거 (레포트가 2개 이상인 종목만 남김)
# 레포트 개수가 1보다 큰 종목코드들의 인덱스(코드명)만 추출
multi_report_codes = report_counts[report_counts > 2].index # 354개

# 해당 코드 리스트에 포함된 행만 선택하여 새로운 데이터프레임 생성 (혹은 덮어쓰기)
data_filtered = data[data['종목코드'].isin(multi_report_codes)].copy()

print(f"필터링 전 데이터 개수: {len(data)}개")
print(f"필터링 후 데이터 개수: {len(data_filtered)}개")

print(data.head())
# 1. 적정가격 데이터 전처리
# 쉼표(,)를 제거하고 숫자형으로 변환합니다.
# 'errors=coerce'는 숫자로 변환 불가능한 값(예: '-', 빈 문자열)을 NaN(결측치)으로 처리합니다.
data_filtered['적정가격_수치'] = pd.to_numeric(data_filtered['적정가격'].astype(str).str.replace(',', ''), errors='coerce')

# 적정가격이 0인 경우(목표가 미제시 등) 수익률이 -100%로 계산되는 것을 막기 위해 NaN으로 변경
data_filtered.loc[data_filtered['적정가격_수치'] == 0, '적정가격_수치'] = np.nan

# 2. 현재가격 데이터 확인 (이미 숫자형이지만 안전을 위해 변환 시도)
data_filtered['현재가격'] = pd.to_numeric(data_filtered['현재가격'], errors='coerce')

# 3. 수익률(괴리율) 계산
# 공식: ((적정가격 - 현재가격) / 현재가격) * 100
data_filtered['기대수익률'] = ((data_filtered['적정가격_수치'] - data_filtered['현재가격']) / data_filtered['현재가격']) * 100

# 4. 보기 좋게 소수점 둘째 자리에서 반올림
data_filtered['기대수익률'] = data_filtered['기대수익률'].round(2)

# 5. 결과 확인 (수익률이 높은 순서대로 정렬해서 보기)
print(data_filtered[['종목명', '현재가격', '적정가격', '기대수익률']].sort_values(by='기대수익률', ascending=False).head(10))

# 6. 최종 파일 저장
# 계산에 쓴 임시 컬럼('적정가격_수치')은 저장할 때 제외해도 됩니다.
final_columns = ["작성일", "종목명", "종목코드", "제목", "적정가격", "현재가격", "기대수익률", "평가의견", "작성자", "작성기관", "기업정보", "첨부파일"]
data_filtered.to_csv("리포트_데이터_최종.csv", columns=final_columns, index=False, encoding="utf-8-sig")

# 1. 집계 기준 설정
agg_rules = {
    '종목명': 'first',
    '현재가격': 'first',
    '적정가격_수치': 'mean',    # 평균 적정가
    '기대수익률': 'mean',       # 평균 수익률
    '평가의견': lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0] # 최빈값
}

# 2. 그룹화 및 집계 실행
final_df = data_filtered.groupby('종목코드').agg(agg_rules).reset_index()

# 3. 컬럼명 변경
final_df.rename(columns={
    '적정가격_수치': '평균적정가격',
    '기대수익률': '평균기대수익률',
    '평가의견': '대표평가의견'
}, inplace=True)

# ============================================================
# [에러 해결 부분]
# 결측치(NaN)가 있으면 int로 변환이 불가능하므로 0으로 채웁니다.
final_df['평균적정가격'] = final_df['평균적정가격'].fillna(0)
final_df['평균기대수익률'] = final_df['평균기대수익률'].fillna(0)
# ============================================================

# 4. 반올림 및 정수 변환
final_df['평균적정가격'] = final_df['평균적정가격'].round(0).astype(int)
final_df['평균기대수익률'] = final_df['평균기대수익률'].round(2)

# 5. 수익률 높은 순으로 정렬 (평균적정가격이 0인 경우 맨 뒤로 가게 됨)
final_df = final_df.sort_values(by='평균기대수익률', ascending=False)

# 6. 최종 컬럼 순서 정리
target_columns = ['종목코드', '종목명', '현재가격', '평균적정가격', '평균기대수익률', '대표평가의견']
final_df = final_df[target_columns]

# 결과 출력
print(f"최종 요약된 기업 수: {len(final_df)}개")
print(final_df.head(10))

print(f"1. 수집된 전체 리포트 개수: {len(data)}개")
print(f"   (수집된 고유 종목 수: {data['종목코드'].nunique()}개)")

print("-" * 30)

# 1개짜리 제거 로직 후
print(f"2. 레포트가 2개 이상인 리포트 개수: {len(data_filtered)}개")
print(f"   (필터링 후 살아남은 종목 수: {data_filtered['종목코드'].nunique()}개)")

print("-" * 30)

# 그룹화 후
print(f"3. 최종 결과 데이터프레임 행 개수: {len(final_df)}개")

# 파일 저장
final_df.to_csv("종목별_평균수익률_요약.csv", index=False, encoding="utf-8-sig")