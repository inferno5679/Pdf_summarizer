from flask import Flask, render_template, request,redirect,flash, url_for
import os
from GPT import *
import secrets
from markdown2 import markdown

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
prompt=""
summary=""
chat_bot_response=[]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename == '' or not uploaded_file:
            flash("File not uploaded", "message")
        else:
            temp_path = os.path.join("temp", uploaded_file.filename)
            uploaded_file.save(temp_path)
            # print(temp_path)
            total_images = get_pdf_page_count(temp_path)
            # print(total_images)
            selection = request.form['selection']
            # print(selection)
            if selection == "whole":
                prompt = initial_summary(path=temp_path, start=2, end=total_images-8)
                summary = markdown(final_summary(prompt=prompt))
                os.remove(temp_path)

                with open('info.txt', 'w') as file:
                    file.write(prompt)
                
                return render_template('index.html', summary=summary)
            elif selection == "range":
                start_page = request.form['start_page']
                end_page = request.form['end_page']

                if start_page and end_page:
                    start_page = int(start_page)
                    end_page = int(end_page)
                    # print(start_page, end_page)
                    if start_page > end_page:
                        flash("Start Page cannot be greater than End Page", 'message')
                        return redirect('/')
                    
                    elif start_page > total_images or end_page > total_images or start_page <= 0 or end_page <= 0:
                        flash("Exceeded the page range", "message")
                        return redirect('/')
                    
                    else:
                        prompt = initial_summary(path=temp_path, start=start_page, end=end_page)
                        summary = markdown(final_summary(prompt=prompt))
                        os.remove(temp_path)
                        with open('info.txt', 'w',encoding='utf-8') as file:
                            file.write(prompt)
                        start_page = None
                        end_page = None
                        return render_template('index.html', summary=summary)
                else:
                    flash("Start Page and End Page cannot be empty", 'message')
                    return redirect('/')

    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def gpt_chat_bot():
    if request.method == 'POST':
        input_prompt = str(request.form['input_prompt'])
        summary = str(request.form['hidden_summ'])
        with open("info.txt",'r') as file:
            content = file.readlines()
        content = ' '.join(content)
        # print(content)
        if content=="":
            content = summary
        if input_prompt == "" and chat_bot_response != []:
            chat = ''.join(chat_bot_response)
            flash("Please enter a prompt", 'message')
            return render_template('index.html', summary=summary,chat=chat)
        else:
            # chat = markdown(chat_bot(content=prompt, input_prompt=input_prompt))
            question = "<div class='question'><b>Q- " + input_prompt + "</b></div>"
            Answer = "<div class='answer'>A- " + chat_bot(content=content, input_prompt=input_prompt) + "</div>"
            chat_bot_response.append(Answer)
            chat_bot_response.append("\n\n")
            chat_bot_response.append(question)
            chat = markdown(''.join(chat_bot_response[::-1]))
            return render_template('index.html', chat=chat, summary=summary)
        
    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists('temp'):
        os.makedirs('temp')
    if os.path.exists("info.txt"):
        os.remove("info.txt")
    app.run(debug=True)
