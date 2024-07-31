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
folder_list = ['Bright_05','Bright_03','Bright_01','Teeth_05','Resol_05']
#folder_list = ['Bright_005','Bright_015','Bright_025','Teeth_025','Resol_025']
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
target_name = 'Bright'

df_BRT = pd.DataFrame(columns=['Bright', 'Sec', 'Dose','STD', 'Median'])
df_dark = pd.DataFrame(columns=['Bright','Dark_Median'])

if __name__ == "__main__":
    # Clear Folder
    func_tool.clear_folder(folder_path)

    # Output folder check
    output_path = os.path.join(folder_path,output_folder)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Measure the median in each test case
    for test_case in folder_list:

        if folder_list[0] in test_case:
            B_num = 2
        elif folder_list[1] in test_case:
            B_num = 1
        elif folder_list[2] in test_case:
            B_num = 0
        else :
            B_num= 3

        test_case_folder = os.path.join(folder_path,test_case)
        target_file_path = test_case_folder+'/'+target_name+'.raw'
        raw_image = image_tool.open_raw_image(target_file_path,height,width,1)
        # print ( np.median(raw_image))

        print(test_case, B_num)

        if B_num < 3:
            Bright_median = str(int(np.median(raw_image))).zfill(4)
            Bright_file_name = test_case_folder + '/A0' + str(B_num) + '_' + Bright_median + '.raw'
            B_index = 'A0'+ str(B_num)
            ExT = X_exp_time[B_num]
            Dose =  1220.2*float(ExT)+ 3.5293
            # print ( B_num, B_index, ExT, Dose, int(Bright_median) )
            df_BRT = df_BRT.append({'Bright':B_index,
                                    'Sec':ExT,
                                    'Dose':Dose,
                                    'STD': int(np.std(raw_image)),
                                    'Median':int(Bright_median)},
                                   ignore_index=True)
        elif B_num == 3:
            if folder_list[3] in test_case:
                Bright_file_name = test_case_folder + '/'+ folder_list[3]+'_OC_Sum' + '.raw'
            elif folder_list[4] in test_case:
                Bright_file_name = test_case_folder + '/'+ folder_list[4]+'_OC_Sum' + '.raw'
        print(Bright_file_name)
        image_tool.save_raw_image(Bright_file_name, raw_image)
        Raw_file_loc = output_folder + '/'
        shutil.move(Bright_file_name, Raw_file_loc)

    print ( df_BRT )

    Test_serise_num = input("Which test results ? ( 01 ): ")
    Bake_hr_this = input ("How long baking process done? ( ex : 018 ) : ")
    output_file_n = 'Bright_Image_Info_'+Test_serise_num+'th_'+Bake_hr_this+'hr'
    Dark_output_file_name = 'DK_Info_'+Test_serise_num+'th_'+Bake_hr_this+'hr'

    df_BRT.to_excel(output_folder+'/'+output_file_n+'.xlsx')
    #==========Plot
    x_dose = df_BRT['Dose'].values.reshape(-1,1)
    y_dn = df_BRT['Median'].values
    x_fitting, y_fitting, model_coef, model_intercpt, r2score = fitting_tool.linearRegression(x_dose,y_dn)
    plt.figure()
    plt.scatter(x_dose,y_dn,color='blue')
    for y_value, x_value in zip(y_dn, x_dose):
        plt.text(x_value, y_value, f'{y_value}', ha='right')
    plt.plot(x_fitting, y_fitting, color='red', linestyle='--')
    plt.text(0.2, 0.9, f'Y = {model_coef[0]:.2f}X +( {model_intercpt:.2f} )', fontsize=10,
             transform=plt.gca().transAxes)
    plt.text(0.2, 0.85, f'R2 = {math.floor(r2score*1000)/1000}', fontsize=10,
             transform=plt.gca().transAxes)
    plt.xlabel('Exposure Dose[uGy]')
    plt.ylabel('Median [DN]')
    plt.title(' X-ray Response Curve ')
    plt.ylim([0,4000])
    plt.xlim([0, max(x_fitting)])
    plt.grid()
    plt.savefig(output_folder+'/Xray_response.jpg', bbox_inches='tight')
    plt.close()

    pattern = re.compile(r'(\d+)\+\.raw')

    for test_case in folder_list:
        # print ( test_case )
        files_with_plus = []
        test_case_folder = os.path.join(folder_path,test_case)

        Dark_image_name = 'D0000.raw'
        Dark_image_path = test_case_folder+'/'+Dark_image_name
        D_raw_image = image_tool.open_raw_image(Dark_image_path,height,width,1)
        Dark_median = str(int(np.median(D_raw_image))).zfill(4)

        df_dark = df_dark.append({'Bright':test_case, 'Dark_Median': int(np.median(D_raw_image))}, ignore_index=True)
        New_D_image_name = test_case + '_' + Dark_image_name[:-4]+'_'+Dark_median+'.raw'
        image_tool.save_raw_image(New_D_image_name, D_raw_image)
        image_tool.save_simple_bmp(output_folder + '/'+New_D_image_name[:-4],D_raw_image,DRange_F)
        Raw_file_loc = output_folder + '/'
        shutil.move(New_D_image_name, Raw_file_loc)

    df_dark.to_excel(output_folder + '/' + Dark_output_file_name + '.xlsx')
    func_tool.Dark_Case_Plot(output_folder, df_dark)
