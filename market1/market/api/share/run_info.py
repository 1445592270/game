import logging

import pymongo

from market.const import TaskType
from market.ctx import ctx

logger = logging.getLogger(__name__)


def get_mongo():
    return ctx.mongo_client


async def get_curves(
    task_type: TaskType, task_id: str, skip: int = 0, limit: int = 100000
):
    """获取收益曲线

    :param task_type: sim/bt/compile
    :param task_id: xxxx
    """
    mongo_client = get_mongo()
    col_name = "task_info_" + str(task_id)
    db_name = "task_result_" + task_type.value
    col = mongo_client[db_name][col_name]["returns"]
    total_cnt = await col.count_documents({})
    data = await col.find(
        {},
        {"_id": False, "day": True, "returns": True, "bench_returns": True},
        skip=skip,
        limit=limit,
        sort=[("day", pymongo.DESCENDING)],
    ).to_list(None)
    # mongo 查询到的数据排序可能有问题，这里重新排序一下
    data.sort(key=lambda v: v["day"])
    #print(data,total_cnt,'3333333333333333333333333333333333333333这是data11111111111')
    return total_cnt, data


async def get_orders(
    task_type: TaskType, task_id: str, skip: int = 0, limit: int = 100000
):
    """获取下单信息

    :param task_type: sim/bt/compile
    :param task_id: xxxx
    """
    mongo_client = get_mongo()
    col_name = "task_info_" + str(task_id)
    db_name = "task_result_" + task_type.value
    col = mongo_client[db_name][col_name]["orders"]
    total_cnt = await col.count_documents({})
    data = await col.find(
        {},
        {
            "_id": False,
            "day": True,
            "returns": True,
            "bench_returns": True,
            "symbol": True,
            "limit_price": True,
            "volume": True,
            "filled_volume": True,
            "trade_vwap": True,
            "open_vwap": True,
            "create_ts": True,
            "update_ts": True,
            "side": True,
            "action": True,
            "style": True,
            # { "style" : 1, "props" : { "trade_type" : 0, "limit_price" : 0 } },
            "status": True,
            "fee": True,
            "pnl": True,
            "trade_amount": True,
            "current": True,
        },
        skip=skip,
        limit=limit,
        sort=[("day", pymongo.DESCENDING)],
    ).to_list(None)
    # mongo 查询到的数据排序可能有问题，这里重新排序一下
    data.sort(key=lambda v: v["day"])
    return total_cnt, data


async def get_positions(
    task_type: TaskType, task_id: str, skip: int = 0, limit: int = 100000
):
    """获取持仓信息

    :param task_type: sim/bt/compile
    :param task_id: xxxx
    """
    mongo_client = get_mongo()
    col_name = "task_info_" + str(task_id)
    db_name = "task_result_" + task_type.value
    col = mongo_client[db_name][col_name]["positions"]
    total_cnt = await col.count_documents({})
    data = await col.find(
        {},
        {
            "_id": False,
            "day": True,
            "returns": True,
            "bench_returns": True,
            "symbol": True,
            "multiplier": True,
            "side": True,
            "volume": True,
            "open_vwap": True,
            "hold_vwap": True,
            "market_value": True,
            "close_price": True,
            "sum_pnl": True,
            "today_pnl": True,
            "create_ts": True,
            "update_ts": True,
        },
        skip=skip,
        limit=limit,
        sort=[("day", pymongo.DESCENDING)],
    ).to_list(None)
    # mongo 查询到的数据排序可能有问题，这里重新排序一下
    data.sort(key=lambda v: v["day"])
    return total_cnt, data


async def get_indicators(task_type: TaskType, task_id: str):
    """获取技术指标信息

    :param task_type: sim/bt/compile
    :param task_id: xxxx
    """
    mongo_client = get_mongo()
    col_name = "task_info_" + str(task_id)
    db_name = "task_result_" + task_type.value
    col = mongo_client[db_name][col_name]["analyze"]
    datas = await col.find(
        {"rtype": "basic"},
        {
            "_id": False,
            "day": True,
            "cum_returns": True,
            "annual_returns": True,
            "cum_bench_returns": True,
            "annual_bench_returns": True,
            "alpha": True,
            "beta": True,
            "sharpe_ratio": True,
            "max_drawdown": True,
            "max_drawdown_period": True,
            "daily_win_raito": True,
            "win_ratio": True,
            "pnl_ratio": True,
        },
        skip=0,
        limit=1,  # 只取一条
        sort=[("day", pymongo.DESCENDING)],
    ).to_list(None)
    if not datas:
        logger.warning("No indicators found for %s[%s]", task_id, task_type)
        return {}
    data = datas[0]
    # TODO: 获取近一月的收益信息
    if "cum_returns" in data:
        data["retruns1m"] = data["cum_returns"]
    if "cum_bench_returns" in data:
        data["retruns1m_bench"] = data["cum_bench_returns"]
    for k in data:
        if data[k] == float("nan"):
            data[k] = 0.0
    #print(data,'8888888888888888888888888999999999999999999   这是data')
    return data


