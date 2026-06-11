import os
import argparse
import jieba

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--benchmark', type=str)
    parser.add_argument('--max_batch_size', type=int)
    parser.add_argument('--model_path', type=str)
    parser.add_argument('--top_p', type=float, default=0.9)
    parser.add_argument('--temperature', type=float, default=0.0)
    parser.add_argument('--block_size', type=int, default=2048) # tokens for one memory inference
    parser.add_argument('--max_chunk_per_block', type=int, default=16*1024) # chunks per block slice
    parser.add_argument('--max_length', type=int, default=64) # max output length
    parser.add_argument('--max_seq_len', type=int, default=0) # max input+output length
    parser.add_argument('--max_query_seq_len', type=int, default=0) # max input seq len
    parser.add_argument('--template', type=str, default="QWEN3_TEMPLATE")
    parser.add_argument('--output_file', type=str, default="")
    parser.add_argument('--case_name', type=str, default="anonymous")

    args = parser.parse_args()

    return args
