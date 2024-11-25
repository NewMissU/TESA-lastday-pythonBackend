from flask import Flask,request,jsonify,make_response,abort,render_template,session,send_file
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import psycopg2
import psycopg2.extras

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3', 'ogg', 'mp4', 'pdf', 'zip', 'c', 'jpg'}
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', '84a4e46d-b5fc-458f-a4c7-0e908524dd66')  # ใช้ค่า SECRET_KEY ที่เก็บไว้ใน .env หรือค่าคงที่ที่ปลอดภัย


#Database connection parameter
DB_USER = os.getenv("DB_USER") # ดึงข้อมูลจาก .env มาใช้งาน
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST", "localhost")  # ค่าเริ่มต้นคือ localhost
DB_PORT = os.getenv("DB_PORT", "5433")

print("Username : " , DB_USER)
print("Password : " , DB_PASSWORD)
print("DatabaseName : " , DB_NAME)
print("Host : " , DB_HOST)
print("Port : " , DB_PORT)

#connect to the PostgreSQL database
def connection_db():
    conn = psycopg2.connect(
        dbname = DB_NAME,
        user = DB_USER,
        password = DB_PASSWORD,
        host = DB_HOST,
        port = DB_PORT,
    )
    return conn

#cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

def check_api(api_key):
    conn = connection_db()
    cur = conn.cursor()
    cur.execute('SELECT api_key FROM api_keys;')
    all_apiKey = cur.fetchall()
    for eachkey in all_apiKey:
        # print(type(eachkey[0]))
        # print(f"API KEY {api_key} type : {type(api_key)} | API {eachkey[0]} IN DB : {type(str(eachkey[0]))}")
        if api_key == eachkey[0]:
            print("VALID API KEY")
            cur.close()
            conn.close()
            return True
    print("Invalid API KEY")
    cur.close()
    conn.close()
    return False

SUCCESS_API = ""

@app.route("/")
def index():
    session.pop('api_key', None)
    return render_template('login.html')

@app.route("/verify",methods=['POST'])
def verify_apikey():
    apikey = request.form['apiKey']
    if check_api(apikey) == True:
        session['api_key'] = apikey
        return render_template('upload.html')
    else:
        return render_template('login.html')

# ฟังก์ชันตรวจสอบว่าไฟล์มีนามสกุลที่อนุญาตหรือไม่
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload_file():
    # ตรวจสอบว่าไฟล์ถูกส่งมาหรือไม่
    if 'file' not in request.files: # มีไฟล์ที่ส่งมา # 'file' มาจากชื่อของฟิลด์ name ที่คุณกำหนดไว้ใน <input> ของฟอร์ม HTML
        return jsonify({"error": "No file part"}) # ไม่ได้แนบไฟล์มา
    
    file = request.files['file']  # เข้าถึงไฟล์ที่ส่งมา ค่าที่ POST มา -> ['file'] เป็น FileStorage
    print(file)
    #request.files ใช้สำหรับดึงไฟล์ที่ถูกอัปโหลด (เช่น ฟอร์มที่มี enctype="multipart/form-data").
    # ใช้ request.files['file'] เพื่อเข้าถึงไฟล์ที่ถูกอัปโหลด.    

    # ตรวจสอบว่าไฟล์มีชื่อหรือไม่
    if file.filename == '': # ไม่ใส่ไฟล์
        return jsonify({"error": "No selected file"})

    # ตรวจสอบว่าไฟล์มีนามสกุลที่อนุญาตหรือไม่
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)  # ป้องกันการใช้ชื่อไฟล์ที่ไม่ปลอดภัย
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # บันทึกไฟล์ลงในโฟลเดอร์
        return jsonify({"message": "File uploaded successfully", "filename": filename}), 200

    return jsonify({"error": "Invalid file type"}), 400

