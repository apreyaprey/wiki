import random
from markdown2 import Markdown

from re import search
from django import forms
from django.forms.forms import Form
from django.forms.widgets import Textarea
from django.http.response import HttpResponse
from django.shortcuts import render

from . import util

markdowner = Markdown()


class NewSearch(forms.Form):
    item = forms.CharField()


class Content(forms.Form):
    heading = forms.CharField(label="Heading")
    textarea = forms.CharField(widget=forms.Textarea, label="")


def index(request):
    if request.method == "POST":
        form = NewSearch(request.POST)

        if form.is_valid():

            task = form.cleaned_data["item"]
            subString = [i for i in util.list_entries() if task in i]
            # check if the entry exist and give out the result page with a heading

            if task in util.list_entries():
                page = util.get_entry(task)
                converted_page = markdowner.convert(page)
                return render(request, "encyclopedia/search.html", {
                    'form': NewSearch(),
                    'content': converted_page,
                    'result': task
                })
            elif len(subString) != 0:
                return render(request, "encyclopedia/index.html", {
                    'form': NewSearch(),
                    "entries": subString
                })
            # otherwise give an error page

            else:
                return render(request, "encyclopedia/error.html", {
                    'form': NewSearch(),
                    'message': "Not found",
                    'errorTitle': "Search results"
                })

        else:
            # if the search is invalid then the same form is returned
            return render(request, "encyclopedia/index.html", {
                'form': form
            })

    # this is the main page
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(), 'form': NewSearch()

    })


def entry(request, title):

    if title in util.list_entries():
        page = util.get_entry(title)
        converted_page = markdowner.convert(page)
        return render(request, "encyclopedia/entry.html", {
            'content': converted_page,
            'form': NewSearch(),
            'title': title
        })


def create(request):
    if request.method == 'POST':

        content = Content(request.POST)

        if content.is_valid():

            title = content.cleaned_data['heading']
            textarea = content.cleaned_data['textarea']

            if title in util.list_entries():
                return render(request, "encyclopedia/error.html", {
                    'form': NewSearch(),
                    'message': "Page already exist",
                    'errorTitle': "Error"
                })
            else:
                util.save_entry(title, textarea)

                converted_page = markdowner.convert(textarea)

                return render(request, "encyclopedia/entry.html", {
                    'content': converted_page,
                    'form': NewSearch(),
                    'title': title
                })

    return render(request, "encyclopedia/create.html", {
        'content': Content(),
        'form': NewSearch()
    })


def edit(request, title):

    if request.method == 'GET':

        content = util.get_entry(title)
        page = Content(initial={'textarea': content, 'heading': title})

        return render(request, "encyclopedia/edit.html", {
            'form': NewSearch(),
            'content': page
        })

    if request.method == 'POST':
        page = Content(request.POST)

        if page.is_valid():
            textarea = page.cleaned_data["textarea"]
            converted_page = markdowner.convert(textarea)
            util.save_entry(title, textarea)

            return render(request, "encyclopedia/entry.html", {
                'title': title,
                'content': converted_page,
                'form': NewSearch()
            })


def randomPage(request):

    list = util.list_entries()
    listlength = len(list)-1

    randomIndex = random.randint(0, listlength)
    title = list[randomIndex]
    content = util.get_entry(title)
    converted_page = markdowner.convert(content)

    return render(request, "encyclopedia/entry.html", {
        'form': NewSearch(),
        'title': title,
        'content': converted_page
    })
