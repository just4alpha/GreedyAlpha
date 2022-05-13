# -*- coding:UTF-8 -*-
import talib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Widget
from matplotlib import ticker as tk
from mplfinance.original_flavor import candlestick_ohlc

indicators = ["kama", "mavol", "macd"]
data_path = "data/01-chart-01"
file_name = "AAPL-20200101-20220228-1d.csv"

data = None
show_data = None
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
data_size = 0
text_data = {}
axes_data = {}
vlines = {}
hlines = {}
background = None

s_idx = -90
e_idx = -1
current_x = -1
button_flag = False

fig = plt.figure()


def load_data():
    global data, show_data, data_size
    data = pd.read_csv("%s/%s" % (data_path, file_name))
    data.index = data["Date"].apply(lambda x: pd.Timestamp(x).strftime('%Y-%m-%d'))
    data.drop("Date", axis=1, inplace=True)

    for item in indicators:
        eval("indicators_%s()" % item)
    
    show_data = data.iloc[s_idx: e_idx]


def indicators_kama():
    data["kama"] = talib.KAMA(data["Close"], timeperiod=30)


def indicators_mavol():
    data["mavol"] = talib.MA(data["Volume"], timeperiod=20)


def indicators_macd():
    data["macd"], data["macd_signal"], data["macd_hist"] = talib.MACD(data["Close"])


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
    if button_flag:
        return
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
        elif key == "macd":
            ax.set_title("  ".join([key.upper(), "DIF: %.3f" % show_data["macd"][idx], "DEA: %.3f" % show_data["macd_signal"][idx], "MACD: %.3f" % (show_data["macd_hist"][idx]*2)]),
                loc='left', y=1, fontsize="large")
        elif key == "vol":
            ax.set_title("  ".join(["交易量", "%.2f W" % (show_data["Volume"][idx]/10000)]),
                loc='left', y=1, fontsize="large")
    # show text
    ax = axes_data["main"]
    x, y = 0.1, 0.9
    if idx < data_size / 2:
        x = 0.9
    key_show = "%.1f" % x
    key_hide = "%.1f" % (1-x)
    textstr = '\n'.join((
        r'%s' % show_data.index[idx],
        r'开盘: %.1f' % show_data["Open"][idx],
        r'收盘: %.1f' % show_data["Close"][idx],
        r'最高: %.1f' % show_data["High"][idx],
        r'最低: %.1f' % show_data["Low"][idx],
        r'均值: %.1f' % show_data["kama"][idx]))
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

    # show cursor
    for line in vlines.values():
        line.set_xdata(idx)
        line.set_visible(True)
    find = False
    for key, line in hlines.items():
        ax = axes_data.get(key)
        if ax is not None and event.inaxes == ax:
            line.set_ydata(event.ydata)
            line.set_visible(True)
            find = True
        else:
            line.set_visible(False)
    if not find:
        for key, ax in axes_data.items():
            if event.inaxes != ax:
                continue
            hlines[key] = ax.axhline(event.ydata, visible=True, color="r", lw=1, ls="dashdot")
    if background is not None:
        fig.canvas.restore_region(background)
    for key, ax in axes_data.items():
        line = vlines.get(key)
        if line is not None:
            ax.draw_artist(line)
        line = hlines.get(key)
        if line is not None:
            ax.draw_artist(line)
    fig.canvas.blit()


def button_press(event):
    global current_x, button_flag
    idx = int(event.xdata)
    current_x = idx
    button_flag = True



def button_release(event):
    global current_x, button_flag, s_idx, e_idx, show_data, text_data
    button_flag = False

    idx = int(event.xdata)
    diff = idx - current_x
    s_idx -= diff
    e_idx -= diff
    if e_idx > 0:
        e_idx = -1
        s_idx = -90
    show_data = data[s_idx: e_idx]

    for ax in axes_data.values():
        ax.cla()
        plt.clf()
    
    text_data = {}
    
    show_chart()
    
    current_x = -1


