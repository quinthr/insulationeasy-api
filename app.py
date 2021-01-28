import base64, jwt, imghdr, io
from flask import Flask, request, jsonify, render_template
from functools import wraps
from flask_httpauth import HTTPBasicAuth
import smtplib
from email.message import EmailMessage
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter, inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak

from models.installationFormEntry import *
from db import db

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://soundpro_insulationeasy_form_app:bt0{L&+$TYWx@localhost:3306/soundpro_insulationeasy_form_app' #mysql://username:password@server/db
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost:3306/insulationeasyapp' #mysql://username:password@server/db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = 'InsulationEasyAustralia&SoundproofingProductsAustralia'

db.init_app(app)

auth = HTTPBasicAuth()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        secretkey = app.config['SECRET_KEY']
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            if base64.b64decode(token).decode("utf-8") == secretkey:
                print('')
            else:
                return jsonify({'message': 'Token is missing!'}), 401
        else:
            return jsonify({'message': 'Token is missing!'}), 401

        return f(*args, **kwargs)

    return decorated

@app.before_first_request
def createTables():
    with app.app_context():
        db.create_all()

createTables()


@app.route('/')
def first():
    print('HELLO WORLD')
    return print('HELLO WORLD')

@app.route('/api/entries', methods=['GET'])
def getFormEntries():
    entries = InstallationFormEntry.query.all()
    return jsonify({'entries': entries})

@app.route('/api/images', methods=['GET'])
@token_required
def showImages():
    entries = FormImages.query.all()
    img = base64.b64encode(entries[0].imageData)
    decoded= img.decode("utf-8")
    img1 = base64.b64encode(entries[1].imageData)
    decoded2 = img1.decode("utf-8")
    img2 = base64.b64encode(entries[2].imageData)
    decoded3 = img2.decode("utf-8")
    return render_template("image.html",img = decoded, img1=decoded2, img2 = decoded3)

@app.route('/api/signatures', methods=['GET'])
def showSignatures():
    entries = SignatureForm.query.all()
    img = base64.b64encode(entries[0].signatureImage)
    decoded= img.decode("utf-8")
    img1 = base64.b64encode(entries[1].signatureImage)
    decoded2 = img1.decode("utf-8")
    return render_template("signature.html",img = decoded, img1=decoded2)

@app.route('/api/entry/upload', methods=['POST'])
@token_required
def uploadEntry():
    data = request.get_json()
    entry = InstallationFormEntry(formId=data['formId'], orderNumber=data['orderNumber'], builderName=data['builderName'],
                                      address=data['address'], date=data['date'], comments=data['comments'],
                                      workSiteEvaluator=data['workSiteEvaluator'],
                                      workSiteEvaluatedDate=data['workSiteEvaluatedDate'],
                                      builderConfirmation = data['builderConfirmation'],
                                      builderConfirmationDate= data['builderConfirmationDate'],
                                      assessorName = data['assessorName'],
                                      status = 'Done', workerName=data['workerName'])
    db.session.add(entry)
    try:
        db.session.commit()
        return jsonify({'message': 'Added successfully!'})
    except:
        return jsonify({'message': 'Failed to add!'})

@app.route('/api/checklist/upload', methods=['POST'])
@token_required
def uploadChecklist():
    data = request.get_json()
    checklist = Checklist(text=data['text'], status='Done', formId=data['formId'])
    db.session.add(checklist)
    try:
        db.session.commit()
        return jsonify({'message': 'Added successfully!'})
    except:
        return jsonify({'message': 'Failed to add!'})

@app.route('/api/image/upload', methods=['POST'])
@token_required
def uploadImage():
    data = request.get_json()
    if data['imageData'] is None:
        imageData = None
    else:
        imageData = base64.b64decode(data['imageData'])
    image = FormImages(imageName=data['imageName'], imageData=imageData, indexnum=data['indexnum'], status='Done', formId=data['formId'])
    db.session.add(image)
    try:
        db.session.commit()
        return jsonify({'message': 'Added successfully!'})
    except Exception as error:
        print(str(error))
        return jsonify({'message': 'Failed to add!'})

