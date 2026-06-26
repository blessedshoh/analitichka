"""Reference-issue sample data.

Mirrors the figures from the supplied reference PDF so the app renders a
faithful proof-of-concept newsletter out of the box and the frontend opens
pre-filled. Replace these with live/edited values in production.
"""

from __future__ import annotations

import math
from datetime import date, timedelta

from app.models.bloomberg import (
    BloombergData,
    Commodity,
    CommodityTable,
    EquityIndex,
    EquityIndexTable,
    RateCurveRow,
    RateCurveTable,
    TreasuryRow,
    TreasuryTable,
)
from app.models.common import FetchStatus, SourceMeta
from app.models.fx import CbuFxTable, CbuRate, FxCross, FxCrossTable
from app.models.money_market import (
    InterbankRow,
    InterbankTable,
    LiquiditySummary,
    MoneyMarketLocal,
    RepoRow,
    RepoTable,
    UzoniaRow,
    UzoniaTable,
)
from app.models.capital import CapitalTable
from app.models.newsletter import Newsletter, NewsletterMeta
from app.models.news import NewsBlocks
from app.models.stocks import StockRow, StockTable
from app.models.timeseries import ChartSet, TimeSeries


def sample_capital_tables() -> list[CapitalTable]:
    """Representative bond tables (placeholder figures, edit per issue)."""
    return [
        CapitalTable(
            slot="corp_bonds",
            title="КОРПОРАТИВНЫЕ ОБЛИГАЦИИ ВНУТРЕННЕГО РЫНКА УЗБЕКИСТАНА",
            columns=["Эмитент", "Номинальная стоимость", "Ставка купона (%)",
                     "Объём размещения", "Дата эмиссии", "Дата погашения"],
            rows=[
                ["Anorbank", "1 000 000", "24.0", "30.0", "06.03.2025", "06.03.2026"],
                ["Agro Credit", "1 000 000", "23.5", "25.0", "18.02.2025", "18.02.2026"],
                ["KRPU", "1 000 000", "22.0", "40.0", "30.01.2025", "30.01.2026"],
                ["Ipak Yuli", "1 000 000", "21.5", "50.0", "14.02.2025", "14.02.2026"],
                ["Davr Bank", "1 000 000", "23.0", "20.0", "04.03.2025", "04.03.2026"],
            ],
        ),
        CapitalTable(
            slot="gov_bonds",
            title="ИТОГИ РАЗМЕЩЕНИЯ ГОС.ОБЛИГАЦИЙ",
            columns=["Эмитент", "Объявл. объём выпуска", "Объём спроса",
                     "Средняя доходность (%)", "Дата эмиссии", "Дата погашения"],
            rows=[
                ["Минфин", "300", "1 565.67", "12.79", "04.06.2026", "04.06.2029"],
                ["Минфин", "300", "1 002.13", "13.05", "04.06.2026", "04.06.2031"],
                ["Минфин", "300", "1 454.27", "13.42", "04.06.2026", "04.06.2027"],
                ["Минфин", "300", "988.41", "12.95", "04.06.2026", "04.06.2028"],
            ],
        ),
        CapitalTable(
            slot="eurobonds_fx",
            title="ИНФОРМАЦИЯ ПО ЕВРООБЛИГАЦИЯМ УЗБЕКИСТАНА В ИН. ВАЛЮТЕ",
            columns=["Эмитент", "Цена", "Доходность (%)", "Объём",
                     "Срок погашения (г.)", "До погашения (г.)", "Срок обращения"],
            rows=[
                ["Узнацбанк", "106.6", "6.1", "$300 млн", "05.07.2029", "3.1", "5"],
                ["Узнацбанк", "103.7", "6.2", "$300 млн", "17.07.2030", "4.1", "5"],
                ["Алокабанк", "99.8", "7.8", "$300 млн", "18.05.2031", "4.9", "5"],
                ["Минфин", "92.9", "5.5", "$600 млн", "19.02.2031", "4.7", "10"],
                ["Минфин", "93.4", "5.6", "$300 млн", "20.02.2029", "2.7", "5"],
            ],
        ),
        CapitalTable(
            slot="eurobonds_local",
            title="ИНФОРМАЦИЯ ПО ЕВРООБЛИГАЦИЯМ УЗБЕКИСТАНА В НАЦ.ВАЛЮТЕ",
            columns=["Эмитент", "Цена", "Доходность (%)", "Объём",
                     "Срок погашения", "До погашения (г.)", "Срок обращения"],
            rows=[
                ["Узнацбанк", "105.8", "13.9", "1.4 трлн", "05.07.2027", "1.4", "2"],
                ["Минфин", "107.2", "14.6", "1.5 трлн", "17.07.2028", "2.4", "3"],
                ["Минфин", "102.7", "11.4", "12 194 трлн", "29.05.2027", "2.0", "3"],
                ["Ипотека банк", "104.3", "15.1", "0.9 трлн", "19.10.2027", "1.7", "3"],
            ],
        ),
    ]


