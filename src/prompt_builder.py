"""
プロンプト構築モジュール
過去のメールデータから学習用プロンプトを生成
"""

from typing import List, Dict, Any


class PromptBuilder:
    """プロンプトを構築するクラス"""
    
    @staticmethod
    def build_classification_prompt(
        historical_emails: List[Dict[str, Any]],
        new_email: Dict[str, Any],
        max_examples: int = 5
    ) -> str:
        """
        メール分類用のプロンプトを構築
        
        Args:
            historical_emails: 過去のメールデータ（スター情報付き）
            new_email: 判定対象の新着メール
            max_examples: プロンプトに含める例の最大数
            
        Returns:
            構築されたプロンプト文字列
        """
        # スター付きとスターなしの例を取得
        starred_examples = [e for e in historical_emails if e.get('starred', False)]
        unstarred_examples = [e for e in historical_emails if not e.get('starred', False)]
        
        # バランスよく例を選択
        num_starred = min(len(starred_examples), max_examples // 2 + 1)
        num_unstarred = min(len(unstarred_examples), max_examples - num_starred)
        
        selected_starred = starred_examples[:num_starred]
        selected_unstarred = unstarred_examples[:num_unstarred]
        
        # プロンプトを構築
        prompt = """あなたはメール管理のエキスパートです。過去のメールの傾向を学習し、新着メールに「スター（重要マーク）」をつけるべきかを判定してください。

## 過去のメールの傾向

### スターをつけたメール（重要なメール）:
"""
        
        for i, email in enumerate(selected_starred, 1):
            prompt += f"""
{i}. 件名: {email.get('subject', 'N/A')}
   送信者: {email.get('sender', 'N/A')}
   本文: {email.get('body', 'N/A')[:100]}...
"""
        
        prompt += """
### スターをつけなかったメール（通常のメール）:
"""
        
        for i, email in enumerate(selected_unstarred, 1):
            prompt += f"""
{i}. 件名: {email.get('subject', 'N/A')}
   送信者: {email.get('sender', 'N/A')}
   本文: {email.get('body', 'N/A')[:100]}...
"""
        
        prompt += f"""
## 判定対象の新着メール

件名: {new_email.get('subject', 'N/A')}
送信者: {new_email.get('sender', 'N/A')}
本文: {new_email.get('body', 'N/A')}

## 指示

上記の過去のメール傾向を参考に、この新着メールに「スター」をつけるべきかを判定してください。

以下の形式で回答してください：

**判定結果**: [スターをつける / スターをつけない]

**理由**:
- 理由1: [具体的な理由]
- 理由2: [具体的な理由]
- 理由3: [具体的な理由]

**信頼度**: [高 / 中 / 低]

判定の際は、以下の観点を考慮してください：
- 送信者の重要性（上司、クライアント、システムアラートなど）
- 件名のキーワード（緊急、重要、至急、確認依頼など）
- 本文の内容（アクションが必要か、情報共有のみか）
- 過去の類似メールへのスター付与パターン
"""
        
        return prompt
    
    @staticmethod
    def build_simple_prompt(new_email: Dict[str, Any]) -> str:
        """
        シンプルな判定プロンプト（過去データなし）
        
        Args:
            new_email: 判定対象のメール
            
        Returns:
            構築されたプロンプト文字列
        """
        prompt = f"""以下のメールに「スター（重要マーク）」をつけるべきかを判定してください。

件名: {new_email.get('subject', 'N/A')}
送信者: {new_email.get('sender', 'N/A')}
本文: {new_email.get('body', 'N/A')}

以下の形式で回答してください：

**判定結果**: [スターをつける / スターをつけない]

**理由**:
- 理由1: [具体的な理由]
- 理由2: [具体的な理由]

**信頼度**: [高 / 中 / 低]
"""
        return prompt

# Made with Bob