# ตัวอย่างการตรวจสอบ API Key
@app.route('/files', methods=['GET'])
def list_files():
    # ตรวจสอบ API key จาก session หรือ headers
    api_key = session.get('api_key')  # ลองดึง API key จาก session

    if not api_key:
        api_key = request.headers.get('API-Key')  # ถ้าไม่มีใน session ให้ตรวจสอบจาก headers

    if not api_key:
        return jsonify({"error": "Api-key is missing"}), 400

    if check_api(api_key) == False:
        return jsonify({"error": "Invalid API Key"}), 403   

    try:
        # โค้ดการจัดการไฟล์
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            return jsonify({"error": "Upload folder does not exist"}), 404
        
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        audio_files = [file for file in files if file.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']]
        
        return jsonify({"audio_files": audio_files}), 200

    except Exception as e:  
        return jsonify({"error": str(e)}), 500   

# ตัวอย่างการตรวจสอบ API Key
@app.route('/apikey', methods=['GET'])
def get_data1():
    # ตรวจสอบ API key จาก session หรือ headers
    api_key = session.get('api_key')  # ลองดึง API key จาก session

    if not api_key:
        api_key = request.headers.get('API-Key')  # ถ้าไม่มีใน session ให้ตรวจสอบจาก headers

    if not api_key:
        return jsonify({"error": "Api-key is missing"}), 400

    if check_api(api_key) == False:
        return jsonify({"error": "Invalid API Key"}), 403

    # ตรวจสอบ API Key ในฐานข้อมูล
    conn = connection_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM api_keys;')
    rows = cur.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    return jsonify(data),200

# ตัวอย่างการตรวจสอบ API Key

@app.route('/data', methods=['GET'])
def get_data():
    # ตรวจสอบ API key จาก session หรือ headers
    api_key = session.get('api_key')  # ลองดึง API key จาก session

    if not api_key:
        api_key = request.headers.get('API-Key')  # ถ้าไม่มีใน session ให้ตรวจสอบจาก headers

    if not api_key:
        return jsonify({"error": "Api-key is missing"}), 400

    if check_api(api_key) == False:
        return jsonify({"error": "Invalid API Key"}), 403
    
    # ตรวจสอบ API Key ในฐานข้อมูล
    conn = connection_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM api_keys WHERE api_key = %s;', (api_key,))
    row = cur.fetchone()

    conn.close()
    return jsonify(row), 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # ตรวจสอบ API key จาก session หรือ headers
    api_key = session.get('api_key')  # ลองดึง API key จาก session

    if not api_key:
        api_key = request.headers.get('API-Key')  # ถ้าไม่มีใน session ให้ตรวจสอบจาก headers

    if not api_key:
        return jsonify({"error": "Api-key is missing"}), 400

    if check_api(api_key) == False:
        return jsonify({"error": "Invalid API Key"}), 403
    # ระบุพาธของไฟล์ที่ต้องการให้ดาวน์โหลด
    file_path = app.config['UPLOAD_FOLDER'] + filename  # แก้ไขให้เป็นไฟล์ที่ต้องการ   
    try:
        # ส่งไฟล์กลับไปยังไคลเอนต์
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        # จัดการกรณีไฟล์ไม่พบ
        return jsonify({"error": "File not found"}), 404

@app.route('/upload/<filename>', methods=['POST'])
def upload_file_from_url(filename):
    # ตรวจสอบ API key จาก headers
    api_key = request.headers.get('API-Key')  # ตรวจสอบจาก headers

    if not api_key:
        return jsonify({"error": "Api-key is missing"}), 400

    if check_api(api_key) == False:
        return jsonify({"error": "Invalid API Key"}), 403

    # ตรวจสอบว่ามีข้อมูลไฟล์ในคำขอหรือไม่
    if not request.data:
        return jsonify({"error": "No file data"}), 400

    # บันทึกไฟล์โดยใช้ชื่อจากพารามิเตอร์
    secure_name = secure_filename(filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)

    # เขียนข้อมูลไฟล์ลงในพาธที่ระบุ
    with open(save_path, 'wb') as f:
        f.write(request.data)

    return jsonify({"message": "File uploaded successfully", "filename": secure_name}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)