"""Quantx Trade Code
[Portofolio]
stock: ETF: reserve  = 7: 2: 1

[sym]
stock -> [3405, 6501, 6503, 3116, 6902, 9503, 8001, 8473, 8031, 2127]
ETF -> [1357,]

1. initialize(ctx)が呼ばれる
2. registerされた_signal(data)が呼ばれる。buy, sellのsignalが発生。
3. handle_signals(ctx, date, current)が1日ごとに呼ばれる。(dateがiterate)

"""

import numpy as np
import pandas as pd


# Helper funcs
def cumsum_range(array, sum_range=20):
    arr = array.copy()
    for index, _ in enumerate(array[sum_range:]):
        arr[index + sum_range] = sum(array[index : index + sum_range])
    return arr


def average_range(array, avg_range=5):
    arr = array.copy()
    for index, _ in enumerate(array[avg_range:]):
        arr[index + avg_range] = np.average(array[index : index + avg_range])
    return arr


def initialize(ctx):
    """初期化

    最初に一度だけ呼び出される初期化関数。
    使用するデータセットとシグナルの設定を行う。
    ctx.regist_signalでregisterされたシグナルの演算が行われる。

    args:
        - ctx (obj)
    """
    ctx.logger.debug("initialize() called")
    SHORT_TERM = 5
    LONG_TERM = 25
    STOCK_RATIO = 0.7
    ETF_RATIO = 0.2
    assert STOCK_RATIO + ETF_RATIO < 1
    # jp.stocks
    jp_stocks = [1605, 1925, 2503, 4519, 4911, 6301, 6752, 7741, 8001]
    # ETF
    etf_codes = [1357]

    ctx.unit_stock = 100
    ctx.unit_etf = 100
    ctx.stock_percent = STOCK_RATIO / len(jp_stocks)
    ctx.etf_percent = ETF_RATIO / len(etf_codes)
    ctx.codes = jp_stocks + etf_codes
    ctx.symbol_list = ["jp.stock.{}".format(code) for code in ctx.codes]
    ctx.columns_list = ["close_price_adj", "volume_adj", "ns_fear", "ns_optimism"]
    ctx.configure(
        channels={"jp.stock": {"symbols": ctx.symbol_list, "columns": ctx.columns_list}}
    )

    def _signal1(data):
        """ signal_1:

        condition:
            last 20 days,
            ratio(mav_5days - mav_25days) > 0.7
            and
            avs((mav - stock)/mav) < 0.01

            losscut: -0.05
            plofit: 0.15
        args:
            data(Panel)
                - Dimensions: (items) x (major_axis) x (minor_axis)
                - Items axis: open_price, close_price_adj, and so on
                - Major_axis axis: datetime
                - Minor_axis axis: jp.stock.3405, jp.stock.6503, and so on
        returns:
            - dict
                keys - "buy:sig", "sell:sig"
                values - buy_sig(DataFrame), sell_sig(DataFrame)
        """

        df = data["close_price_adj"].fillna(method="ffill")
        mav_long_term = df.rolling(window=LONG_TERM, center=False).mean()
        mav_short_term = df.rolling(window=SHORT_TERM, center=False).mean()

        diff = mav_short_term - mav_long_term
        # calc 20 days condition
        temp_df = df.copy()
        for col in diff.columns:
            temp_df[col] = cumsum_range((diff > 0).astype(int)[col].values) > 14
        # calc abs condition
        temp_df2 = abs((mav_short_term - df) / mav_short_term) < 0.01
        # buy signal is the condition under which both conditions above equal True.
        buy_sig = (temp_df.astype(int) + temp_df2.astype(int)) == 2

        # all false
        sell_sig = buy_sig > 10

        return {"buy:sig1": buy_sig, "sell:sig1": sell_sig}

    def _signal2(data):
        """signal2

        last 20 days,
        ratio(mav_25days - mav_5days) > 0.7
          and
        volume_adj_today > 2 * averqage(volume_adj, last_5days)

        losscut: 0.05
        plofit: abs(stock/mav_25days) < 0.01

        """
        df = data["close_price_adj"].fillna(method="ffill")
        volume = data["volume_adj"].fillna(method="ffill")
        mav_long_term = df.rolling(window=LONG_TERM, center=False).mean()
        mav_short_term = df.rolling(window=SHORT_TERM, center=False).mean()

        diff = mav_short_term - mav_long_term
        # calc 20 days condition and volume conditions
        temp_df = df.copy()
        temp_df2 = volume.copy()
        for col in diff.columns:
            temp_df[col] = cumsum_range((diff < 0).astype(int)[col].values) > 14
            temp_df2[col] = volume[col].values > 2 * average_range(volume[col].values)
        # buy signal is the condition under which both conditions above equal True.
        buy_sig = (temp_df.astype(int) + temp_df2.astype(int)) == 2

        # calc abs condition
        temp_df3 = abs((mav_long_term - df) / mav_long_term) < 0.01
        sell_sig = temp_df3
        return {"buy:sig2": buy_sig, "sell:sig2": sell_sig}

    def _etf_signal(data):
        """etf_signal

        ETF_signal:
            buy: stock_index_optimism > 0.5
            sell: stock_index_fear > 0.5
        """
        opt = data["ns_optimism"].fillna(method="ffill")
        fear = data["ns_fear"].fillna(method="ffill")

        buy_sig = opt >= 0.9
        sell_sig = fear >= 0.9
        return {"buy:etf": buy_sig, "sell:etf": sell_sig}

    # シグナル登録
    ctx.regist_signal("signal1", _signal1)
    ctx.regist_signal("signal2", _signal2)
    ctx.regist_signal("etf_signal", _etf_signal)


