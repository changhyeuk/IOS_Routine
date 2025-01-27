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

# 2025.01.17
# In Case of just take 1 bright / object images by time
# Prepare the bmp images and cal data

# Set folder path
folder_path = './'
#folder_list = ['Bright_025','Bright_015','Bright_005','Resol_025']
folder_list = ['0min','3min','6min']
subfolder_list = ['Bright_025','Object_025']
output_folder = 'Vadav_Cal\Raw_Data'
X_exp_time = ['0.25']

# Set global variable
width = 1620
height = 2230
# Define Dynamic Range
DRange_F = (0,4095)
DRange_N = (0,1000)
case_name = []
dark_level = []
x_begin = []
target_name = 'Bright'

df_BRT = pd.DataFrame(columns=['Time', 'Sec', 'STD', 'Median'])
df_DRK = pd.DataFrame(columns=['Time', 'STD', 'Median'])


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
        #Bright Case
        B_path = './'+test_case+'/'+subfolder_list[0]+'/Bright.raw'
        Bright_raw = image_tool.open_raw_image(B_path,height,width,1)
        Bright_median = int(np.median(Bright_raw))
        Cal_name = 'A00_'+str(Bright_median).zfill(5)+'.raw'
        image_tool.save_raw_image('./'+ output_folder + '/' + Cal_name, Bright_raw)
        image_tool.save_raw_image('./'+ output_folder + '/' + test_case+'_Bright_'+str(Bright_median)+'.raw', Bright_raw)
        #image_tool.save_simple_bmp(Bright_raw)
        shutil.copy('./'+ output_folder + '/' + test_case+'_Bright_'+str(Bright_median)+'.raw',
                    './Vadav_Cal/'+ test_case+'_Bright_'+str(Bright_median)+'.raw')


        O_path = './'+test_case+'/'+subfolder_list[1]+'/Bright.raw'
        shutil.copy(O_path, './'+output_folder+'/'+str(test_case)+'_Object_OC.raw')
        OD_path = './'+test_case+'/'+subfolder_list[1]+'/dark.raw'
        ODark_raw = image_tool.open_raw_image(OD_path,height,width,1)
        ODark_median = int(np.median(ODark_raw))
        image_tool.save_simple_bmp('./'+output_folder+'/'+test_case+'_Object_Dark_'+str(ODark_median),ODark_raw,[0, 4095])

        print(Bright_median, Cal_name)
        Dose = 1220.2 * float(X_exp_time[0]) + 3.5293
        df_BRT = df_BRT.append({'Time': test_case[0],
                                'Sec': X_exp_time[0],
                                'Dose': Dose,
                                'STD': int(np.std(Bright_raw)),
                                'Median': int(Bright_median)},
                               ignore_index=True)

        # print(Bright_median, Cal_name)
        # Dose = 1220.2 * float(X_exp_time[0]) + 3.5293
        df_DRK = df_DRK.append({'Time': test_case[0],
                                'Dose': Dose,
                                'STD': int(np.std(ODark_raw)),
                                'Median': int(ODark_median)},
                               ignore_index=True)


    Test_serise_num = input("Which test results ? ( 01 ): ")
    Bake_hr_this = input("How long baking process done? ( ex : 018 ) : ")
    output_file_n = 'Bright_Image_Info_' + Test_serise_num + 'th_' + Bake_hr_this + 'hr'
    Dark_output_file_name = 'DK_Info_' + Test_serise_num + 'th_' + Bake_hr_this + 'hr'

    df_BRT.to_excel(output_folder+'/'+output_file_n+'.xlsx')
    df_DRK.to_excel(output_folder + '/' + Dark_output_file_name + '.xlsx')

    # Plot Bright Image Median
    # x_time = df_BRT['Time'].values#.reshape(-1, 1)
    # y_dn = df_BRT['Median'].values
    # print(x_time, y_dn)
    # plt.figure()
    # plt.plot(x_time, y_dn, color='blue', marker='o', markersize=8)
    # for y_value, x_value in zip(y_dn, x_time):
    #     plt.text(x_value, y_value, f'{y_value}', ha='right')
    # plt.xlabel('Test Time [ min ]')
    # plt.ylabel('Median [ DN ]')
    # plt.title(' Bright [ Median ] Signal Variation ')
    # plt.ylim([1000, 2000])
    # #plt.xlim([0, max(x_time) * 1.1])
    # plt.grid()
    # plt.savefig(output_folder + '/Bright_Singal_Valriation.jpg', bbox_inches='tight')
    # plt.close()

    func_tool.SimpleCase_Plot(output_folder,'Bright_Variation', df_BRT)
    func_tool.SimpleCase_Plot(output_folder, 'Dark_Variation',df_DRK)
    #print(df_BRT)