@app.route('/api/hazard/upload', methods=['POST'])
@token_required
def uploadHazard():
    data = request.get_json()
    hazard = Hazards(hazardName=data['hazardName'], probability=data['probability'], consequence=data['consequence'],
                     risk=data['risk'], controlMeasure=data['controlMeasure'], person=data['person'],
                     status='Done', formId=data['formId'])
    db.session.add(hazard)
    try:
        db.session.commit()
        return jsonify({'message': 'Added successfully!'})
    except Exception as error:
        print(str(error))
        return jsonify({'message': 'Failed to add!'})

@app.route('/api/signature/upload', methods=['POST'])
@token_required
def uploadSignature():
    data = request.get_json()
    signatureImage = base64.b64decode(data['signatureImage'])
    signature = SignatureForm(signatureName=data['signatureName'], signaturePoints=data['signaturePoints'],
                              signatureImage=signatureImage, formId=data['formId'])
    db.session.add(signature)
    try:
        db.session.commit()
        return jsonify({'message': 'Added successfully!'})
    except Exception as error:
        print(str(error))
        return jsonify({'message': 'Failed to add!'})

@app.route('/api/update/entries', methods=['POST'])
@token_required
def updateFormEntries():
    dataList = request.get_json()
    entries = InstallationFormEntry.query.all()
    list = []
    for entry in entries:
        if entry.formId in dataList['entries']:
            continue
        else:
            dict = {}
            dict['formId'] = entry.formId
            dict['orderNumber'] = entry.orderNumber
            dict['builderName'] = entry.builderName
            dict['address'] = entry.address
            dict['date'] = entry.date
            dict['comments'] = entry.comments
            dict['workSiteEvaluator'] = entry.workSiteEvaluator
            dict['workSiteEvaluatedDate'] = entry.workSiteEvaluatedDate
            dict['builderConfirmation'] = entry.builderConfirmation
            dict['builderConfirmationDate'] = entry.builderConfirmationDate
            dict['assessorName'] = entry.assessorName
            dict['status'] = entry.status
            dict['workerName'] = entry.workerName
            list.append(dict)
    return jsonify({'entries': list})

