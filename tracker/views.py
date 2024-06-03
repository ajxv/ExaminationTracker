from django.http import HttpResponse
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

uploaded_file_path = None

DEANERY_COURSE_MAP = {
    'SCIENCE'   : ['CSC_UG-Computer Science_UG', 'LSC_UG-Life Science_UG'],
    'HUMANITIES': ['HUM_UG-Humanities_UG'],
    'MANAGEMENT': ['COM_UG-Commerce_UG', 'MGT_UG-Management Studies_UG']
}

DEANERY_SUBJECT_MAP = {
    'SCIENCE'   : [],
    'HUMANITIES': [],
    'MANAGEMENT': []
}

PACKET_SIZE = 20


def index(request):
    return render(request, 'index.html')

def import_data(request):
    success = False
    global uploaded_file_path  # Declare the variable as global

    if request.method == "POST":
        date = request.POST['date']
        input_file = request.FILES["inputFile"]

        filename = f"{date}_{input_file.name.replace(' ', '_')}"
        
        file_save_path = os.path.join(INPUT_FILES_PATH, filename)

        with open(file_save_path, 'wb+') as destination:
            for chunk in input_file.chunks():
                destination.write(chunk)
        
            success = True

             # Set the uploaded file path
        uploaded_file_path = file_save_path

    params = {
        'success': success,
    }
    return render(request, 'import_data.html', params)

def generate_deanery_overall_report(request):
    date = request.POST['date']
    deanery = request.POST["deanery"].upper()

    print(date, deanery)

    input_file = glob(f"{INPUT_FILES_PATH}{os.path.sep}{date}_*")[0]

    df = pd.read_excel(input_file)

    # filter by deanery and exam shift
    deanery_data = df.loc[df['Academic Site'].isin(DEANERY_COURSE_MAP[deanery])]

    output_data = {
        'date': [date],
        'deanery': [deanery],
        'packets': [None],
        'present': [deanery_data['Attendance Status'].value_counts().get('Present', 0)],
        'absent': [deanery_data['Attendance Status'].value_counts().get('Absent', 0)],
    }

    output_df = pd.DataFrame(output_data)

    table_html = output_df.to_html()

    params = {
        'table_html': table_html,
        'deanery': deanery,
    }

    return render(request, 'report.html', params)
    

def generate_report(request):
    success = False

    if request.method == "POST":

        if 'report_type' in request.POST:
            return generate_deanery_overall_report(request)

        date = request.POST['date']
        deanery = request.POST["deanery"].upper()
        exam_shift = request.POST['exam_shift']

        output_data = {
            'date': [],
            'subject_code': [],
            'subject_title': [],
            'full_packets': [],
            'last_packets': [],
            'present': [],
            'absent': [],
        }

        print(date, deanery)

        input_file = glob(f"{INPUT_FILES_PATH}{os.path.sep}{date}_*")[0]

        df = pd.read_excel(input_file)

        # filter by deanery and exam shift
        deanery_data = df.loc[(df['Academic Site'].isin(DEANERY_COURSE_MAP[deanery])) & (df['Exam Shift'] == exam_shift)]
        subjects = deanery_data['Subject Code'].unique()

        for subject in subjects:
            # if subject not in DEANERY_SUBJECT_MAP[deanery]:
            #     continue

            subjectwise_data = deanery_data.loc[df['Subject Code'] == subject]

            output_data['date'].append(date)
            output_data['subject_code'].append(subject)
            output_data['subject_title'].append(subjectwise_data['Subject Name(Exam Dependent)'].unique()[0])
            output_data['present'].append(subjectwise_data['Attendance Status'].value_counts().get('Present', 0))
            output_data['absent'].append(subjectwise_data['Attendance Status'].value_counts().get('Absent', 0))
            output_data['full_packets'].append(output_data['present'][-1] // PACKET_SIZE)
            output_data['last_packets'].append(output_data['present'][-1] - (output_data['full_packets'][-1] * PACKET_SIZE))
            

            

        output_df = pd.DataFrame(output_data)
        # output_html_path = os.path.join(OUTPUT_FILES_PATH, 'report.html')
        # output_pdf_path = os.path.join(OUTPUT_FILES_PATH, f'{date}_{deanery}_report.pdf')

        table_html = output_df.to_html()

        params = {
            'table_html': table_html,
            'deanery': deanery,
        }

        return render(request, 'report.html', params)

    params = {
        'success': success,
    }
    return render(request, 'generate_report.html', params)

def generate_packet(request):
    global uploaded_file_path

    if request.method == "POST":
        date = request.POST['date']

        # Check if a file has been uploaded
        uploaded_file_paths = glob(f"{INPUT_FILES_PATH}{os.path.sep}{date}_*")

        # Check if a file has been uploaded
        if uploaded_file_paths:
            uploaded_file_path = uploaded_file_paths[0]  # Choose the first file if multiple are found
            # Read the data from the uploaded file
            df = pd.read_excel(uploaded_file_path)

            # Filter data for the selected date
            df_selected_date = df[df['Subject Exam Date'] == date]

            # Proceed with generating packets
            # Define the packet size
            packet_size = 20  # Adjust this value according to your requirements

            # Filter only present students (assuming 'Present' should be lowercase)
            df_present = df_selected_date[df_selected_date['Attendance Status'].str.lower() == 'present']

            # Custom sort order for Room Number
            room_order = ['M', 'A', 'B', 'H', 'P']
            df_present['RoomOrder'] = df_present['Room Number'].apply(lambda x: room_order.index(x[0]) if x[0] in room_order else 'Unknown')

            # Print any unexpected room numbers
            unknown_rooms = df_present[df_present['RoomOrder'] == 'Unknown']['Room Number'].unique()
            if len(unknown_rooms) > 0:
                print("Unexpected room numbers encountered:", unknown_rooms)

            # Sort the DataFrame by Subject Exam Date, Subject Code, RoomOrder, Room Number, and Seat Number
            df_sorted = df_present.sort_values(by=['Subject Exam Date', 'Subject Code', 'RoomOrder', 'Room Number', 'Seat Number'])

            # Remove the helper column
            df_sorted = df_sorted.drop(columns=['RoomOrder'])

            # Initialize packet number and current subject
            packet_number = 1
            current_date = None
            current_subject = None
            count_within_packet = 0

            # Iterate through the DataFrame to assign packet numbers
            for index, row in df_sorted.iterrows():
                if row['Subject Exam Date'] != current_date or row['Subject Code'] != current_subject:
                    packet_number = 1  # Reset packet number for a new date or new subject
                    count_within_packet = 0
                    current_date = row['Subject Exam Date']
                    current_subject = row['Subject Code']
                count_within_packet += 1
                df_sorted.at[index, 'PacketNumber'] = packet_number
                if count_within_packet == packet_size:
                    packet_number += 1
                    count_within_packet = 0

            # Define the path for the output Excel file
            output_file_path = os.path.join(OUTPUT_FILES_PATH, f'{date}_sorted_packeted_data.xlsx')

            # Save the sorted and packeted DataFrame to a new Excel file
            df_sorted.to_excel(output_file_path, index=False)

            # Provide the Excel file for download
            with open(output_file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename={os.path.basename(output_file_path)}'
            return response
        else:
            return HttpResponse("No file uploaded. Please upload a file first.")
    else:
        return render(request, 'generate_packet.html')