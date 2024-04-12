from flask import Flask, render_template, send_file, request, jsonify
import io
import logging
import pandas as pd
import pyodbc
import base64
import handler
from config.config import Config
import requests
from PIL import Image
from io import BytesIO
import io
import config
import xlsxwriter
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from email.mime.base import MIMEBase
from email import encoders
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

config = Config()
app = Flask(__name__)

# Routes for rendering HTML pages

@app.route('/Report/Jewelers_id/<string:data>')
def home(data):
    return "You are reached to the Power BI report homepage!"


server = config.server_name
database = config.database_name
username = config.logid
password = config.logpass
driver = config.driver

def retrieve_data_and_export(filter_value):
    try:
        conn = pyodbc.connect(
            'DRIVER=' + driver + ';SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password + ';TCON='  + config.TCON)
        cursor = conn.cursor()

        # Modify your SQL query to use the filter_value as a parameter
        query = "EXEC [dbo].[sp_B2B_PBI_Analytics_Excel] @account_name=?"
        cursor.execute(query, (filter_value,))
        headers = [column[0] for column in cursor.description]
        columns = [[] for _ in range(len(headers))]
        data = {col: col_data for col, col_data in zip(headers, columns)}

        # Fetch data from the cursor
        for row in cursor.fetchall():
            for i, value in enumerate(row):
                columns[i].append(value)

        df = pd.DataFrame(data)

        # Download images and insert their paths into DataFrame
        image_paths = []
        for index, row in df.iterrows():
            image_url = row['Image'].replace("\\", "/").strip()  # Correct URL format
            response = requests.get(image_url)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                img.thumbnail((50, 50))  # Resize the image to a smaller size
                img_path = f'.{index}.png'  # Image path
                img.save(img_path)
                image_paths.append(img_path)
            else:
                image_paths.append(None)  # Handle case where image cannot be downloaded
                logging.error(f"Failed to download image from URL: {image_url}")

        df.drop(columns=['Image'], inplace=True)  # Remove the URL column
        df.insert(1, 'Image', image_paths)  # Insert image paths in the second column

        # Write DataFrame to an Excel file
        excel_buffer = io.BytesIO()

        # Trim data (assuming 'df' is your DataFrame)
        df['ID'] = df['ID'].astype(str).str.strip()
        df['Description'] = df['Description'].astype(str).str.strip()
        df['B2B URL'] = df['B2B URL'].astype(str).str.strip()
        df['Item Price'] = df['Item Price'].astype(str).str.strip()
        df['Year'] = df['Year'].astype(str).str.strip()
        df['Month'] = df['Month'].astype(str).str.strip()
        df['Quarter'] = df['Quarter'].astype(str).str.strip()
        df['Sub Category'] = df['Sub Category'].astype(str).str.strip()
        df['Jewelry Collection'] = df['Jewelry Collection'].astype(str).str.strip()
        df['Jewelry_Type'] = df['Jewelry Type'].astype(str).str.strip()
        df['Purchase Type'] = df['Purchase Type'].astype(str).str.strip()
        df['Return Type'] = df['Return Type'].astype(str).str.strip()


        # Add more columns as needed

        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, engine='xlsxwriter')

            # Access the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']

            worksheet.set_column(3, 3, 90)
            worksheet.set_column(4, 21, 40)

            for row_num in range(1, len(df) + 1):
                worksheet.set_row(row_num, 55)  # Increase height to 50

            # Add images to the worksheet
            for idx, image_path in enumerate(df['Image']):
                if image_path is not None:
                    worksheet.insert_image(idx + 1, 1, image_path, {'x_offset': 30, 'y_offset': 20})  # Insert image path in the second column
            for i, width in enumerate([15, 15, 15]):  # You can adjust widths as needed
                worksheet.set_column(i, i, width)

            cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
            for row_num in range(1, len(df) + 1):
                for col_num in range(len(df.columns)):
                    worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], cell_format)

        # Get Excel file content from the buffer
        excel_data = excel_buffer.getvalue()

        cursor.close()
        conn.close()

        return excel_data
    except Exception as e:
        logging.error(f"An error occurred while retrieving data and exporting to Excel: {e}")
        return None

