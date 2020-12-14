from db import db
from models.checklist import *
from models.formImages import *
from models.hazards import *
from models.signatureForm import *

class InstallationFormEntry(db.Model):
    __tablename__ = 'installation_form_entry'

    id = db.Column(db.Integer, primary_key=True)
    formId = db.Column(db.String(512), unique=True)
    orderNumber = db.Column(db.String(512))
    builderName = db.Column(db.String(512))
    address = db.Column(db.String(512))
    date = db.Column(db.String(512))
    comments = db.Column(db.String(1000))
    workSiteEvaluator = db.Column(db.String(512))
    workSiteEvaluatedDate = db.Column(db.String(512))
    builderConfirmation = db.Column(db.String(512))
    builderConfirmationDate = db.Column(db.String(512))
    assessorName = db.Column(db.String(512))
    status = db.Column(db.String(512))
    workerName = db.Column(db.String(512))

    checklists = db.relationship('Checklist', lazy='dynamic')
    images = db.relationship('FormImages', lazy='dynamic')
    hazards = db.relationship('Hazards', lazy='dynamic')
    signatureForms = db.relationship('SignatureForm', lazy='dynamic')

    def __init__(self, formId, orderNumber, builderName, address, date, comments, workSiteEvaluator, workSiteEvaluatedDate, builderConfirmation, builderConfirmationDate, assessorName, status, workerName):
        self.formId = formId
        self.orderNumber = orderNumber
        self.builderName = builderName
        self.address = address
        self.date = date
        self.comments = comments
        self.workSiteEvaluator = workSiteEvaluator
        self.workSiteEvaluatedDate = workSiteEvaluatedDate
        self.builderConfirmation = builderConfirmation
        self.builderConfirmationDate = builderConfirmationDate
        self.assessorName = assessorName
        self.status = status
        self.workerName = workerName

