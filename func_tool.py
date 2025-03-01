import os
import image_tool
import fitting_tool
import matplotlib.pyplot as plt
import numpy as np
import shutil
import pandas as pd
import re
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import matplotlib.patches as patches
import math

from IOS_RS_Analysis import width, height, DRange_F, DRange_N

def find_x_frame(folder_name,threshold):
    initial_dark = image_tool.open_raw_image(folder_name+'/0000.raw',height,width,1)
    ave_frame = []
    file_index = []
    num = 0
    for i in range(0, 10):
        # Raw Image Read and Masking
        img_temp = image_tool.open_raw_image(folder_name + '/000' + str(i) + '.raw',height,width, 1)
        OC_image = img_temp - initial_dark
        image_tool.save_bmp_image(folder_name + '/DSUB_000' + str(i), OC_image, DRange_N, (int(width/2), int(height/2)))
        ave_frame.append(np.std(OC_image))
    for j in (np.diff(ave_frame)-ave_frame[1]):
        num = num + 1
        if j > threshold:
            file_index.append(num)
    #print(file_index)
    if not file_index:
        file_index.append(5)

    x_begin = file_index[0]
    plt.plot(np.diff(ave_frame), 'bo-')
    plt.xlabel('Obtained Frame [#]')
    plt.ylabel('Derivative STD of frames')
    plt.savefig(folder_name + '/Std_Signal_Variation.jpg',bbox_inches='tight')
    plt.close()
    ave_frame.clear()
    return x_begin

def Dark_Sub_n_Sum(folder_name, target_folder, frame_num):

    folders = os.path.split(folder_name)
    case_name = folders[-1]

    if 'Bright_01' in case_name:
        B_num = 0
    elif 'Bright_03' in case_name:
        B_num = 1
    elif 'Bright_05' in case_name:
        B_num = 2

    OC_image = np.zeros((height, width), dtype=np.int16)

    new_dark = image_tool.open_raw_image(folder_name+'/000'+str(frame_num-1)+'.raw',height,width,1)
    image_tool.save_bmp_image(folder_name+'/'+case_name+'_Dark_000'+str(frame_num-1)+'_'+str(int(np.median(new_dark)))\
                              ,new_dark, DRange_F, (width, height))
    image_tool.save_simple_bmp(folder_name+'/'+case_name+'_Dark_000'+str(frame_num-1)+'_'+str(int(np.median(new_dark)))\
                               ,new_dark,DRange_F)
    image_tool.save_raw_image(folder_name+'/'+case_name+'_Dark_000'+str(frame_num-1)+'.raw', new_dark)

    for k in range(frame_num,frame_num+3):
        img_temp = image_tool.open_raw_image(folder_name + '/000' + str(k) + '.raw', height, width, 1)
        OC_image_temp = img_temp - new_dark
        OC_image = OC_image + OC_image_temp
        QC_median = str(int(np.median(OC_image))).zfill(5)

    if 'Bright' in case_name:
        image_tool.save_raw_image(target_folder+'/A0'+str(B_num)+'_'+QC_median+'.raw',OC_image)
        image_tool.save_raw_image(target_folder+'/'+case_name+'_OC_sum_py.raw',OC_image)
        #image_tool.save_simple_bmp(target_folder+'/'+case_name+'_OC_sum',OC_image, DRange_F)
    else:
        image_tool.save_raw_image(target_folder+'/'+case_name+'_OC_sum_py.raw',OC_image)
        image_tool.save_simple_bmp(target_folder+'/'+case_name+'_OC_sum',OC_image, DRange_F)

    return int(np.median(new_dark))

def Dark_Select(source_path,target_path,file_name):
    file_path = os.path.join(source_path,file_name)
    file_list = os.listdir(file_path)
    for file in file_list:
        if 'Dark' in file:
            s_file = os.path.join(file_path,file)
            d_file = os.path.join(target_path,file)
            shutil.move(s_file,d_file)

def clear_folder(folder_path):
    for (path, dir, files) in os.walk(folder_path):
        for filename in files:
            if 'Dark' in filename or '.bmp' in filename or '.jpg' in filename or '.xlsx' in filename:
                file_path = os.path.join(path, filename)
                os.remove(file_path)
        if 'Vadav_Cal' in path:
            shutil.rmtree(path)

def list_subfolders(folder_path):
    subfolders = [f.name for f in os.scandir(folder_path) if f.is_dir()]
    return subfolders

def extract_data(Folder_Path):
    print ( Folder_Path )
    df = pd.DataFrame(columns=['Frame #', 'Median'])
    case_median =[]
    for i in range(0, 10):
        # Raw Image Read and Masking
        img_temp = image_tool.open_raw_image(Folder_Path + '/000' + str(i) + '.raw', height, width, 1)
        temp_median = np.median(img_temp)
        df = df.append({'Frame #': i, 'Median':temp_median}, ignore_index=True)
        case_median.append(temp_median)

    df.to_excel(Folder_Path+'/Median_Signal_Variation.xlsx')
    plt.figure()
    plt.plot(case_median, 'bo-')
    plt.xlabel('Obtained Frame [#]')
    plt.ylabel('Median [DN]')
    plt.savefig(Folder_Path + '/Median_Signal_Variation.jpg', bbox_inches='tight')
    plt.close()


