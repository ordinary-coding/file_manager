import urllib.parse

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
import os

from django.utils.datastructures import MultiValueDictKeyError


def getfile(path):
    file_list = []
    base_dir = path.split('static/')[1]
    print(base_dir)
    for file in os.listdir(path):
        full_path = os.path.join(path, file)
        if os.path.isdir(full_path):
            file_list.append({
                'name': file,
                'full_path': urllib.parse.quote(full_path),
                'type': 'D'
            })
        else:
            file_list.append({
                'name': file,
                'full_path': os.path.join(base_dir, file),
                'type': 'F'
            })
    return file_list


def index(request):
    req_path = request.GET.get('full_path')
    template = loader.get_template('files/index.html')
    top_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/videos')
    if req_path:
        file_list = getfile(req_path)
    else:
        file_list = getfile(top_dir)
    prev_dir = os.path.dirname(req_path) if req_path and req_path != top_dir else None
    if prev_dir:
        prev_dir = urllib.parse.quote(prev_dir)
    return HttpResponse(template.render({"files": file_list, "full_path": req_path, 'prev_dir': prev_dir}, request))


def upload(request):
    save_path = request.GET.get('save_path')
    return render(request, 'files/upload.html', {"save_path": save_path})


def upload_action(request):
    file_name = request.POST['file_name']
    save_path = request.POST['save_path']
    try:
        original = request.FILES['upload_file']
        if original is not None:
            save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/videos')
            save_dir = save_path if save_path != 'None' else save_dir
            if file_name != 'None' and file_name is not None and file_name != '':
                file_name = file_name + '.' + original.name.split('.')[-1]
            else:
                file_name = original.name
            with open(os.path.join(save_dir, file_name), 'wb+') as up_file:
                for chunk in original.chunks():
                    up_file.write(chunk)
    except MultiValueDictKeyError as e:
        pass
    return HttpResponseRedirect("/files/?full_path="+save_path)


def mkdir(request):
    current_path = request.POST['current_path']
    dir_name = request.POST['dir_name']
    if current_path == 'None':
        current_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/videos')
    os.mkdir(os.path.join(current_path, dir_name))
    return HttpResponseRedirect("/files/?full_path=" + current_path)