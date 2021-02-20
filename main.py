import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QPixmap, QImage, QTextCursor
from PyQt5.QtCore import pyqtSignal, QObject
import requests
from FitRequest import smsCode, login, search, submit, FIT_STORE
import time
import threading

url = "https://www.styd.cn/web/user/img_captcha"


class Stream(QObject):
    """Redirects console output to text widget."""
    newText = pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))


class MainUi(QWidget):
    def __init__(self):
        super().__init__()
        self.initGUI()
        self.cookieSubmit = None
        # 注掉这句就可以打印到控制台，方便调试
        sys.stdout = Stream(newText=self.onUpdateText)

        print("-------------------------------------")
        print("---------------使用须知---------------")
        print("提示: 在第一次使用该程序,需要联系作者帮忙查询菲特会员卡ID")
        print("提示: 预约抢号功能只能在所填日期48小时内进行抢号")
        print("提示: 单车号的座次请使用菲特公众号自行查询")
        print("在执行程序时,程序出现未响应为正常情况,因为没使用多线程所以该程序处于阻塞状态")
        print("使用预约功能该程序会进入阻塞状态, 当时间达到指定日期的前48小时后开始抢单车号")
        print("使用抢号功能程序会立即执行抢单车号任务!")
        print("-------------------------------------")
        print("-------------------------------------")

    def onUpdateText(self, text):
        """Write console output to text widget."""
        cursor = self.process.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.process.setTextCursor(cursor)
        self.process.ensureCursorVisible()

    def closeEvent(self, event):
        """Shuts down application on close."""
        # Return stdout to defaults.
        sys.stdout = sys.__stdout__
        super().closeEvent(event)

    def initGUI(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setWindowTitle("菲特自动预约单车课程序")
        self.resize(800, 600)
        self.center()

        self.btn = QPushButton('开始抢号', self)
        self.btn.move(400, 320)
        self.btn.resize(200, 80)
        self.btn.clicked.connect(self.OnBtnClicked)

        self.schedulebtn = QPushButton('开始预约', self)
        self.schedulebtn.move(200, 320)
        self.schedulebtn.resize(200, 80)
        self.schedulebtn.clicked.connect(self.schedule)

        # 控制台打印信息
        self.process = QTextEdit(self, readOnly=True)
        self.process.ensureCursorVisible()
        self.process.setLineWrapColumnOrWidth(500)
        self.process.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.process.setFixedWidth(800)
        self.process.setFixedHeight(200)
        self.process.move(0, 400)

        # 会员卡ID
        self.cardEdit = QLineEdit(self)
        self.cardEdit.resize(200, 40)
        self.cardEdit.setPlaceholderText("请输入会员卡ID")

        # 手机号输入框
        self.mobileEdit = QLineEdit(self)
        self.mobileEdit.resize(200, 40)
        self.mobileEdit.setPlaceholderText("请输入手机号")

        # 短信验证码输入框
        self.smscodeEdit = QLineEdit(self)
        self.smscodeEdit.resize(200, 40)
        self.smscodeEdit.setPlaceholderText("请输入短信验证码")

        # 日期输入框
        self.dateEdit = QLineEdit(self)
        self.dateEdit.resize(200, 40)
        self.dateEdit.setPlaceholderText("请输入日期, 格式为2020-02-01")

        self.numEdit = QLineEdit(self)
        self.numEdit.resize(120, 40)
        self.numEdit.setPlaceholderText("请输入单车号:1")

        # self.cardEdit.move(250, 60)
        # self.mobileEdit.move(250, 110)
        # self.dateEdit.move(250, 210)
        # self.smscodeEdit.move(250, 160)

        # 图形验证码输入框
        self.codeEdit = QLineEdit(self)
        self.codeEdit.resize(200, 40)
        self.codeEdit.setPlaceholderText("请输入图形验证码")

        # 图形验证码
        self.img = MyQLabel(self)
        self.flush()
        self.img.move(450, 133)
        self.img.connect_customized_slot(self.flush)

        self.smsbtn = QPushButton('获取验证码', self)
        self.smsbtn.resize(100, 45)
        self.smsbtn.clicked.connect(self.findSmsCode)

        self.cardEdit.move(250, 30)
        self.mobileEdit.move(250, 80)
        self.codeEdit.move(250, 130)
        self.smscodeEdit.move(250, 180)
        self.dateEdit.move(250, 230)
        self.numEdit.move(450, 230)
        self.smsbtn.move(450, 180)

        # 单选按钮
        layout = QHBoxLayout()  # 实例化一个布局
        self.btn1 = QRadioButton("洸河店")  # 实例化一个选择的按钮
        self.btn1.toggled.connect(lambda: self.btnstate(self.btn1))  # 绑定点击事件

        self.btn2 = QRadioButton("金菲特")
        self.btn2.toggled.connect(lambda: self.btnstate(self.btn2))

        self.btn3 = QRadioButton("万达店")
        self.btn3.toggled.connect(lambda: self.btnstate(self.btn3))

        self.btn4 = QRadioButton("新体店")
        self.btn4.toggled.connect(lambda: self.btnstate(self.btn4))

        self.btn5 = QRadioButton("济安桥店")
        self.btn5.toggled.connect(lambda: self.btnstate(self.btn5))

        self.btn6 = QRadioButton("龙行店")
        self.btn6.toggled.connect(lambda: self.btnstate(self.btn6))

        self.btn7 = QRadioButton("冠亚店")
        self.btn7.toggled.connect(lambda: self.btnstate(self.btn7))

        self.btn8 = QRadioButton("秀水店")
        self.btn8.toggled.connect(lambda: self.btnstate(self.btn8))

        self.btn9 = QRadioButton("古槐店")
        self.btn9.toggled.connect(lambda: self.btnstate(self.btn9))

        layout.addWidget(self.btn1)
        layout.addWidget(self.btn2)
        layout.addWidget(self.btn3)
        layout.addWidget(self.btn4)
        layout.addWidget(self.btn5)
        layout.addWidget(self.btn6)
        layout.addWidget(self.btn7)
        layout.addWidget(self.btn8)
        layout.addWidget(self.btn9)
        self.setLayout(layout)  # 界面添加 layout

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def flush(self):
        res = requests.get(url)
        img = QImage.fromData(res.content)
        self.img.setPixmap(QPixmap.fromImage(img))
        self.imgCookie = res.cookies

    def findSmsCode(self):
        mobile = self.mobileEdit.text()
        code = self.codeEdit.text()
        smsCode(self.imgCookie, mobile, code)
        self.flush()

    def schedule(self):
        date = self.dateEdit.text()
        datetime = time.mktime(time.strptime(str(date) + ' 09:00:00', '%Y-%m-%d %H:%M:%S'))
        now = time.time() + (48 * 3600)
        while True:
            if datetime < now:
                break
            print((time.time() - datetime) / 1000)
        self.OnBtnClicked()

    def OnBtnClicked(self):
        """Runs the main function."""
        mobile = self.mobileEdit.text()
        smscode = self.smscodeEdit.text()
        num = self.numEdit.text()
        date = self.dateEdit.text()
        if self.cookieSubmit == None:
            self.cookieSubmit = login(mobile, smscode)
        print("打印保存的cookie信息", self.cookieSubmit)
        id = search(self.cookieSubmit, self.store, date)
        flag = False
        count = 0
        while flag == False and count < 20:
            flag = submit(self.cookieSubmit, self.cardEdit.text(), id, num)
            time.sleep(5)
            count += 1
            print("第%d次预约完毕, 返回成功结果" % (count), flag)

    def btnstate(self, btn):  # 自定义点击事件函数
        keys = FIT_STORE.keys()
        for key in keys:
            if btn.text() == key:
                if btn.isChecked() == True:
                    self.store = FIT_STORE.get(btn.text())
                    print("选择门店 %s 门店ID为 %d" % (btn.text(), FIT_STORE.get(btn.text())))


class MyQLabel(QLabel):
    # 自定义单击信号
    clicked = pyqtSignal()

    def __int__(self):
        super().__init__()

    # 重写鼠标单击事件
    def mousePressEvent(self, QMouseEvent):  # 单击
        self.clicked.emit()

    # 可在外部与槽函数连接
    def connect_customized_slot(self, func):
        self.clicked.connect(func)

# 会员卡ID 8937756
def main():
    app = QApplication(sys.argv)
    gui = MainUi()
    gui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()