def Sum_extract_Data(Folder_Path, List, Out_Folder):
    dfs = []
    for test_case in List:
        test_case_folder = os.path.join(Folder_Path, test_case)
        df_each = pd.read_excel(test_case_folder+'/Median_Signal_Variation.xlsx', engine='openpyxl')
        dfs.append(df_each)

    Case_Out_folder = os.path.join(Folder_Path, Out_Folder)

    merged_df = pd.concat(dfs,ignore_index=True)
    merged_df.to_excel(Case_Out_folder+'/All_Median_Signal_Variation.xlsx')

    x_median = merged_df['Median']

    plt.figure()
    for i in range(0, 50, 10):
        if i < 10:
            color = 'red'
            group_label = List[0]
        elif i < 20:
            color = 'orange'
            group_label = List[1]
        elif i < 30:
            color = 'yellow'
            group_label = List[2]
        elif i < 40:
            color = 'blue'
            group_label = List[3]
        else:
            color ='green'
            group_label = List[4]
        plt.plot(merged_df.loc[i:i+9,'Median'], linestyle='-', marker='o', color=color,label=group_label)
        plt.legend(loc='upper center')
    plt.xlabel('Obtained Frame [#]')
    plt.ylabel('Median [DN]')
    plt.ylim([1000,3000])
    plt.savefig(Case_Out_folder + '/All_Median_Signal_Variation.jpg', bbox_inches='tight')
    plt.close()


def Single_extract_Data(Folder_Path, List, Out_Folder):
    dfs = []
    for test_case in List:
        test_case_folder = os.path.join(Folder_Path, test_case)
        df_each = pd.read_excel(test_case_folder+'/Median_Signal_Variation.xlsx', engine='openpyxl')
        dfs.append(df_each)

    Case_Out_folder = os.path.join(Folder_Path, Out_Folder)

    merged_df = pd.concat(dfs,ignore_index=True)
    merged_df.to_excel(Case_Out_folder+'/All_Median_Signal_Variation.xlsx')

    x_median = merged_df['Median']

    plt.figure()
    plt.plot(x_median, linestyle='-', marker='o', color='blue')#,label=group_label)
    plt.legend(loc='upper center')
    plt.xlabel('Obtained Frame [#]')
    plt.ylabel('Median [DN]')
    plt.savefig(Case_Out_folder + '/All_Median_Signal_Variation.jpg', bbox_inches='tight')
    plt.close()


def X_Response(Folder_Path,Out_Folder,ExposureT,Dark_Info):
    # # uGy = 1220.2 x sec  + 3.5293
    df = pd.DataFrame(columns=['Bright','sec','Dose', 'STD', 'Median'])

    num = 0
    for i in ExposureT:
        file_string = 'A0'+str(num)
        num=num+1
        out_files = os.listdir(Folder_Path+Out_Folder)
        match_files = [file for file in out_files if file_string in file]
        targe_file = os.path.join(Folder_Path,Out_Folder,match_files[0])
        select_image = image_tool.open_raw_image(targe_file, height, width, 1)
        cal_dose = 1220.2*float(i)+ 3.5293
        df = df.append({'Bright': file_string, 'sec': i, 'Dose': cal_dose,'STD':int(np.std(select_image)),
                        'Median':int(np.median(select_image))}, ignore_index=True)

    Test_serise = input("Which test results ? ( 01 ): ")
    Bake_hr = input ("How long baking process done? ( ex : 018 ) : ")
    output_file_name = 'Bright_Image_Info_'+Test_serise+'th_'+Bake_hr+'hr'
    Dark_output_file_name = 'DK_Info_'+Test_serise+'th_'+Bake_hr+'hr'

    df.to_excel(os.path.join(Folder_Path,Out_Folder) + '/'+output_file_name+'.xlsx')
    Dark_Info.to_excel(os.path.join(Folder_Path,Out_Folder)+'/'+Dark_output_file_name+'.xlsx')
    x_dose = df['Dose'].values.reshape(-1,1)
    y_dn = df['Median'].values

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
    plt.ylim([0,3000])
    plt.xlim([0, max(x_fitting)])
    plt.grid()
    plt.savefig(os.path.join(Folder_Path,Out_Folder)+'/'+output_file_name+'.jpg', bbox_inches='tight')
    plt.close()

