import pandas as pd

# Define the packet size
packet_size = 20  # Adjust this value according to your requirements

# Define the path to your Excel file
file_path = r'C:\Users\Admin\Documents\Atten\UG.xlsx'  # Update the file name accordingly

# Read the data from the Excel file
df = pd.read_excel(file_path)

# Filter only present students (assuming 'Present' should be lowercase)
df_present = df[df['Attendance Status'].str.lower() == 'present']

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
output_file_path = r'C:\Users\Admin\Documents\Atten\UG-sorted_packeted_data1.xlsx'

# Save the sorted and packeted DataFrame to a new Excel file
df_sorted.to_excel(output_file_path, index=False)

print("Processing complete. The sorted and packeted data has been saved to:", output_file_path)
