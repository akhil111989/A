import pandas as pd
import requests

# ---------------- NSE BHAVCOPY (PRICE DATA) ---------------- #
def download_bhavcopy():
    url = "https://archives.nseindia.com/products/content/sec_bhavdata_full.csv"
    
    df = pd.read_csv(url)
    
    df = df[["SYMBOL", "CLOSE", "HIGH", "LOW"]]
    df.columns = ["symbol", "close", "high", "low"]

    df.to_csv("bhavcopy.csv", index=False)
    print("Bhavcopy saved")

if __name__ == "__main__":
    download_bhavcopy()
