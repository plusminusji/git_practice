# 화면이 구성되는 code의 집합
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, \
    QVBoxLayout, QMessageBox

# 클래스 선언
class View(QWidget):

    # 생성자 함수
    def ___init___(self):
        super().__init__()
        self.initUI()

    # 유저인테페이스 함수를 생성
    def initUI(self):
        # 윈도우 버튼 생성
        self.btn1 = QPushButton('Message', self)
        # 버튼의 위치 수정
        # 수직 레이아웃 위젯 생성
        vbox = QVBoxLayout()
        # 비어있는 공간 생성
        vbox.addStretch(1)
        # 버튼 추가
        vbox.addWidget(self.btn1)
        # 비어있는 공간 생성
        vbox.addStretch(1)
        # 빈공간 - 버튼 - 빈공간 순으로 수직 배치된 레이아웃 생성
        self.setLayout(vbox)


        # 새로운 화면에 제목
        self.setWindowTitle("Calculator")
        # 새로운 화면의 사이즈
        self.resize(256, 256)
        # 윈도우 화면 출력
        self.show()

    def activeMessage(self):
        QMessageBox.informatoin(self, 'information', 'Button Clicked!')
        