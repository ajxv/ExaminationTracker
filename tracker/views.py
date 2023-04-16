from django.shortcuts import render
import os


INPUT_FILES_PATH = "input_files"
OUTPUT_FILES_PATH = "output_files"

def index(request):
    return render(request, 'index.html')

def import_data(request):
    success = False

    if request.method == "POST":
        date = request.POST['date']
        input_file = request.FILES["inputFile"]

        filename = f"{date}_{input_file.name.replace(' ', '_')}"

        if not os.path.exists(INPUT_FILES_PATH):
            os.mkdir(INPUT_FILES_PATH)
        
        file_save_path = os.path.join(INPUT_FILES_PATH, filename)

        with open(file_save_path, 'wb+') as destination:
            for chunk in input_file.chunks():
                destination.write(chunk)
        
            success = True

    params = {
        'success': success,
    }
    return render(request, 'import_data.html', params)

def generate_report(request):
    return render(request, 'generate_report.html')