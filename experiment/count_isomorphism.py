#!/usr/bin/env python3
"""
JSONファイルの同型性を分析するCLIツール

指定したディレクトリ内のすべてのJSONファイルを解析し、
同型（内容が同じ）なファイルをグループ化して報告します。
"""

import argparse
import json
import pathlib
import re
from collections import Counter, defaultdict
from typing import Optional


def normalize_json(data) -> str:
    """
    JSON データを正規化された文字列表現に変換
    
    数値の表現ゆれ（0.0 vs 0など）を統一するため、
    先にデータを再帰的に正規化してからダンプします
    
    Args:
        data: 正規化する JSON データ
        
    Returns:
        JSON の正規化された文字列表現
    """
    def normalize_value(obj):
        """値を再帰的に正規化"""
        if isinstance(obj, dict):
            return {k: normalize_value(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [normalize_value(item) for item in obj]
        elif isinstance(obj, float):
            # 浮動小数点数を正規化
            # 整数値の浮動小数点（0.0, 1.0など）は整数に変換
            if obj == int(obj):
                return int(obj)
            return obj
        else:
            return obj
    
    normalized_obj = normalize_value(data)
    return json.dumps(normalized_obj, sort_keys=True, ensure_ascii=False)


def extract_task_number(dir_name: str) -> Optional[int]:
    """
    ディレクトリ名からタスク番号を抽出
    
    例: "task_01" -> 1, "task_01_repeat02" -> 1
    
    Args:
        dir_name: ディレクトリ名
        
    Returns:
        タスク番号、またはマッチしない場合は None
    """
    match = re.match(r"task_(\d+)(?:_repeat\d+)?", dir_name)
    if match:
        return int(match.group(1))
    return None


def group_directories_by_task(directory: pathlib.Path) -> dict:
    """
    ディレクトリをタスク単位でグループ化
    
    Args:
        directory: 分析対象のトップレベルディレクトリ
        
    Returns:
        タスク番号 -> [ディレクトリパスのリスト] のマッピング
    """
    task_groups = defaultdict(list)
    
    # task_* パターンのディレクトリを検索
    for item in sorted(directory.iterdir()):
        if item.is_dir():
            task_num = extract_task_number(item.name)
            if task_num is not None:
                task_groups[task_num].append(item)
    
    return dict(sorted(task_groups.items()))


def analyze_task_jsons(
    task_dirs: list[pathlib.Path],
    json_filename: str = "BehaviorTree.json"
) -> dict:
    """
    複数のディレクトリ（タスク内のリピート）から JSON ファイルの同型性を分析
    
    Args:
        task_dirs: タスク関連のディレクトリリスト（タスク01, 01_repeat02, など）
        json_filename: 検索する JSON ファイル名
        
    Returns:
        分析結果を含む辞書
    """
    # JSON ファイルを収集
    json_files_info = []  # (file_path, dir_name) のタプル
    invalid_files = []
    
    for task_dir in sorted(task_dirs):
        json_path = task_dir / json_filename
        if json_path.exists():
            json_files_info.append((json_path, task_dir.name))
        else:
            invalid_files.append(task_dir.name)
    
    if not json_files_info:
        return {
            "total_dirs": len(task_dirs),
            "found_files": 0,
            "missing_dirs": invalid_files,
            "unique_count": 0,
            "groups": []
        }
    
    # 各ファイルを正規化して収集
    normalized_map = {}  # normalized_json -> list of (file_path, dir_name)
    failed_files = []
    
    for json_path, dir_name in json_files_info:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                normalized = normalize_json(data)
                
                if normalized not in normalized_map:
                    normalized_map[normalized] = []
                normalized_map[normalized].append((json_path, dir_name))
        except Exception as e:
            failed_files.append((dir_name, str(e)))
    
    # 結果を集計
    groups = []
    for normalized, files_info in normalized_map.items():
        groups.append({
            "count": len(files_info),
            "files_info": files_info,  # (path, dir_name) のタプルリスト
            "dir_names": [dir_name for _, dir_name in files_info]
        })
    
    # カウントの多い順にソート
    groups.sort(key=lambda x: x["count"], reverse=True)
    
    return {
        "total_dirs": len(task_dirs),
        "found_files": len(json_files_info),
        "missing_dirs": invalid_files,
        "failed_files": failed_files,
        "unique_count": len(groups),
        "groups": groups
    }


def analyze_directory(
    directory: pathlib.Path,
    pattern: str = "*.json",
    recursive: bool = True
) -> dict:
    """
    ディレクトリ内の JSON ファイルの同型性を分析
    
    Args:
        directory: 分析対象のディレクトリ
        pattern: JSON ファイルのパターン（デフォルト: "*.json"）
        recursive: サブディレクトリも検索するか（デフォルト: True）
        
    Returns:
        分析結果を含む辞書
    """
    if not directory.exists() or not directory.is_dir():
        raise ValueError(f"ディレクトリが存在しません: {directory}")
    
    # JSON ファイルを収集
    if recursive:
        json_files = list(directory.rglob(pattern))
    else:
        json_files = list(directory.glob(pattern))
    
    if not json_files:
        return {
            "total_files": 0,
            "valid_files": 0,
            "unique_count": 0,
            "groups": []
        }
    
    # 各ファイルを正規化して収集
    normalized_map = {}  # normalized_json -> list of file paths
    invalid_files = []
    
    for json_file in sorted(json_files):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                normalized = normalize_json(data)
                
                if normalized not in normalized_map:
                    normalized_map[normalized] = []
                normalized_map[normalized].append(json_file)
        except Exception as e:
            invalid_files.append((json_file, str(e)))
    
    # 結果を集計
    groups = []
    for normalized, files in normalized_map.items():
        groups.append({
            "count": len(files),
            "first_file": files[0],
            "all_files": files
        })
    
    # カウントの多い順にソート
    groups.sort(key=lambda x: x["count"], reverse=True)
    
    return {
        "total_files": len(json_files),
        "valid_files": sum(g["count"] for g in groups),
        "invalid_files": invalid_files,
        "unique_count": len(groups),
        "groups": groups
    }


def print_task_analysis_results(results_by_task: dict, directory: pathlib.Path, verbose: bool = False):
    """
    タスク単位の分析結果を CLI に出力
    
    Args:
        results_by_task: タスク番号 -> 分析結果 のマッピング
        directory: 分析したトップレベルディレクトリ
        verbose: 詳細情報を表示するか
    """
    print(f"\n{'='*70}")
    print(f"Task-based JSON Isomorphism Analysis")
    print(f"Directory: {directory}")
    print(f"{'='*70}")
    
    for task_num in sorted(results_by_task.keys()):
        results = results_by_task[task_num]
        
        print(f"\n{'─'*70}")
        print(f"Task {task_num}: Unique JSON Patterns")
        print(f"{'─'*70}")
        
        print(f"Total directories: {results['total_dirs']}")
        print(f"Found JSON files: {results['found_files']}")
        
        if results['missing_dirs']:
            print(f"Missing JSON files in: {', '.join(results['missing_dirs'])}")
        
        if 'failed_files' in results and results['failed_files']:
            print(f"Failed to read:")
            for dir_name, error in results['failed_files']:
                print(f"  - {dir_name}: {error}")
        
        if results['unique_count'] == 0:
            print("No valid JSON files found for this task.")
            continue
        
        print(f"Unique patterns: {results['unique_count']}")
        
        for pattern_idx, group in enumerate(results['groups'], 1):
            print(f"\n  Pattern {pattern_idx}: {group['count']} occurrence(s)")
            
            # 最初のファイルのディレクトリ名を表示
            first_dir = group['dir_names'][0]
            print(f"    First file: {first_dir}/BehaviorTree.json")
            
            # 全ファイルを表示
            if verbose or len(group['dir_names']) <= 5:
                for dir_name in group['dir_names']:
                    print(f"      - {dir_name}")
            else:
                # 簡潔表示
                for dir_name in group['dir_names'][:3]:
                    print(f"      - {dir_name}")
                print(f"      ... ({len(group['dir_names']) - 3} more)")
    
    print(f"\n{'='*70}")


def print_analysis_results(results: dict, directory: pathlib.Path, verbose: bool = False):
    """
    分析結果を CLI に出力
    
    Args:
        results: analyze_directory() の戻り値
        directory: 分析したディレクトリ
        verbose: 詳細情報を表示するか
    """
    print(f"\n{'='*70}")
    print(f"JSON Isomorphism Analysis: {directory}")
    print(f"{'='*70}")
    
    print(f"\nTotal JSON files found: {results['total_files']}")
    print(f"Valid JSON files: {results['valid_files']}")
    print(f"Invalid/Unreadable files: {len(results['invalid_files'])}")
    print(f"Unique JSON patterns: {results['unique_count']}")
    
    if results['invalid_files']:
        print(f"\nInvalid files:")
        for filepath, error in results['invalid_files']:
            print(f"  - {filepath.name}: {error}")
    
    if results['unique_count'] == 0:
        print("\nNo valid JSON files found.")
        return
    
    print(f"\n{'='*70}")
    print("Unique JSON Patterns:")
    print(f"{'='*70}")
    
    for idx, group in enumerate(results['groups'], 1):
        print(f"\nPattern {idx}: {group['count']} file(s)")
        print(f"  First file: {group['first_file'].relative_to(directory)}")
        
        if verbose and len(group['all_files']) > 1:
            print(f"  All files:")
            for filepath in group['all_files']:
                print(f"    - {filepath.relative_to(directory)}")
    
    print(f"\n{'='*70}")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="JSONファイルの同型性を分析します",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # タスク単位での分析（デフォルト）
  python count_isomorphism.py results/experiment_001
  
  # 詳細表示（すべてのファイルを列挙）
  python count_isomorphism.py results/experiment_001 --verbose
  
  # 全ファイルに対する従来の分析
  python count_isomorphism.py results/experiment_001 --no-task-mode
        """
    )
    
    parser.add_argument(
        "directory",
        type=pathlib.Path,
        help="分析対象のディレクトリ"
    )
    
    parser.add_argument(
        "--no-task-mode",
        action="store_true",
        help="タスク単位での分析を行わず、全ファイルを分析"
    )
    
    parser.add_argument(
        "--json-file",
        type=str,
        default="BehaviorTree.json",
        help="分析対象の JSON ファイル名（デフォルト: BehaviorTree.json）"
    )
    
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.json",
        help="全ファイル分析時の検索パターン（デフォルト: *.json）"
    )
    
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="サブディレクトリを検索しない"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="詳細情報を表示"
    )
    
    args = parser.parse_args()
    
    try:
        if args.no_task_mode:
            # 従来の全ファイル分析モード
            results = analyze_directory(
                args.directory,
                pattern=args.pattern,
                recursive=not args.no_recursive
            )
            print_analysis_results(results, args.directory, verbose=args.verbose)
        else:
            # タスク単位での分析モード（デフォルト）
            task_groups = group_directories_by_task(args.directory)
            
            if not task_groups:
                print(f"No task directories found in {args.directory}")
                return 1
            
            results_by_task = {}
            for task_num, task_dirs in task_groups.items():
                results_by_task[task_num] = analyze_task_jsons(
                    task_dirs,
                    json_filename=args.json_file
                )
            
            print_task_analysis_results(results_by_task, args.directory, verbose=args.verbose)
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
