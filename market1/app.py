#!/usr/bin/env python3
import sys
from pathlib import Path

import click
import uvicorn

from market.main import app

sys.path.insert(0, Path(__file__).absolute().parent.as_posix())


@click.command()
@click.option("--host", "-h", default="0.0.0.0", help="监听地址")
@click.option("--port", "-p", default=8000, help="监听端口.")
def main(host="0.0.0.0", port=8000):
    """策略市场入口"""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
