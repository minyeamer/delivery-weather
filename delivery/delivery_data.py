import numpy as np
import pandas as pd


def make_seoul_delivery(origin_df: pd.DataFrame, start_date=None, end_date=None) -> pd.DataFrame:
    """
    원본 데이터프레임에서 '서울특별시' 부분을 추출하는 함수
    origin_df: 원본 데이터프레임
    start_date: 맨 윗 열의 '일자' 인덱스 (MM-DD)
    end_date: 맨 아랫 열의 '일자' 인덱스 (MM-DD)
    seoul_df: '행정구역'에서 '서울특별시'에 해당하는 행만 걸러낸 데이터프레임, 함수 반환값
    """
    
    seoul_df = origin_df[ origin_df['행정구역'] == '서울특별시' ]
    seoul_df = pd.pivot_table(seoul_df, index=['행정구역', '일자', '분류'], aggfunc=np.sum)
    seoul_df = seoul_df.reset_index()
    del seoul_df['행정구역']
    del seoul_df['시간']

    seoul_df = detach_year(seoul_df)
    seoul_df = seoul_df.set_index('일자')
    
    return seoul_df.loc[start_date : end_date]


def detach_year(origin_df: pd.DataFrame) -> pd.DataFrame:
    """
    원본 데이터프레임의 '일자' 열에 속한 데이터에서 연도와 월일을 분리
    origin_df: 원본 데이터프레임 (한글)
    detached_df: 원본 데이터프레임의 사본 (원본 데이터프레임 변형 방지 목적), 함수 반환값
    """

    detached_df = origin_df.copy()

    for row in detached_df.iterrows():
        date = row[1]['일자']
        detached_df.at[row[0], '일자'] = date[5:]

    return detached_df


def detach_month(origin_df: pd.DataFrame) -> pd.DataFrame:
    """
    원본 데이터프레임의 '일자' 열에 속한 데이터에서 월과 일을 분리
    origin_df: 원본 데이터프레임 (영문)
    detached_df: 원본 데이터프레임의 사본 (원본 데이터프레임 변형 방지 목적), 함수 반환값
    """

    detached_df = origin_df.copy()

    for row in detached_df.iterrows():
        date = row[1]['date']
        detached_df.at[row[0], 'date'] = date[-2:]

    return detached_df


def count_by_category(origin_df: pd.DataFrame, sum_df: pd.DataFrame, categories: list) -> pd.DataFrame:
    """
    음식 '분류' 별로 '주문횟수'를 추출해서 새로운 열을 만드는 함수
    origin_df: 원본 데이터프레임
    sum_df: '총주문횟수' 열을 가지고 있는 데이터프레임
    categories: 음식 분류 목록
    counting_df: sum_df의 사본 (원본 데이터인 sum_df의 변형 방지 목적), 함수 반환값
    each_delivery: 특정 음식 '분류'에 해당하는 행만 추출한 데이터프레임
    """

    counting_df = sum_df.copy()

    for category in categories:
        each_delivery = origin_df[ origin_df['분류'] == category ].copy()
        del each_delivery['분류']
        counting_df = counting_df.join(each_delivery)
        counting_df.rename(columns={'주문횟수':category}, inplace=True)

    counting_df = counting_df.fillna(0)

    return counting_df


def rename_kor_to_eng(origin_df: pd.DataFrame) -> pd.DataFrame:
    """
    한글로 된 열 이름을 영어로 변환하는 함수
    origin_df: 원본 데이터프레임
    renamed_df: 원본 데이터프레임의 사본 (원본 데이터프레임 변형 방지 목적), 함수 반환값
    en_dictionary: 한영 변환할 때 문자열을 매칭시키기 위해 사용하는 딕셔너리
    en_categories: 영어로 변환된 열 이름을 정렬하기 위해 사용하는 리스트
    """

    renamed_df = origin_df.copy()

    en_dictionary = dict()
    en_dictionary['총주문횟수'] = 'sum'
    en_dictionary['도시락'] = 'dosirak'
    en_dictionary['돈까스/일식'] = 'jpfood'
    en_dictionary['분식'] = 'bunsik'
    en_dictionary['심부름'] = 'simburum'
    en_dictionary['아시안/양식'] = 'wsfood'
    en_dictionary['족발/보쌈'] = 'bossam'
    en_dictionary['중식'] = 'cnfood'
    en_dictionary['찜탕'] = 'tang'
    en_dictionary['치킨'] = 'chicken'
    en_dictionary['카페/디저트'] = 'dessert'
    en_dictionary['패스트푸드'] = 'fastfood'
    en_dictionary['피자'] = 'pizza'
    en_dictionary['한식'] = 'krfood'
    en_dictionary['회'] = 'sashimi'

    renamed_df.rename(columns=en_dictionary, inplace=True)
    renamed_df.index.name = 'date'

    en_categories = list(en_dictionary.values())
    en_categories = [en_categories[0]] + sorted(en_categories[1:])
    renamed_df = renamed_df.reindex(columns=en_categories)

    return renamed_df


def get_dataframe(year: str, start_date=None, end_date=None, directory='') -> pd.DataFrame:
    """
    특정 기간에 해당하는 데이터프레임을 반환하는 함수
    year: 연도
    start_date: 시작 일자 (MM-DD)
    end_date: 종료 일자 (MM-DD)
    directory: 데이터가 위치한 디렉토리 (상대 경로)
    """

    original_delivery = pd.read_csv(f'{directory}KT_DLVR_{year}.csv', encoding='utf-8')

    seoul_delivery = make_seoul_delivery(original_delivery, start_date, end_date)
    sum_delivery = pd.pivot_table(seoul_delivery, index=['일자'], aggfunc=np.sum)
    sum_delivery.rename(columns={'주문횟수':'총주문횟수'}, inplace=True)
    delivery_categories = sorted(list(set(seoul_delivery['분류'])))

    counted_delivery = count_by_category(seoul_delivery, sum_delivery, delivery_categories)
    del counted_delivery['배달전문업체']
    del counted_delivery['야식']

    counted_delivery_en = rename_kor_to_eng(counted_delivery)

    return counted_delivery_en
