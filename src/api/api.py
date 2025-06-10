import os, uuid
from functools import wraps
from src.core.config import Config
from src.sqldb.admin_auth import AdminAuthManager
from src.controller.system_controller import SystemController
from flask import Blueprint, request, jsonify, session, current_app

api_blueprint = Blueprint('api', __name__)
system_controller = SystemController()
admin_auth = AdminAuthManager()

def is_admin_logged_in():
    return session.get('admin_logged_in') is True

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_logged_in():
            return jsonify({'error': 'Admin login required'}), 401
        return f(*args, **kwargs)

    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@api_blueprint.route('/api/query', methods=['POST'])
def query():
    data = request.json
    query_text = data.get('query', '')
    session_id = data.get('session_id')
    if not query_text:
        return jsonify({'error': 'Query is required'}), 400
    response = system_controller.process_query(query_text, session_id)
    return jsonify(response)

@api_blueprint.route('/api/sessions', methods=['GET'])
def get_sessions():
    user_id = session.get('user_id', 'anonymous')
    sessions = system_controller.get_user_sessions(user_id)
    return jsonify({'sessions': sessions})

@api_blueprint.route('/api/sessions', methods=['POST'])
def create_session():
    user_id = session.get('user_id', 'anonymous')
    session_data = system_controller.create_session(user_id)
    return jsonify(session_data)

@api_blueprint.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    session_data = system_controller.get_session(session_id)
    if not session_data:
        return jsonify({'error': 'Session not found'}), 404
    return jsonify(session_data)

@api_blueprint.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    success = system_controller.delete_session(session_id)
    if success:
        return jsonify({'success': True, 'message': 'Session deleted'})
    return jsonify({'error': 'Failed to delete session'}), 500

@api_blueprint.route('/api/upload', methods=['POST'])
@admin_login_required
def upload_document():
    if 'document' not in request.files:
        return jsonify({'error': 'No document part'}), 400
    files = request.files.getlist('document')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No selected file'}), 400
    results = []
    for file in files:
        if file and allowed_file(file.filename):
            original_filename = file.filename
            unique_filename = str(uuid.uuid4()) + '_' + original_filename
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            success = system_controller.process_document(filepath, unique_filename, original_filename)
            results.append({'filename': original_filename, 'success': success, 'id': unique_filename})
        else:
            results.append({'filename': file.filename, 'success': False, 'error': 'File type not allowed'})
    successful_uploads = [r for r in results if r['success']]
    if len(successful_uploads) == len(files):
        return jsonify({'success': True, 'message': f'{len(successful_uploads)} document(s) uploaded and processed successfully.', 'results': results})
    if len(successful_uploads) > 0:
        return jsonify({'success': False, 'message': f'{len(successful_uploads)} of {len(files)} documents uploaded. Some failed.', 'results': results}), 207
    return jsonify({'success': False, 'message': 'No documents were successfully uploaded.', 'results': results}), 400

@api_blueprint.route('/api/documents', methods=['GET'])
@admin_login_required
def get_documents():
    documents = system_controller.get_documents()
    return jsonify({'documents': documents})

@api_blueprint.route('/api/document/<document_id>', methods=['DELETE'])
@admin_login_required
def delete_document_route(document_id):
    if not document_id:
        return jsonify({'error': 'Document ID is required'}), 400
    success = system_controller.delete_document(document_id)
    if success:
        return jsonify({'success': True, 'message': f'Document {document_id} deleted successfully.'})
    return jsonify({'error': f'Failed to delete document {document_id}. It might not exist or an error occurred.'}), 500

@api_blueprint.route('/api/documents/delete', methods=['POST'])
@admin_login_required
def mass_delete_documents():
    data = request.get_json()
    ids = data.get('ids', [])
    if not ids or not isinstance(ids, list):
        return jsonify({'error': 'No document IDs provided.'}), 400
    deleted, failed = [], []
    for doc_id in ids:
        if system_controller.delete_document(doc_id):
            deleted.append(doc_id)
        else:
            failed.append(doc_id)
    if failed:
        return jsonify({
            'success': False,
            'message': f"Deleted {len(deleted)} document(s), failed to delete {len(failed)}.",
            'deleted_ids': deleted,
            'failed_ids': failed
        }), 207
    return jsonify({
        'success': True,
        'message': f"Deleted {len(deleted)} document(s) successfully.",
        'deleted_ids': deleted
    })

@api_blueprint.route('/api/admins', methods=['GET'])
@admin_login_required
def get_admins():
    admins = admin_auth.get_all_admins()
    return jsonify({'admins': admins})

@api_blueprint.route('/api/admin/<username>', methods=['DELETE'])
@admin_login_required
def delete_admin(username):
    data = request.get_json() or {}
    serial_key = data.get('serial_key', '')
    if serial_key != Config.ADMIN_SERIAL_KEY:
        return jsonify({'error': 'Invalid software serial key.'}), 403
    current_admin = session.get('admin_username')
    if username == current_admin:
        session.clear()
        deleted, msg = admin_auth.delete_admin(username)
        if deleted:
            return jsonify({'success': True, 'message': 'You have deleted your own account and have been signed out.'})
        return jsonify({'error': msg}), 500
    deleted, msg = admin_auth.delete_admin(username)
    if deleted:
        return jsonify({'success': True, 'message': f'Admin {username} deleted.'})
    return jsonify({'error': msg}), 500

@api_blueprint.route('/api/admins/delete', methods=['POST'])
@admin_login_required
def mass_delete_admins():
    data = request.get_json() or {}
    usernames = data.get('usernames', [])
    serial_key = data.get('serial_key', '')
    if serial_key != Config.ADMIN_SERIAL_KEY:
        return jsonify({'error': 'Invalid software serial key.'}), 403
    current_admin = session.get('admin_username')
    deleted, failed, self_deleted = [], [], False
    for username in usernames:
        ok, msg = admin_auth.delete_admin(username)
        if ok:
            deleted.append(username)
            if username == current_admin:
                self_deleted = True
        else:
            failed.append({'username': username, 'error': msg})
    if self_deleted:
        session.clear()
    return jsonify({
        'success': True,
        'deleted': deleted,
        'failed': failed,
        'self_deleted': self_deleted
    })

@api_blueprint.route('/api/sessions/delete', methods=['POST'])
def mass_delete_sessions():
    data = request.get_json() or {}
    ids = data.get('ids', [])
    if not ids or not isinstance(ids, list):
        return jsonify({'error': 'No session IDs provided.'}), 400
    deleted, failed = [], []
    for session_id in ids:
        if system_controller.delete_session(session_id):
            deleted.append(session_id)
        else:
            failed.append(session_id)
    if failed:
        return jsonify({
            'success': False,
            'message': f"Deleted {len(deleted)} session(s), failed to delete {len(failed)}.",
            'deleted_ids': deleted,
            'failed_ids': failed
        }), 207
    return jsonify({
        'success': True,
        'message': f"Deleted {len(deleted)} session(s) successfully.",
        'deleted_ids': deleted
    })

@api_blueprint.route('/api/sessions/<session_id>/rename', methods=['POST'])
def rename_session(session_id):
    data = request.get_json() or {}
    new_name = data.get('name', '').strip()
    if not new_name:
        return jsonify({'error': 'Session name cannot be empty.'}), 400
    session_data = system_controller.get_session(session_id)
    if not session_data:
        return jsonify({'error': 'Session not found.'}), 404
    session_data['name'] = new_name
    ok = system_controller.session_controller.save_session(session_data)
    if ok:
        return jsonify({'success': True, 'message': 'Session renamed.'})
    return jsonify({'error': 'Failed to save session.'}), 500
