from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def import_data(request):
    return render(request, 'import_data.html')

def generate_report(request):
    return render(request, 'generate_report.html')