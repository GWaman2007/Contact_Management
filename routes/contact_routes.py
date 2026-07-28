import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from extensions import db
from models import Contact

contact_bp = Blueprint('contacts', __name__)

def allowed_file(filename):
    """Check if uploaded file has an allowed image extension."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']

def handle_photo_upload(req):
    """Extract and save uploaded photo file if present."""
    if 'photo_file' in req.files:
        file = req.files['photo_file']
    elif 'photo' in req.files:
        file = req.files['photo']
    else:
        file = None

    if file and file.filename != '':
        if allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(save_path)
            return unique_filename
    return None


# Helper decorator to allow optional or required JWT authentication
@contact_bp.route('/create', methods=['POST'])
@contact_bp.route('/api/contacts/create', methods=['POST'])
@jwt_required()
def create_contact():
    """
    Endpoint to create a new contact.
    Accepts JSON or multipart/form-data.
    Fields: name, ph_no, email, company_name, hide_code, photo_file (file upload or string)
    """
    user_id = int(get_jwt_identity())

    # Get data from JSON or form fields
    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})

    name = data.get('name', '').strip()
    ph_no = data.get('ph_no', '').strip() or data.get('ph_number', '').strip() or data.get('phone', '').strip()
    email = data.get('email', '').strip()
    company_name = data.get('company_name', '').strip() or data.get('company', '').strip()
    hide_code = data.get('hide_code', '').strip() or data.get('code', '').strip()

    if not name or not ph_no:
        return jsonify({
            "status": 400,
            "error": "Bad Request",
            "message": "Name and Ph No. are required fields."
        }), 400

    # Handle photo upload or photo string
    uploaded_photo = handle_photo_upload(request)
    photo_file = uploaded_photo or data.get('photo_file', '')

    contact = Contact(
        user_id=user_id,
        name=name,
        ph_no=ph_no,
        email=email,
        company_name=company_name,
        photo_file=photo_file,
        hide_code=hide_code if hide_code else None
    )

    db.session.add(contact)
    db.session.commit()

    return jsonify({
        "status": 201,
        "message": "Contact created successfully",
        "contact": contact.to_dict(include_hide_code=True)
    }), 201


@contact_bp.route('/get', methods=['GET'])
@contact_bp.route('/get/<int:c_id>', methods=['GET'])
@contact_bp.route('/api/contacts/get', methods=['GET'])
@contact_bp.route('/api/contacts/get/<int:c_id>', methods=['GET'])
@jwt_required()
def get_contacts(c_id=None):
    """
    Endpoint to fetch contacts.
    - If c_id is provided: returns single contact.
    - If no c_id: returns list of contacts for logged-in user.
    - General view excludes hidden contacts (hide_code is set) UNLESS 'code' parameter is provided.
    """
    user_id = int(get_jwt_identity())
    given_code = request.args.get('code', '').strip() or request.args.get('hide_code', '').strip()

    # Case 1: Fetch single contact by ID
    if c_id:
        contact = Contact.query.filter_by(c_id=c_id, user_id=user_id).first()
        if not contact:
            return jsonify({
                "status": 404,
                "error": "Not Found",
                "message": f"Contact with c_id {c_id} not found."
            }), 404

        # Check if contact is hidden
        if contact.hide_code and contact.hide_code.strip():
            if given_code != contact.hide_code:
                return jsonify({
                    "status": 403,
                    "error": "Forbidden",
                    "message": "This contact is hidden. Provide the correct hide_code to view."
                }), 403

        return jsonify({
            "status": 200,
            "contact": contact.to_dict(include_hide_code=True)
        }), 200

    # Case 2: Fetch contacts list
    query = Contact.query.filter_by(user_id=user_id)

    if given_code:
        # Show contacts matching the given hide_code
        query = query.filter(Contact.hide_code == given_code)
    else:
        # General view: hide contacts that have a hide_code set
        query = query.filter((Contact.hide_code == None) | (Contact.hide_code == ''))

    contacts = query.order_by(Contact.name.asc()).all()

    return jsonify({
        "status": 200,
        "count": len(contacts),
        "contacts": [c.to_dict(include_hide_code=bool(given_code)) for c in contacts]
    }), 200


@contact_bp.route('/search', methods=['GET'])
@contact_bp.route('/api/contacts/search', methods=['GET'])
@jwt_required()
def search_contacts():
    """
    Endpoint to search contacts by keyword (q).
    HIDDEN CONTACT FEATURE:
    - Normal search: excludes contacts with hide_code.
    - Hidden search: when 'code' parameter is provided, searches ONLY within contacts matching that hide_code.
    """
    user_id = int(get_jwt_identity())
    q = request.args.get('q', '').strip()
    given_code = request.args.get('code', '').strip() or request.args.get('hide_code', '').strip()

    query = Contact.query.filter_by(user_id=user_id)

    if given_code:
        # Reveal contacts matching the specific hide_code
        query = query.filter(Contact.hide_code == given_code)
    else:
        # General search: exclude hidden contacts
        query = query.filter((Contact.hide_code == None) | (Contact.hide_code == ''))

    # If text search query is provided
    if q:
        search_filter = f"%{q}%"
        query = query.filter(
            (Contact.name.ilike(search_filter)) |
            (Contact.ph_no.ilike(search_filter)) |
            (Contact.email.ilike(search_filter)) |
            (Contact.company_name.ilike(search_filter))
        )

    results = query.order_by(Contact.name.asc()).all()

    return jsonify({
        "status": 200,
        "search_query": q,
        "code_provided": bool(given_code),
        "count": len(results),
        "contacts": [c.to_dict(include_hide_code=bool(given_code)) for c in results]
    }), 200


@contact_bp.route('/update/<int:c_id>', methods=['PUT', 'POST'])
@contact_bp.route('/api/contacts/update/<int:c_id>', methods=['PUT', 'POST'])
@jwt_required()
def update_contact(c_id):
    """
    Endpoint to update an existing contact by c_id.
    Accepts JSON or multipart form data.
    """
    user_id = int(get_jwt_identity())
    contact = Contact.query.filter_by(c_id=c_id, user_id=user_id).first()

    if not contact:
        return jsonify({
            "status": 404,
            "error": "Not Found",
            "message": f"Contact with c_id {c_id} not found."
        }), 404

    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})

    if 'name' in data and data['name'].strip():
        contact.name = data['name'].strip()
    if 'ph_no' in data and data['ph_no'].strip():
        contact.ph_no = data['ph_no'].strip()
    elif 'phone' in data and data['phone'].strip():
        contact.ph_no = data['phone'].strip()
    if 'email' in data:
        contact.email = data['email'].strip()
    if 'company_name' in data:
        contact.company_name = data['company_name'].strip()
    if 'hide_code' in data:
        contact.hide_code = data['hide_code'].strip() if data['hide_code'].strip() else None

    # Handle optional photo update
    uploaded_photo = handle_photo_upload(request)
    if uploaded_photo:
        contact.photo_file = uploaded_photo
    elif 'photo_file' in data:
        contact.photo_file = data['photo_file'].strip()

    db.session.commit()

    return jsonify({
        "status": 200,
        "message": "Contact updated successfully",
        "contact": contact.to_dict(include_hide_code=True)
    }), 200


@contact_bp.route('/delete/<int:c_id>', methods=['DELETE', 'POST'])
@contact_bp.route('/api/contacts/delete/<int:c_id>', methods=['DELETE', 'POST'])
@jwt_required()
def delete_contact(c_id):
    """
    Endpoint to delete a contact by c_id.
    """
    user_id = int(get_jwt_identity())
    contact = Contact.query.filter_by(c_id=c_id, user_id=user_id).first()

    if not contact:
        return jsonify({
            "status": 404,
            "error": "Not Found",
            "message": f"Contact with c_id {c_id} not found."
        }), 404

    db.session.delete(contact)
    db.session.commit()

    return jsonify({
        "status": 200,
        "message": f"Contact with c_id {c_id} deleted successfully."
    }), 200


@contact_bp.route('/uploads/<filename>', methods=['GET'])
@jwt_required()
def serve_upload(filename):
    """
    Secure endpoint to serve uploaded contact photo.
    Requires JWT authentication and verifies that the file belongs to a contact owned by the user.
    If the contact is hidden, also requires valid hide_code.
    """
    user_id = int(get_jwt_identity())
    given_code = request.args.get('code', '').strip() or request.args.get('hide_code', '').strip()

    # Find contact owned by current user matching photo_file
    contact = Contact.query.filter_by(user_id=user_id, photo_file=filename).first()

    if not contact:
        return jsonify({
            "status": 403,
            "error": "Forbidden",
            "message": "Access denied. Photo not found or does not belong to your account."
        }), 403

    # Check if contact is hidden
    if contact.hide_code and contact.hide_code.strip():
        if given_code != contact.hide_code:
            return jsonify({
                "status": 403,
                "error": "Forbidden",
                "message": "This photo belongs to a hidden contact. Provide the correct hide_code to access."
            }), 403

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

