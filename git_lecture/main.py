import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, \
    QVBoxLayout, QMessageBox

# 클래스 선언(클래스 상속)
class Calculator(QWidget):

    # 생성자 함수
    def __init__(self):
        # QWidget 클래스의 생성자 함수를 실행
        super().__init__()
        # 클래스에서 생성한 함수를 실행
        self.initUI()

    def initUI(self):


        # ------- 1차 수정 추가 부분 -------
        # 윈도우 버튼 생성
        self.btn1 = QPushButton('Message', self)
        # 해당하는 버튼이 클릭이 됐을 때 이벤트를 발생 (activeMessage 함수 실행)
        self.btn1.clicked.connect(self.activeMessage)
        # ------- 1차 수정 추가 부분 -------
        
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

    # 버튼 클릭 시 실행할 이벤트 함수 생성
    def activeMessage(self):
        # 버튼 클릭 시 메시지 박스 출력
        QMessageBox.information(self, 'information', 'Button Clicked!')

if __name__ == "__main__":
    # 클래스 생성
    app = QApplication(sys.argv)
    # 클래스 생성
    view = Calculator()
    # 애플리케이션에서 이벤트를 처리하는 루프 생성
    sys.exit(app.exec_())



