from pdf2image import convert_from_path,pdfinfo_from_path
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
from io import BytesIO
import base64
from openai import OpenAI
import httpx
import time

def get_pdf_page_count(path):
    try:
        info = pdfinfo_from_path(path,
            poppler_path=r"D:\Projects\openAI-env\poppler\poppler-24.02.0\Library\bin")
        page_count = info['Pages']
        return page_count
    except (PDFInfoNotInstalledError, PDFPageCountError, PDFSyntaxError) as e:
        print(f"Error: {e}")
        return None

def convert_doc_to_images(path,start_page,end_page):
    images = convert_from_path(pdf_path=path,
        poppler_path=r"C:\Users\arpan.doogar\Downloads\Release-24.02.0-0\poppler-24.02.0\Library\bin",
        first_page=start_page,last_page=end_page)
    return images

def get_img_uri(img):
    buffer = BytesIO()
    img.save(buffer, format="jpeg")
    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
    data_uri = f"data:image/jpeg;base64,{base64_image}"
    return data_uri

def analyze_image(img_url):
    system_prompt = '''
    You will be provided with multiple images of pdf pages or slides. Your goal is to summarize the content that you see
    in technical terms, as if you were delivering a presentation.
    It is very important that you only convey the IMPORTANT/RELEVANT information and give the output in bullets
    points for the summarization of the whole page/slide

    If there are diagrams, describe the diagrams and explain their meaning.
    For example: if there is a diagram describing a process flow, say something like "the process flow starts with X then we have Y and Z..."

    If there is any financial information then give the figures in the form of either amount or percentages.
    For example : if in a graph between X and Y describe the value of X and Y for a particular entry on the graph 

    If there are tables, describe logically the content in the tables
    For example: if there is a table listing items and prices, say something like "the prices are the following: A for X, B for Y..."

    DO NOT include terms referring to the content format
    DO NOT mention the content type - DO focus on the content itself
    Do NOT mention that the content is confidential or not for sharing
    For example: if there is a diagram/chart and text on the image, talk about both without mentioning that one is a chart and the other is text.
    Simply describe what you see in the diagram and what you understand from the text.

    You should keep it concise, but keep in mind your audience cannot see the images so be exhaustive in describing the content.

    Exclude elements that are not relevant to the content:
    DO NOT mention page numbers or the position of the elements on the images.

    ------
    If there is an identifiable title, identify the title to give the output in the following format:

    {TITLE}
    {Content description}

    If there is no clear title, simply return the content description.

    '''

    http_client = httpx.Client(verify=False)
    client = OpenAI(api_key,http_client=http_client)
    response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    temperature=0,
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": img_url,
                },
            ],
        }
    ],
        max_tokens=2048,
        top_p=0.1
    )

    return response.choices[0].message.content


def analyze_doc_image(img):
    img_uri = get_img_uri(img)
    data = analyze_image(img_uri)
    return data


def initial_summary(path, start, end):
    images = convert_doc_to_images(path, start, end)
    data = []
    for img in images:
        try:
            data.append(analyze_doc_image(img))
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                print("Rate limit exceeded. Waiting before retrying...")
                time.sleep(60)
                data.append(analyze_doc_image(img))
            else:
                raise e
    summary = "\n _______________________________ \n".join(data)
    return summary



def final_summary(prompt):
    text = prompt
    system_prompt='''
    you will be provided text which has been summarized from a pdf your job is to only talk about the the 
    important points from the text provided in about 10 to 15 detailed bullet points.

    If the information is talking about who made the presentation or the sources DO NOT INCLUDE it in the response
    DO NOT INCLUDE the THANK YOU SLIDES or the Cover Pages

    Give a good and plain summary of the whole information which is provided to you try not to include any information about
    the team or organization who made the pdf and rather more on the actual content of the summarized text.

    '''
    http_client = httpx.Client(verify=False)
    client = OpenAI(api_key,http_client=http_client)
    response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0,
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": text,
        }
    ],
        max_tokens=2048,
        top_p=0.1
    )

    return response.choices[0].message.content.strip()

def chat_bot(content,input_prompt):

    system_prompt = '''
    You will be provided with an input prompt and content as context that can be used to reply to the prompt.
    
    You will do 2 things:
    
    1. First, you will internally assess whether the content provided is relevant to reply to the input prompt. 
    
    2a. If that is the case, answer directly using this content. If the content is relevant, use elements found in the content to craft a reply to the input prompt.

    2b. If the content is not relevant, use your own knowledge to reply or say that you don't know how to respond if your knowledge is not sufficient to answer.
    
    Stay concise with your answer, replying specifically to the input prompt without mentioning additional information provided in the context content.
    '''

    http_client = httpx.Client(verify=False)
    client = OpenAI(api_key,http_client=http_client)

    model="gpt-4o"

    prompt = f"INPUT PROMPT:\n{input_prompt}\n-------\nCONTENT:\n{content}"
    
    completion = client.chat.completions.create(
        model=model,
        temperature=0.5,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return completion.choices[0].message.content

path = r"D:\Nuvama Report_Family - 3320.pdf"
content = initial_summary(path,7,20)
input_prompt = "what is the IRR for a certain instrument"
print(chat_bot(content=content,input_prompt=input_prompt))
