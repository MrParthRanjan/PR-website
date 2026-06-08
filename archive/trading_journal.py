"""
trading_journal.py — Python port of the MAHAKAAL trading-journal workbook.
Classes: SessionEngine, Trade, Analytics. No third-party deps for core engine.
"""
from __future__ import annotations
import csv
import datetime as _dt
from dataclasses import dataclass, field
from typing import Optional

# --- Reference data (SETTINGS!N2:O9 + Essential config) ---
CONTRACT_MULTIPLIERS = {
    "Gold": 100, "BTC": 1, "ETH": 1, "EUR/USD": 100_000,
    "GBP/USD": 100_000, "NAS100": 1, "US30": 1, "Crude": 1_000,
}
INSTRUMENT_GROUP = {
    "Gold": "FX", "BTC": "FX", "ETH": "FX", "EUR/USD": "FX",
    "GBP/USD": "FX", "Crude": "FX", "NAS100": "IDX", "US30": "IDX",
}
DEFAULT_GROUP = "FX"
FX_SESSIONS = [("Asia", 0.0, 7.0), ("London", 7.0, 12.0),
               ("NY-London Overlap", 12.0, 16.0), ("New York", 16.0, 21.0)]
IDX_SESSIONS = [("Pre-Market", 8.0, 13.5), ("New York", 13.5, 20.0)]
IST_OFFSET_HOURS = 5.5  # IST = UTC+5:30, no India DST


class SessionEngine:
    @staticmethod
    def _last_sunday(year, month):
        if month == 12:
            d = _dt.date(year, 12, 31)
        else:
            d = _dt.date(year, month + 1, 1) - _dt.timedelta(days=1)
        return d - _dt.timedelta(days=(d.weekday() - 6) % 7)

    @staticmethod
    def _nth_sunday(year, month, n):
        d = _dt.date(year, month, 1)
        first_sun = d + _dt.timedelta(days=(6 - d.weekday()) % 7)
        return first_sun + _dt.timedelta(weeks=n - 1)

    @classmethod
    def uk_dst_active(cls, utc_dt):
        y = utc_dt.year
        return cls._last_sunday(y, 3) <= utc_dt.date() < cls._last_sunday(y, 10)

    @classmethod
    def us_dst_active(cls, utc_dt):
        y = utc_dt.year
        return cls._nth_sunday(y, 3, 2) <= utc_dt.date() < cls._nth_sunday(y, 11, 1)

    @staticmethod
    def instrument_group(instrument):
        return INSTRUMENT_GROUP.get(instrument, DEFAULT_GROUP)

    @classmethod
    def ist_to_utc(cls, ist_dt):
        return ist_dt - _dt.timedelta(hours=IST_OFFSET_HOURS)

    @classmethod
    def classify(cls, ist_dt, instrument):
        if not instrument:
            return "No Instrument"
        utc_dt = cls.ist_to_utc(ist_dt)
        if utc_dt.weekday() >= 5:
            return "Market Closed"
        group = cls.instrument_group(instrument)
        tod = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
        if group == "IDX":
            shift = 1.0 if cls.us_dst_active(utc_dt) else 0.0
            windows = IDX_SESSIONS
        else:
            shift = 1.0 if cls.uk_dst_active(utc_dt) else 0.0
            windows = FX_SESSIONS
        for name, start, end in windows:
            if (start - shift) <= tod < (end - shift):
                return name
        return "Market Closed"


@dataclass
class Trade:
    instrument: str
    direction: str
    lots: float
    entry: float
    stop_loss: float
    take_profit: float
    exit_price: float
    timestamp: Optional[_dt.datetime] = None
    session_override: str = ""
    fresh: bool = True
    emotional: bool = False
    exec_quality: float = 0.0
    setup: str = ""
    trigger: str = ""
    htf_bias: str = ""
    confluence: str = ""
    mistake: str = ""
    emotion: str = ""
    multiplier: float = field(init=False, default=0.0)
    risk: float = field(init=False, default=0.0)
    target_profit: float = field(init=False, default=0.0)
    planned_rr: float = field(init=False, default=0.0)
    r_achieved: float = field(init=False, default=0.0)
    pnl: float = field(init=False, default=0.0)
    result: str = field(init=False, default="")
    validity: str = field(init=False, default="")
    session: str = field(init=False, default="")

    def __post_init__(self):
        self.multiplier = CONTRACT_MULTIPLIERS.get(self.instrument, 1)
        self._compute()

    def _compute(self):
        sl_dist = abs(self.entry - self.stop_loss)
        self.risk = sl_dist * self.lots * self.multiplier
        self.target_profit = abs(self.take_profit - self.entry) * self.lots * self.multiplier
        self.planned_rr = abs(self.take_profit - self.entry) / sl_dist if sl_dist else 0.0
        if sl_dist == 0:
            self.r_achieved = 0.0
        elif self.direction.lower() == "buy":
            self.r_achieved = (self.exit_price - self.entry) / sl_dist
        else:
            self.r_achieved = (self.entry - self.exit_price) / sl_dist
        self.pnl = self.r_achieved * self.risk
        self.result = self._classify_result()
        self.validity = "INVALID" if (not self.fresh or self.emotional) else "VALID"
        if self.session_override:
            self.session = self.session_override
        elif self.timestamp is not None:
            self.session = SessionEngine.classify(self.timestamp, self.instrument)
        else:
            self.session = ""

    def _classify_result(self):
        z = self.r_achieved
        if z <= -1:
            return "Loss"
        if z >= self.planned_rr and self.planned_rr > 0:
            return "Win"
        if z > 0:
            return "Partial TP"
        if z > -0.2:
            return "BE"
        return "Loss"

    @property
    def r_multiple(self):
        return self.r_achieved


