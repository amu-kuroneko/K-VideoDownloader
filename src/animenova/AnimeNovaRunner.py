# --- coding: utf-8 ---
"""
AnimeNova の実行クラスモジュール
"""

import time
from AbstractRunner import AbstractRunner
from animenova.AnimeNovaManager import AnimeNovaManager

class AnimeNovaRunner(AbstractRunner):
    """
    AnimeNova の実行クラス
    """

    domainPattern = 'www\.animenova\.org'
    """
    サポートするドメイン
    """

    patterns = ['.+']
    """
    サポートする AnimeNova のパスの正規表現のパターンリスト
    """

    def run(self):
        """
        AnimeNova の実行
        """
        destination = input('Output Path > ')
        manager = AnimeNovaManager(self.url, destination)
        manager.start()
        time.sleep(1)
        return

