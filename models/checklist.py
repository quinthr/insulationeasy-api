from db import db

class Checklist(db.Model):
    __tablename__ = 'installation_form_checklist'

    check_id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(512))
    status = db.Column(db.String(512))

    formId = db.Column(db.String(512), db.ForeignKey('installation_form_entry.formId'))
    form = db.relationship('InstallationFormEntry')

    def __init__(self, text, status, formId):
        self.text = text
        self.status = status
        self.formId = formId