"""
データローダーモジュール
メールデータ（JSON/CSV）を読み込む機能を提供
"""

import json
from typing import List, Dict, Any
from pathlib import Path


class EmailDataLoader:
    """メールデータを読み込むクラス"""
    
    @staticmethod
    def load_json(file_path: str) -> List[Dict[str, Any]]:
        """
        JSONファイルからメールデータを読み込む
        
        Args:
            file_path: JSONファイルのパス
            
        Returns:
            メールデータのリスト
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ {len(data)}件のメールデータを読み込みました: {file_path}")
            return data
        except FileNotFoundError:
            print(f"✗ ファイルが見つかりません: {file_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"✗ JSON解析エラー: {e}")
            return []
    
    @staticmethod
    def load_csv(file_path: str) -> List[Dict[str, Any]]:
        """
        CSVファイルからメールデータを読み込む
        
        Args:
            file_path: CSVファイルのパス
            
        Returns:
            メールデータのリスト
        """
        try:
            import csv
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            print(f"✓ {len(data)}件のメールデータを読み込みました: {file_path}")
            return data
        except FileNotFoundError:
            print(f"✗ ファイルが見つかりません: {file_path}")
            return []
        except Exception as e:
            print(f"✗ CSV読み込みエラー: {e}")
            return []
    
    @staticmethod
    def filter_starred_emails(emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        スター付きメールのみを抽出
        
        Args:
            emails: メールデータのリスト
            
        Returns:
            スター付きメールのリスト
        """
        starred = [email for email in emails if email.get('starred', False)]
        print(f"✓ スター付きメール: {len(starred)}件 / 全体: {len(emails)}件")
        return starred
    
    @staticmethod
    def filter_unstarred_emails(emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        スターなしメールのみを抽出
        
        Args:
            emails: メールデータのリスト
            
        Returns:
            スターなしメールのリスト
        """
        unstarred = [email for email in emails if not email.get('starred', False)]
        print(f"✓ スターなしメール: {len(unstarred)}件 / 全体: {len(emails)}件")
        return unstarred
    
    @staticmethod
    def get_email_summary(emails: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        メールデータの統計情報を取得
        
        Args:
            emails: メールデータのリスト
            
        Returns:
            統計情報の辞書
        """
        total = len(emails)
        starred = len([e for e in emails if e.get('starred', False)])
        unstarred = total - starred
        
        return {
            'total': total,
            'starred': starred,
            'unstarred': unstarred,
            'star_rate': round(starred / total * 100, 1) if total > 0 else 0
        }

# Made with Bob
