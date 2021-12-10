from flask import Flask, render_template, request, url_for, redirect, session
import pymongo
import bcrypt


from flask import render_template, jsonify, send_file
from flask import request, redirect
from werkzeug.utils import secure_filename
import pathlib
import time
from datetime import datetime
import os
import uuid
import zipfile
from bson import ObjectId
from os.path import basename
from PIL import Image
import threading
import shutil

#set app as a Flask instance 
app = Flask(__name__)
#encryption relies on secret keys so they could be run
app.secret_key = "testing"
#connoct to your Mongo DB database
client = pymongo.MongoClient("mongodb://localhost:27017")
#app.config["MONGO_URI"] = "mongodb://localhost:27017/files_db"
#get the database name
db = client.get_database('total_records')
#get the particular collection that contains the data
records = db.register

files_record=db.files




app.config["ALLOWED_FILE_EXTENSIONS"] = [
    "JPEG", "JPG", "PNG", "GIF", "PDF", "ZIP","MP4","MP3"]
app.config["MAX_FILE_FILESIZE"] = 50 * 1024 * 1024


#assign URLs to have a particular route 
@app.route("/", methods=['post', 'get'])
def index():
    message = ''
    #if method post in index
    
    if "email" in session:
        return redirect(url_for("files"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        #if found in database showcase that it's found 
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            #hash the password and encode it
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            #assing them in a dictionary in key value pairs
            user1 =email
            path="E://uploads//"+user1

            # Check whether the specified path exists or not
            isExist = os.path.exists(path)

            if not isExist:
                 os.makedirs(path)
                 print("The new directory is created!")

           

            user_input = {'name': user, 'email': email, 'password': hashed, 'created_at':datetime.now()}
            #insert it in the record collection
            records.insert_one(user_input)
            
            return redirect(url_for("login"))
    return render_template('index.html')



@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("files"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        #check if email exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            #encode the password and check if it matches
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('files'))
            else:
                if "email" in session:
                    return redirect(url_for("files"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html')

# @app.route('/logged_in')
# def logged_in():
#     if "email" in session:
#         email = session["email"]
#         return render_template('upload_file.html', email=email)
#     else:
#         return redirect(url_for("login"))

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')






def allowed_file(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_FILE_EXTENSIONS"]:
        return True
    else:
        return False


def allowed_file_filesize(filesize):

    if int(filesize) <= app.config["MAX_FILE_FILESIZE"]:
        return True
    else:
        return False




@app.route("/upload-file", methods=["GET", "POST"])
def upload_file():

    if request.method == "POST":
        
        user1 = session["email"]
        path="E://uploads//"+user1

        # Check whether the specified path exists or not
        isExist = os.path.exists(path)

        if not isExist:
            os.makedirs(path)

        print("The new directory is created!")
        app.config['UPLOAD_FOLDER'] = path
       
        file = request.files["file"]
        print(request.full_path)
        if file.filename == "":
            print("No filename")
            return redirect(request.url)

        if allowed_file(file.filename):
                i = 0
               
                filename = file.filename
                print(filename)
           
                print(os.path.isfile(filename))


                dir_list = os.listdir(path)
                for i in range(len(dir_list)):
                    print(dir_list[i])
                    if dir_list[i] == filename:
                        filename = "Copy of "+filename

                file_extension = pathlib.Path(filename).suffix

                
                print("File Extension: ", file_extension)

                print("url -", request.url)

                file.save(os.path.join(
                app.config['UPLOAD_FOLDER'], filename))

                
                # if(file_extension==".jpg" or file_extension=='.png' or file_extension=='.jpeg'):

                #     picture = Image.open(path+"\\"+filename)
                #     picture.save(path+"\\"+filename, "JPEG",
				#     optimize = True,
				#     quality = 50)



                # if(file_extension==".mp4" ):
                #     c='ffmpeg -i input.mp4 -vcodec libx264 -crf 27 -preset veryfast -c:a copy -s 960x540 output.mp4'
                #     a1='ffmpeg -i '
                #     a2=path+"\\"+filename
                #     a3=' -vcodec libx264 -crf 27 -preset ultrafast -c:a copy -s 960x540 '
                #     a4=path+"\\"+"1"+filename
                #     s=a1+a2+a3+a4
                #     print(s)
                #     os.system(s)      

                try:
                    t1=threading.Thread(target=comp,args=(file_extension,path,filename,user1))    # 1st thread with subscription_1 and watchlist_1
                    # t2=threading.Thread(target=demo,args=(7002,ss2,watchlist2,))    # 2st thread with subscription_2 and watchlist_2
                    # t3=threading.Thread(target=demo,args=(7003,ss3,watchlist3,))    # 3st thread with subscription_3 and watchlist_3

                    t1.start()
                    # t2.start()
                    # t3.start()
                except Exception as e:
                    print(e)  

                db.files.insert_one(
                        {'file_id':str(uuid.uuid4()),'file_name':filename, 'file_type':file_extension,
                        'file_size':os.path.getsize(path+"//"+filename),'created_at':datetime.now(),
                        'name': user1, 'file_url': app.config['UPLOAD_FOLDER']+"//"+filename})

                print("File saved")
                return redirect(request.url)
                
        else:
                    print("That file extension is not allowed")
                    return redirect(request.url)

    return render_template("upload_file.html")

def comp(file_extension,path,filename,user1):
    if(file_extension==".jpg" or file_extension=='.png' or file_extension=='.jpeg'):

                    picture = Image.open(path+"\\"+filename)
                    z=file_extension[1:]
                    print(z)
                    picture.save(path+"\\"+filename,
				    optimize = True,
				    quality = 50)



    if(file_extension==".mp4" ):
        isExist = os.path.exists('E:/temp/'+user1)
        if(isExist==True):
        #    shutil.copy2(path+"\\"+filename, 'E:/temp/'+user1+'/'+filename)
            pass
        else:
            os.makedirs('E:/temp/'+user1)
            # shutil.copy2(path+"\\"+filename, 'E:/temp/'+user1+'/'+filename)

        c='ffmpeg -i input.mp4 -vcodec libx264 -crf 27 -preset veryfast -c:a copy -s 960x540 output.mp4'
        a1='ffmpeg -i '
        a2="\""+path+"\\"+filename+"\""
        a3=' -vcodec libx264 -crf 27 -preset ultrafast -c:a copy -s 960x540 '
        a4="\""+'E:/temp/'+user1+"\\"+"1"+filename+"\""
        s=a1+a2+a3+a4
        print(s)
       
        os.system(s)     
        os.remove(path+"//"+filename) 

        os.rename('E:/temp/'+user1+"//"+"1"+filename,path+"//"+filename)

    print(path)
    print(os.path.getsize(path+"//"+filename))
    db.files.update_one({'file_url': path+"//"+filename} , {'$set' : {'file_size' : os.path.getsize(path+"//"+filename)}})


@app.route("/files")
def files():
    """Endpoint to list files on the server."""
    if "email" in session:
        email = session["email"]
        
        user1 = session["email"]
        print(user1)
        path="E://uploads//"+user1
        print(path)
        app.config['UPLOAD_FOLDER'] = path
        files = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(path):
                files.append(filename)
        return render_template('files.html', title="page",  jsonfile=files)
    else:
        return redirect(url_for("login"))
    


@app.route("/getfile/<file_name>")
def get_file(file_name):
    print(file_name)
    path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    print(path)
    return send_file(path, as_attachment=True)

@app.route("/getfileFromSharing/<file_id>")
def get_file_FromSharing(file_id):
    print(file_id)
    file= files_record.find_one({'_id':ObjectId(file_id)})
    
    file_url=file['file_url']
    print(file_url)
    return send_file(file_url, as_attachment=True)



@app.route("/share/<file_name>",methods=["POST","GET"])
def share(file_name):
    #return send_file(path, as_attachment=True)
    if request.method == "POST":
        email = request.form.get("email")
        print(email)
        print(file_name)
        path=os.path.join(app.config['UPLOAD_FOLDER'])+"//"+file_name
        print(path)

        a=files_record.find_one({'file_url': path })
       # b=records.find_one({'email': sess })

        print(a)
        print(a['_id'])
        print(a['name'])
      
        files_record.update_one({'file_url': path } , {'$addToSet' : {'shared_user_id':email }})
       
        records.update_one({'email':email},{'$addToSet':{'shared_with_me':{'author_id':session['email'],'file12_id':a['_id'],'file_path':path}}})
    return render_template("share.html")



@app.route("/shared_with_me",methods=["POST","GET"])
def shared_with_me():
    #return send_file(path, as_attachment=True)
    c= records.find_one({'email':session['email']})
    print("11111111################")
    print("###################")
    print(c['name'])

    d=c['shared_with_me']


    print(d[0]['file_path'])

    #sharing_list=[]
    file_name=[]

    for i in range(0,len(d)):
        print(i)
        buff=d[i]['file_path'].split("//")[-1]
        
        file_name.append([buff,d[i]['file12_id']])
        print(file_name)


    #print(d['author_id'])
    print("###################")
    print(d)
    
    return render_template("shared_with_me.html",jsonfile=file_name)




if __name__ == "__main__":
  app.run(host='0.0.0.0',debug=True)


