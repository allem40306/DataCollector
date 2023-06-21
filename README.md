# Data Collector

## `getData.py`
- 輸出: `{timestamp}/youbike.json`
    - 編號、經緯度、名稱、剩餘車位、總共車位
- 輸出: `{timestamp}/rainfall.json`
    - 經緯度、名稱、10 分鐘累積雨量、1 小時累積雨量、3 小時累積雨量
- 輸出: `{timestamp}/temperture.json`
    - 經緯度、名稱、溫度

## `youbikeMerge.py`
- 到 https://data.gov.tw/dataset/128428 下載 `.csv` 檔，重新命名為 `mrtStationEntrance.csv`
- 輸出: `final/Youbike.npz`
    - 剩餘車位、10 分鐘累積雨量、1 小時累積雨量、3 小時累積雨量、溫度、一天當作的星期幾、時間
- 輸出: `final/Youbike.csv`
    - 任兩個站點之間的距離

## `mrtMerge.py`
- 輸出 `final/MRT.npz`
    - 進站人次、出站人次、1 小時累積雨量、溫度、一天當作的星期幾、時間
- 輸出: `final/MRT.csv`
    - 任兩個站點之間的距離

## `pemsCsvConvert.py`
- 將 PEMS distance 的 `.csv` 檔重新編號。