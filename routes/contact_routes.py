from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Contact

contact_bp = Blueprint('contacts', __name__)

@contact_bp.route('/create', methods=['POST'])
@contact_bp.route('/api/contacts/create', methods=['POST'])
@jwt_required()
def create_contact():
    """
    Endpoint to create a new contact.
    Fields: name, ph_no, email, company_name, relation_profession, image_url, hide_code
    """
    user_id = int(get_jwt_identity())

    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})

    name = data.get('name', '').strip()
    ph_no = data.get('ph_no', '').strip() or data.get('ph_number', '').strip() or data.get('phone', '').strip()
    email = data.get('email', '').strip()
    company_name = data.get('company_name', '').strip() or data.get('company', '').strip()
    relation_profession = data.get('relation_profession', '').strip() or data.get('relation', '').strip() or data.get('profession', '').strip()
    image_url = data.get('image_url', '').strip() or data.get('img_url', '').strip() or data.get('profile_image_url', '').strip()
    hide_code = data.get('hide_code', '').strip() or data.get('code', '').strip()

    if not name or not ph_no:
        return jsonify({
            "status": 400,
            "error": "Bad Request",
            "message": "Name and Ph No. are required fields."
        }), 400

    contact = Contact(
        user_id=user_id,
        name=name,
        ph_no=ph_no,
        email=email,
        company_name=company_name,
        relation_profession=relation_profession,
        image_url=image_url,
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
            (Contact.company_name.ilike(search_filter)) |
            (Contact.relation_profession.ilike(search_filter))
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
    if 'relation_profession' in data:
        contact.relation_profession = data['relation_profession'].strip()
    elif 'relation' in data:
        contact.relation_profession = data['relation'].strip()
    elif 'profession' in data:
        contact.relation_profession = data['profession'].strip()
    if 'image_url' in data:
        contact.image_url = data['image_url'].strip()
    elif 'img_url' in data:
        contact.image_url = data['img_url'].strip()
    elif 'profile_image_url' in data:
        contact.image_url = data['profile_image_url'].strip()
    if 'hide_code' in data:
        contact.hide_code = data['hide_code'].strip() if data['hide_code'].strip() else None

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
