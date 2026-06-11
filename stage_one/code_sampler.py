import json
import torch
import argparse
import numpy as np
import random
import os
from typing import 

def set_seed(seed:int = 42):
    """
    固定所有随机种子以确保实验的可复现性。
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)  # 适用于多GPU环境
    os.environ['PYTHONHASHSEED'] = str(seed)

seed_value = 42
set_seed(seed_value)

def parse_args():
    parser=argparse.ArgumentParser(usage="该项目用于从构建好的code graph中采样出一个最小依赖子集，并将该子集存放到固定文件夹下")
    parser.add_argument("--graph_path",type=str,default="./output.graph.json")

    args=parser.parse_args()
    return args

class Sampler():
    def __init__(
        node_keys:
    ):

    



def main():
    args=parse_args()
    graph=None
    with open(args.graph_path,"r",encoding="utf-8") as f:
        graph=json.load(f)

        



