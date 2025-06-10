import sys
from PyQt5.QtWidgets import (QWidget, QApplication, QVBoxLayout, QPushButton,
                             QLineEdit, QHBoxLayout, QLabel, QMessageBox)
from PyQt5.QtGui import QFont, QMovie
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
import mysql.connector

def db_connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="aq_ceo"
    )

class AnimatedButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet("""
            QPushButton {
                background-color: #004085;
                border-radius: 6px;
                color: white;
                font-weight: 600;
                padding: 12px 28px;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #002752;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(180)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)

    def enterEvent(self, event):
        rect = self.geometry()
        self.anim.stop()
        self.anim.setStartValue(rect)
        self.anim.setEndValue(rect.adjusted(-3, -3, 3, 3))
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        rect = self.geometry()
        self.anim.stop()
        self.anim.setStartValue(rect)
        self.anim.setEndValue(rect.adjusted(3, 3, -3, -3))
        self.anim.start()
        super().leaveEvent(event)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CEO Platform - Log In")
        self.setFixedSize(500, 570)
        self.center()
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1f2937, stop:1 #3b4252);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                color: #e0e6f0;
            }
            QLabel#title_label {
                font-size: 28px;
                font-weight: 700;
                color: #f5f7fa;
                margin-bottom: 30px;
                text-align: center;
            }
            QLabel#label_input {
                font-weight: 600;
                font-size: 14px;
                color: #a0aec0;
                margin-bottom: 6px;
            }
            QLineEdit {
                border-radius: 8px;
                padding: 12px 14px;
                font-size: 16px;
                border: 1.5px solid #4c566a;
                background: #2e3440;
                color: #d8dee9;
                selection-background-color: #5e81ac;
            }
            QLineEdit:focus {
                border-color: #81a1c1;
                background: #3b4252;
                color: #e5e9f0;
            }
            QLabel#error {
                color: #bf616a;
                font-size: 13px;
                margin: 4px 0 10px 0;
            }
        """)
        self.setup_ui()

    def center(self):
        qr = self.frameGeometry()
        cp = QApplication.desktop().screen().rect().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Logo Placeholder with GIF
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        movie = QMovie("logo_6.gif")
        logo_label.setMovie(movie)
        movie.start()
        main_layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        # Username label and input
        user_label = QLabel("Username")
        user_label.setObjectName("label_input")

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Enter your username")

        # Password label and input
        pass_label = QLabel("Password")
        pass_label.setObjectName("label_input")

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")

        main_layout.addWidget(user_label)
        main_layout.addWidget(self.user_input)
        main_layout.addWidget(pass_label)
        main_layout.addWidget(self.password_input)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        btn_login = AnimatedButton("Log In")
        btn_login.clicked.connect(self.attempt_login)

        btn_signin = AnimatedButton("Sign Up")
        btn_signin.clicked.connect(self.open_sign_in)

        buttons_layout.addWidget(btn_login)
        buttons_layout.addWidget(btn_signin)

        main_layout.addLayout(buttons_layout)

        # Help button centered below
        btn_help = AnimatedButton("Help")
        btn_help.setFixedWidth(100)
        btn_help.clicked.connect(self.show_help)
        main_layout.addWidget(btn_help, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def show_help(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Help")
        msg.setText("ℹ️ Developed by ENG Taha and ENG abdulqader\nFor CEO platform support, contact: \nHave a productive day! 🚀")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def attempt_login(self):
        username = self.user_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password.")
            return
        if self.load_data(username, password):
            QMessageBox.information(self, "Welcome!",
                                    f"Hello, {username}! You have successfully logged in. 🎉")

        else:
            QMessageBox.critical(self, "Access Denied", "Invalid username or password. Please try again!")

    def load_data(self, username, password):
        try:
            conn = db_connect()
            cursor = conn.cursor()
            query = "SELECT * FROM employer WHERE Name = %s AND password = %s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return bool(result)
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Error connecting to the database:\n{err}")
            return False

    def open_sign_in(self):
        self.sign_in_window = SignInWindow()
        self.sign_in_window.show()
        self.close()

class SignInWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CEO Platform - Sign Up")
        self.setFixedSize(480, 560)
        self.center()
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2e3440, stop:1 #4c566a);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #d8dee9;
            }
            QLabel#title_label {
                font-size: 26px;
                font-weight: 700;
                margin-bottom: 30px;
                color: #eceff4;
                text-align: center;
            }
            QLabel#label_input {
                font-weight: 600;
                font-size: 14px;
                color: #88c0d0;
                margin-bottom: 6px;
            }
            QLineEdit {
                border-radius: 8px;
                padding: 12px 14px;
                font-size: 16px;
                border: 1.5px solid #4c566a;
                background: #3b4252;
                color: #d8dee9;
                selection-background-color: #81a1c1;
            }
            QLineEdit:focus {
                border-color: #81a1c1;
                background: #434c5e;
                color: #eceff4;
            }
            QLabel#error {
                color: #bf616a;
                font-size: 13px;
                margin: 4px 0 10px 0;
            }
        """)
        self.setup_ui()

    def center(self):
        qr = self.frameGeometry()
        cp = QApplication.desktop().screen().rect().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        label_user = QLabel("New Username")
        label_user.setObjectName("label_input")
        self.new_user = QLineEdit()
        self.new_user.setPlaceholderText("Enter your username")

        label_pass = QLabel("New Password")
        label_pass.setObjectName("label_input")
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("Enter password")

        label_confirm = QLabel("Confirm Password")
        label_confirm.setObjectName("label_input")
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Re-enter password")

        main_layout.addWidget(label_user)
        main_layout.addWidget(self.new_user)
        main_layout.addWidget(label_pass)
        main_layout.addWidget(self.new_password)
        main_layout.addWidget(label_confirm)
        main_layout.addWidget(self.confirm_password)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        btn_signin = AnimatedButton("Sign Up")
        btn_signin.clicked.connect(self.add_employer)

        btn_return = AnimatedButton("Back to Login")
        btn_return.clicked.connect(self.return_to_main)

        buttons_layout.addWidget(btn_signin)
        buttons_layout.addWidget(btn_return)

        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def add_employer(self):
        username = self.new_user.text().strip()
        password = self.new_password.text()
        confirm_pw = self.confirm_password.text()

        if not username or not password or not confirm_pw:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return
        if password != confirm_pw:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match.")
            return

        try:
            conn = db_connect()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM employer WHERE Name = %s", (username,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Username Taken", "Username already taken, please choose another.")
                cursor.close()
                conn.close()
                return

            cursor.execute("INSERT INTO employer (Name, password) VALUES (%s, %s)", (username, password))
            conn.commit()

            cursor.close()
            conn.close()

            QMessageBox.information(self, "Success", "Account created successfully! You can now log in.")

            self.new_user.clear()
            self.new_password.clear()
            self.confirm_password.clear()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Error: {err}")

    def return_to_main(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 12))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
