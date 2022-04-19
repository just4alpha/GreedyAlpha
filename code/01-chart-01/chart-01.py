# -*- coding:UTF-8 -*-
import talib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker as tk
from mplfinance.original_flavor import candlestick_ohlc

indicators = ["kama", "mavol", "macd"]
data_path = "data/01-chart-01"
file_name = "AAPL-20200101-20220228-1d.csv"

data = None


def load_data():
    global data
    data = pd.read_csv("%s/%s" % (data_path, file_name))
    data.index = data["Date"].apply(lambda x: pd.Timestamp(x).strftime('%Y-%m-%d'))
    data.drop("Date", axis=1, inplace=True)

    for item in indicators:
        eval("indicators_%s()" % item)
    
    data = data.iloc[-100:]


def indicators_kama():
    data["kama"] = talib.KAMA(data["Close"], timeperiod=30)


def indicators_mavol():
    data["mavol"] = talib.MA(data["Volume"], timeperiod=20)


def indicators_macd():
    data["macd"], data["macd_signal"], data["macd_hist"] = talib.MACD(data["Close"])


def show_chart():
    fig = plt.figure()
    fig.set_size_inches((20, 16))
    ax_main = fig.add_subplot(3, 1, 1)
    ax_macd = fig.add_subplot(3, 1, 2, sharex=ax_main)
    ax_vol = fig.add_subplot(3, 1, 3, sharex=ax_main)

    def format_date(x, pos):
        if x < 0 or x > len(data.index) - 1:
            return ''
        return data.index[int(x)]
    ax_main.xaxis.set_major_formatter(tk.FuncFormatter(format_date))
    ax_main.xaxis.set_major_locator(tk.MultipleLocator(5))

    ohlc = []
    i = 0
    idxs = range(len(data.index))
    for date, row in data.iterrows():
        openp, highp, lowp, closep = row[:4]
        ohlc.append([i, openp, highp, lowp, closep])
        i += 1
    
    ax_main.plot(idxs, data["kama"], label="KAMA")
    candlestick_ohlc(ax_main, ohlc, colorup="r", colordown="g", width=0.8)
    ax_main.legend()

    ax_macd.plot(data.index, data["macd"], label="macd", color="y")
    ax_macd.plot(data.index, data["macd_signal"], label="signal", color="b")
    macd_hist = data[data.macd_hist >= 0].macd_hist
    ax_macd.bar(macd_hist.index.tolist(), macd_hist, color="r")
    macd_hist = data[data.macd_hist < 0].macd_hist
    ax_macd.bar(macd_hist.index.tolist(), macd_hist, color="g")
    ax_macd.get_xaxis().set_visible(False)
    ax_macd.legend()

    volume = data[data.Volume >= data.mavol].Volume
    ax_vol.bar(volume.index.tolist(), volume, color="r")
    volume = data[data.Volume < data.mavol].Volume
    ax_vol.bar(volume.index.tolist(), volume, color="g")
    ax_vol.get_xaxis().set_visible(False)

    fig.tight_layout()
    plt.show()
    # fig.savefig("imgs/chart-01.png", bbox_inches="tight")


def main():
    load_data()
    show_chart()


if __name__ == "__main__":
    main()

