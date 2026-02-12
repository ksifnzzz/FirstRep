from pykrx import stock

def test_monthly_fetch():
    print("Testing stock.get_market_ohlcv with monthly frequency...")
    # 2023년 삼성전자(005930) 월봉 데이터 조회 ("m" 파라미터 사용)
    df = stock.get_market_ohlcv("20230101", "20231231", "005930", "m")
    
    print("\nResult DataFrame Head:")
    print(df.head())
    print("\nColumns:")
    print(df.columns)

if __name__ == "__main__":
    test_monthly_fetch()