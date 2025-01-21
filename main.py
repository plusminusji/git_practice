import sys
from PyQt5.QtWidgets import QApplication, QWidget

# 클래스 선언(클래스 상속)
class Calculator(QWidget):

    # 생성자 함수
    def __init__(self):
        # QWidget 클래스의 생성자 함수를 실행
        super().__init__()
        # 클래스에서 생성한 함수를 실행
        self.initUI()

    def initUI(self):
        # 새로운 화면에 제목
        self.setWindowTitle("Calculator")
        # 새로운 화면의 사이즈
        self.resize(256, 256)
        # 윈도우 화면 출력
        self.show()

if __name__ == "__main__":
    # 클래스 생성
    app = QApplication(sys.argv)
    # 클래스 생성
    view = Calculator()
    # 애플리케이션에서 이벤트를 처리하는 루프 생성
    sys.exit(app.exec_())

    

