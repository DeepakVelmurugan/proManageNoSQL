from flask import Flask,jsonify,request
from CRUD import CRUD
app = Flask(__name__)

def check_and_call(option,reqData = None):
    #check story id
    if reqData != None and 'story_id' not in reqData.keys():
        return {"message" : "Error", "extra_info" : "Story not found"}
    obj = CRUD.CRUD()
    function_mapping = {'connect' : obj.connect, 'insert' : obj.insert_story , 'update' : obj.update_story, 'delete' : obj.delete_story}
    if reqData is None:
        return function_mapping[option]()
    return function_mapping[option](reqData)

@app.route('/',methods=['GET'])
def index():
    result = check_and_call('connect')
    if result['message'] == 'Success':
        return '<b><i> Database connection successfull </i></b>'
    return jsonify({'error': result['extra_info']}), 500

@app.route('/insert',methods=['POST'])
def insert_entry():
    reqData = request.get_json(force=True)
    result = check_and_call('insert',reqData)
    if result['message'] == 'Success':
        return '<b>Inserted successfully</b>'
    return jsonify({'error': result['extra_info']})

@app.route('/update',methods=['POST'])
def update_entry():
    reqData = request.get_json(force=True)
    result = check_and_call('update',reqData)
    if result['message'] == 'Success':
        return '<b>Updated successfully</b>'
    else:
        return jsonify({'error': result['extra_info']})
    
@app.route('/delete', methods=['POST'])
def delete_entry():
    reqData = request.get_json(force=True)
    result = check_and_call('delete',reqData)
    if result['message'] == 'Success':
        return '<b>Delete successfully</b>'
    else:
        return jsonify({'error':result['extra_info']})

@app.route('/select', methods=['GET'])
def select_entry():
    story_id = request.headers.get('story_id')
    selectObj = CRUD.CRUD()
    result = selectObj.select_story(story_id)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000,debug=True)