def _ok(src: str) -> SourceMeta:
    return SourceMeta(source=src, status=FetchStatus.OK)


def _series(name, start, n=140, drift=0.0, amp=1.0, base_noise=0.3):
    dates, vals, v = [], [], float(start)
    d0 = date.today() - timedelta(days=n)
    for i in range(n):
        v += drift + amp * math.sin(i / 9.0) * base_noise + (amp * 0.2)
        dates.append((d0 + timedelta(days=i)).strftime("%d.%m.%Y"))
        vals.append(round(v, 2))
    return TimeSeries(name=name, dates=dates, values=vals)


def sample_charts() -> ChartSet:
    return ChartSet(
        system_liquidity=_series("Общая ликвидность", 12000, amp=900, drift=10),
        cb_operations=_series("Операции ЦБ", 20000, amp=1200, drift=120, base_noise=0.2),
        vix=_series("VIX", 18, amp=2.5, drift=0.0, base_noise=0.5),
        embi=_series("EMBI", 300, amp=8, drift=0.1),
    )


def sample_newsletter() -> Newsletter:
    cbu_fx = CbuFxTable(
        meta=_ok("cbu.uz JSON"),
        rows=[
            CbuRate(code="USDUZS", price=11990.26, change_1m=-30.96, change_6m=-20.17, change_12m=-506.68),
            CbuRate(code="EURUZS", price=13738.44, change_1m=239.77, change_6m=-349.79, change_12m=-666.78),
            CbuRate(code="RUBUZS", price=162.23, change_1m=-7.30, change_6m=10.98, change_12m=2.85),
            CbuRate(code="CNHUZS", price=1769.91, change_1m=1.59, change_6m=63.91, change_12m=29.66),
            CbuRate(code="GBPUZS", price=15861.91, change_1m=-298.22, change_6m=-262.09, change_12m=-1002.71),
        ],
    )

    uzonia = UzoniaTable(
        meta=_ok("cbu.uz scrape"),
        rows=[
            UzoniaRow(date="22.06.2026", on=13.35, w1=13.35, m1=13.12, m3=13.57, m6=13.98),
            UzoniaRow(date="19.06.2026", on=13.35, w1=13.35, m1=13.12, m3=13.59, m6=13.98),
            UzoniaRow(date="18.06.2026", on=13.35, w1=13.34, m1=13.06, m3=13.58, m6=13.99),
            UzoniaRow(date="17.06.2026", on=13.35, w1=13.32, m1=13.05, m3=13.59, m6=13.99),
            UzoniaRow(date="16.06.2026", on=13.29, w1=13.32, m1=13.05, m3=13.60, m6=14.00),
        ],
    )

    repo = RepoTable(
        meta=_ok("cbu.uz scrape"),
        rows=[
            RepoRow(date="23.06.2026", deals=22, avg_rate=13.58, volume=2118690),
            RepoRow(date="22.06.2026", deals=19, avg_rate=13.54, volume=2506980),
            RepoRow(date="19.06.2026", deals=20, avg_rate=13.34, volume=3309980),
            RepoRow(date="18.06.2026", deals=26, avg_rate=13.14, volume=5052880),
            RepoRow(date="17.06.2026", deals=24, avg_rate=13.13, volume=2939560),
        ],
    )

    interbank = InterbankTable(
        meta=_ok("cbu.uz scrape"),
        rows=[
            InterbankRow(tenor="O/N", date="23.06.2026", rate=13.38, trend=-0.04, volume=999000),
            InterbankRow(tenor="1 неделя", date="13.06.2026", rate=13.30, trend=-0.05, volume=1210000),
            InterbankRow(tenor="1 месяц", date="01.06.2026", rate=17.00, trend=3.55, volume=21000),
            InterbankRow(tenor="3 месяца", date="26.05.2026", rate=10.00, trend=-5.00, volume=245000),
            InterbankRow(tenor="6 месяцев", date="14.05.2026", rate=15.80, trend=3.80, volume=109000),
            InterbankRow(tenor="1 год", date="18.03.2026", rate=16.50, trend=-1.50, volume=300000),
        ],
    )

    summary = LiquiditySummary(
        date="22.06.2026", total_liquidity=18.11, deviation_from_norm=-1.50,
        cb_withdrawal_ops=79.8, cb_provision_ops=0, meta=_ok("cbu.uz scrape"),
    )

    money_market = MoneyMarketLocal(uzonia=uzonia, repo=repo, interbank=interbank, summary=summary)

    def curve(name, rows):
        return RateCurveTable(name=name, rows=[RateCurveRow(**r) for r in rows])

    bloomberg = BloombergData(
        meta=_ok("Bloomberg export (sample)"),
        rate_curves=[
            curve("СТАВКА USD SOFR (%)", [
                {"date": "23.06.2026", "on": 3.81, "m1": 3.64, "m3": 3.73, "m6": 3.86, "m12": 4.03},
                {"date": "31.12.2025", "on": 3.67, "m1": 3.69, "m3": 3.46, "m6": 3.57, "m12": 3.42},
            ]),
            curve("СТАВКА EURO STR (%)", [
                {"date": "22.06.2026", "on": 2.18, "m1": 1.97, "m3": 1.95, "m6": 1.95, "m12": 1.95},
                {"date": "31.12.2025", "on": 2.93, "m1": 1.94, "m3": 2.03, "m6": 2.11, "m12": 2.24},
            ]),
            curve("СТАВКА EURIBOR (%)", [
                {"date": "23.06.2026", "on": None, "m1": 2.28, "m3": 2.31, "m6": 2.63, "m12": 2.81},
                {"date": "31.12.2025", "on": None, "m1": 1.94, "m3": 2.03, "m6": 2.11, "m12": 2.24},
            ]),
            curve("СТАВКА HIBOR CNH (%)", [
                {"date": "23.06.2026", "on": 2.49, "m1": 2.96, "m3": 2.97, "m6": 3.03, "m12": 3.35},
                {"date": "31.12.2025", "on": 4.38, "m1": 3.68, "m3": 2.92, "m6": 2.99, "m12": 3.08},
            ]),
            curve("СТАВКА SHIBOR CNY (%)", [
                {"date": "23.06.2026", "on": 1.46, "m1": 1.43, "m3": 1.43, "m6": 1.45, "m12": 1.48},
                {"date": "31.12.2025", "on": 1.33, "m1": 1.59, "m3": 1.60, "m6": 1.63, "m12": 1.65},
            ]),
            curve("СТАВКА RUONIA RUB (%)", [
                {"date": "23.06.2026", "on": 14.08, "m1": 14.11, "m3": 14.99, "m6": 14.59},
                {"date": "29.12.2025", "on": 15.85, "m1": 16.15, "m3": 16.64, "m6": 18.00},
            ]),
        ],
        fx=FxCrossTable(meta=_ok("Bloomberg export (sample)"), rows=[
            FxCross(code="EURUSD", price=1.1389, change_1m=-0.0214, change_6m=-0.0406, change_12m=-0.0189),
            FxCross(code="USDRUB", price=74.55, change_1m=3.17, change_6m=-3.60, change_12m=-3.95),
            FxCross(code="EURRUB", price=84.90, change_1m=2.08, change_6m=-7.24, change_12m=-5.95),
            FxCross(code="GBPUSD", price=1.3216, change_1m=-0.0218, change_6m=-0.0309, change_12m=-0.0309),
            FxCross(code="USDCNH", price=6.79, change_1m=-0.01, change_6m=-0.23, change_12m=-0.18),
            FxCross(code="USDCHF", price=0.8094, change_1m=0.0235, change_6m=0.0215, change_12m=-0.0034),
            FxCross(code="USDJPY", price=161.51, change_1m=2.33, change_6m=8.04, change_12m=2.55),
            FxCross(code="USDTRY", price=46.48, change_1m=0.78, change_6m=3.65, change_12m=6.86),
            FxCross(code="USDKZT", price=486.28, change_1m=14.23, change_6m=-23.25, change_12m=-35.34),
            FxCross(code="USDAED", price=3.6730, change_1m=0.0001, change_6m=0.0001, change_12m=0.0006),
        ]),
        commodities=CommodityTable(rows=[
            Commodity(name="Золото", price=4119.59, change_1m=-389.73, change_6m=-364.86, change_12m=751.23),
            Commodity(name="Серебро", price=62.00, change_1m=-13.54, change_6m=-9.43, change_12m=25.90),
            Commodity(name="Платина", price=1643.48, change_1m=-283.99, change_6m=-646.26, change_12m=345.85),
            Commodity(name="Палладий", price=1239.61, change_1m=-112.80, change_6m=-617.69, change_12m=160.84),
            Commodity(name="Нефть", price=77.26, change_1m=-26.28, change_6m=14.85, change_12m=5.78),
            Commodity(name="Нат. газ", price=3.23, change_1m=0.32, change_6m=-1.18, change_12m=-0.47),
            Commodity(name="Хлопок", price=78.33, change_1m=-1.90, change_6m=10.87, change_12m=9.61),
            Commodity(name="Сахар", price=605.25, change_1m=-54.00, change_6m=53.25, change_12m=-36.50),
        ]),
        equities=EquityIndexTable(rows=[
            EquityIndex(name="S&P500", price=7472.8, change_1m=-0.7, change_6m=563.0, change_12m=1447.6),
            EquityIndex(name="MSCI EM", price=1786.2, change_1m=116.7, change_6m=415.6, change_12m=620.5),
            EquityIndex(name="EURO Stoxx", price=664.4, change_1m=18.5, change_6m=56.9, change_12m=113.1),
            EquityIndex(name="Footsie", price=10438.0, change_1m=-58.5, change_6m=511.0, change_12m=1647.0),
        ]),
        treasuries=TreasuryTable(rows=[
            TreasuryRow(tenor="3 года", yld=4.21, change_1m=0.04, change_6m=0.63, change_12m=0.40),
            TreasuryRow(tenor="5 лет", yld=4.25, change_1m=0.02, change_6m=0.55, change_12m=0.34),
            TreasuryRow(tenor="10 лет", yld=4.48, change_1m=0.07, change_6m=0.32, change_12m=0.20),
            TreasuryRow(tenor="30 лет", yld=4.94, change_1m=0.12, change_6m=0.12, change_12m=0.09),
        ]),
    )

    stocks = StockTable(
        meta=SourceMeta(source="Telegram + Claude (sample)", status=FetchStatus.OK),
        rows=[
            StockRow(ticker="TSMI*", price_prev=1570.90, price_curr=1566.68, change_pct=-0.27, change_pct_calc=-0.27),
            StockRow(ticker="URTS", price_prev=8345, price_curr=8389, change_pct=0.53, change_pct_calc=0.53),
            StockRow(ticker="UZTL", price_prev=6000, price_curr=6049, change_pct=0.82, change_pct_calc=0.82),
            StockRow(ticker="HMKB", price_prev=66.99, price_curr=67.00, change_pct=0.01, change_pct_calc=0.01),
            StockRow(ticker="UZMK", price_prev=5790, price_curr=5762, change_pct=-0.48, change_pct_calc=-0.48),
            StockRow(ticker="QZSM", price_prev=1200, price_curr=1200, change_pct=0.00, change_pct_calc=0.00),
            StockRow(ticker="SQBN", price_prev=34.00, price_curr=33.49, change_pct=-1.50, change_pct_calc=-1.50),
            StockRow(ticker="IPTB", price_prev=3.23, price_curr=3.20, change_pct=-0.96, change_pct_calc=-0.93, flagged=True, note="extracted % differs from recomputed"),
            StockRow(ticker="BIOK", price_prev=15.232, price_curr=15.250, change_pct=0.12, change_pct_calc=0.12),
            StockRow(ticker="KVTS", price_prev=2430, price_curr=2315, change_pct=-4.73, change_pct_calc=-4.73),
            StockRow(ticker="CBSK", price_prev=3.07, price_curr=3.01, change_pct=-1.95, change_pct_calc=-1.95),
        ],
    )

    news = NewsBlocks(
        us=(
            "Трамп объявил о ядерной сделке с Ираном и снятии блокады Ормузского пролива\n"
            "Президент США Дональд Трамп заявил о заключении соглашения с Ираном, "
            "предусматривающего бессрочный и полный контроль над иранскими ядерными объектами. "
            "Взамен Вашингтон снял блокаду стратегического Ормузского пролива, полностью восстановив "
            "движение коммерческого транспорта, что уже спровоцировало снижение текущих мировых цен "
            "на нефть после фиксации рекордного суточного трафика в 19 млн баррелей.\n"
            "Договорённости также включают частичное смягчение санкций для преодоления гуманитарного "
            "кризиса, а разблокированные средства Ирана будут размещены на контролируемых США счетах эскроу."
        ),
        europe=(
            "ЕЦБ получил одобрение Европарламента по проекту цифрового евро\n"
            "Во вторник прошёл ключевой экономический комитет внешнего Европейского парламента, "
            "официально поддержав запуск единой суверенной электронной платёжной системы. Признание "
            "весьма заметно символично, поскольку расчищает путь к более широкому внедрению и "
            "фактически реализации пластиковых банковских карт на фоне постепенного ослабления роли наличных.\n"
            "Параллельно ЕЦБ продолжает удерживать ставку на текущем уровне, оценивая инфляционные риски."
        ),
        asia=(
            "Оман и Иран создают рабочую группу по управлению Ормузским проливом\n"
            "Официальные представители обеих стран подтвердили намерение обеспечить непрерывность "
            "судоходства и совместно координировать режим прохода судов через стратегический пролив.\n"
            "Деловая активность в Японии вновь ускорилась до трёхлетнего максимума: совокупный "
            "индекс деловой активности PMI поднялся выше отметки 52, отражая ускорение роста "
            "промышленного производства и устойчивый внутренний спрос."
        ),
        cis=(
            "Ставка ЦБ РФ может снизиться до 12% к концу 2026 года — Аксаков\n"
            "Глава комитета Госдумы по финансовому рынку Анатолий Аксаков ожидает четырёх "
            "последовательных снижений ключевой ставки по 50 базисных пунктов в течение второго "
            "полугодия при условии устойчивого замедления инфляции к целевому уровню.\n"
            "Минфин РФ разместил выпуск ОФЗ совокупным объёмом свыше 540 млрд рублей при сохранении "
            "повышенного спроса со стороны институциональных инвесторов."
        ),
        capital_markets=[
            "«Алокабанк» завершил 2025 год с убытком по МСФО. Чистый убыток составил 193,9 млрд "
            "сумов против прибыли в 252,9 млрд сумов годом ранее. Отрицательный результат обусловлен "
            "слабым ростом чистых процентных доходов и сокращением чистой процентной маржи."
        ],
    )

    return Newsletter(
        meta=NewsletterMeta(weekday="ВТОРНИК", issue_date=date.today().strftime("%d.%m.%Y"), issue_number=40),
        news=news,
        cbu_fx=cbu_fx,
        money_market=money_market,
        bloomberg=bloomberg,
        stocks=stocks,
        capital_tables=sample_capital_tables(),
        charts=sample_charts(),
    )
