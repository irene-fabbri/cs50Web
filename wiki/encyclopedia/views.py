import markdown2
import random
from datetime import datetime

from django.shortcuts import render
from django import forms
from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def read(request, name):
    #read the page name, if exists
    entry = util.get_entry(name)
    if not entry:
        return render(request, "encyclopedia/error.html", { "message": "No pages found." })
    # convert the text from merkdown2 to html (consider using re for the next step in the future)
    html = markdown2.Markdown().convert(entry)
    return render(request, "encyclopedia/entry.html", { "title":name, "text": html })

def search(request):
    # use the searchbar to look for entries
    if request.method == "POST":
        page = request.POST.get('q').strip()
        if page:
            if page in util.list_entries():
                # if there is an exact correspondence, read the selected page
                return read(request, page)
            # otherwise, print all the entries that contain the given page
            results = [x for x in util.list_entries() if page in x]
            return render(request, "encyclopedia/index.html", {
                "entries": results
            })

def add(request):
    if request.method == "POST":
        # Get the title and the content from a form
        title = request.POST.get('title').strip()
        content = "#"+title+"\n"+request.POST.get('content')
        if not util.get_entry(title):
            #if there's no entry with the same title, save it and read it
            util.save_entry(title,content)
            return read(request, title)
        else:
            return render(request, "encyclopedia/error.html", { "message": "the page already exists" })
    #render the page with the form to fill
    return render(request, "encyclopedia/add.html")

def edit(request, title):
    if request.method == "POST":
        # Get the title and the edited content from a form
        page = request.POST.get('page')
        content = request.POST.get('edited')
        util.save_entry(page,content)
        return read(request, page)
    # render the page with the form to fill, containing the pre-existing test
    content = util.get_entry(title)
    return render(request, "encyclopedia/edit.html", { "title":title, "content":content })

def random_page(request):
    # pick a random title and read the corrisponding page
    random.seed(datetime.now().timestamp())
    entry = random.choice(util.list_entries())
    return read(request, entry)
