import os
import matplotlib.pyplot as plt
import fitting_tool
import numpy as np
import pandas as pd
import func_tool
import image_tool
import shutil
import re
import math

# Set folder path
folder_path = './'
folder_list = 'Bright_025'
output_folder = 'Vadav_Cal\Raw_Data'
X_exp_time = ['0.05','0.15','0.25']

# Set global variable
width = 1620
height = 2230
# Define Dynamic Range
DRange_F = (0,4095)
DRange_N = (0,1000)
case_name = []
dark_level = []
x_begin = []
target_list = ['Bright','dark']

df_BRT = pd.DataFrame(columns=['Bright', 'Sec', 'Dose','STD', 'Median'])
df_dark = pd.DataFrame(columns=['Bright','Dark_Median'])

if __name__ == "__main__":
    # Clear Folder
    func_tool.clear_folder(folder_path)

    # Output folder check
    output_path = os.path.join(folder_path,output_folder)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for target_name in target_list:
        test_case_folder = os.path.join(folder_path,folder_list)
        target_file_path = test_case_folder + '/' + target_name + '.raw'
        raw_image = image_tool.open_raw_image(target_file_path,height,width,1)
        target_median = str(int(np.median(raw_image))).zfill(4)
        Save_file_name = target_name+'_'+ target_median
        image_tool.save_simple_bmp(output_folder + '/' + Save_file_name, raw_image, DRange_F)
        print(target_file_path)
        shutil.copy(target_file_path,output_folder+'/'+Save_file_name+'.raw')