def generateFormPDF(data):
    entry = InstallationFormEntry.query.filter_by(formId=data['formId']).first()
    checklist = Checklist.query.filter_by(formId=entry.formId).all()
    _checked1 = False
    _checked2 = False
    _checked3 = False
    _checked4 = False
    _checked5 = False
    _checked6 = False
    _checked11 = False
    _checked12 = False
    _checked13 = False
    _checked14 = False
    _checked15 = False
    _checked16 = False
    _checked17 = False
    for check in checklist:
        if check.text == '_checked1':
            _checked1 = True
        elif check.text == '_checked2':
            _checked2 = True
        elif check.text == '_checked3':
            _checked3 = True
        elif check.text == '_checked4':
            _checked4 = True
        elif check.text == '_checked5':
            _checked5 = True
        elif check.text == '_checked6':
            _checked6 = True
        elif check.text == '_checked11':
            _checked11 = True
        elif check.text == '_checked12':
            _checked12 = True
        elif check.text == '_checked13':
            _checked13 = True
        elif check.text == '_checked14':
            _checked14 = True
        elif check.text == '_checked15':
            _checked15 = True
        elif check.text == '_checked16':
            _checked16 = True
        elif check.text == '_checked17':
            _checked17 = True
    signatures = SignatureForm.query.filter_by(formId=entry.formId).all()
    for signature in signatures:
        if "BuilderSignature" in signature.signatureName:
            builderSignatureImage = ImageReader(io.BytesIO(signature.signatureImage))
        elif "WorkEvaluatorSignature" in signature.signatureName:
            workEvaluatorSignatureImage = ImageReader(io.BytesIO(signature.signatureImage))
    hazardsDB = Hazards.query.filter_by(formId=entry.formId).order_by(Hazards.hazardName.asc()).all()
    imagesDB = FormImages.query.filter_by(formId=entry.formId).all()
    fileName = f"pdf/InsulationEasyForm-{entry.orderNumber}.pdf"
    print(fileName)
    pdf = canvas.Canvas(fileName)
    form = pdf.acroForm
    pdf.setTitle('Insulation Easy Safety Installation Form')
    pdf.drawImage('./assets/images/logo.png', 20, 790, width=150, height=35, mask='auto')
    pdf.setFont(psfontname='Helvetica', size=20)
    pdf.drawCentredString(325, 795, 'Job Safety Analysis')
    pdf.setFont(psfontname='Helvetica', size=12)
    pdf.drawCentredString(300, 770, '*** JSA MUST BE COMPLETED BEFORE STARTING WORK ***')
    pdf.setFont(psfontname='Helvetica', size=14)
    pdf.drawString(30, 740, f'Order #: {entry.orderNumber}')
    pdf.drawString(450, 740, f'Date: {entry.date}')
    pdf.drawString(30, 720, f'Builder Name: {entry.builderName}')
    pdf.drawString(30, 700, f'Address: {entry.address}')
    pdf.drawString(30, 680, 'Items to be checked BEFORE commencement of the installation:')
    pdf.setFont(psfontname='Helvetica', size=12)

    pdf.drawString(35, 661, 'General State of the Work Site is SAFE and Tidy?')
    if _checked1:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=305, y=660)
        pdf.drawString(317, 661, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=345, y=660)
        pdf.drawString(357, 661, 'No')

    else:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=305, y=660)
        pdf.drawString(317, 661, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=345, y=660)
        pdf.drawString(357, 661, 'No')

    pdf.drawString(35, 641, 'Ceiling has no cracks?')
    if _checked2:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=160, y=640)
        pdf.drawString(172, 641, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=200, y=640)
        pdf.drawString(212, 641, 'No')

    else:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=160, y=640)
        pdf.drawString(172, 641, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=200, y=640)
        pdf.drawString(212, 641, 'No')


    pdf.drawString(35, 621, 'Floors clean and tidy?')
    if _checked3:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=160, y=620)
        pdf.drawString(172, 621, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=200, y=620)
        pdf.drawString(212, 621, 'No')

    else:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=160, y=620)
        pdf.drawString(172, 621, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=200, y=620)
        pdf.drawString(212, 621, 'No')

    pdf.drawString(35, 601, 'A safety environment exists?')
    if _checked4:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=190, y=600)
        pdf.drawString(202, 601, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=230, y=600)
        pdf.drawString(242, 601, 'No')

    else:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=190, y=600)
        pdf.drawString(202, 601, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=230, y=600)
        pdf.drawString(242, 601, 'No')

    pdf.drawString(35, 581, 'Lights in place & in working order?')
    if _checked5:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=220, y=580)
        pdf.drawString(232, 581, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=260, y=580)
        pdf.drawString(272, 581, 'No')

    else:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=220, y=580)
        pdf.drawString(232, 581, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=260, y=580)
        pdf.drawString(272, 581, 'No')

    pdf.drawString(35, 561, 'Is the ceiling lining made of asbestos?')
    if _checked6:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=240, y=560)
        pdf.drawString(252, 561, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=280, y=560)
        pdf.drawString(292, 561, 'No')

    else:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=240, y=560)
        pdf.drawString(252, 561, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=280, y=560)
        pdf.drawString(292, 561, 'No')

    pdf.setFont(psfontname='Helvetica', size=14)
    pdf.drawString(30, 540, 'Items to be checked AFTER commencement of the installation:')
    pdf.setFont(psfontname='Helvetica', size=12)
    pdf.drawString(35, 521, 'General State of the Work Site is SAFE and Tidy?')
    if _checked11:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=305, y=520)
        pdf.drawString(317, 521, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=345, y=520)
        pdf.drawString(357, 521, 'No')

    else:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=305, y=520)
        pdf.drawString(317, 521, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=345, y=520)
        pdf.drawString(357, 521, 'No')

    pdf.drawString(35, 501, 'Ceiling has no cracks?')
    if _checked12:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=160, y=500)
        pdf.drawString(172, 501, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=200, y=500)
        pdf.drawString(212, 501, 'No')

    else:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=160, y=500)
        pdf.drawString(172, 501, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=200, y=500)
        pdf.drawString(212, 501, 'No')

    pdf.drawString(35, 481, 'Floors clean and tidy?')
    if _checked13:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=160, y=480)
        pdf.drawString(172, 481, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=200, y=480)
        pdf.drawString(212, 481, 'No')

    else:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=160, y=480)
        pdf.drawString(172, 481, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=200, y=480)
        pdf.drawString(212, 481, 'No')

    pdf.drawString(35, 461, 'Lights in place & in working order?')
    if _checked14:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=220, y=460)
        pdf.drawString(232, 461, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=260, y=460)
        pdf.drawString(272, 461, 'No')

    else:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=220, y=460)
        pdf.drawString(232, 461, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=260, y=460)
        pdf.drawString(272, 461, 'No')

    pdf.drawString(35, 441, 'Insulation packaging removed from site?')
    if _checked17:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=260, y=440)
        pdf.drawString(272, 441, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=300, y=440)
        pdf.drawString(312, 441, 'No')

    else:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=260, y=440)
        pdf.drawString(272, 441, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=300, y=440)
        pdf.drawString(312, 441, 'No')

    pdf.drawString(35, 421, 'Access Aperture clean?')
    if _checked16:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=170, y=420)
        pdf.drawString(182, 421, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=210, y=420)
        pdf.drawString(222, 421, 'No')

    else:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=170, y=420)
        pdf.drawString(182, 421, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=210, y=420)
        pdf.drawString(222, 421, 'No')

    pdf.drawString(35, 401,
                   'Default minimum clearance of insulation around all recessed lights and electrical equipment')
    pdf.drawString(50, 381, 'achieved as per AS/NZS 3000:2007?')
    if _checked17:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=260, y=380)
        pdf.drawString(272, 381, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=300, y=380)
        pdf.drawString(312, 381, 'No')

    else:
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=False,
                      x=260, y=380)
        pdf.drawString(272, 381, 'Yes')
        form.checkbox(borderStyle='solid', borderWidth=1, borderColor=HexColor('#000000'),
                      fillColor=HexColor('#FFFFFF'),
                      textColor=HexColor('#000000'), forceBorder=True, size=10, fieldFlags=1,
                      checked=True,
                      x=300, y=380)
        pdf.drawString(312, 381, 'No')

    pdf.drawString(30, 360,
                   '(Check all areas of the ceiling, if the ceiling is asbestos or you are unsure of its composition you')
    pdf.drawString(30, 340, ' must assume it is ASBESTOS and follow Higgins Asbestos Management Plan)')
    pdf.drawString(30, 320, 'Comments: ')
    comments = entry.comments
    text = pdf.beginText(35, 305)
    for line in comments.splitlines(False):
        text.textLine(line.rstrip())
    pdf.drawText(text)
    pdf.line(30, 220, 550, 220)
    pdf.drawString(30, 200, f'Builder\'s Confirmation: {entry.builderConfirmation}')
    pdf.drawString(300, 200, f'Date: {entry.builderConfirmationDate}')
    pdf.drawString(30, 180, 'Signature')
    pdf.drawImage(builderSignatureImage, 30, 130, width=150, height=35, mask='auto')
    pdf.drawString(30, 100, f'Work Evaluator: {entry.workSiteEvaluator}')
    pdf.drawString(300, 100, f'Date: {entry.workSiteEvaluatedDate}')
    pdf.drawString(30, 80, 'Signature')
    pdf.drawImage(workEvaluatorSignatureImage, 30, 30, width=150, height=35, mask='auto')
    pdf.showPage()
    pdf.drawCentredString(300, 795, 'Job Safety Analysis (JSA) Worksheet')
    pdf.setFont(psfontname='Helvetica', size=9)
    pdf.drawString(30, 780, 'A-Common or Repeating, B-Known to Occur, C-Could Occur, D-Not Likely to Happen, E-Practically Impossible')
    pdf.drawString(30, 760, '1-Fatal or permanent serious injury, 2-Lost time injury or illness, 3-Medical treatment required, 4-First aid treatment, 5-Incident report only')
    pdf.setFont(psfontname='Helvetica', size=12)
    probabilityList = []
    consequenceList = []
    for hazard in hazardsDB:
        currentprobability = 'Not applicable'
        currentconsequence = 'Not applicable'
        if hazard.probability == 'A - Common or repeating':
            currentprobability = 'A'
        elif hazard.probability == 'B - Known to occur':
            currentprobability = 'B'
        elif hazard.probability == 'C - Could occur':
            currentprobability = 'C'
        elif hazard.probability == 'D - Not likely to happen':
            currentprobability = 'D'
        elif hazard.probability == 'E - Practically impossible':
            currentprobability = 'E'
        probabilityList.append(currentprobability)
        if hazard.consequence == '1 - Fatal or permanent serious injury':
            currentconsequence = '1'
        elif hazard.consequence == '2 - Lost time injury or illness':
            currentconsequence = '2'
        elif hazard.consequence == '3 - Medical treatment required':
            currentconsequence = '3'
        elif hazard.consequence == '4 - First aid treatment':
            currentconsequence = '4'
        elif hazard.consequence == '5 - Incident report only':
            currentconsequence = '5'
        consequenceList.append(currentconsequence)
    hazards = [('Hazards', 'Probability', 'Consequence', 'Risk', 'Control Measure', 'Person'),
               ('Electrocution', probabilityList[0], consequenceList[0], hazardsDB[0].risk, hazardsDB[0].controlMeasure,
                hazardsDB[0].person),
               ('Biohazards, Sna...', probabilityList[1], consequenceList[1], hazardsDB[1].risk, hazardsDB[1].controlMeasure,
                hazardsDB[1].person),
               ('Heat', probabilityList[2], consequenceList[2], hazardsDB[2].risk, hazardsDB[2].controlMeasure,
                hazardsDB[2].person),
               ('Falls from Height', probabilityList[3], consequenceList[3], hazardsDB[3].risk, hazardsDB[3].controlMeasure,
                hazardsDB[3].person),
               ('Asbestos', probabilityList[4], consequenceList[4], hazardsDB[4].risk, hazardsDB[4].controlMeasure,
                hazardsDB[4].person)]
    table = Table(hazards, colWidths=90, rowHeights=40)
    table.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('ALIGN', (0,0),(-1,-1), 'CENTER'),
        ('VALIGN', (0,0),(-1,-1), 'MIDDLE'),
    ]))
    table.wrapOn(pdf, 500, 500)
    table.drawOn(pdf, 20, 500)
    pdf.line(30, 480, 550, 480)
    pdf.drawString(30, 460, 'Images taken')
    index = 0
    for image in imagesDB:
        if image.imageData is not None:
            currentImage = ImageReader(io.BytesIO(image.imageData))
            if index == 0:
                pdf.drawImage(currentImage, 50, 240, width=200, height=200, mask='auto')
            elif index == 1:
                pdf.drawImage(currentImage, 300, 240, width=200, height=200, mask='auto')
            elif index == 2:
                pdf.drawImage(currentImage, 50, 20, width=200, height=200, mask='auto')
            elif index == 3:
                pdf.drawImage(currentImage, 300, 20, width=200, height=200, mask='auto')
                pdf.showPage()
            elif index == 4:
                pdf.drawImage(currentImage, 50, 590, width=200, height=200, mask='auto')
            elif index == 5:
                pdf.drawImage(currentImage, 300, 590, width=200, height=200, mask='auto')
            elif index == 6:
                pdf.drawImage(currentImage, 50, 360, width=200, height=200, mask='auto')
            elif index == 7:
                pdf.drawImage(currentImage, 300, 360, width=200, height=200, mask='auto')
            elif index == 8:
                pdf.drawImage(currentImage, 50, 140, width=200, height=200, mask='auto')
            elif index == 9:
                pdf.drawImage(currentImage, 300, 140, width=200, height=200, mask='auto')
        index = index + 1
    pdf.save()
    return fileName

