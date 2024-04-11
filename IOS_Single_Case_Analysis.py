# 20240226 The Code that I have developed previously was committed and pushed

import os
import matplotlib.pyplot as plt
import pandas as pd
import func_tool

# Set folder path
folder_path = './'
folder_list = ['Bright_05']
output_folder = 'Raw_Data'
X_exp_time = ['0.5']

# Set global variable
width = 1620
height = 2230
# Define Dynamic Range
DRange_F = (0,4095)
DRange_N = (0,1000)
case_name = []
dark_level = []
x_begin = []

if __name__ == "__main__":
    # Clear Folder
    func_tool.clear_folder(folder_path)

    # Output folder check
    output_path = os.path.join(folder_path,output_folder)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Measure the median in each test case
    for test_case in folder_list:
        test_case_folder = os.path.join(folder_path,test_case)
        func_tool.extract_data(test_case_folder)

    # Find the X-ray Frame in each test case
    for test_case in folder_list:
        test_case_folder = os.path.join(folder_path,test_case)
        # Find the x-ray exposure starting frame
        X_frame = func_tool.find_x_frame(test_case_folder,5)
        print(test_case, ' X-ray Exposure at ', X_frame)
        x_begin.append(X_frame)

    print ('X-ray Exposure started at ', x_begin)
    visual_check = input (" The x-ray begin frames were detected? Y/N ")

    if visual_check == 'y' or visual_check == 'Y':
        print(visual_check)
        new_x_begin = x_begin

    else :
        print( ' Not Ok ')
        update_x_begin = input("Update the x-ray begin frame : ")
        new_x_begin = [int(xframe) for xframe in update_x_begin.split()]
        print (update_x_begin)

    x_i = 0

    df_dark = pd.DataFrame(columns=['Median'])

    for test_case in folder_list:
        test_case_folder = os.path.join(folder_path,test_case)
        d_value = func_tool.Dark_Sub_n_Sum(test_case_folder,output_path, new_x_begin[x_i])
        # print('Case : ', test_case, ' , Dark Median : ', d_value)
        # print(df_dark)
        Single_Output_File_Name = 'DK_Single_info_'+test_case
    df_dark.to_excel(os.path.join(folder_path,output_folder)+'/'+Single_Output_File_Name+'.xlsx')

    # Plot the all sum median value
    func_tool.Single_extract_Data(folder_path,folder_list, output_folder )

    # Copy Dark frame from each case to ./Vadav_Cal/Raw_Data
    for test_case in folder_list:
        print ('Used Dark at ',test_case,' case is copied ')
        func_tool.Dark_Select(folder_path,output_path,test_case)
