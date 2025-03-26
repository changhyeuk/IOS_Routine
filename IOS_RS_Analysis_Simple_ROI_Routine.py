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
folder_list = ['0min','3min','6min']
subfolder_list = ['Bright_025', 'Object_025']
output_folder = 'Vadav_Cal/Raw_Data'
X_exp_time = ['0.25']

# Set global variable
width = 1620
height = 2230
DRange_F = (0, 4095)
DRange_N = (0, 1000)
df_BRT = pd.DataFrame(columns=['Time', 'Sec', 'STD', 'Median'])
df_DRK = pd.DataFrame(columns=['Time', 'STD', 'Median'])

# 사용자 입력: ROI 적용 여부 및 범위
use_roi = input("Do you want to apply ROI? If No, It will Use Default Setting (yes/no): ").strip().lower()
if use_roi == "yes":
    roi_x1 = int(input("Enter ROI start row (x1): "))
    roi_x2 = int(input("Enter ROI end row (x2): "))
    roi_y1 = int(input("Enter ROI start column (y1): "))
    roi_y2 = int(input("Enter ROI end column (y2): "))
else:
    roi_x1, roi_x2, roi_y1, roi_y2 = 300, 700, 600, 1000  # 기본 ROI

if __name__ == "__main__":
    func_tool.clear_folder(folder_path)
    output_path = os.path.join(folder_path, output_folder)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for test_case in folder_list:
        print(test_case)

        # Bright Case
        B_path = f'./{test_case}/{subfolder_list[0]}/Bright.raw'
        Bright_raw = image_tool.open_raw_image(B_path, height, width, 1)
        Bright_median = int(np.median(Bright_raw[roi_x1:roi_x2, roi_y1:roi_y2]))

        Cal_name = f'A00_{str(Bright_median).zfill(5)}.raw'
        image_tool.save_raw_image(f'./{output_folder}/{Cal_name}', Bright_raw)
        image_tool.save_raw_image(f'./{output_folder}/{test_case}_Bright_{Bright_median}.raw', Bright_raw)
        shutil.copy(f'./{output_folder}/{test_case}_Bright_{Bright_median}.raw',
                    f'./Vadav_Cal/{test_case}_Bright_{Bright_median}.raw')

        # ✅ Object 이미지 복사 추가
        O_path = f'./{test_case}/{subfolder_list[1]}/Bright.raw'
        shutil.copy(O_path, f'./{output_folder}/{test_case}_Object_OC.raw')

        # Object Dark Case
        OD_path = f'./{test_case}/{subfolder_list[1]}/dark.raw'
        ODark_raw = image_tool.open_raw_image(OD_path, height, width, 1)
        ODark_median = int(np.median(ODark_raw[roi_x1:roi_x2, roi_y1:roi_y2]))

        image_tool.save_simple_bmp(f'./{output_folder}/{test_case}_Object_Dark_{ODark_median}', ODark_raw, [0, 4095])

        print(Bright_median, Cal_name)
        Dose = 1220.2 * float(X_exp_time[0]) + 3.5293

        df_BRT = pd.concat([df_BRT, pd.DataFrame([{'Time': test_case[0], 'Sec': X_exp_time[0], 'Dose': Dose,
                                                   'STD': int(np.std(Bright_raw)), 'Median': int(Bright_median)}])],
                           ignore_index=True)
        df_DRK = pd.concat([df_DRK, pd.DataFrame(
            [{'Time': test_case[0], 'Dose': Dose, 'STD': int(np.std(ODark_raw)), 'Median': int(ODark_median)}])],
                           ignore_index=True)

    Test_serise_num = input("Which test results? (01): ")
    Bake_hr_this = input("Process condition? (e.g., 90C-66hr-100torr): ")

    output_file_n = f'Bright_Image_Info_{Test_serise_num}th_{Bake_hr_this}'
    Dark_output_file_name = f'DK_Info_{Test_serise_num}th_{Bake_hr_this}'
    print(Dark_output_file_name)

    df_BRT.to_excel(f'{output_folder}/{output_file_n}.xlsx')
    df_DRK.to_excel(f'{output_folder}/{Dark_output_file_name}.xlsx')

    func_tool.SimpleCase_Plot(output_folder, 'Bright_Variation', df_BRT)
    func_tool.SimpleCase_Plot(output_folder, 'Dark_Variation', df_DRK)
