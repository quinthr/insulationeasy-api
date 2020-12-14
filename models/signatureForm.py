from db import db

class SignatureForm(db.Model):
    __tablename__ = 'installation_form_signatures'

    signatureId = db.Column(db.Integer, primary_key=True)
    signatureName = db.Column(db.String(512))
    signaturePoints = db.Column(db.TEXT)
    signatureImage = db.Column(db.BLOB)

    formId = db.Column(db.String(512), db.ForeignKey('installation_form_entry.formId'))
    form = db.relationship('InstallationFormEntry')

    def __init__(self, signatureName, signaturePoints, signatureImage, formId):
        self.signatureName = signatureName
        self.signaturePoints = signaturePoints
        self.signatureImage = signatureImage
        self.formId = formId


