from django.shortcuts import render
from .models import Song

def login(request):
    return render(request, 'musicplayer/login.html')

def register(request):
    return render(request, 'musicplayer/register.html')

def recover(request):
    return render(request, 'musicplayer/recover.html')


"""
@app.route('/register', methods=['GET', 'POST'])
def register():

@app.route('/recover', methods=['POST', 'GET'])
def recover():

@app.route('/confirm_email/<token>', methods=['POST', 'GET'])
def confirm(token):

@app.route('/hello', methods=['POST', 'GET'])
def hello():

@app.route("/auth", methods=['POST', 'GET'])
def auth():

@app.route('/logout')
def logout():
"""

