import pandas as pd
import matplotlib.pyplot as plt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from fpdf import FPDF

# Step 1: Load Event Data from CSV and Create User Profiles
def load_event_data(file_path):
    return pd.read_csv(file_path)

def create_user_profiles(df):
    user_profiles = df.drop_duplicates(subset='PRN No.')
    return user_profiles

# Step 2: Generate Attendance Graph for a Selected User
def generate_attendance_graph(df, prn, user_name):
    attendance_count = df[df['PRN No.'] == prn].shape[0]
    total_events = df['Event'].nunique()

    plt.bar([user_name], [attendance_count], color='blue')
    plt.axhline(y=total_events, color='r', linestyle='--', label="Total Events")
    plt.ylabel('Number of Events Attended')
    plt.title(f'Attendance for {user_name}')
    plt.legend()
    plt.show()

# Step 3: Send Email with QR Code and Certificate
def send_email(user_email, user_name, certificate_path, qr_code_path):
    from_email = "adimaitre56@gmail.com"
    password = "ounu waxo ljte shjl"
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = user_email
    msg['Subject'] = "Congratulations on completing all event sessions!"
    
    body = f"Hi {user_name},\n\nCongratulations on completing all event sessions! " \
           f"Find attached your certificate and our Instagram QR code.\n\nBest regards,\nEvent Team"\
           f"{qr_code_path}, 'instagram_qr.png'"
    msg.attach(MIMEText(body, 'plain'))
    
    attach_file(msg, certificate_path, 'certificate.pdf')
    attach_file(msg, qr_code_path, 'instagram_qr.png')

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)  # Make sure credentials are correct and access is allowed.
    text = msg.as_string()
    server.sendmail(from_email, user_email, text)
    server.quit()

def attach_file(msg, file_path, filename):
    with open(file_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={filename}')
        msg.attach(part)

# Step 4: Generate Certificate PDF
def generate_certificate(user_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(200, 10, text=f"Certificate of Completion", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.cell(200, 10, text=f"This certifies that {user_name}", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.cell(200, 10, text="has successfully completed all event sessions.", new_x="LMARGIN", new_y="NEXT", align='C')
    
    cert_path = f"{user_name}_certificate.pdf"
    pdf.output(cert_path)
    return cert_path

# User selection for displaying attendance
def select_user(user_profiles):
    print("Select a user to view attendance:")
    for i, user in enumerate(user_profiles['Name'], 1):
        print(f"{i}. {user}")
    selection = int(input("\nEnter the number corresponding to the user: "))
    return user_profiles.iloc[selection - 1]

# Main function to execute the program
def main(event_file, qr_code_path):
    event_data = load_event_data(event_file)
    user_profiles = create_user_profiles(event_data)
    
    # Allow user to select a specific profile for graph
    selected_user = select_user(user_profiles)
    prn = selected_user['PRN No.']
    user_name = selected_user['Name']
    user_email = selected_user['Email ID']
    
    # Generate and display the attendance graph
    generate_attendance_graph(event_data, prn, user_name)
    
    # Check if the user has attended all events
    total_events = event_data['Event'].nunique()
    user_attendance = event_data[event_data['PRN No.'] == prn].shape[0]
    
    if user_attendance == total_events:
        cert_path = generate_certificate(user_name)
        send_email(user_email, user_name, cert_path, qr_code_path)

if __name__ == "__main__":
    event_file = "D:\\Python_Projects\\event_analysis\\event.csv"  # Path to your events CSV file
    qr_code_path = "D:\\Python_Projects\\event_analysis\\instagram_qr.png"  # Path to your Instagram QR code image
    main(event_file, qr_code_path)
