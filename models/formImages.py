from db import db

class FormImages(db.Model):
    __tablename__ = 'installation_form_images'

    imageName = db.Column(db.String(512), primary_key=True)
    imageData = db.Column(db.LargeBinary(length=(2**32)-1))
    indexnum = db.Column(db.String(512))
    status = db.Column(db.String(512))

    formId = db.Column(db.String(512), db.ForeignKey('installation_form_entry.formId'))
    form = db.relationship('InstallationFormEntry')

    def __init__(self, imageName, imageData, indexnum, status, formId):
        self.imageName = imageName
        self.imageData = imageData
        self.indexnum = indexnum
        self.status = status
        self.formId = formId