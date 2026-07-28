from datetime import datetime, timezone
from extensions import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship to Contact
    contacts = db.relationship('Contact', backref='owner', lazy=True, cascade="all, delete-orphan")

    def set_password(self, raw_password):
        """Hashes raw password using Bcrypt."""
        self.password = bcrypt.generate_password_hash(raw_password).decode('utf-8')

    def check_password(self, raw_password):
        """Verifies raw password against stored Bcrypt hash."""
        return bcrypt.check_password_hash(self.password, raw_password)

    def to_dict(self):
        """Returns JSON representation of user object (excluding password)."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Contact(db.Model):
    __tablename__ = 'contacts'

    c_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    ph_no = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    company_name = db.Column(db.String(120), nullable=True)
    relation_profession = db.Column(db.String(120), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    hide_code = db.Column(db.String(50), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self, include_hide_code=False):
        """Returns JSON representation of contact."""
        data = {
            "c_id": self.c_id,
            "user_id": self.user_id,
            "name": self.name,
            "ph_no": self.ph_no,
            "email": self.email or "",
            "company_name": self.company_name or "",
            "relation_profession": self.relation_profession or "",
            "image_url": self.image_url or "",
            "is_hidden": bool(self.hide_code and self.hide_code.strip()),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        if include_hide_code:
            data["hide_code"] = self.hide_code or ""
        return data
