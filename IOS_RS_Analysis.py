# 20240226 The Code that I have developed previously was committed and pushed

import os
import matplotlib.pyplot as plt
import func_tool

# Set folder path
folder_path = './'
folder_list = ['Bright_05','Bright_03','Bright_01','Teeth_05','Resol_05']
output_folder = 'Vadav_Cal\Raw_Data'
X_exp_time = ['0.1','0.3','0.5']

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
        print ()

    x_i = 0
    for test_case in folder_list:
        test_case_folder = os.path.join(folder_path,test_case)
        d_value = func_tool.Dark_Sub_n_Sum(test_case_folder,output_path, new_x_begin[x_i])
        print('Case : ', test_case, ' , Dark Median : ', d_value)
        case_name.append(test_case)
        dark_level.append(d_value)
        x_i += 1

    plt.plot(case_name,dark_level,'bo-')
    temp_d = dark_level[0]
    result = [((value - int(temp_d))/value)*100 for value in dark_level]

    fig, ax1 = plt.subplots()
    ax1.plot(case_name,dark_level,'bo-')
    for i, v in enumerate(case_name):
        ax1.text(v,dark_level[i],dark_level[i],horizontalalignment='center',verticalalignment='bottom')
    ax1.set_ylabel('Dark Median [DN]',color='blue')
    ax1.set_xlabel('Test Case')
    ax1.set_ylim((min(dark_level) -200),4095)
    ax2 = ax1.twinx()
    ax2.plot(case_name,result, 'ro-')
    ax2.set_ylabel('Signal Variation with Bright_05 [%]',color='red')
    # plt.show()
    plt.savefig(output_folder + '/Dark_Level_Variation.jpg',bbox_inches='tight')
    plt.close()

    # Plot the all sum median value
    func_tool.Sum_extract_Data(folder_path,folder_list, output_folder )
    func_tool.X_Response(folder_path,output_folder,X_exp_time)

    # Copy Dark frame from each case to ./Vadav_Cal/Raw_Data
    for test_case in folder_list:
        print ('Used Dark at ',test_case,' case is copied ')
        func_tool.Dark_Select(folder_path,output_path,test_case)