async def get_today_returns(
    task_type: TaskType, task_id: str, skip: int = 0, limit: int = 1
):
    """获取当日的收益信息

    :param task_type: sim/bt/compile
    :param task_id: xxxx
    """
    mongo_client = get_mongo()
    col_name = "task_info_" + str(task_id)
    db_name = "task_result_" + task_type.value
    col = mongo_client[db_name][col_name]["returns"]
    data = await col.find(
        {},
        {
            "_id": False,
            "day": True,
            "returns": True,
            "daily_returns": True,
            "bench_returns": True,
            "daily_bench_returns": True,
        },
        skip=skip,
        limit=limit,
        sort=[("day", pymongo.DESCENDING)],
    ).to_list(None)
    # mongo 查询到的数据排序可能有问题，这里重新排序一下
    data.sort(key=lambda v: v["day"])
    #print(data,'data::::::这是data1212122333333333333333331111111111111222222222')
    return data


async def get_top_orders(
    task_type: TaskType, task_id: str,
):
    """获取模拟交易的牛股（收益高的订单）

    :param task_type: sim/bt/compile
    :param task_id: xxxx
    """


async def get_period_returns(task_id: str):
    """获取 1 月 /3 月 /6 月 /12 月的收益"""
    mongo_client = get_mongo()
    col_name = "task_info_" + str(task_id)
    db_name = "task_result_T_SIM"
    col = mongo_client[db_name][col_name]["analyze"]
    data = await col.find(
        {"rtype": "period"},
        {
            "_id": False,
            "1m": {"$slice": -1},
            "1m.cum_returns": True,
            "3m": {"$slice": -1},
            "3m.cum_returns": True,
            "6m": {"$slice": -1},
            "6m.cum_returns": True,
            "12m": {"$slice": -1},
            "12m.cum_returns": True,
        },
        sort=[("day", pymongo.DESCENDING)],
    ).to_list(None)
    info = {}
    for key in ("1m", "3m", "6m", "12m"):
        try:
            info[f"returns_{key}"] = data[0][key][0]["cum_returns"]
        except (KeyError, IndexError):
            info[f"returns_{key}"] = 0.0

    return info


async def get_portfolio_info(task_type: TaskType, task_id: str):
    """获取策略持仓信息"""
    mongo_client = get_mongo()
    col_name = "task_info_" + str(task_id)
    db_name = "task_result_" + task_type.value
    col = mongo_client[db_name][col_name]["portfolios"]
    datas = await col.find(
        {"id": "portfolio"},
        {"_id": False},
        sort=[("day", pymongo.DESCENDING)],
        limit=1,
    ).to_list(1)
    if not datas:
        return {}
    return datas[0]


async def get_today_positons(task_type: TaskType, task_id: str):
    """获取持仓信息

    :param task_type: sim/bt/compile
    :param task_id: xxxx
    """
    mongo_client = get_mongo()
    col_name = "task_info_" + str(task_id)
    db_name = "task_result_" + task_type.value
    col = mongo_client[db_name][col_name]["positions"]
    current_day_info = await col.aggregate(
        [{"$group": {"_id": "max", "current_day": {"$max": "$day"}}}]
    ).to_list(1)
    try:
        current_day = current_day_info[0]["current_day"]
    except (IndexError, KeyError):
        return []
    data = await col.find(
        {"day": current_day},
        {
            "_id": False,
            "day": True,
            "returns": True,
            "bench_returns": True,
            "symbol": True,
            "multiplier": True,
            "side": True,
            "volume": True,
            "open_vwap": True,
            "hold_vwap": True,
            "market_value": True,
            "close_price": True,
            "sum_pnl": True,
            "today_pnl": True,
            "create_ts": True,
            "update_ts": True,
        },
    ).to_list(None)
    # mongo 查询到的数据排序可能有问题，这里重新排序一下
    return data
