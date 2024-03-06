# ========================================
# 2023/11/30 Rolling GOC  Code Completed
# ========================================
import os
import image_tool

# Set Parameter
#======================================================
# Read the file name at the folder
folder_path = r'./Vadav_Cal/Raw_Data/'
width = 1620
height = 2230
# Define Dynamic Range
D_Range_Object = (0,4095)
D_Range_Raw = (0,4095)
D_Range_1 = (0,1000)
D_Range_2 = (0,1500)
D_Range_3 = (0,2500)
D_Size = (1620, 2230)
#======================================================

file_list = os.listdir(folder_path)
for file in file_list:
    ext = os.path.splitext(file)[-1]
    f_name = os.path.splitext(file)[0]
    if ext == '.raw' and 'Dark' not in f_name and 'Bright' not in f_name:
        target_file = os.path.join(folder_path,file)
        print(target_file)
        Source_file = image_tool.open_raw_image(target_file,height,width,1)
        image_tool.save_simple_bmp(target_file[:-4],Source_file,D_Range_1)
        image_tool.save_simple_bmp(target_file[:-4],Source_file,D_Range_2)
        image_tool.save_simple_bmp(target_file[:-4],Source_file,D_Range_3)