class Analytics:
    def __init__(self, trades):
        self.trades = trades

    @property
    def total_trades(self):
        return len(self.trades)

    @property
    def valid_trades(self):
        return sum(1 for t in self.trades if t.validity == "VALID")

    @property
    def invalid_trades(self):
        return sum(1 for t in self.trades if t.validity == "INVALID")

    @property
    def total_r(self):
        return sum(t.r_multiple for t in self.trades)

    @property
    def expectancy(self):
        return self.total_r / self.total_trades if self.total_trades else 0.0

    @property
    def win_rate(self):
        wins = sum(1 for t in self.trades if t.result == "Win")
        return wins / self.total_trades if self.total_trades else 0.0

    @property
    def profit_factor(self):
        gw = sum(t.r_multiple for t in self.trades if t.r_multiple > 0)
        gl = abs(sum(t.r_multiple for t in self.trades if t.r_multiple < 0))
        return "∞ No Losses" if gl == 0 else gw / gl

    def edge_table(self, attr):
        groups = {}
        for t in self.trades:
            key = getattr(t, attr, "") or "(blank)"
            groups.setdefault(key, []).append(t)
        out = {}
        for key, ts in groups.items():
            n = len(ts)
            wins = sum(1 for t in ts if t.result == "Win")
            tot_r = sum(t.r_multiple for t in ts)
            out[key] = {"count": n, "win_pct": wins / n if n else 0.0,
                        "avg_r": tot_r / n if n else 0.0, "total_r": tot_r}
        return out

    def r_distribution(self):
        b = {"<=-1": 0, "-1 to 0": 0, "0 to 1": 0, "1 to 2": 0, "2 to 3": 0, "3+": 0}
        for t in self.trades:
            r = t.r_multiple
            if r <= -1: b["<=-1"] += 1
            elif r < 0: b["-1 to 0"] += 1
            elif r < 1: b["0 to 1"] += 1
            elif r < 2: b["1 to 2"] += 1
            elif r < 3: b["2 to 3"] += 1
            else: b["3+"] += 1
        return b

    def equity_curve(self):
        cum, out = 0.0, []
        for t in self.trades:
            cum += t.r_multiple
            out.append(cum)
        return out

    def max_drawdown(self):
        peak, mdd = float("-inf"), 0.0
        for cum in self.equity_curve():
            peak = max(peak, cum)
            mdd = min(mdd, cum - peak)
        return mdd

    def summary(self):
        return {
            "total_trades": self.total_trades, "valid": self.valid_trades,
            "invalid": self.invalid_trades, "total_r": round(self.total_r, 2),
            "expectancy": round(self.expectancy, 3), "win_rate": round(self.win_rate, 3),
            "profit_factor": self.profit_factor, "max_drawdown_r": round(self.max_drawdown(), 2),
        }

    @classmethod
    def from_csv(cls, path):
        trades = []
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                ts = None
                if row.get("timestamp"):
                    try:
                        ts = _dt.datetime.fromisoformat(row["timestamp"])
                    except ValueError:
                        ts = None
                trades.append(Trade(
                    instrument=row["instrument"].strip(), direction=row["direction"].strip(),
                    lots=float(row["lots"]), entry=float(row["entry"]),
                    stop_loss=float(row["stop_loss"]), take_profit=float(row["take_profit"]),
                    exit_price=float(row["exit_price"]), timestamp=ts,
                    session_override=row.get("session_override", "").strip(),
                    fresh=str(row.get("fresh", "true")).lower() in ("true", "1", "yes", "y"),
                    emotional=str(row.get("emotional", "false")).lower() in ("true", "1", "yes", "y"),
                    exec_quality=float(row.get("exec_quality") or 0),
                    setup=row.get("setup", "").strip(), trigger=row.get("trigger", "").strip(),
                    htf_bias=row.get("htf_bias", "").strip(), confluence=row.get("confluence", "").strip(),
                    mistake=row.get("mistake", "").strip(), emotion=row.get("emotion", "").strip(),
                ))
        return cls(trades)


if __name__ == "__main__":
    demo = [
        Trade("Gold", "Buy", 0.083, 4562, 4550, 4598, 4598,
              timestamp=_dt.datetime(2026, 1, 6, 14, 30), setup="Breakout", exec_quality=4),
        Trade("NAS100", "Sell", 1, 21000, 21080, 20760, 20850,
              timestamp=_dt.datetime(2026, 1, 7, 20, 0), setup="Reversal",
              emotional=True, exec_quality=2),
    ]
    a = Analytics(demo)
    for k, v in a.summary().items():
        print(f"{k:16}: {v}")