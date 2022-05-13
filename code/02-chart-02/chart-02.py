# -*- coding:UTF-8 -*-
import talib
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import ticker as tk

indicators = ["ma", "macd", "mavol", "kdj", "flow"]
data_path = "data/01-chart-02"
kline_name = "0700-kline.csv"
flow_name = "0700-flow.csv"


props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
data = None
data_size = 0
text_data = {}
axes_data = {}
fig = plt.figure()



def load_data():
    global data, data_size
    data = pd.read_csv("%s/%s" % (data_path, kline_name))
    data["time"] = data["time_key"].apply(
        lambda x: pd.Timestamp(x).strftime('%H:%M'))

    for item in indicators:
        eval("indicators_%s()" % item)
    
    data = data.iloc[-331:]
    indicators_ma()

    data.index = data.time
    data_size = len(data)


def indicators_ma():
    data["ma"] = data['turnover'].cumsum()/data["volume"].cumsum()


def indicators_mavol():
    data["mavol"] = talib.MA(data["volume"], timeperiod=20)


def indicators_macd():
    data["macd"], data["macd_signal"], data["macd_hist"] = talib.MACD(
        data["close"])


def indicators_kdj():
    data["K"], data["D"] = talib.STOCH(data["high"].values,
        data["low"].values,
        data["close"].values,
        fastk_period=9,
        slowk_period=3,
        slowk_matype=0,
        slowd_period=3,
        slowd_matype=0)
    data["J"] = 3 * data["K"] - 2 * data["D"]


def indicators_flow():
    df = pd.read_csv("%s/%s" % (data_path, flow_name))
    data["flow"] = df["in_flow"]


def enter_axes(event):
    ax = event.inaxes
    if ax is None:
        return
    idx = int(event.xdata)
    x = 0.1
    if idx < data_size / 2:
        x = 0.9
    key_show = '%.1f' % x
    if text_data.get(key_show) is not None:
        text_data[key_show].set_visible(True)
    key_hide = '%.1f' % (1-x)
    if text_data.get(key_hide) is not None:
        text_data[key_hide].set_visible(False)
    event.canvas.draw_idle()


def leave_axes(event):
    ax = event.inaxes
    if ax is None:
        return
    for text in text_data.values():
        text.set_visible(False)
    event.canvas.draw_idle()


def on_move(event):
    ax = event.inaxes
    if ax is None:
        return
    idx = int(event.xdata)
    if idx < 0 or idx >= data_size:
        return

    # show title
    for key, ax in axes_data.items():
        if key == "main":
            continue
        if key == "kdj":
            ax.set_title("  ".join([key.upper(), "K: %.3f" % data["K"][idx], "D: %.3f" % data["D"][idx], "J: %.3f" % data["J"][idx]]),
                loc='left', y=1, fontsize="large")
        elif key == "macd":
            ax.set_title("  ".join([key.upper(), "DIF: %.3f" % data["macd"][idx], "DEA: %.3f" % data["macd_signal"][idx], "MACD: %.3f" % (data["macd_hist"][idx]*2)]),
                loc='left', y=1, fontsize="large")
        elif key == "vol":
            ax.set_title("  ".join(["交易量", "%.2f W" % (data["volume"][idx]/10000)]),
                loc='left', y=1, fontsize="large")
        elif key == "flow":
            ax.set_title("  ".join(["资金流向", "%.2f W" % (data["flow"][idx]/10000)]),
                loc='left', y=1, fontsize="large")

    # show text
    ax = axes_data["main"]
    x, y = 0.1, 0.9
    if idx < data_size / 2:
        x = 0.9
    key_show = "%.1f" % x
    key_hide = "%.1f" % (1-x)
    textstr = '\n'.join((
        r'%s' % data["time_key"][idx],
        r'开盘: %.1f' % data["open"][idx],
        r'收盘: %.1f' % data["close"][idx],
        r'最高: %.1f' % data["high"][idx],
        r'最低: %.1f' % data["low"][idx],
        r'均值: %.1f' % data["ma"][idx]))
    text = text_data.get(key_show)
    if text is None:
        text = ax.text(x, y, textstr, transform=ax.transAxes, fontsize=14,
                       verticalalignment='top', bbox=props, clip_on=False)
        text_data[key_show] = text
    else:
        if text_data.get(key_hide) is not None:
            text_data[key_hide].set_visible(False)
        if not text.get_visible():
            text.set_visible(True)
        text.set_text(textstr)

    event.canvas.draw_idle()


def show_chart():
    fig.set_size_inches((20, 16))
    ax_main = fig.add_subplot(5, 1, 1)
    ax_macd = fig.add_subplot(5, 1, 2, sharex=ax_main)
    ax_kdj = fig.add_subplot(5, 1, 3, sharex=ax_main)
    ax_vol = fig.add_subplot(5, 1, 4, sharex=ax_main)
    ax_flow = fig.add_subplot(5, 1, 5, sharex=ax_main)

    axes_data["main"] = ax_main
    axes_data["macd"] = ax_macd
    axes_data["kdj"] = ax_kdj
    axes_data["vol"] = ax_vol
    axes_data["flow"] = ax_flow

    def format_time(x, pos):
        if x < 0 or x > len(data.index) - 1:
            return ''
        return data.time[int(x)]
    ax_main.xaxis.set_major_formatter(tk.FuncFormatter(format_time))

    ax_main.plot(data.index, data["close"], label="close")
    ax_main.plot(data.index, data["ma"], label="ma")
    ax_main.get_xaxis().set_visible(False)

    ax_macd.plot(data.index, data["macd"], label="macd", color='y')
    ax_macd.plot(data.index, data["macd_signal"], label="signal", color='b')
    macd_hist = data[data.macd_hist >= 0].macd_hist
    ax_macd.bar(macd_hist.index.tolist(), macd_hist*2, color='r')
    macd_hist = data[data.macd_hist < 0].macd_hist
    ax_macd.bar(macd_hist.index.tolist(), macd_hist*2, color='g')
    ax_macd.get_xaxis().set_visible(False)
    ax_macd.legend()

    ax_kdj.plot(data.index, data["K"], label="K")
    ax_kdj.plot(data.index, data["D"], label="D")
    ax_kdj.plot(data.index, data["J"], label="J")
    ax_kdj.plot(data.index, [80] * data_size)
    ax_kdj.plot(data.index, [50] * data_size)
    ax_kdj.plot(data.index, [20] * data_size)
    ax_kdj.get_xaxis().set_visible(False)
    ax_kdj.legend()

    volume = data[data.volume >= data.mavol].volume
    ax_vol.bar(volume.index.tolist(), volume, color='r')
    volume = data[data.volume < data.mavol].volume
    ax_vol.bar(volume.index.tolist(), volume, color='g')
    ax_vol.get_xaxis().set_visible(False)
    ax_vol.get_yaxis().set_visible(False)

    flow = data[data.flow >= 0].flow
    ax_flow.bar(flow.index.tolist(), flow, color='r')
    flow = data[data.flow < 0].flow
    ax_flow.bar(flow.index.tolist(), flow, color='g')
    ax_flow.get_yaxis().set_visible(False)
    ax_flow.xaxis.set_major_locator(tk.MultipleLocator(10))

    fig.canvas.mpl_connect('axes_enter_event', enter_axes)
    fig.canvas.mpl_connect('axes_leave_event', leave_axes)
    fig.canvas.mpl_connect('motion_notify_event', on_move)

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.25)
    plt.show()
    # plt.savefig("chart.png")


def main():
    load_data()
    show_chart()


if __name__ == "__main__":
    main()