@app.route('/api/send/email', methods=['POST'])
def sendEmail():
    db.session.commit()
    data = request.get_json()
    entry = InstallationFormEntry.query.filter_by(formId=data['formId']).first()
    checklists = Checklist.query.filter_by(formId=entry.formId).all()
    hazards = Hazards.query.filter_by(formId=entry.formId).order_by(Hazards.hazardName.asc()).all()
    generateFormPDF(data)
    checklists_dict = [
        {'checkName': 'General State of the Work Site is SAFE and tidy', 'checked': 'false', 'text': '_checked1'},
        {'checkName': 'Ceiling has no cracks', 'checked': 'false', 'text': '_checked2'},
        {'checkName': 'Floors clean and tidy', 'checked': 'false', 'text': '_checked3'},
        {'checkName': 'Lights in place & in working order', 'checked': 'false', 'text': '_checked4'},
        {'checkName': 'A safe working environment exists', 'checked': 'false', 'text': '_checked5'},
        {'checkName': 'Is the Ceiling lining made of asbestos?', 'checked': 'false', 'text': '_checked6'},
        {'checkName': 'General State of Work Site is SAFE and tidy', 'checked': 'false', 'text': '_checked11'},
        {'checkName': 'Ceiling has no cracks', 'checked': 'false', 'text': '_checked12'},
        {'checkName': 'Floors clean and tidy', 'checked': 'false', 'text': '_checked13'},
        {'checkName': 'Lights in place & in working order', 'checked': 'false', 'text': '_checked14'},
        {'checkName': 'Insulation packaging removed from site', 'checked': 'false', 'text': '_checked15'},
        {'checkName': 'Access Aperture clean', 'checked': 'false', 'text': '_checked16'},
        {'checkName': 'Default Minimum clearance of insulation around all recessed lights And electrical equipment achieved as per AS/NZS 3000:2007', 'checked': 'false', 'text': '_checked17'},
    ]

    checklists_html = ''
    checklists_html2 = ''
    index = 1;
    for checklist_dict in checklists_dict:
        for checklist in checklists:
            if str(checklist_dict['text']) == str(checklist.text):
                checklist_dict['checked'] = 'true'
        if checklist_dict['checked'] == 'true' and index < 7:
            checklists_html = checklists_html + " "+checklist_dict['checkName']+"? &#9745; Yes &#9744; No<br />"
        elif checklist_dict['checked'] == 'false' and index < 7:
            checklists_html = checklists_html + " "+checklist_dict['checkName']+"? &#9744; Yes &#9745; No<br />"
        elif checklist_dict['checked'] == 'true' and index >= 7:
            checklists_html2 = checklists_html2 + " " + checklist_dict['checkName'] + "? &#9745; Yes &#9744; No<br />"
        elif checklist_dict['checked'] == 'false' and index >= 7:
            checklists_html2 = checklists_html2 + " " + checklist_dict['checkName'] + "? &#9744; Yes &#9745; No<br />"
        index = index + 1

    msg = EmailMessage()
    msg['Subject'] = 'Insulation Easy Australia Installation Form Order #:'+entry.orderNumber
    msg['From'] = 'support@insulationeasy.com.au'
    msg['To'] = 'quinth.anthony@gmail.com'

    msg.set_content('This is a plain text email')

    msg.add_alternative(f"""\
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
        <title>Demystifying Email Design</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    </head>
    <body style="margin: 0; padding: 0;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%">
        <tr>
            <td style="padding: 10px 0 30px 0;">
                <table align="center" border="0" cellpadding="0" cellspacing="0" width="700"
                       style="border: 1px solid #cccccc; border-collapse: collapse;">
                    <tr>
                        <td align="center" bgcolor="#333"
                            style="padding: 40px 0 30px 0; color: #153643; font-size: 28px; font-weight: bold; font-family: Arial, sans-serif;">
                            <img src="https://insulationeasy.com.au/wp-content/uploads/2019/06/logo-png-e1564465409459.png"
                                 alt="Creating Email Magic" style="display: block;"/>
                        </td>
                    </tr>
                    <tr>
                        <td bgcolor="#ffffff" style="padding: 40px 25px 40px 25px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td style="color: #153643; font-family: Arial, sans-serif; font-size: 24px; text-align:center;">
                                        <b>Installation Form Order #: {entry.orderNumber}</b>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 20px 0 30px 0; color: #153643; font-family: Arial, sans-serif; font-size: 16px; line-height: 20px;">
                                        Insulation Easy Australia<br/>
                                        Tel: 03 9687 7283<br/>
                                        https://insulationeasy.com.au/<br/>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="color: #153643; font-family: Arial, sans-serif; font-size: 24px; text-align:left;">
                                        <b>{entry.builderName}</b>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 20px 0 30px 0; color: #153643; font-family: Arial, sans-serif; font-size: 16px; line-height: 20px;">
                                        Address: {entry.address}<br/>
                                        Date: {entry.date}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 20px 0 30px 0; color: #153643; font-family: Arial, sans-serif; font-size: 16px; line-height: 20px;">
                                        Items to be checked BEFORE commencement of the installation<br/>
                                        {checklists_html}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 20px 0 30px 0; color: #153643; font-family: Arial, sans-serif; font-size: 16px; line-height: 20px;">
                                        Check all areas of the ceiling, if the ceiling is asbestos or you are unsure of its composition you must assume it is ASBESTOS and follow Higgins Asbestos Management Plan)<br/>
                                        Comments<br/>
                                        {entry.comments}<br/>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 20px 0 30px 0; color: #153643; font-family: Arial, sans-serif; font-size: 16px; line-height: 20px;">
                                        Items to be checked AFTER commencement of the installation<br/>
                                        {checklists_html2}
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <table style="border: 1px solid black; border-collapse: collapse; width: 100%">
                                            <tr style="border: 1px solid black; border-collapse: collapse;">
                                                <th style="border: 1px solid black; border-collapse: collapse;">Hazard</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">Probability</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">Consequence</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">Risk</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">Control Measure</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">Person</th>
                                            </tr>
                                            <tr style="border: 1px solid black; border-collapse: collapse;">
                                                <th style="border: 1px solid black; border-collapse: collapse;">Electrocution</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[0].probability}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[0].consequence}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[0].risk}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[0].controlMeasure}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[0].person}</th>
                                            </tr>
                                            <tr style="border: 1px solid black; border-collapse: collapse;">
                                                <th style="border: 1px solid black; border-collapse: collapse;">Biohazards, Snakes and Spiders</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[1].probability}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[1].consequence}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[1].risk}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[1].controlMeasure}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[1].person}</th>
                                            </tr>
                                            <tr style="border: 1px solid black; border-collapse: collapse;">
                                                <th style="border: 1px solid black; border-collapse: collapse;">Heat</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[2].probability}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[2].consequence}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[2].risk}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[2].controlMeasure}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[2].person}</th>
                                            </tr>
                                            <tr style="border: 1px solid black; border-collapse: collapse;">
                                                <th style="border: 1px solid black; border-collapse: collapse;">Falls from Height</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[3].probability}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[3].consequence}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[3].risk}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[3].controlMeasure}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[3].person}</th>
                                            </tr>
                                            <tr style="border: 1px solid black; border-collapse: collapse;">
                                                <th style="border: 1px solid black; border-collapse: collapse;">Asbestos (lagging or loose fill insulation)</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[4].probability}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[4].consequence}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[4].risk}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[4].controlMeasure}</th>
                                                <th style="border: 1px solid black; border-collapse: collapse;">{hazards[4].person}</th>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 20px 0 30px 0; color: #153643; font-family: Arial, sans-serif; font-size: 16px; line-height: 20px;">
                                        Worksite Evaluated by: {entry.workSiteEvaluator}<br/>
                                        Date: {entry.workSiteEvaluatedDate}<br/>
                                        Signature Attached below<br />
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 20px 0 30px 0; color: #153643; font-family: Arial, sans-serif; font-size: 16px; line-height: 20px;">
                                        Builder Confirmation: {entry.builderConfirmation}<br/>
                                        Date: {entry.builderConfirmationDate}<br/>
                                        Signature Attached below<br />
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 20px 0 30px 0; color: #153643; font-family: Arial, sans-serif; font-size: 16px; line-height: 20px;">
                                        Geoff Aldridge<br/>
                                        Manager<br/>
                                        Insulation Easy Australia<br/>
                                        geoff@insulationeasy.com.au<br/>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 20px 0 30px 0; color: #153643; font-family: Arial, sans-serif; font-size: 16px; line-height: 20px; float:right;">
                                        <br/>
                                    </td>
                                </tr>
    
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td bgcolor="#333" style="padding: 30px 30px 30px 30px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td style="color: #ffffff; font-family: Arial, sans-serif; font-size: 14px;"
                                        width="75%">
                                        &reg;2020 Insulation Easy Australia<br/>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    </body>
    </html>
    --
    This e-mail was sent from a contact form on Insulation Easy Australia (https://insulationeasy.com.au)
    """, subtype='html')

    images = FormImages.query.filter_by(formId=entry.formId).all()
    for image in images:
        if image.imageData is not None:
            msg.add_attachment(image.imageData, maintype='image', subtype=imghdr.what(None, image.imageData), filename=image.imageName)

    signatures = SignatureForm.query.filter_by(formId=entry.formId).all()
    print(signatures)
    for signature in signatures:
        print(signature)
        print(signature.signatureName)
        msg.add_attachment(signature.signatureImage, maintype='image', subtype=imghdr.what(None, signature.signatureImage), filename=signature.signatureName)

    pdffile = f'pdf/InsulationEasyForm-{entry.orderNumber}.pdf'
    with open(pdffile, 'rb') as f:
        file_data = f.read()
        file_name = f.name

    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

    with smtplib.SMTP_SSL('mail.insulationeasy.com.au', 465) as smtp:
        smtp.login('support@insulationeasy.com.au', '@#IEA12Xx')
        smtp.send_message(msg)

    return jsonify({'message': 'Added successfully!'})


if __name__ == '__main__':
    app.run(port=8270, debug=True)