from django.shortcuts import render
import os
from glob import glob
import pandas as pd

INPUT_FILES_PATH = f"tracker{os.path.sep}input_files"
OUTPUT_FILES_PATH = f"tracker{os.path.sep}output_files"

if not os.path.exists(INPUT_FILES_PATH):
    os.mkdir(INPUT_FILES_PATH)
    
if not os.path.exists(OUTPUT_FILES_PATH):
    os.mkdir(OUTPUT_FILES_PATH)

DEANERY_DICT = {
    'SCIENCE'   : ['CSC_UG-Computer Science_UG', 'LSC_UG-Life Science_UG'],
    'HUMANITIES': ['HUM_UG-Humanities_UG'],
    'MANAGEMENT': ['COM_UG-Commerce_UG', 'MGT_UG-Management Studies_UG']
}



def index(request):
    return render(request, 'index.html')

def import_data(request):
    success = False

    if request.method == "POST":
        date = request.POST['date']
        input_file = request.FILES["inputFile"]

        filename = f"{date}_{input_file.name.replace(' ', '_')}"
        
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
    success = False

    if request.method == "POST":

        date = request.POST['date']
        deanery = request.POST["deanery"].upper()

        output_data = {
            'date': date,
            'subject_code': None,
            'subject_title': None,
            'packets': None,
            'present': None,
            'absent': None,
        }

        print(date, deanery)

        input_file = glob(f"{INPUT_FILES_PATH}{os.path.sep}{date}_*")[0]

        df = pd.read_excel(input_file)

        deanery_data = df.loc[df['Academic Site'].isin(DEANERY_DICT[deanery])]
        subjects = deanery_data['Subject Code'].unique()

        for subject in subjects:
            subjectwise_data = deanery_data.loc[df['Subject Code'] == subject]

            output_data['subject_code'] = subject
            output_data['subject_title'] = subjectwise_data['Subject Name(Exam Dependent)'].unique()
            output_data['present'] = subjectwise_data['Attendance Status'].value_counts().get('Present', 0)
            output_data['absent'] = subjectwise_data['Attendance Status'].value_counts().get('Absent', 0)
            

        output_df = pd.DataFrame(output_data)
        output_html_path = os.path.join(OUTPUT_FILES_PATH, 'report.html')
        output_pdf_path = os.path.join(OUTPUT_FILES_PATH, f'{date}_{deanery}_report.pdf')

        output_df.to_html(output_html_path)

    params = {
        'success': success,
    }
    return render(request, 'generate_report.html', params)