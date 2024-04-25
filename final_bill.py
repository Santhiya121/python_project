import os
import mysql.connector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import fitz  # PyMuPDF

def extract_bill_number_from_pdf(pdf_file_path):
    try:
        with fitz.open(pdf_file_path) as pdf_document:
            extracted_text = ""
            for page in pdf_document:
                extracted_text += page.get_text()
            return extracted_text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF '{pdf_file_path}': {e}")
        return None

def send_email(sender_email, sender_password, receiver_email, bill_number, pdf_file_path):
    gmail_app_password = sender_password
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'Regarding Your Bill'

    body = f"Dear Customer,\n\nThank you for purchasing our products! Your bill number {bill_number} is ready for processing. Please check.\n\nBest regards"
    message.attach(MIMEText(body, 'plain'))

    # Attach the PDF file
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_attachment = MIMEApplication(pdf_file.read(), _subtype="pdf")
        pdf_attachment.add_header('content-disposition', 'attachment', filename=os.path.basename(pdf_file_path))
        message.attach(pdf_attachment)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    
    try:
        server.login(sender_email, gmail_app_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"Email sent to {receiver_email} for bill number {bill_number}")
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {str(e)}")
    finally:
        server.quit()

def process_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".pdf"):
                pdf_file_path = os.path.join(root, filename)
                extracted_text = extract_bill_number_from_pdf(pdf_file_path)

                if extracted_text:
                    # Split the extracted text based on "BILL NUMBER:" to isolate each bill's information
                    bill_infos = extracted_text.split("BILL NUMBER:")
                    for bill_info in bill_infos[1:]:  # Skip the first entry (before the first "BILL NUMBER:")
                        lines = bill_info.strip().split("\n")
                        if lines:
                            bill_number = lines[0].strip()  # Extract the bill number
                            print(f"Extracted Bill Number: {bill_number}")

                            # Query the database with the extracted bill number
                            query = f"SELECT id, email FROM customertale WHERE Id = '{bill_number}'"
                            cursor.execute(query)
                            rows = cursor.fetchall()

                            if rows:
                                sender_email = 'santhiyar121@gmail.com'
                                sender_password = 'dfxj xcux cjac lpyk'
                                for row in rows:
                                    user_id, email = row
                                    send_email(sender_email, sender_password, email, bill_number, pdf_file_path)
                            else:
                                print(f"No matching records found for bill number {bill_number}")
                else:
                    print(f"Failed to extract text from PDF '{pdf_file_path}'.")

if __name__ == "__main__":
    # Provide the parent folder path containing subfolders with PDF files
    parent_folder_path = input("Enter the parent folder path: ")
    
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="San#19",
            database="personinfo"
        )

        if connection.is_connected():
            cursor = connection.cursor()
            process_folder(parent_folder_path)

    except mysql.connector.Error as error:
        print(f"Error connecting to MySQL: {error}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()