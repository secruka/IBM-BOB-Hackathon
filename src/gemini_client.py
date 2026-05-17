"""
Gemini APIクライアントモジュール
Google Gemini APIとの通信を管理
"""

import os
from typing import Dict, Any, Optional
from google import genai
from dotenv import load_dotenv


class GeminiClient:
    """Gemini APIクライアントクラス"""
    
    def __init__(self, api_key: Optional[str] = None, model_id: str = "gemini-2.0-flash-exp"):
        """
        初期化
        
        Args:
            api_key: Gemini APIキー（Noneの場合は環境変数から取得）
            model_id: 使用するモデルID
        """
        # 環境変数を読み込み
        load_dotenv()
        
        # APIキーの設定
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEYが設定されていません。.envファイルを確認してください。")
        
        self.model_id = model_id
        
        # Geminiクライアントの初期化
        self.client = genai.Client(api_key=self.api_key)
        
        print(f"✓ Gemini APIクライアントを初期化しました（モデル: {self.model_id}）")
    
    def generate_content(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1000,
        top_p: float = 0.95
    ) -> str:
        """
        プロンプトからコンテンツを生成
        
        Args:
            prompt: 入力プロンプト
            temperature: 生成の多様性（0.0-1.0、低いほど決定的）
            max_tokens: 最大トークン数
            top_p: Top-pサンプリング値
            
        Returns:
            生成されたテキスト
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config={
                    'temperature': temperature,
                    'max_output_tokens': max_tokens,
                    'top_p': top_p,
                }
            )
            
            return response.text
            
        except Exception as e:
            print(f"✗ Gemini API呼び出しエラー: {e}")
            raise
    
    def classify_email(
        self,
        prompt: str,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        メール分類用の特化メソッド
        
        Args:
            prompt: 分類用プロンプト
            temperature: 生成の多様性
            
        Returns:
            分類結果を含む辞書
        """
        try:
            # APIを呼び出し
            response_text = self.generate_content(
                prompt=prompt,
                temperature=temperature,
                max_tokens=1000
            )
            
            # レスポンスをパース
            result = self._parse_classification_response(response_text)
            result['raw_response'] = response_text
            
            return result
            
        except Exception as e:
            print(f"✗ メール分類エラー: {e}")
            return {
                'should_star': False,
                'confidence': '不明',
                'reasons': [f'エラーが発生しました: {str(e)}'],
                'raw_response': '',
                'error': str(e)
            }
    
    def _parse_classification_response(self, response_text: str) -> Dict[str, Any]:
        """
        分類レスポンスをパース
        
        Args:
            response_text: APIからのレスポンステキスト
            
        Returns:
            パースされた結果の辞書
        """
        # デフォルト値
        result = {
            'should_star': False,
            'confidence': '中',
            'reasons': []
        }
        
        # 判定結果を抽出
        if 'スターをつける' in response_text and 'スターをつけない' not in response_text.split('判定結果')[1].split('\n')[0]:
            result['should_star'] = True
        
        # 理由を抽出
        if '理由' in response_text:
            lines = response_text.split('\n')
            for line in lines:
                if line.strip().startswith('-') or line.strip().startswith('•'):
                    reason = line.strip().lstrip('-•').strip()
                    if reason and '理由' not in reason:
                        result['reasons'].append(reason)
        
        # 信頼度を抽出
        if '信頼度' in response_text:
            if '高' in response_text.split('信頼度')[1].split('\n')[0]:
                result['confidence'] = '高'
            elif '低' in response_text.split('信頼度')[1].split('\n')[0]:
                result['confidence'] = '低'
            else:
                result['confidence'] = '中'
        
        return result
    
    def test_connection(self) -> bool:
        """
        API接続をテスト
        
        Returns:
            接続成功の場合True
        """
        try:
            response = self.generate_content(
                prompt="こんにちは。簡単に挨拶を返してください。",
                temperature=0.1,
                max_tokens=50
            )
            print(f"✓ API接続テスト成功: {response[:50]}...")
            return True
        except Exception as e:
            print(f"✗ API接続テスト失敗: {e}")
            return False

# Made with Bob