@app.route('/Report/Jewelers_id/<path:data>/<path:data1>/Order')
def jewelers_order_report(data, data1):
    try:
        # Decode the base64 encoded data
        decoded_data = base64.b64decode(data).decode('utf-8')
        decoded_data1 = base64.b64decode(data1).decode('utf-8')
        # Assuming decoded_data is the filter value, you can use it in your application logic
        # Your other logic for obtaining report_id, embed_url, and embed_token
        report_id = handler.config.REPORT_ID_ORDER
        embed_url = handler.get_embed_url(report_id)
        embed_token = handler.get_access_token()
        # Log the decoded data
        app.logger.info(f"Decoded data: {decoded_data}")
        app.logger.info(f"Decoded data1: {decoded_data1}")
        return render_template('order_report.html', embed_url=embed_url, embed_token=embed_token,
                               Jewelers_id=decoded_data, Jewelers_id1=decoded_data1)
    except Exception as e:
        app.logger.error(f"An error occurred in jewelers_order_report: {e}")

@app.route('/Report/Jewelers_id/Sales/<path:data>/Order')
def jewelers_order_report1(data):
    try:
        # Decode the base64 encoded data
        decoded_data = base64.b64decode(data).decode('utf-8')
        # Assuming decoded_data is the filter value, you can use it in your application logic

        # Your other logic for obtaining report_id, embed_url, and embed_token
        report_id = handler.config.REPORT_ID_SALESMAN
        embed_url = handler.get_embed_url(report_id)
        embed_token = handler.get_access_token()

        # Log the decoded data
        app.logger.info(f"Decoded data: {decoded_data}")

        return render_template('Salesman.html', embed_url=embed_url, embed_token=embed_token,
                               Sales_id=decoded_data)
    except Exception as e:
        # Handle exceptions here
        app.logger.error(f"Error processing request: {str(e)}")
        # Return an error response or redirect to an error page

@app.route('/download_csv/<path:data>', methods=['GET'])
def download_csv(data):
    try:
        # Use the dynamic filter value (data) in your retrieve_data_and_export function

        csv_data = retrieve_data_and_export(data)
        if not isinstance(csv_data, bytes):
            csv_data = csv_data.encode()
        # Create a BytesIO object to store the data
        buffer = io.BytesIO(csv_data)
        # Return the file as an attachment
        return send_file(buffer, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name='ASHI-Analytics_Report.xlsx')
    except Exception as e:
        logging.error(f"An error occurred in download_csv: {e}")

@app.route('/send-email/<string:data>', methods=['GET', 'POST'])
def send_email(data):
    try:
        recipients = request.form['recipient']
        cc = request.form.get('cc', '').strip()
        subject = request.form['subject']
        body = request.form['body']

        # Fetch the CSV file content from the download_csv route
        csv_data_response = requests.get(f'http://localhost:5000/download_csv/{data}')
        if csv_data_response.status_code == 200:
            csv_data = csv_data_response.content

            # Split the recipients and CC addresses by comma and remove any extra spaces
            recipients_list = [recipient.strip() for recipient in recipients.split(',')]
            cc_list = [c.strip() for c in cc.split(',')]

            # Compose email
            msg = MIMEMultipart()
            msg['From'] = 'no-reply@ashidiamonds.com'
            msg['To'] = ', '.join(recipients_list)
            msg['Cc'] = ', '.join(cc_list)
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Attach CSV file
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(csv_data)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="ASHI-Analytics_Report.xlsx"')
            msg.attach(part)

            # Send email using smtplib
            smtp_server = config.SMTP_SERVER
            smtp_port = config.SMTP_PORT
            sender_email = config.SENDER_EMAIL
            sender_password = config.SENDER_PASSWORD

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)

            # Combine recipients and CC into one list
            all_recipients = recipients_list + cc_list

            # Ensure proper formatting for recipients
            to_addrs = all_recipients

            server.sendmail(sender_email, to_addrs, msg.as_string())
            server.quit()

            return jsonify({'message': 'Email sent successfully'})
        else:
            return jsonify({'error': 'Failed to fetch excel data'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)



'''''''''''

ReportSection4f6efc02d8b2ef134d9b


ReportSection886526c8274918113c1b
ReportSection021dbe73049900d6d28a
ReportSection158f7199a8cb11347181
ReportSectionb883514b5a008f2cf3f6
ReportSectionfdd75562d9d8b6b21eba
ReportSectionfb46805b79aa80c77c3b
ReportSectionc6f485dbd4a995e4d133
ReportSection171029db52e688e1ecb0
ReportSection3f998fc4c670152df728
ReportSection05cd8683127a4a032dde
ReportSectionbf68587d97b6809af588
ReportSectionc09c681597a1d9a3af58
ReportSection5d25180e9cabe04f8ddc
ReportSection675b6d054bbda6e42f15

'''''''''''
