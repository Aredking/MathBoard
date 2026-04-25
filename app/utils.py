"""
Вспомогательные утилиты.
"""

import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def save_uploaded_file(file, subfolder='tasks'):
    if not file:
        return None
    original_filename = secure_filename(file.filename)
    name, ext = os.path.splitext(original_filename)
    unique_name = f"{uuid.uuid4().hex}_{name}{ext}"
    if subfolder == 'avatars':
        upload_folder = current_app.config['AVATAR_FOLDER']
    else:
        upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, unique_name)
    file.save(file_path)
    return unique_name


def delete_uploaded_file(filename, subfolder='tasks'):
    if not filename:
        return
    if subfolder == 'avatars':
        folder = current_app.config['AVATAR_FOLDER']
    else:
        folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(folder, filename)
    if os.path.exists(file_path):
        os.remove(file_path)


def generate_slug(text):
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def format_datetime(dt, format='%d.%m.%Y %H:%M'):
    if dt:
        return dt.strftime(format)
    return ''