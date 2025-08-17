import sys
import requests
import csv
import io
import base64
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import hashlib
import random
import string
from tabulate import tabulate

GITHUB_TOKEN = "<token>"
REPO_NAME = "IchigoSolos69/IRC"
FILE_PATH = "userdata.csv"

class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(300, 300, 400, 200)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        self.email_label = QtWidgets.QLabel("Email:")
        self.email_input = QtWidgets.QLineEdit()
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)

        self.password_label = QtWidgets.QLabel("Password:")
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.login_button = QtWidgets.QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.register_label = QtWidgets.QLabel()
        self.register_label.setText('<a href="#">Register</a>')
        self.register_label.setAlignment(Qt.AlignCenter)
        self.register_label.setOpenExternalLinks(False)
        self.register_label.linkActivated.connect(self.open_register)
        layout.addWidget(self.register_label)

        self.setLayout(layout)

    def fetch_csv_content(self):
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            try:
                content = base64.b64decode(response.json()['content']).decode('utf-8')
                sha = response.json()['sha']
                print("LoginWindow: Fetched CSV content from GitHub successfully.")
                return content, sha
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Error decoding CSV content: {e}")
                print("LoginWindow Failed: Error decoding CSV content.")
                return None, None
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Failed to access CSV on GitHub.")
            print("LoginWindow Failed: Could not access CSV on GitHub.")
            return None, None

    def open_admin_panel(self):
        try:
            self.admin_panel = AdminPanel()
            self.admin_panel.show()
            print("AdminPanel: Opened Admin Panel successfully.")
        except Exception as e:
            print(f"AdminPanel Failed: Could not open Admin Panel. Error: {e}")
    
    def login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        
        if not email or not password:
            QtWidgets.QMessageBox.warning(self, "Error", "Please enter both email and password.")
            print("Login Failed: Missing email or password.")
            return

        csv_content, _ = self.fetch_csv_content()   
        if csv_content:
            csv_reader = csv.reader(io.StringIO(csv_content))
            for row in csv_reader:
                if row[1] == email and row[5] == password:
                    QtWidgets.QMessageBox.information(self, "Login", "Login successful!")
                    print("Login: Login successful.")
                    if row[1] == "ircADMIN":
                        print("Admin: Admin detected. Opening Admin Panel.")
                        self.close()
                        self.open_admin_panel()
                    return
            print("Login Failed: Incorrect email or password.")
            QtWidgets.QMessageBox.warning(self, "Login Failed", "Invalid email or password.")

    def open_register(self):
        try:
            self.register_window = RegisterWindow()
            self.register_window.show()
            print("RegisterWindow: Register window opened successfully.")
        except Exception as e:
            print(f"RegisterWindow Failed: Could not open Register window. Error: {e}")

class RegisterWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register")
        self.setGeometry(300, 300, 400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        self.name_label = QtWidgets.QLabel("Name:")
        self.name_input = QtWidgets.QLineEdit()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        self.email_label = QtWidgets.QLabel("Email:")
        self.email_input = QtWidgets.QLineEdit()
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)

        self.prn_label = QtWidgets.QLabel("PRN:")
        self.prn_input = QtWidgets.QLineEdit()
        layout.addWidget(self.prn_label)
        layout.addWidget(self.prn_input)

        self.college_label = QtWidgets.QLabel("College Name:")
        self.college_dropdown = QtWidgets.QComboBox()
        self.college_dropdown.addItems(["PCCOE", "COEP", "MIT", "VIT", "BVDU", "Other"])
        layout.addWidget(self.college_label)
        layout.addWidget(self.college_dropdown)

        self.phone_label = QtWidgets.QLabel("Phone Number:")
        self.phone_input = QtWidgets.QLineEdit()
        layout.addWidget(self.phone_label)
        layout.addWidget(self.phone_input)

        self.password_label = QtWidgets.QLabel("Password:")
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.register_button = QtWidgets.QPushButton("Register")
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def generate_user_code(self, name, email, prn):
        data = f"{name}{email}{prn}"
        salt = "UniqueSaltValue"

        hash_object = hashlib.sha256((data + salt).encode())
        hash_hex = hash_object.hexdigest()

        base_code = hash_hex[:6]
        letter = random.choice(string.ascii_uppercase)
        insert_position = random.randint(0, 5)
        final_code = base_code[:insert_position] + letter + base_code[insert_position:]

        return final_code.upper()

    def fetch_csv_content(self):
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            try:
                content = base64.b64decode(response.json()['content']).decode('utf-8')
                sha = response.json()['sha']
                print("GenUserCode: Fetched CSV content from GitHub successfully.")
                return content, sha
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Error decoding CSV content: {e}")
                print("GenUserCode Failed: Error decoding CSV content.")
                return None, None
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Failed to access CSV on GitHub.")
            print("GenUserCode Failed: Could not access CSV on GitHub.")
            return None, None

    def update_csv(self, content, sha):
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        new_content = base64.b64encode(content.encode("utf-8")).decode('utf-8')
        
        data = {
            "message": "Updated CSV with new registration",
            "content": new_content,
            "sha": sha,
        }
        response = requests.put(url, json=data, headers=headers)
        
        if response.status_code == 200:
            QtWidgets.QMessageBox.information(self, "Registration", "Registration successful!")
            print("UpdateCSV: CSV updated successfully on GitHub.")
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Failed to update CSV on GitHub.")
            print("UpdateCSV Failed: Could not update CSV on GitHub.")

    def register(self):
        name = self.name_input.text()
        email = self.email_input.text()
        prn = self.prn_input.text()
        college = self.college_dropdown.currentText()
        phone = self.phone_input.text()
        password = self.password_input.text()

        if not all([name, email, prn, college, phone, password]):
            QtWidgets.QMessageBox.warning(self, "Error", "All fields must be filled.")
            print("Registration Failed: Some fields are empty.")
            return

        unique_code = self.generate_user_code(name, email, prn)

        csv_content, sha = self.fetch_csv_content()
        
        if csv_content:
            csv_data = io.StringIO(csv_content)
            reader = csv.reader(csv_data)
            rows = list(reader)
            rows.append([name, email, prn, college, phone, password, unique_code])  

            csv_data = io.StringIO()
            writer = csv.writer(csv_data, lineterminator='\n')
            writer.writerows(rows)
            csv_data.seek(0)

            self.update_csv(csv_data.read(), sha)
            self.send_email(email, name)
            self.close()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Failed to retrieve CSV content for registration.")
            print("Registration: Failed to retrieve CSV content for registration.")

    def send_email(self, user_email, user_name):
        sender_email = "adimaitre56@gmail.com"
        sender_password = "zyuw ofez kkpf hqdx"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = user_email
        msg['Subject'] = "Welcome to the International Relations Community"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f6f6f6; color: #333; margin: 0; padding: 0;">
                <div style="max-width: 600px; margin: 40px auto; padding: 20px; background-color: #fff; border: 1px solid #e0e0e0; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
                    <div style="text-align: center; padding: 20px 0; border-bottom: 1px solid #e0e0e0;">
                        <h1 style="font-size: 24px; color: #4285f4; margin: 0;">Dear {user_name},</h1>
                    </div>
                    
                    <div style="padding: 20px;">
                        <p style="line-height: 1.6; margin: 15px 0;">Thank you for completing your registration. We are delighted to welcome you to our community, marking the beginning of what promises to be an exciting journey together.</p>
                        <p style="line-height: 1.6; margin: 15px 0;">As a member, you will have the opportunity to engage in a variety of events, participate in thought-provoking discussions, and connect with fellow enthusiasts who share your passion for international relations.</p>
                        <p style="line-height: 1.6; margin: 15px 0;">To stay informed about our latest initiatives, announcements, and events, we encourage you to follow us on our social media platforms:</p>
                        
                        <div style="text-align: center; margin: 20px 0;">
                            <a href="https://www.instagram.com/pccoe_ircell/" target="_blank" style="text-decoration: none; color: #4285f4; font-size: 16px;">
                                <img src="https://raw.githubusercontent.com/IchigoSolos69/IRC/main/insta.jpg" alt="Instagram" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"> Instagram
                            </a>
                            <a href="https://www.facebook.com/p/IR-Cell-61551872357933" target="_blank" style="text-decoration: none; color: #4285f4; font-size: 16px; margin-left: 15px;">
                                <img src="https://raw.githubusercontent.com/IchigoSolos69/IRC/main/fb.jpg" alt="Facebook" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"> Facebook
                            </a>
                            <a href="https://www.linkedin.com/company/pccoe-ir-cell/" target="_blank" style="text-decoration: none; color: #4285f4; font-size: 16px; margin-left: 15px;">
                                <img src="https://raw.githubusercontent.com/IchigoSolos69/IRC/main/ln.png" alt="LinkedIn" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"> LinkedIn
                            </a>
                        </div>

                        <p style="line-height: 1.6; margin: 15px 0;">We are confident that your involvement will significantly enhance our collective efforts, and we eagerly anticipate your contributions in the near future.</p>
                        <p style="line-height: 1.6; margin: 15px 0;">Once again, thank you for joining us. We look forward to embarking on this journey together!</p>
                        <p style="line-height: 1.6; margin: 15px 0;">Best regards,<br>
                        <strong>International Relations Cell<br>
                        Pimpri Chinchwad College of Engineering</strong></p>
                    </div>
                    <div style="text-align: center; padding: 15px; font-size: 12px; color: #888; border-top: 1px solid #e0e0e0; margin-top: 20px;">
                        <p>This email was sent automatically by the International Relations Cell Technical Team, PCCOE. Please do not reply. <br>
                    Stay connected with us on social media for updates on upcoming events and initiatives.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                try:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    print("Email: Server login successful.")
                except smtplib.SMTPAuthenticationError:
                    QtWidgets.QMessageBox.warning(self, "Error", "Authentication failed. Check your email and password.")
                    print("Email Failed: Authentication error.")
                    return
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Error", f"Failed to connect to the server: {e}")
                    print(f"Email Failed: Server connection error - {e}")
                    return
                
                try:
                    server.sendmail(sender_email, user_email, msg.as_string())
                    QtWidgets.QMessageBox.information(self, "Success", "Email sent successfully!")
                    print("Email: Email sent successfully.")
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Error", f"Could not send email: {e}")
                    print(f"Email Failed: Email sending error - {e}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Unexpected error while setting up email server: {e}")
            print(f"General Error: {e}")

class AdminPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Panel")
        self.setGeometry(300, 300, 800, 600)
        self.init_ui()

    def fetch_csv_content(self):
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  
            
            content = base64.b64decode(response.json()['content']).decode('utf-8')
            sha = response.json().get('sha')
            return content, sha

        except requests.exceptions.HTTPError as http_err:
            QtWidgets.QMessageBox.warning(self, "HTTP Error", f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError:
            QtWidgets.QMessageBox.warning(self, "Connection Error", "Could not connect to GitHub. Check your network connection.")
        except requests.exceptions.Timeout:
            QtWidgets.QMessageBox.warning(self, "Timeout Error", "The request timed out. Please try again.")
        except requests.exceptions.RequestException as req_err:
            QtWidgets.QMessageBox.warning(self, "Error", f"An error occurred: {req_err}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to access CSV on GitHub: {e}")
        
        return None, None

    def get_userinfo(self):
        in_encry_key = self.encry_key_input.text()
        csv_content, _ = self.fetch_csv_content()

        if csv_content:
            try:
                csv_reader = csv.reader(io.StringIO(csv_content))
                headers = ["Name", "Email ID", "PRN No.", "College Name", "Phone No.", "Password", "Encryption Key"]
                
                for row in csv_reader:
                    if len(row) == 7:
                        name, email, prn, college, phno, password, encry_key = row
                        
                        if encry_key == in_encry_key:
                            userinfo = [name, email, prn, college, phno, password, encry_key]
                            user_info_table = tabulate([userinfo], headers=headers, tablefmt='grid')
                            self.result_display.setPlainText(user_info_table)
                            return
                self.result_display.setPlainText("No user found with this encryption key.")
            except csv.Error as e:
                QtWidgets.QMessageBox.warning(self, "CSV Error", f"Error processing CSV content: {e}")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Unexpected error: {e}")
        else:
            self.result_display.setPlainText("Failed to retrieve data.")

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        self.encry_key_label = QtWidgets.QLabel("Encryption Key:")
        self.encry_key_input = QtWidgets.QLineEdit()
        layout.addWidget(self.encry_key_label)
        layout.addWidget(self.encry_key_input)

        self.encry_key_search_button = QtWidgets.QPushButton("Search")
        self.encry_key_search_button.clicked.connect(self.get_userinfo)
        layout.addWidget(self.encry_key_search_button)

        self.result_display = QtWidgets.QPlainTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
