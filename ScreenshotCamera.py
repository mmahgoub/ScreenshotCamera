import sys
import signal
import time
from urllib.parse import urlparse
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
import pymysql.cursors


class ScreenshotCamera(QWebView):

    def __init__(self, urls, showWindow=False, timeout=30, folder=None):
        self.app = QApplication(sys.argv)
        self.counter = 1
        self.totalcount = len(urls)
        self.timeout = timeout
        self.showWindow = showWindow
        self.folder = folder
        QWebView.__init__(self)
        self.loadFinished.connect(self._loadFinished)
        self.urls = urls
        self.crawl()
        self.app.exec_()

    def crawl(self):
        if self.urls:
            url = self.urls.pop(0)
            self.timeout_timer = QTimer()
            self.timeout_timer.timeout.connect(self._request_timed_out)
            self.timeout_timer.start(self.timeout * 1000)
            print('[{a} of {b}]'.format(
                a=self.counter, b=self.totalcount), url)
            self.load(QUrl(url))
            self.counter = self.counter + 1
            if self.showWindow:
                self.show()
        else:
            self.app.quit()

    def _request_timed_out(self):
        self._error = 'Custom request timeout value exceeded.'
        self.timeout_timer.stop()
        self.stop()
        self.loadFinished.emit(False)

    def _loadFinished(self, result):
        if result:
            frame = self.page().mainFrame()
            url = str(frame.url().toString())
            self.page().setViewportSize(frame.contentsSize())
            image = QImage(self.page().viewportSize(), QImage.Format_ARGB32)
            painter = QPainter(image)
            frame.render(painter)
            painter.end()
            if self.folder:
                imgname = '{b}/{a}.png'.format(
                    a=urlparse(url).hostname, b=self.folder)
            else:
                imgname = '{a}.png'.format(a=urlparse(url).hostname)
            print('saving', imgname)
            image.save(imgname)
            image.detach()
        else:
            print("Page not loaded!")
        self.page().setViewportSize(QSize(1024, 600))
        self.crawl()
