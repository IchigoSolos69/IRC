import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Circle
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import csv
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox, QMessageBox, QLineEdit
import sys
import os
import logging

# Set up logging
logging.basicConfig(filename='event_analysis.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EventAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Event Analysis Program')
        self.setGeometry(300, 200, 500, 400)

        self.layout = QVBoxLayout()

        self.label = QLabel('Select Event CSV File(s):')
        self.layout.addWidget(self.label)

        self.upload_button = QPushButton('Upload Event CSV')
        self.upload_button.clicked.connect(self.upload_csv)
        self.layout.addWidget(self.upload_button)

        self.search_label = QLabel('Search User:')
        self.layout.addWidget(self.search_label)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText('Enter user name...')
        self.search_box.textChanged.connect(self.filter_users)
        self.layout.addWidget(self.search_box)

        self.user_select_label = QLabel('Select User:')
        self.layout.addWidget(self.user_select_label)

        self.user_dropdown = QComboBox()
        self.layout.addWidget(self.user_dropdown)

        self.view_graph_button = QPushButton('View Attendance Graph')
        self.view_graph_button.clicked.connect(self.show_attendance_graph)
        self.layout.addWidget(self.view_graph_button)

        self.send_email_button = QPushButton('Send Certificate')
        self.send_email_button.clicked.connect(self.send_single_certificate)
        self.layout.addWidget(self.send_email_button)

        self.send_bulk_email_button = QPushButton('Send Bulk Emails')
        self.send_bulk_email_button.clicked.connect(self.send_bulk_certificates)
        self.layout.addWidget(self.send_bulk_email_button)

        self.view_history_button = QPushButton('View Historical Data')
        self.view_history_button.clicked.connect(self.view_historical_data)
        self.layout.addWidget(self.view_history_button)

        self.setLayout(self.layout)
        self.event_data = None
        self.qr_code_path = "D:\\Python_Projects\\irc\\instagram_qr.png"
        self.user_profiles = pd.DataFrame()  # Keep user profiles across multiple events
        self.historical_data = pd.DataFrame()  # Store historical attendance
    
    def upload_csv(self):
        csv_files, _ = QFileDialog.getOpenFileNames(self, 'Open Event CSV File(s)', '', 'CSV Files (*.csv)')
        if csv_files:
            try:
                for csv_file in csv_files:
                    event_data = pd.read_csv(csv_file)
                    self.user_profiles = pd.concat([self.user_profiles, event_data], ignore_index=True)
                self.populate_user_dropdown()
                QMessageBox.information(self, 'File Upload', 'Event CSV File(s) loaded successfully.')
                logging.info(f'CSV files {csv_files} uploaded successfully.')
            except Exception as e:
                logging.error(f'Error loading CSV files: {e}')
                QMessageBox.warning(self, 'Error', f'Failed to load the CSV file(s): {e}')
        else:
            logging.warning('No CSV file selected.')

    def populate_user_dropdown(self):
        self.user_dropdown.clear()
        if not self.user_profiles.empty:
            for name in self.user_profiles['Name'].unique():
                self.user_dropdown.addItem(name)

    def filter_users(self):
        filter_text = self.search_box.text().lower()
        self.user_dropdown.clear()

        if not self.user_profiles.empty:
            filtered_names = self.user_profiles[self.user_profiles['Name'].str.lower().str.contains(filter_text)]['Name'].unique()
            for name in filtered_names:
                self.user_dropdown.addItem(name)

    def show_attendance_graph(self):
        if self.user_profiles.empty:
            QMessageBox.warning(self, 'Warning', 'Please upload the event CSV file first.')
            return

        selected_user = self.user_dropdown.currentText()
        if selected_user:
            selected_user_data = self.user_profiles[self.user_profiles['Name'] == selected_user]
            event_columns = [col for col in selected_user_data.columns if col.startswith('Event')]
            attendance_count = (selected_user_data[event_columns] == 'A').sum().sum()
            total_events = len(event_columns)

            plt.figure(figsize=(8, 5))
            plt.bar([selected_user], [attendance_count], color='#4CAF50', edgecolor='black', linewidth=1.5)
            plt.axhline(y=total_events, color='red', linestyle='--', label="Total Events")
            plt.ylabel('Number of Events Attended', fontsize=12)
            plt.title(f'Attendance for {selected_user}', fontsize=14)
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()  # Adjust layout for better fit
            plt.show()
        else:
            QMessageBox.warning(self, 'Warning', 'No user selected.')

    def view_historical_data(self):
        if self.user_profiles.empty:
            QMessageBox.warning(self, 'Warning', 'No historical data available.')
            return

        selected_user = self.user_dropdown.currentText()
        if selected_user:
            user_history = self.user_profiles[self.user_profiles['Name'] == selected_user]
            user_prn = user_history['PRN No.'].iloc[0]
            self.show_user_history(selected_user, user_history, user_prn)
            logging.info(f'Historical data viewed for {selected_user}.')
        else:
            QMessageBox.warning(self, 'Warning', 'No user selected.')

    def show_user_history(self, user_name, user_history, user_prn):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Attendance Data for {user_name}")
        dialog.setGeometry(400, 200, 600, 500)  # Increased height for extra content

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        name_label = QLabel(f"<h2 style='margin: 0;'>Name of the Student:</h2> <p style='font-size: 16px; margin: 5px 0;'>{user_name}</p>")
        prn_label = QLabel(f"<h2 style='margin: 0;'>PRN Number of the Student:</h2> <p style='font-size: 16px; margin: 5px 0;'>{user_prn}</p>")

        layout.addWidget(name_label)
        layout.addWidget(prn_label)

        # Get event columns
        event_columns = [col for col in user_history.columns if col.startswith('Event')]
        
        # Determine attended sessions and calculate attendance percentage
        attended_sessions = (user_history[event_columns] == 'A').sum().sum()
        total_sessions = len(event_columns)
        attendance_percentage = (attended_sessions / total_sessions) * 100 if total_sessions > 0 else 0

        # Create a list of attended events
        attended_events = user_history[event_columns].columns[(user_history[event_columns] == 'A').any()]
        
        attended_events_label = QLabel("<h3>Events Attended:</h3>")
        attended_events_list = QLabel(f"<p style='font-size: 16px; margin: 5px 0;'>{', '.join(attended_events)}</p>")
        
        layout.addWidget(attended_events_label)
        layout.addWidget(attended_events_list)

        # Create a tube circle style attendance display
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect='equal'))

        # Draw the tube circle with a thick border for a modern look
        outer_radius = 0.4
        inner_radius = 0.3
        circle_outer = Circle((0, 0), outer_radius, color='#D3D3D3', ec='none')
        circle_inner = Circle((0, 0), inner_radius, color='white', ec='none')
        
        ax.add_artist(circle_outer)
        ax.add_artist(circle_inner)

        # Draw the attendance arc
        theta = np.linspace(0, 2 * np.pi * (attendance_percentage / 100), 100)
        x = outer_radius * np.cos(theta)
        y = outer_radius * np.sin(theta)
        ax.fill(x, y, color='#4CAF50', ec='none')

        # Create a border for the tube effect
        ax.add_artist(Circle((0, 0), outer_radius, color='black', linewidth=5, fill=False))

        # Add attendance percentage text with a modern font style
        ax.text(0, 0, f"{attendance_percentage:.1f}%", ha='center', va='center', fontsize=20, color='black', fontweight='bold', family='sans-serif')

        # Set limits and hide axes
        ax.set_xlim(-0.5, 0.5)
        ax.set_ylim(-0.5, 0.5)
        ax.axis('off')  # Hide the axes

        # Adjust the background color for a more vibrant look
        fig.patch.set_facecolor('#f0f0f0')

        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)

        dialog.exec_()

    def send_single_certificate(self):
        if self.qr_code_path is None:
            QMessageBox.warning(self, 'Warning', 'Please upload the QR code image first.')
            logging.warning('Attempted to send certificate without uploading QR code image.')
            return

        selected_user = self.user_dropdown.currentText()
        if selected_user:
            user_profile = self.user_profiles[self.user_profiles['Name'] == selected_user].iloc[0]
            user_name = user_profile['Name']
            user_email = user_profile['Email ID']

            event_columns = [col for col in self.user_profiles.columns if col.startswith('Event')]
            user_attendance = user_profile[event_columns].tolist()

            if all(att == 'A' for att in user_attendance):
                cert_path = self.generate_certificate(user_name)
                self.send_email(user_email, user_name, cert_path, self.qr_code_path)
                logging.info(f'Certificate sent to {user_name} ({user_email}).')
                QMessageBox.information(self, 'Success', f'Certificate sent to {user_name} ({user_email}).')
            else:
                logging.info(f'{user_name} has incomplete attendance and was skipped.')
                QMessageBox.information(self, 'Warning', f'{user_name} has incomplete attendance and was skipped.')
        else:
            QMessageBox.warning(self, 'Warning', 'No user selected.')

    def send_bulk_certificates(self):
        if self.qr_code_path is None:
            QMessageBox.warning(self, 'Warning', 'Please upload the QR code image first.')
            logging.warning('Attempted to send certificates without uploading QR code image.')
            return

        event_columns = [col for col in self.user_profiles.columns if col.startswith('Event')]

        for idx, user_profile in self.user_profiles.iterrows():
            user_name = user_profile['Name']
            user_email = user_profile['Email ID']

            user_attendance = user_profile[event_columns].tolist()

            if all(att == 'A' for att in user_attendance):
                cert_path = self.generate_certificate(user_name)
                self.send_email(user_email, user_name, cert_path, self.qr_code_path)
                logging.info(f'Certificate sent to {user_name} ({user_email}).')
            else:
                logging.info(f'{user_name} has incomplete attendance and was skipped.')
                QMessageBox.information(self, 'Warning', f'{user_name} has incomplete attendance and was skipped.')

        QMessageBox.information(self, 'Bulk Email', 'Certificates sent to all users who completed the event.')

    def generate_certificate(self, user_name):
        template_path = "D:\\Python_Projects\\irc\\output.png"
        img = Image.open(template_path)

        draw = ImageDraw.Draw(img)
        font_path = "D:\\Python_Projects\\irc\\birthstone.ttf" 
        font_size = 169
        font = ImageFont.truetype(font_path, font_size)

        text_bbox = draw.textbbox((0, 0), user_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        position = ((img.width - text_width) // 2, 760) 

        draw.text(position, user_name, font=font, fill="black")

        cert_path = f"{user_name}_certificate.pdf"
        img.save(cert_path, "PDF")

        return cert_path

    def send_email(self, user_email, user_name, cert_path, qr_code_path):
        sender_email = "knowjapanircell@gmail.com"
        sender_password = "hwoh aozb gdlo baec"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = user_email
        msg['Subject'] = "Congratulations on Completing Know Japan 2024"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif; 
                    background-color: #f6f6f6; 
                    color: #333;
                }}
                .container {{
                    max-width: 600px; 
                    margin: 40px auto; 
                    padding: 20px; 
                    background-color: #fff; 
                    border: 1px solid #e0e0e0; 
                    border-radius: 10px; 
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center; 
                    padding: 20px 0; 
                    border-bottom: 1px solid #e0e0e0;
                }}
                .header h1 {{
                    font-size: 24px; 
                    color: #4285f4; 
                    margin: 0;
                }}
                .content {{
                    padding: 20px;
                }}
                .content p {{
                    line-height: 1.6; 
                    margin: 15px 0;
                }}
                .social-links {{
                    display: flex;
                    justify-content: center;
                    gap: 15px;
                    padding: 0;
                    margin-top: 10px;
                }}
                .social-link {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #ADD8E6;
                    color: #ffffff;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                }}
                .cta-button {{
                    display: inline-block; 
                    margin: 20px 0; 
                    padding: 12px 20px; 
                    background-color: #ADD8E6; 
                    color: #FFFFFF; 
                    border-radius: 5px; 
                    text-align: center; 
                    text-decoration: none; 
                    font-size: 16px; 
                    font-weight: bold;
                }}
                .cta-button:hover {{
                    background-color: #4285f4; /* Darker blue on hover */
                }}
                .footer {{
                    text-align: center; 
                    padding: 15px; 
                    font-size: 12px; 
                    color: #888;
                    border-top: 1px solid #e0e0e0; 
                    margin-top: 20px;
                }}
                @media screen and (max-width: 480px) {{
                    .container {{
                        width: 100%;
                        padding: 10px;
                    }}
                    .social-links {{
                        flex-direction: column;
                        gap: 10px;
                    }}
                    .cta-button, .social-link {{
                        width: 100%;
                        text-align: center;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Congratulations, {user_name}!</h1>
                </div>
                
                <div class="content">
                    <p>We are thrilled to extend our warmest congratulations to you for successfully completing all the event sessions organized by the International Relations Cell at PCCOE.</p>
                    <p>Your dedication and active participation have truly stood out, and we commend your outstanding efforts. As a token of our appreciation, we have attached your certificate for this accomplishment.</p>
                    <p>Stay connected with us on social media:</p>
                    
                    <div class="social-links">
                        <a href="https://www.instagram.com/pccoe_ircell/" class="social-link">Instagram</a>
                        <a href="https://www.facebook.com/p/IR-Cell-61551872357933" class="social-link">Facebook</a>
                        <a href="https://www.linkedin.com/company/pccoe-ir-cell/" class="social-link">LinkedIn</a>
                    </div>
                    
                    <a href="https://www.pccoepune.com/ir/ir-home.php" class="cta-button">Visit Our Webpage</a>
                    
                    <p>Once again, congratulations on this significant achievement! We eagerly anticipate your continued participation in our future events and wish you all the best in your endeavors.</p>
                    
                    <p>Best regards,<br>
                    <strong>International Relations Cell<br>
                    Pimpri Chinchwad College of Engineering</strong></p>

                    <img src="cid:instagram_qr" alt="Instagram QR Code" style="width: 200px; height: auto; display: block; margin: 0 auto;" />
                </div>
                
                <div class="footer">
                    <p>This email was sent automatically by the International Relations Cell Technical Team, PCCOE. Please do not reply. <br>
                    Stay connected with us on social media for updates on upcoming events and initiatives.</p>
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))


        with open(qr_code_path, "rb") as img_file:
            img = MIMEImage(img_file.read())
            img.add_header("Content-ID", "<instagram_qr>")
            img.add_header("Content-Disposition", "inline", filename = qr_code_path)
            msg.attach(img)

        # Attach the certificate
        with open(cert_path, "rb") as cert_file:
            cert = MIMEBase('application', 'octet-stream')
            cert.set_payload(cert_file.read())
            encoders.encode_base64(cert)
            cert.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(cert_path)}"')
            msg.attach(cert)

        # Send email
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, msg.as_string())
            server.quit()
            logging.info(f'Email sent to {user_email} successfully.')
        except Exception as e:
            logging.error(f'Failed to send email to {user_email}: {e}')
            QMessageBox.warning(self, 'Error', f'Failed to send email to {user_email}: {e}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EventAnalysisApp()
    ex.show()
    sys.exit(app.exec_())