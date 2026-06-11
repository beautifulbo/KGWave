import jieba
import os
import sys
import argparse
from typing import List, Dict, Any
from pathlib import Path
import json
import jieba.analyse
import multiprocessing as mp


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, default="./data/text")
    parser.add_argument('--output_path', type=str, default="./data/text/keywords.json")
    # 并行工作进程数，默认为 CPU 核心数
    parser.add_argument('--workers', type=int, default=mp.cpu_count(),
                        help="并行工作进程数，默认为 CPU 核心数")
    args = parser.parse_args()
    return args


def process_single_doc(item):
    """
    处理单个文档：提取关键词并构建位置索引。
    必须是顶层函数（不能是 lambda 或嵌套函数），否则 multiprocessing 无法 pickle 序列化。

    Args:
        item: (doc_id, text_content) 元组

    Returns:
        (doc_id, keywords_list, index_dict) 三元组
    """
    doc_id, text = item

    # --- 关键词提取 ---
    # TextRank：基于图排序的关键词提取，取 top50 名词
    textrank_n_voc = set(
        jieba.analyse.textrank(text, topK=50, withWeight=False, allowPOS=('n',))
    )
    # TF-IDF：基于词频-逆文档频率的关键词提取，取 top5000 名词
    tfidf_n_voc = set(
        jieba.analyse.extract_tags(text, topK=5000, withWeight=False, allowPOS=('n',))
    )
    # 取交集：同时被两种算法认可的词作为最终关键词
    voc = list(textrank_n_voc & tfidf_n_voc)

    # --- 构建 词 -> 位置列表 的倒排索引 ---
    index_dict = dict()
    for tk in jieba.tokenize(text):
        # tk = (词, 起始位置, 结束位置)
        if tk[0] in index_dict:
            index_dict[tk[0]].append([tk[1], tk[2]])
        else:
            index_dict[tk[0]] = [[tk[1], tk[2]]]

    # 只保留关键词对应的位置信息，减少内存占用
    doc_idx = {word: index_dict[word] for word in voc if word in index_dict}

    return doc_id, voc, doc_idx


def text_parser(
        data: Dict[str, str],
        num_workers: int = 4
) -> tuple[Dict[str, List[str]], Dict[str, Any]]:
    """
    使用 multiprocessing.Pool 数据并行处理所有文档。
    每个文档的处理完全独立，天然适合并行化。

    与原版区别：
    - 去掉了 jieba.enable_parallel()，避免与外层多进程嵌套导致 fork 问题和性能下降
    - 改为外层按文档粒度并行，每个 worker 独立处理一个完整文档

    Args:
        data: {文档路径: 文本内容} 字典
        num_workers: 并行工作进程数

    Returns:
        (result, idx) 二元组
        - result: {doc_id: [关键词列表]}
        - idx:    {doc_id: {词: [[起始, 结束], ...]}}
    """
    result = dict()
    idx = dict()

    # 将 (doc_id, text) 对列表传入进程池
    # pool.map 自动将任务均匀分配给各 worker，收集返回结果
    with mp.Pool(processes=num_workers) as pool:
        for doc_id, voc, doc_idx in pool.map(process_single_doc, data.items()):
            result[doc_id] = voc
            idx[doc_id] = doc_idx

    return result, idx


def load_data(
        file_path: List[str]
) -> Dict[str, str]:
    """顺序读取所有文本文件到内存（I/O bound，收益有限，保持简单）"""
    data = dict()
    for file in file_path:
        with open(file, "r", encoding="utf-8") as f:
            data[file] = f.read()
    return data

def edge_generate(
        idx:Dict[str, Any],
        file_name:str
)->Dict[str, List[Any]]:
    with open(file_name,"r",encoding="utf-8") as f:
        text=f.read()
        words=list(idx.keys())
        for word in words:
            start,end=idx[word]
            start=max(0,start-60)
            
    return edge 



if __name__ == "__main__":
    # spawn 方式启动子进程，避免 fork 带来的 jieba 全局状态继承问题
    import time
    mp.set_start_method("spawn")

    args = parse_args()

    # 收集所有 .txt 文件路径
    file_path = Path(args.path)
    file_path = list(file_path.glob("*.txt"))
    file_path = [os.path.join(args.path, i.name) for i in file_path]

    # 加载数据
    data = load_data(file_path)


    t0=time.time()
    # 数据并行处理：按文档粒度分配给多个进程
    print(f"使用 {args.workers} 个进程并行处理 {len(data)} 个文档...")
    result, idx = text_parser(data, num_workers=args.workers)
    print(f"Time Cost:{time.time()-t0:.2f}s.")

    # 合并关键词结果和索引结果，写入 JSON
    text = {**result, **idx}
    with open(args.output_path, "w", encoding="utf-8") as f:
        json.dump(text, f,indent=4,ensure_ascii=False)

    print("Stage one text entity extraction finish!")
