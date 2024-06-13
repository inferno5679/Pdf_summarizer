from flask import Flask, render_template, request,redirect,flash, url_for
import os
from GPT import *
import secrets
from markdown2 import markdown

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
prompt=""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def summarize():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename == '' or not uploaded_file:
            flash("File not uploaded","message")
        else:
            temp_path = os.path.join("temp", uploaded_file.filename)
            uploaded_file.save(temp_path)
            total_images = get_pdf_page_count(temp_path)
            print(total_images)
            selection = request.form['selection']
            print(selection)
            if selection == "whole":
                prompt = initial_summary(path=temp_path,start=2,end=total_images)
                summary = markdown(final_summary(prompt=prompt))
                os.remove(temp_path)
                return render_template('index.html', summary=summary)
            
            elif selection == "range":
                start_page = request.form['start_page']
                end_page = request.form['end_page']

                if start_page and end_page:
                    start_page = int(start_page)
                    end_page = int(end_page)
                    print(start_page,end_page)
                    if start_page>end_page:
                        flash("start Page cannot be greater than end page",'message')
                        return redirect('/')
                    
                    elif start_page > total_images or end_page > total_images or start_page <= 0 or end_page <=0:
                        flash("Exceeded the page range","message")
                        return redirect('/')
                    
                    else:
                        prompt = initial_summary(path=temp_path,start=start_page,end=end_page)
                        summary = markdown(final_summary(prompt=prompt))
                        os.remove(temp_path)
                        start_page = None
                        end_page = None
                        return render_template('index.html', summary=summary)
                else:
                    flash("Start Page and End page cannot be empty")
                    redirect('/')

    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists('temp'):
        os.makedirs('temp')
    app.run(debug=True)
