"""
メール分類器モジュール
メールのスター付け判定を行うメインロジック
"""

from typing import List, Dict, Any
from .data_loader import EmailDataLoader
from .prompt_builder import PromptBuilder
from .gemini_client import GeminiClient


class EmailClassifier:
    """メール分類器クラス"""
    
    def __init__(self, gemini_client: GeminiClient):
        """
        初期化
        
        Args:
            gemini_client: Gemini APIクライアント
        """
        self.gemini_client = gemini_client
        self.data_loader = EmailDataLoader()
        self.prompt_builder = PromptBuilder()
    
    def classify_single_email(
        self,
        new_email: Dict[str, Any],
        historical_emails: List[Dict[str, Any]],
        use_history: bool = True,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        単一のメールを分類
        
        Args:
            new_email: 判定対象のメール
            historical_emails: 過去のメールデータ
            use_history: 過去データを使用するか
            temperature: 生成の多様性
            
        Returns:
            分類結果
        """
        print(f"\n📧 メール分類開始: {new_email.get('subject', 'N/A')}")
        
        # プロンプトを構築
        if use_history and historical_emails:
            prompt = self.prompt_builder.build_classification_prompt(
                historical_emails=historical_emails,
                new_email=new_email,
                max_examples=5
            )
        else:
            prompt = self.prompt_builder.build_simple_prompt(new_email)
        
        # Gemini APIで分類
        result = self.gemini_client.classify_email(
            prompt=prompt,
            temperature=temperature
        )
        
        # メール情報を結果に追加
        result['email'] = {
            'id': new_email.get('id'),
            'subject': new_email.get('subject'),
            'sender': new_email.get('sender')
        }
        
        return result
    
    def classify_multiple_emails(
        self,
        new_emails: List[Dict[str, Any]],
        historical_emails: List[Dict[str, Any]],
        use_history: bool = True,
        temperature: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        複数のメールを分類
        
        Args:
            new_emails: 判定対象のメールリスト
            historical_emails: 過去のメールデータ
            use_history: 過去データを使用するか
            temperature: 生成の多様性
            
        Returns:
            分類結果のリスト
        """
        results = []
        
        print(f"\n🔄 {len(new_emails)}件のメールを分類します...")
        
        for i, email in enumerate(new_emails, 1):
            print(f"\n--- [{i}/{len(new_emails)}] ---")
            
            result = self.classify_single_email(
                new_email=email,
                historical_emails=historical_emails,
                use_history=use_history,
                temperature=temperature
            )
            
            results.append(result)
            
            # 結果を表示
            self._print_result(result)
        
        return results
    
    def _print_result(self, result: Dict[str, Any]) -> None:
        """
        分類結果を見やすく表示
        
        Args:
            result: 分類結果
        """
        email_info = result.get('email', {})
        should_star = result.get('should_star', False)
        confidence = result.get('confidence', '不明')
        reasons = result.get('reasons', [])
        
        print(f"\n📋 判定結果:")
        print(f"   件名: {email_info.get('subject', 'N/A')}")
        print(f"   送信者: {email_info.get('sender', 'N/A')}")
        print(f"   ⭐ スター: {'つける' if should_star else 'つけない'}")
        print(f"   🎯 信頼度: {confidence}")
        
        if reasons:
            print(f"   💡 理由:")
            for i, reason in enumerate(reasons, 1):
                print(f"      {i}. {reason}")
    
    def get_classification_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分類結果のサマリーを取得
        
        Args:
            results: 分類結果のリスト
            
        Returns:
            サマリー情報
        """
        total = len(results)
        starred = len([r for r in results if r.get('should_star', False)])
        unstarred = total - starred
        
        high_confidence = len([r for r in results if r.get('confidence') == '高'])
        medium_confidence = len([r for r in results if r.get('confidence') == '中'])
        low_confidence = len([r for r in results if r.get('confidence') == '低'])
        
        return {
            'total': total,
            'starred': starred,
            'unstarred': unstarred,
            'star_rate': round(starred / total * 100, 1) if total > 0 else 0,
            'confidence_distribution': {
                'high': high_confidence,
                'medium': medium_confidence,
                'low': low_confidence
            }
        }
    
    def print_summary(self, results: List[Dict[str, Any]]) -> None:
        """
        分類結果のサマリーを表示
        
        Args:
            results: 分類結果のリスト
        """
        summary = self.get_classification_summary(results)
        
        print("\n" + "="*60)
        print("📊 分類結果サマリー")
        print("="*60)
        print(f"総メール数: {summary['total']}件")
        print(f"スター付け: {summary['starred']}件 ({summary['star_rate']}%)")
        print(f"スターなし: {summary['unstarred']}件")
        print(f"\n信頼度分布:")
        print(f"  高: {summary['confidence_distribution']['high']}件")
        print(f"  中: {summary['confidence_distribution']['medium']}件")
        print(f"  低: {summary['confidence_distribution']['low']}件")
        print("="*60)

# Made with Bob
