import os
import pandas as pd
import matplotlib.pyplot as plt
import math

# Set folder path
folder_path = './'
target_folder = 'Vadav_Cal/Raw_Data'

width = 1620
height = 2230

inner_colors = ['red','royalblue', 'forestgreen', 'goldenrod', 'darkorange','lightcoral','fuchsia','blueviolet',
                'navy','seagreen', 'crimson', 'lawngreen', 'olive', 'orangered', 'dimgrey', 'fuchsia', 'blue',
                'aqua', 'lime','darkkhaki','saddlebrown','darkred']

# 파일 리스트 가져오기
file_list = os.listdir(os.path.join(folder_path, target_folder))

# 두 개의 다른 키워드를 처리하기 위한 리스트 생성
categories = ["Bright", "DK"]
data = {category: {"dfs": [], "df_hr": [], "df_case": []} for category in categories}

# 파일 리스트에서 'Bright'와 'DK'를 분리하여 저장
for file in file_list:
    for category in categories:
        if category in file and file.endswith('.xlsx'):
            print(os.path.join(folder_path, target_folder, file))
            df_each = pd.read_excel(os.path.join(folder_path, target_folder, file), engine='openpyxl')
            data[category]["dfs"].append(df_each)
            data[category]["df_hr"].append(int(file[-10:-7]))
            data[category]["df_case"].append(int(file[-15:-13]))

# Bright와 DK 각각에 대해 처리
for category in categories:
    dfs = data[category]["dfs"]
    df_hr = data[category]["df_hr"]
    df_case = data[category]["df_case"]

    if len(dfs) == 0:
        continue  # 해당 카테고리에 파일이 없으면 스킵

    plt.figure()
    all_medianD = []
    j = 0

    for df in dfs:
        DoseX = df['Time'].values.reshape(-1, 1)
        MedianD = df['Median'].values
        all_medianD.extend(MedianD)

        plt.plot(DoseX, MedianD,
                 color=inner_colors[j], marker='o', linestyle='-', label=f'{j+1} : {df_hr[j]} hr ')
        for y_value, x_value in zip(MedianD, DoseX):
            plt.text(x_value, y_value, f'{int(y_value):d}', ha='right')
        j += 1

    plt.ylim([math.floor(min(all_medianD)/100)*100, math.ceil(max(all_medianD)/100)*100])
    plt.xlabel('Time [min]')
    plt.ylabel('Mean [LSB]')
    plt.title(f'{category} Signal Variation')
    plt.grid()
    plt.legend(fontsize='small')
    save_path = os.path.join(folder_path, target_folder, f'{category}_Signal_Variation.jpg')
    plt.savefig(save_path, bbox_inches='tight')
    print(f'Saved: {save_path}')