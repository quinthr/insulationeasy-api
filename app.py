import base64
from flask import Flask, request, jsonify, render_template


from models.installationFormEntry import *
from db import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost:3306/insulationeasyapp' #mysql://username:password@server/db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = 'InsulationEasyAustralia&SoundproofingProductsAustralia'
db.init_app(app)

@app.before_first_request
def createTables():
    with app.app_context():
        db.create_all()

createTables()

@app.route('/api/entries', methods=['GET'])
def getFormEntries():
    entries = InstallationFormEntry.query.all()
    return jsonify({'entries': entries})

@app.route('/api/images', methods=['GET'])
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
def uploadEntry():
    print('CALLED')
    data = request.get_json()
    print(data)
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
def uploadChecklist():
    print('CALLED')
    data = request.get_json()
    checklist = Checklist(text=data['text'], status='Done', formId=data['formId'])
    db.session.add(checklist)
    try:
        db.session.commit()
        return jsonify({'message': 'Added successfully!'})
    except:
        return jsonify({'message': 'Failed to add!'})

@app.route('/api/image/upload', methods=['POST'])
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
        print("Success")
        return jsonify({'message': 'Added successfully!'})
    except Exception as error:
        print(str(error))
        return jsonify({'message': 'Failed to add!'})

@app.route('/api/hazard/upload', methods=['POST'])
def uploadHazard():
    data = request.get_json()
    hazard = Hazards(hazardName=data['hazardName'], probability=data['probability'], consequence=data['consequence'],
                     risk=data['risk'], controlMeasure=data['controlMeasure'], person=data['person'],
                     status='Done', formId=data['formId'])
    db.session.add(hazard)
    try:
        db.session.commit()
        print("Success")
        return jsonify({'message': 'Added successfully!'})
    except Exception as error:
        print(str(error))
        return jsonify({'message': 'Failed to add!'})

@app.route('/api/signature/upload', methods=['POST'])
def uploadSignature():
    data = request.get_json()
    signatureImage = base64.b64decode(data['signatureImage'])
    signature = SignatureForm(signatureName=data['signatureName'], signaturePoints=data['signaturePoints'],
                              signatureImage=signatureImage, formId=data['formId'])
    db.session.add(signature)
    try:
        db.session.commit()
        print("Success")
        return jsonify({'message': 'Added successfully!'})
    except Exception as error:
        print(str(error))
        return jsonify({'message': 'Failed to add!'})

@app.route('/api/update/entries', methods=['POST'])
def updateFormEntries():
    dataList = request.get_json()
    entries = InstallationFormEntry.query.all()
    list = []
    for entry in entries:
        if entry.formId in dataList['entries']:
            print('In list')
            print(entry.formId)
            continue
        else:
            print('Not in list')
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
    print(list)
    return jsonify({'entries': list})





if __name__ == '__main__':
    app.run(port=8270, debug=True)