def on_scroll(event):
    ax = event.inaxes
    if ax is None:
        return
    global s_idx, e_idx, show_data, text_data
    diff = int(data_size * 0.1 / 2)
    if event.button == "down":
        s_idx += diff
        e_idx -= diff
    elif event.button == "up":
        s_idx -= diff
        e_idx += diff
    if e_idx > 0:
        e_idx = -1
    show_data = data[s_idx: e_idx]
    for ax in axes_data.values():
        ax.cla()
        plt.clf()
    text_data = {}
    show_chart()

def clear(event):
    global background
    background = (fig.canvas.copy_from_bbox(fig.bbox))
    for line in vlines.values():
        line.set_visible(False)
    for line in hlines.values():
        line.set_visible(False)

def show_chart():
    global data_size
    data_size = len(show_data)

    fig.set_size_inches((20, 16))
    ax_main = fig.add_subplot(3, 1, 1)
    ax_macd = fig.add_subplot(3, 1, 2, sharex=ax_main)
    ax_vol = fig.add_subplot(3, 1, 3, sharex=ax_main)

    axes_data["main"] = ax_main
    axes_data["macd"] = ax_macd
    axes_data["vol"] = ax_vol

    def format_date(x, pos):
        if x < 0 or x > len(show_data.index) - 1:
            return ''
        return show_data.index[int(x)]
    ax_main.xaxis.set_major_formatter(tk.FuncFormatter(format_date))
    ax_main.xaxis.set_major_locator(tk.MultipleLocator(5 if data_size <= 90 else int(data_size/18)))

    ohlc = []
    i = 0
    idxs = range(len(show_data.index))
    for date, row in show_data.iterrows():
        openp, highp, lowp, closep = row[:4]
        ohlc.append([i, openp, highp, lowp, closep])
        i += 1
    
    ax_main.plot(idxs, show_data["kama"], label="KAMA")
    candlestick_ohlc(ax_main, ohlc, colorup="r", colordown="g", width=0.8)
    ax_main.legend()

    ax_macd.plot(show_data.index, show_data["macd"], label="macd", color="y")
    ax_macd.plot(show_data.index, show_data["macd_signal"], label="signal", color="b")
    macd_hist = show_data[show_data.macd_hist >= 0].macd_hist
    ax_macd.bar(macd_hist.index.tolist(), macd_hist, color="r")
    macd_hist = show_data[show_data.macd_hist < 0].macd_hist
    ax_macd.bar(macd_hist.index.tolist(), macd_hist, color="g")
    ax_macd.get_xaxis().set_visible(False)
    ax_macd.get_yaxis().set_visible(False)
    ax_macd.legend()

    volume = show_data[show_data.Volume >= show_data.mavol].Volume
    ax_vol.bar(volume.index.tolist(), volume, color="r")
    volume = show_data[show_data.Volume < show_data.mavol].Volume
    ax_vol.bar(volume.index.tolist(), volume, color="g")
    ax_vol.get_xaxis().set_visible(False)
    ax_vol.get_yaxis().set_visible(False)

    fig.canvas.mpl_connect('axes_enter_event', enter_axes)
    fig.canvas.mpl_connect('axes_leave_event', leave_axes)
    fig.canvas.mpl_connect('motion_notify_event', on_move)
    fig.canvas.mpl_connect('button_press_event', button_press)
    fig.canvas.mpl_connect('button_release_event', button_release)
    fig.canvas.mpl_connect('scroll_event', on_scroll)
    fig.canvas.mpl_connect('draw_event', clear)


    plt.tight_layout()
    plt.subplots_adjust(hspace=0.2)

    global vlines, hlines
    xmid = data_size/2
    ymid = min(show_data["Low"]) + (max(show_data["High"]) - min(show_data["Low"]))/2
    vlines = dict([(key, ax.axvline(xmid, color="r", lw=1, ls="dashdot"))
                           for key, ax in axes_data.items()])
    hlines = {"main": ax_main.axhline(ymid, visible=True, color="r", lw=1, ls="dashdot")}

    plt.show()


def main():
    load_data()
    show_chart()


if __name__ == "__main__":
    main()

