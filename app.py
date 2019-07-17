from flask import Flask, render_template, request, url_for, redirect ,session, flash, logging
import os
import json
from functools import wraps
from collections import defaultdict


app = Flask(__name__)

def parsejson(name):
    with open(name+'.json') as json_data:
        data = json.load(json_data)
        scraped_data_link = defaultdict(list)

        for i in range(len(data)):
            tempid = 'id'+str(i)
            tempList = []

            link = data[i]['display_url']
            tempList.append(link)

            like = data[i]['edge_liked_by']['count']
            tempList.append(like)

            tempcomment = defaultdict(list)

            if data[i]['edge_media_to_comment']['count'] != 0:
                comment_data = data[i]['edge_media_to_comment']['data']
                for comment in comment_data:
                    username = comment['owner']['username']
                    text = comment['text']

                    tempcomment[tempid].append((username,text))
            else:
                tempcomment[tempid].append('No Comments')

            tempcomment = dict(tempcomment)
            tempList.append(tempcomment)
            scraped_data_link[tempid].append(tempList)

        scraped_data_link = dict(scraped_data_link)

        return scraped_data_link

@app.route('/')
def index():
    return render_template('home.html') 

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):

        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized Credentials not provided', 'danger')
            return redirect(url_for('login'))

    return wrap

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out','success')
    return redirect(url_for('login'))

@app.route('/scrape', methods=['GET', 'POST'])
@is_logged_in
def scrape():
    if request.method == "POST":

        brand = request.form['brand']
        product = request.form['product']
        session['brand'] = brand
        session['product'] = product

        return redirect(url_for("scrape_result"))

    return render_template('scrape.html')

@app.route('/scrape_result')
@is_logged_in
def scrape_result():
    os.system('instagram-scraper --tag '+ str(session['brand']) +','+ str(session['product']) +' -u '+ str(session['username']) +' -p '+ str(session['password']) +' -m 3 --comment -t JPG')

    try:
        scraped_data_link = parsejson(session['brand']+'/'+session['brand'])
    except:
        flash('No result for'+session['brand'], 'danger')

    try:
        scraped_data_link1 = parsejson(session['product']+'/'+session['product'])
    except:
        flash('No result for'+session['product'], 'danger')

    return render_template('scrape_result.html',scraped_data_link=scraped_data_link,scraped_data_link1=scraped_data_link1,brand=session['brand'],product=session['product'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']

        session['logged_in'] = True
        session['username'] = username
        session['password'] = password

        flash('Thanks For credentials', 'success')
        return redirect(url_for('scrape'))

    return render_template('login.html')



if __name__ == "__main__":
    app.secret_key = 'secret123'
    app.run(debug=True)