def Dark_SubNSum(folder_name, target_folder, frame_num):

    folders = os.path.split(folder_name)
    case_name = folders[-1]

    if 'Bright_01' in case_name:
        B_num = 0
    elif 'Bright_03' in case_name:
        B_num = 1
    elif 'Bright_05' in case_name:
        B_num = 2

    OC_image = np.zeros((height, width), dtype=np.int16)

    new_dark = image_tool.open_raw_image(folder_name+'/000'+str(frame_num-1)+'.raw',height,width,1)
    image_tool.save_bmp_image(folder_name+'/'+case_name+'_Dark_000'+str(frame_num-1)+'_'+str(int(np.median(new_dark)))\
                              ,new_dark, DRange_F, (width, height))
    image_tool.save_simple_bmp(folder_name+'/'+case_name+'_Dark_000'+str(frame_num-1)+'_'+str(int(np.median(new_dark)))\
                               ,new_dark,DRange_F)
    image_tool.save_raw_image(folder_name+'/'+case_name+'_Dark_000'+str(frame_num-1)+'.raw', new_dark)

    for k in range(frame_num,frame_num+3):
        img_temp = image_tool.open_raw_image(folder_name + '/000' + str(k) + '.raw', height, width, 1)
        OC_image_temp = img_temp - new_dark
        OC_image = OC_image + OC_image_temp
        QC_median = str(int(np.median(OC_image))).zfill(5)

    if 'Bright' in case_name:
        image_tool.save_raw_image(target_folder+'/A0'+str(B_num)+'_'+QC_median+'.raw',OC_image)
        image_tool.save_raw_image(target_folder+'/'+case_name+'_OC_sum_py.raw',OC_image)
        #image_tool.save_simple_bmp(target_folder+'/'+case_name+'_OC_sum',OC_image, DRange_F)
    else:
        image_tool.save_raw_image(target_folder+'/'+case_name+'_'+QC_median+'_OC_sum_py.raw',OC_image)
        image_tool.save_simple_bmp(target_folder+'/'+case_name+'_'+QC_median+'_OC_sum',OC_image, DRange_F)

    return int(np.median(new_dark)), int(np.median(OC_image))

def Dark_Case_Plot(outputfolder,df):
    print (df)
    Dark_case = df['Bright']
    Dark_median = df['Dark_Median']

    base_value = Dark_median[0]
    percentage_change = [(value - base_value) / base_value * 100 for value in Dark_median]

    fig, ax1 = plt.subplots()

    ax1.plot(Dark_case, Dark_median, linestyle='-', marker='o', color='orange')
    for i, value in enumerate(Dark_median):
        ax1.text(Dark_case[i], value + 20, str(value), ha='center')

    ax1.set_ylim([0, 4095])
    ax1.set_xlabel('Test Case')
    ax1.set_ylabel('Median [DN]')
    ax1.set_title('Dark Median Variation')
    ax1.grid()

    # Create a second y-axis for the percentage change
    ax2 = ax1.twinx()
    ax2.plot(Dark_case, percentage_change, linestyle='--', marker='x', color='red')
    for i, pct in enumerate(percentage_change):
        ax2.text(Dark_case[i], pct + 2, f'{pct:.1f}%', ha='center', color='red')
    ax2.set_ylim([0, 100])
    ax2.set_ylabel('Percentage Change [%]', color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    plt.savefig(outputfolder+'/Dark_Varation.jpg',bbox_inches='tight')

def Dynamic_Range_Selection(raw_i):
    temp = int(np.median(raw_i))
    if temp > 3500:
        DR_Max = 4095
    else:
        DR_Max = ((int(np.median(raw_i)) + 499) // 500) * 500
    DR = (0, DR_Max)
    return DR

def ROI_Selection(T_file,ratio_set):

    print(ratio_set)

    if ratio_set == 0:
        ratio = 1
    else:
        ratio = 1.37


    clicked_points = []
    print(np.min(T_file), np.max(T_file))
    T_max_500 = 500 * round(np.max(T_file) / 500)

    fig, ax = plt.subplots()
    ax.imshow(T_file, cmap='gray', vmin=np.min(T_file), vmax=np.max(T_file))
    fig.canvas.mpl_connect('button_press_event', lambda event: image_tool.onclick(event, clicked_points))
    plt.show()

    point_i, point_e, s_width, s_height = image_tool.digit_points(clicked_points)
    #print(point_i, point_e, s_width, s_height)
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.imshow(T_file, cmap='gray', vmin=0, vmax=4095)#T_max_500)
    ax1.set_title(f'Original Image\nDisplay Range [0 {T_max_500}]')
    # ax1.axis('off')
    ax1.get_xaxis().set_visible(False)
    ax1.get_yaxis().set_visible(False)

    # rect = patches.Rectangle(point_i, s_width, s_height, linewidth=1, edgecolor='r', facecolor='none')
    rect = patches.Rectangle(point_i, s_width, int(s_width * ratio), linewidth=1, edgecolor='r', facecolor='none')

    ax1.add_patch(rect)
    select_image = T_file[int(point_i[1]):int(point_i[1] + (point_e[0] - point_i[0]) * ratio),
                   int(point_i[0]): int(point_e[0])]
    ax2.imshow(select_image, cmap='gray', vmin=0, vmax=T_max_500)
    # ax2.axis('off')
    ax2.get_xaxis().set_visible(False)
    ax2.get_yaxis().set_visible(False)
    ax2.set_title(f'Selected Area\nDisplay Range [0 {T_max_500}]')
    # fig.suptitle('UB97 ' +str(file_list) + ' ['+ str(N_Range_1[0])+' '+str(N_Range_1[1]) +']')
    #plt.savefig(folder_path + file_list[0] + '_ImageSelection.tif')
    plt.show()
    return point_i, point_e, ratio