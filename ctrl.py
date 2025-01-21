# 버튼들의 기능 부분을 작성하는 파일
from PyQt5.QtWidgets import QMessageBox

class Control:
    # 생성자 함수 생성
    def __init__(self, view):
        self.view = view
        self.connectSignal()
    
    def connectSignal(self):
        self.view.btn1.clicked.connect(self.view.activeMessage)


