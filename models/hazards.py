from db import db

class Hazards(db.Model):
    __tablename__ = 'installation_form_hazards'

    hazardId = db.Column(db.Integer, primary_key=True)
    hazardName = db.Column(db.String(512))
    probability = db.Column(db.String(512))
    consequence = db.Column(db.String(512))
    risk = db.Column(db.String(512))
    controlMeasure = db.Column(db.String(512))
    person = db.Column(db.String(512))
    status = db.Column(db.String(512))

    formId = db.Column(db.String(512), db.ForeignKey('installation_form_entry.formId'))
    form = db.relationship('InstallationFormEntry')

    def __init__(self, hazardName, probability, consequence, risk, controlMeasure, person, status, formId):
        self.hazardName = hazardName
        self.probability = probability
        self.consequence = consequence
        self.risk = risk
        self.controlMeasure = controlMeasure
        self.person = person
        self.status = status
        self.formId = formId
