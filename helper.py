import smtplib
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def client_connection(user_email, user_email_password, sent_from, to, email_text):
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.ehlo()
    smtp_server.login(user_email, user_email_password)
    smtp_server.sendmail(sent_from, to, email_text)
    smtp_server.close()
    logging.info("Email sent successfully for cloud build!")


def send_cloud_build_failed_email(
        project: str,
        pipeline: str,
        user_email: str,
        user_email_password: str,
        receiver_email: str
):
    sent_from = user_email
    to = [receiver_email]
    subject = 'Pipeline Cloud Build Status'
    body = f'''
    This is to inform the status of cloud build of your pipeline: "{pipeline}"
    for project: "{project}" has failed!
    '''
    email_text = """
    From: {}
    To: {}
    Subject: {}

    {}
    """.format(sent_from, ", ".join(to), subject, body)

    try:
        client_connection(user_email, user_email_password, sent_from, to, email_text)
    except Exception as e:
        raise ValueError(f"Some error occurred in sending email: {e}")


def send_cloud_build_success_email(
        project: str,
        pipeline: str,
        user_email: str,
        user_email_password: str,
        receiver_email: str
):
    sent_from = user_email
    to = [receiver_email]
    subject = 'Pipeline Cloud Build Status'
    body = f'''
    This is to inform the status of cloud build of your pipeline: "{pipeline}"
    for project: "{project}" has executed successfully.
    '''
    email_text = """
    From: {}
    To: {}
    Subject: {}

    {}
    """.format(sent_from, ", ".join(to), subject, body)

    try:
        client_connection(user_email, user_email_password, sent_from, to, email_text)
    except Exception as e:
        raise ValueError(f"Some error occurred in sending email: {e}")
