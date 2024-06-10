from django.shortcuts import render
from django.http import Http404
import markdown2
from . import util
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
import random

def index(request): 
    return render(request, 'encyclopedia/index.html', {
        "entries": util.list_entries()
    })

def entry(request, title):
    try:
        entry = markdown2.markdown(util.get_entry(title))
    except TypeError:
        raise Http404('Page ' + title + ' does not exist')
    return render(request, 'encyclopedia/entry.html', {        
        'title': title,
        'entry': entry
    })

def search(request):
    userInput = request.GET.get('q')
    try:
        return entry(request, userInput)
    except Http404:
        list_entries = list(filter(lambda e: userInput.lower() in e.lower(), util.list_entries()))
        return render(request, 'encyclopedia/search.html', {        
        'entries': list_entries
        })

class CreateForm(forms.Form):
    title = forms.CharField(label='Title')
    title.widget.attrs.update({'class': 'form-control'})
    content = forms.CharField(label='Content', widget=forms.Textarea())
    content.widget.attrs.update({'class': 'form-control'})
    
    def clean_title(self):
        data = self.cleaned_data['title']
        if data.lower() in [i.lower() for i in util.list_entries()]:
            raise ValidationError('An entry already exists with the provided title')
        elif any(not c.isalnum() for c in data):
            raise ValidationError('Title must contain exclusively alphanumeric characters')
        return data

def create(request):
    if request.method == 'POST':
        form = CreateForm(request.POST)
        if form.is_valid():
            title = form.clean_title()
            content = form.cleaned_data['content']           
            util.save_entry(title, content)
            url = reverse('encyclopedia:entry', kwargs={'title': title})
            return HttpResponseRedirect(url)
        else:
            return render(request, 'encyclopedia/create.html', {
            'form': form
            })
    return render(request, 'encyclopedia/create.html', {
        'form': CreateForm()
    })

class EditForm(forms.Form):
    content = forms.CharField(label='Content', widget=forms.Textarea())
    content.widget.attrs.update({'class': 'form-control'})

def edit(request, title):
    if util.get_entry(title) is None:
        raise Http404('Page ' + title + ' does not exist')
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            util.save_entry(title, content)
            url = reverse('encyclopedia:entry', kwargs={'title': title})
            return HttpResponseRedirect(url)
        else:
            return render(request, 'encyclopedia/edit.html', {
            'form': form
            })        
    
    data = {'content': util.get_entry(title)}
    form = EditForm(data)
    return render(request, 'encyclopedia/edit.html', {
            'form': form,
            'title': title
            })

def lucky(request):
    title = random.choice(util.list_entries())
    url = reverse('encyclopedia:entry', kwargs={'title': title})
    return HttpResponseRedirect(url)
