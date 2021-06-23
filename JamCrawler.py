import sys
from PySide6 import QtCore, QtWidgets, QtGui
from bs4 import BeautifulSoup as BS
import requests

class AsyncCrawl(QtCore.QThread):
    # Sinais para retornar para a thread principal
    logSignal = QtCore.Signal(str)
    contentSignal = QtCore.Signal(str)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def setURL(self, url):
        self.url = url

    def run(self):

        self.logSignal.emit("STATUS::Starting the crawling")
        req = requests.get(self.url)
        soup = BS(req.text, "html.parser")

        entries = soup.select(".game_cell")
       
        for game in entries:
            gameLink = game.select_one(".label > .title")
            self.contentSignal.emit(f'# {gameLink.text}\n')

            entryPageUrl = gameLink.get("href")

            entryPage = requests.get(entryPageUrl)
            self.logSignal.emit("STATUS::folowing "+entryPageUrl)
            entryPageBS = BS(entryPage.text, "html.parser")
            gameUrl = entryPageBS.select_one('[name="twitter:url"]')
            gameUrl = gameUrl.get("content")
            try:
                imgUrl = entryPageBS.select_one('[property="og:image"]').get("content")
            except:
                imgUrl = ""

            self.contentSignal.emit(f'\
[![{gameLink.text}]({imgUrl})]({gameUrl})\n\n')
        


class Window(QtWidgets.QWidget):

    urlSignal = QtCore.Signal(str)

    def __init__(self):
        super().__init__();

        self.mainLayout = QtWidgets.QHBoxLayout(self);

        self.setWindowTitle("Jam Crawler");

        self.input1 = QtWidgets.QLineEdit("URL da Jam")
        self.button1 = QtWidgets.QPushButton("Gerar Postagem")
        self.button1.clicked.connect(self.GeneratePost)

        self.editor = QtWidgets.QPlainTextEdit("Wolala")
        self.log = QtWidgets.QPlainTextEdit("LOG:")
        self.log.setReadOnly(True)

        self.leftMenu = QtWidgets.QVBoxLayout(self)

        self.leftMenu.addWidget(self.input1)
        self.leftMenu.addWidget(self.button1)
        self.leftMenu.addWidget(self.log)

        self.mainLayout.addLayout(self.leftMenu)
        self.mainLayout.addWidget(self.editor)


    @QtCore.Slot()
    def GeneratePost(self):
        self.editor.clear()
        self.Crawler = AsyncCrawl()
        self.urlSignal.connect(self.Crawler.setURL)
        self.urlSignal.emit(self.input1.text())

        self.Crawler.logSignal.connect(self.WriteLog)
        self.Crawler.contentSignal.connect(self.WriteContent)

        self.Crawler.start()
        



    def WriteLog(self, log):
        self.log.appendPlainText(log)

    def WriteContent(self, content):
        self.editor.appendPlainText(content)

if __name__ == "__main__":

    app = QtWidgets.QApplication([])

    widget = Window()
    widget.resize(600, 400)
    widget.show()
    
    sys.exit(app.exec())
