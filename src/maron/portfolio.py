class Portfolio:
    """通貨毎のportfolioを計算する
    
    ['config', 'currency', 'capital_used', 'cash', 'pnl', 'valuation', 
    'portfolio_value', 'positions_value', 'returns', 'symbols', 
    'starting_cash', 'start_date', 'date', 'positions', 'storage'])

    """

    default = {
        "amount": 0,
        "total_buy_price": 0,
        "total_sell_price": 0,
        "buy_price": 0,
        "sell_price": 0,
        "value": 0,
        "position_ratio": 0,
        "portfolio_ratio": 0,
        "pnl": 0,
        "returns": 0,
    }

    def __init__(self):
        self.positions = Portfolio.default
        self.DIMS = [
            'portfolio_value', 'cash', 'positions_value', 'returns', 'pnl',
            'positions'
        ]

    def _positions(self):
        """positions
        positions[sym].keys = [
            "amount",                 # 保有株数
            "total_buy_price",        # 今までの総購入額
            "total_sell_price",       # 今までの総売却額
            "buy_price",              # 現在のポジションの総購入額(amountが0になると0にリセットされる)
            "sell_price",             # 現在のポジションの総売却額(amountが0になると0にリセットされる)
            "value",                  # 現在の評価額
            "position_ratio",         # 保有銘柄の中での割合,
            "portfolio_ratio",        # 資産全体での割合
            "pnl",                    # 損益額
            "returns",                # 損益率
        ]
        """
        return self.positions

    def order(self, sym, amount):
        if self.positions[sym]["amount"] + amount < 0:
            raise ValueError(
                "Can not order \n"
                f"position: {self.positions[sym]}, order amount:{amount}")
        self.positions[sym]["amount"] += amount

    def update(self):
        pass

    def dims(self):
        pass

    def to_list(self):
        pass
