import imaplib
import email
from email.header import decode_header
from email.utils import parseaddr
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

class EmailClient:
    def __init__(self, email_address: str, password: str, imap_server: str, port: int = 993):
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.port = port
        self.imap = None

    def connect(self) -> bool:
        try:
            self.imap = imaplib.IMAP4_SSL(self.imap_server, self.port)
            self.imap.login(self.email_address, self.password)
            return True
        except Exception as e:
            print(f"Failed to connect: {str(e)}")
            return False

    def disconnect(self):
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass

    def list_mailboxes(self) -> list:
        if not self.imap:
            return []
        
        mailboxes = []
        try:
            result, data = self.imap.list()
            if result == 'OK':
                for item in data:
                    decoded = item.decode('utf-8')
                    mailboxes.append(decoded)
        except Exception as e:
            print(f"Error listing mailboxes: {str(e)}")
        return mailboxes

    def get_emails(self, mailbox: str = 'INBOX', limit: int = 10) -> list:
        if not self.imap:
            print("Not connected to email server")
            return []

        emails = []
        try:
            self.imap.select(mailbox)
            
            # get unread emails in the last 10 days
            since_date = (datetime.now() - timedelta(days=10)).strftime("%d-%b-%Y")
            search_criteria = f'(UNSEEN SINCE {since_date})'
            
            # NOTE: This actually gets all emails every time. This allows
            # you to run the demo multiple times.
            # The lines above are how you _would_ filter by unread
            # emails in the last 10 days.
            search_criteria = 'ALL' 
            
            result, data = self.imap.search(None, search_criteria)
            if result != 'OK':
                return []

            email_ids = data[0].split()
            for email_id in email_ids[-limit:]:
                result, data = self.imap.fetch(email_id, '(RFC822)')
                if result != 'OK':
                    continue

                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                subject = decode_header(msg["subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                
                sender = decode_header(msg.get("from", ""))[0][0]
                if isinstance(sender, bytes):
                    sender = sender.decode()
                
                # Extract just the email address using parseaddr
                _, sender = parseaddr(sender)

                # Extract the email body (plain text)
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            charset = part.get_content_charset() or "utf-8"
                            body = part.get_payload(decode=True).decode(charset, errors="replace")
                            break
                else:
                    charset = msg.get_content_charset() or "utf-8"
                    body = msg.get_payload(decode=True).decode(charset, errors="replace")

                emails.append({
                    'id': email_id.decode(),
                    'subject': subject,
                    'sender': sender,
                    'date': msg.get("date", ""),
                    'content': body
                })

        except Exception as e:
            print(f"Error fetching emails: {str(e)}")
        
        return emails 

    def send_email(self, to_address, subject, body):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.email_address
        msg['To'] = to_address

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(self.email_address, self.password)
            server.sendmail(self.email_address, [to_address], msg.as_string()) 