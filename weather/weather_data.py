import numpy as np
import pandas as pd


def clean_up_data(origin_df: pd.DataFrame, start_date=None, end_date=None) -> pd.DataFrame:
    """
    원본 데이터프레임에서 불필요한 행과 열을 제거하는 함수
    origin_df: 원본 데이터프레임
    start_date: 맨 윗 열의 '일자' 인덱스 (MM-DD)
    end_date: 맨 아랫 열의 '일자' 인덱스 (MM-DD)
    weather_df: 원본 데이터프레임에서 전처리된 데이터프레임, 함수 반환값
    """
    
    weather_df = origin_df.copy()

    del weather_df['지점']
    del weather_df['지점명']
    weather_df = weather_df.fillna(0.0)

    weather_df = detach_year(weather_df)

    weather_df = weather_df.set_index('일자')
    
    return weather_df.loc[start_date : end_date]


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
    en_dictionary['평균기온'] = 'temp'
    en_dictionary['강수량'] = 'rain'
    en_dictionary['평균풍속'] = 'wind'
    en_dictionary['최심신적설'] = 'snow'
    en_dictionary['평균전운량'] = 'cloud'

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
    start_date: 시작 일자
    end_date: 종료 일자
    directory: 데이터가 위치한 디렉토리 (상대 경로)
    """

    original_weather = pd.read_csv(f'{directory}WEATHER_{year}.csv', encoding='utf-8')

    weather = clean_up_data(original_weather, start_date, end_date)

    weather_en = rename_kor_to_eng(weather)

    return weather_en
