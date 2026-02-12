"""
BAA(Bold Asset Allocation) 전략에 사용되는 자산들의 월봉 데이터를 수집하여
엑셀 파일로 저장하는 스크립트입니다.
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd

# src 폴더에 있는 함수를 사용하기 위해 경로 설정이나 모듈 구조를 활용합니다.
# 이 스크립트는 프로젝트 루트에서 실행하는 것을 가정합니다.

# 스크립트가 위치한 경로를 sys.path에 추가하여 src 모듈을 찾을 수 있도록 보장합니다.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.stock_data import fetch_multiple_stocks

def create_baa_asset_report():
    """
    BAA 전략 자산의 최근 2년치 월봉 데이터를 조회하여 엑셀 파일로 저장합니다.
    """
    # 1. BAA 전략 자산 티커 정의
    # 공격자산, 수비자산, 카나리아 자산을 모두 포함하고 중복을 제거합니다.
    aggressive_assets = ["QQQ", "VEA", "VWO", "BND"]
    defensive_assets = ["BIL", "IEF", "TLT", "LQD", "TIP", "BND", "DBC"]
    canary_assets = ["SPY", "VEA", "VWO", "BND"]

    # 중복을 제거하되 요청하신 순서(공격 -> 수비 -> 카나리아)를 유지합니다.
    tickers_list = []
    seen = set()
    for ticker in aggressive_assets + defensive_assets + canary_assets:
        if ticker not in seen:
            tickers_list.append(ticker)
            seen.add(ticker)

    # 2. 데이터 조회 기간 설정 (최근 2년)
    end_date = datetime.now()
    # 넉넉하게 2년치 데이터를 가져오기 위해 731일을 뺍니다.
    start_date = end_date - timedelta(days=731)

    end_date_str = end_date.strftime("%Y-%m-%d")
    start_date_str = start_date.strftime("%Y-%m-%d")

    # 3. 결과를 저장할 output 폴더를 먼저 생성합니다.
    # 스크립트 파일의 위치를 기준으로 output 폴더 경로를 설정합니다.
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    excel_filename = os.path.join(output_dir, "baa_monthly_data.xlsx")

    print("BAA 자산 월봉 데이터 수집을 시작합니다.")
    print(f"조회 기간: {start_date_str} ~ {end_date_str}")
    print(f"대상 티커: {tickers_list}")

    # 3. fetch_multiple_stocks 함수를 사용하여 월봉 데이터 조회
    monthly_data = fetch_multiple_stocks(
        tickers=tickers_list,
        start_date=start_date_str,
        end_date=end_date_str,
        interval="monthly"
    )

    # 4. 조회된 데이터가 있는지 확인하고 결과를 처리합니다.
    successful_tickers = [ticker for ticker, df in monthly_data.items() if not df.empty]

    if not successful_tickers:
        print("\n모든 티커의 데이터를 조회하지 못했습니다. 인터넷 연결을 확인하거나 잠시 후 다시 시도해주세요.")
        print(f"'{output_dir}' 폴더는 생성되었지만, 데이터가 없어 엑셀 파일은 만들지 않습니다.")
        return

    print(f"\n총 {len(successful_tickers)}개 티커의 데이터 조회를 성공했습니다.")

    try:
        # 5. 데이터를 하나의 시트로 통합 (날짜 기준, 수정 종가 사용)
        print(f"\n'{excel_filename}' 파일에 데이터를 저장합니다...")
        
        combined_df = pd.DataFrame()
        
        for ticker in tickers_list:
            if ticker in monthly_data and not monthly_data[ticker].empty:
                df = monthly_data[ticker]
                
                # 수정 종가(Adj Close)가 있으면 사용하고, 없으면 Close 사용 (미국 주식은 보통 Adj Close 존재)
                col_name = "Adj Close" if "Adj Close" in df.columns else "Close"
                price_data = df[col_name]
                
                # 데이터가 DataFrame인 경우(예: 중복 컬럼 등) 첫 번째 컬럼을 Series로 변환하여 오류 방지
                if isinstance(price_data, pd.DataFrame):
                    price_data = price_data.iloc[:, 0]
                
                price_data.name = ticker  # 컬럼명을 티커 이름으로 설정
                
                if combined_df.empty:
                    combined_df = price_data.to_frame()
                else:
                    # 날짜(인덱스)를 기준으로 외부 조인하여 데이터 병합
                    combined_df = combined_df.join(price_data, how="outer")
        
        combined_df.sort_index(inplace=True)
        combined_df.index.name = "Date"
        combined_df.to_excel(excel_filename)

        print(f"\n성공적으로 '{excel_filename}' 파일을 생성했습니다.")

    except ImportError:
        print("\n엑셀 파일 저장을 위해 'openpyxl' 라이브러리가 필요합니다.")
        print("터미널에서 'pip install openpyxl' 명령어를 실행하여 설치해주세요.")
    except Exception as e:
        print(f"\n엑셀 파일 저장 중 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    create_baa_asset_report()