def handle_signals(ctx, date, current):
    """日毎の処理

    株の売買をどの程度するか・損切り・利確の設定を行う。

    args:
        ctx(obj)
            - getSecurity(sym): Securityオブジェクト(銘柄情報)を返すメソッド。
            - portfolio: ポートフォリオ
            - localStorage: キャッシュとして使えるオブジェクト。
        date(datetime.datetime)
        current(DataFrame)
            - index = datetime
            - columns = (initializeで登録したcolumns) + (registerしたsignal関数でreturnしているsignal)
    """
    ctx.logger.debug("handle_signals called")

    LOSS_CUT_STOCK = -0.08
    PLOFIT_STOCK = 0.15
    LOSS_CUT_ETF = -0.05
    PLOFIT_ETF = 0.03

    done_syms = set([])
    # 損切り・利確
    for (sym, val) in ctx.portfolio.positions.items():
        # returnsは損益率 = (時価-購入価格)/購入価格
        returns = val["returns"]
        if "1357" in sym:
            loss_cut = LOSS_CUT_ETF
            plofit = PLOFIT_ETF
        else:
            loss_cut = LOSS_CUT_STOCK
            plofit = PLOFIT_STOCK
        if returns < loss_cut:
            sec = ctx.getSecurity(sym)
            sec.order(-val["amount"], comment="損切り: %f" % returns)
            done_syms.add(sym)
        elif returns > plofit:
            sec = ctx.getSecurity(sym)
            sec.order(-val["amount"], comment="利確: %f" % returns)
            done_syms.add(sym)

    # signal buy
    buy_signals = ["buy:sig1", "buy:sig2"]
    for buy_signal in buy_signals:
        buy = current[buy_signal].dropna()
        # buy = buy[~buy.index.isin(done_syms)]
        for (sym, val) in buy.items():
            # exclude ETF
            if "1357" in sym:
                continue
            sec = ctx.getSecurity(sym)
            sec.order(ctx.unit_stock, comment=buy_signal)
            done_syms.add(sym)
            ctx.logger.debug("BUY: %s, %s, %f" % (buy_signal, sec.code(), val))

    # signal sell
    sell_signals = ["sell:sig1", "sell:sig2"]
    for sell_signal in sell_signals:
        sell = current[sell_signal].dropna()
        sell = sell[~sell.index.isin(done_syms)]
        for (sym, val) in sell.items():
            # exclude ETF
            if "1357" in sym:
                continue
            sec = ctx.getSecurity(sym)
            sec.order(ctx.unit_stock * -1, comment=sell_signal)
            done_syms.add(sym)
            ctx.logger.debug("SELL: %s, %s, %f" % (sell_signal, sec.code(), val))

    # ETF signal buy
    buy = current["buy:etf"].dropna()
    buy = buy[~buy.index.isin(done_syms)]
    sec_etf = ctx.getSecurity("jp.stock.1357")
    sec_etf.order_target_percent(ctx.etf_percent, comment="ETF SIGNAL BUY")
    done_syms.add("jp.stock.1357")
    ctx.logger.debug("BUY: %s " % 1357)

    # ETF signal sell
    sell = current["sell:etf"].dropna()
    sell = sell[~sell.index.isin(done_syms)]
    sec_etf = ctx.getSecurity("jp.stock.1357")
    sec_etf.order(ctx.unit_etf * -1, comment="ETF SIGNAL SELL")
    done_syms.add("jp.stock.1357")
    ctx.logger.debug("SELL: %s" % 1357)
