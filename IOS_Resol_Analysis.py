
import os
import matplotlib.pyplot as plt
import pandas as pd
import func_tool
import image_tool
import numpy as np

# Set folder path
folder_path = './'
folder_list = ['Resol_05']#, 'Bright_03', 'Bright_01']
output_folder = 'Raw_Data'
X_exp_time = ['0.5']
T_file_list = ['D0001.raw']#['Bright.raw', 'D0001.raw']

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
        print ( test_case )
        for T_file in T_file_list:
        #     raw_file_path = os.path.join(folder_path,test_case,T_file)
        #     raw_image = image_tool.open_raw_image(raw_file_path,height,width,1)
        #     T_file_Name = T_file[:-4]+'_'+str(int(np.median(raw_image)))
        #     T_file_path =  os.path.join(folder_path,test_case,T_file_Name)
        #
        #     if T_file == 'D0001.raw':
        #         image_tool.save_simple_bmp(T_file_path, raw_image, DRange_F)
        #     else :
        #         D_Range = func_tool.Dynamic_Range_Selection(raw_image)
        #         image_tool.save_simple_bmp(T_file_path, raw_image, DRange_F)
        #         image_tool.save_simple_bmp(T_file_path, raw_image, D_Range)
        #     #print(D_Range)
