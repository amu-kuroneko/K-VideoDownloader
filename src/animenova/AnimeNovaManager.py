# --- coding: utf-8 ---
"""
AnimeNova から動画をダウンロードするためのクラスモジュール
"""

from urllib import request
from urllib import parse
import os
import re
import threading

class AnimeNovaManager(threading.Thread):
    """
    AnimeNova から動画をダウンロードするクラス
    """

    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
    """
    普通にアクセスすると 403 になるので偽装する UserAgent
    """
    
    VIDEO_URL_PATTERN = [
        r"file:\s+\"(http[^\"]+)\",",
        r"src:\s+\"(http[^\"]+)\","
    ]

    def __init__(self, target, output_path=''):
        """
        AnimeNova の操作を行うためのコンストラクタ
        @param path ダウンロードした動画ファイルを出力するパス
        """
        super(AnimeNovaManager, self).__init__()

        self.target = None
        """
        ダウンロード対象の URL
        """
        self.directory = None
        """
        ファイルを出力するディレクトリ
        """
        self.filename = None
        """
        出力するファイル名
        """

        self.setTarget(target)
        self.setOutputPath(output_path)
        return

    def setTarget(self, target):
        """
        ダウンロードの対象となる URL を設定する
        @param target ダウンロード対象 URL
        """
        self.target = target
        return

    def setOutputPath(self, output_path):
        """
        ファイルを出力するパスを設定する
        @param output_path ファイルを出力するパス
        """
        if len(output_path) == 0 or output_path[0] != '~':
            path = os.path.abspath(output_path)
        else:
            path = os.path.expanduser(output_path)

        if os.path.isdir(path) or output_path[-1] == '/':
            self.directory = path
        else:
            self.directory = os.path.dirname(path)
            self.filename = os.path.basename(path)
        return

    def makeDirectory(self, directory):
        """
        ディレクトリの存在を確認して、ない場合はそのディレクトリを作成する
        @param directory 作成さうるディレクトリのパス
        @return ディレクトリ作成成功時、もしくは作成不要時に True を、失敗時に False を返す
        """
        if not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except OSError as exception:
                print('ディレクトリの作成に失敗しました(%s)' % directory)
                return False
        return True

    def getFilename(self, url):
        """
        URL からファイル名を取得する
        @param url ファイル名を取得するための URL
        @return URL のパスから抽出したファイル名
        """
        path = parse.urlparse(url).path.rstrip('/')
        if len(path) != 0:
            return os.path.basename(path)
        else:
            if os.path.exist('%s/undefined' % self.directory):
                number = 0
                while True:
                    if not os.path.exist('%s/undefined_%d' % (self.directory, number)):
                        return 'undefined_%d' % number
            else:
                return 'undefined'

    def download(self, url, path):
        """
        指定された URL からダウンロードする
        @param url ダウンロードする URL
        @param path ダウンロードしたファイルを設置するパス
        @return 成功時に True を、失敗時に False を返す
        """
        try:
            print("Downloading from %s" % url)
            request.urlretrieve(url, path + '.downloading')
            os.rename(path + '.downloading', path)
            print("Downloaded to %s" % path)
        except:
            print('ダウンロードに失敗しました')
            return False
        return True

    def run(self):
        """
        動画のダウンロードを開始する
        @param url AnimeNova の URL
        """
        if not self.makeDirectory(self.directory):
            return
        iframe_sources = self.getIframeSources(self.target)
        if not iframe_sources:
            return
        for source in iframe_sources:
            url = self.getVideoUrl(source)
            if not self.filename:
                self.filename = self.getFilename(url)
            if self.download(url, "%s/%s" % (self.directory, self.filename)):
                break
        return

    def getIframeSources(self, url):
        """
        AnimeNova のページから iframe の src を取得する
        @param url AnimeNova の URL
        @return iframe の source リストを返す
            失敗時にも空のリストを返す
        """
        response = request.urlopen(
            request.Request(url, data=None, headers={'User-Agent': self.USER_AGENT}))
        if response.getcode() != 200:
            print('AnimeNova へのアクセスに失敗しました (%d)' % response.getcode())
            return []
        html = str(response.read())
        matches = re.findall(r"<iframe\s[^>]*src=\"([^\"]+)\"", html)
        if len(matches) == 0:
            print('AnimeNova の iframe を取得できませんでした')
            return []
        return [source for source in matches if source.startswith('http')]

    def getVideoUrl(self, url):
        """
        AnimeNova の iframe 先のサイトから動画の URL を抽出する
        @param url AnimeNova の iframe 先のサイトの URL
        @return 成功時に動画の URL を、失敗時に None を返す
        """
        response = request.urlopen(
            request.Request(url, data=None, headers={'User-Agent': self.USER_AGENT}))
        if response.getcode() != 200:
            print('AnimeNova の iframe へのアクセスに失敗しました (%d)' % response.getcode())
            return None
        html = str(response.read())
        for pattern in self.VIDEO_URL_PATTERN:
            matches = re.findall(pattern, html)
            if len(matches) != 0:
                return matches[0]
        print('動画ファイルの URL の取得に失敗しました')
        return None

