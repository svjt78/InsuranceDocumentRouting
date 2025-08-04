import os
import requests
import json
from dotenv import load_dotenv
from .config import AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, USER_EMAIL, ATTACHMENTS_DIR
load_dotenv()

def get_access_token():
    url = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": AZURE_CLIENT_ID,
        "client_secret": AZURE_CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "https://graph.microsoft.com/.default"
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def fetch_unread_emails(token):
    url = f"https://graph.microsoft.com/v1.0/users/{USER_EMAIL}/mailFolders/Inbox/messages?$filter=isRead eq false&$top=1"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("value", [])

def download_attachments(message_id, token):
    url = f"https://graph.microsoft.com/v1.0/users/{USER_EMAIL}/messages/{message_id}/attachments"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    attachments = response.json()["value"]
    
    attachment_list = []
    
    for att in attachments:
        if att["@odata.type"] == "#microsoft.graph.fileAttachment" and (att["name"].endswith(".pdf") or att["name"].endswith(".docx")):
            file_data = att["contentBytes"]
            attachment_list.append({
                "filename": att["name"],
                "content_base64": file_data
            })
    
    return attachment_list

def extract_email_data():
    token = get_access_token()
    emails = fetch_unread_emails(token)
    
    if not emails:
        print("No unread emails.")
        return
    email = emails[0]  # Get the first unread email
    message_id = email["id"]
    subject = email["subject"]
    body = email["body"]["content"]
    attachments = download_attachments(message_id, token)
    
    email_data = {
        "subject": subject,
        "body": body,
        "attachments": attachments
    }
    
    return email_data