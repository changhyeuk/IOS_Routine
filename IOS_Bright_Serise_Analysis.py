import os

import func_tool
import image_tool
import fitting_tool

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import math
from mpl_toolkits.mplot3d import Axes3D

# Set folder path
folder_path = './'
target_folder = 'Vadav_Cal\Raw_Data'
width = 1620
height = 2230

file_list = os.listdir(folder_path)
dfs = []
dfd = []
df_hr =[]
max_median =[]

df_slop = pd.DataFrame(columns=['Serise', 'Slop', 'Intercept','Max Median'])
df_dark = pd.DataFrame(columns=['Serise', 'Median','Hr'])

# Output folder check
output_path = os.path.join(folder_path, target_folder)
if not os.path.exists(output_path):
    os.makedirs(output_path)


for file in file_list:
    if 'DK_Info_' in file and file.endswith('.xlsx'):
        #print(file, file[8:10], file[-9:-7])
        df_excel = pd.read_excel(file,engine='openpyxl')
        #print(df_excel)
        df_dark = df_dark.append({'Serise':int(file[8:10]),
                                   'Median':df_excel.iloc[0,1],
                                   'Hr':int(file[-9:-7])}, ignore_index=True)
print(df_dark)

Ex_Serise = df_dark['Serise']
Ex_Median = df_dark['Median']
Temp_Med = Ex_Median[0]
Ratio = [((value - int(Temp_Med)) / value) * 100 for value in Ex_Median]


fig, ax1 = plt.subplots()
df_dark['Serise'] = df_dark['Serise'].astype(str)
ax1.plot(df_dark['Serise'],df_dark['Median'],Marker='o',linestyle='-' )
for i in range(len(Ex_Serise)):
    plt.text(Ex_Serise[i], Ex_Median[i], str(Ex_Median[i]), ha='left')
ax1.set_xlabel('Test Serise')
ax1.set_ylabel('Mean [DN]')
ax1.set_ylim((min(Ex_Median) - 200), 2500)
ax2 = ax1.twinx()
ax2.plot(Ex_Serise, Ratio, 'ro-')
ax2.set_ylabel('Dark Signal Variation with Initial Result[%]',color='red')
plt.title('Bright 05 Dark Signal Variation')
plt.savefig(os.path.join(folder_path,target_folder)+'/'+str(i+1)+'_Dark_Signal_Variation.jpg', bbox_inches='tight')

for file in file_list:
    if 'Bright' in file and file.endswith('.xlsx'):
        df_each = pd.read_excel(file, engine='openpyxl')
        dfs.append(df_each)
        df_hr.append(int(file[-9:-7]))

plt.figure()
j = 0
inner_colors = ['royalblue', 'forestgreen', 'goldenrod', 'darkorange','lightcoral','fuchsia','blueviolet']
for df in dfs:
    print(j)
    DoseX = df['Dose'].values.reshape(-1,1)
    MedianD = df['Median'].values

    max_median.append(df.loc[2,'Median'])

    DoseX_fit, MedianD_fit, model_coef, model_intercpt, r2score = fitting_tool.linearRegression(DoseX,MedianD)
    plt.plot(DoseX_fit, MedianD_fit, color=inner_colors[j], linestyle='--')
    label_s_2 = f'Y = {model_coef[0]:.2f}X +( {model_intercpt:.2f} )'
    label_s_3 = f'R2 = {int(r2score * 100) / 100}'

    df_slop = df_slop.append({'Serise':df_hr[j],'Slop':model_coef[0],'Intercept':model_intercpt},ignore_index=True)
    plt.scatter(DoseX, MedianD, color=inner_colors[j], marker='o', linestyle='-',
                label=str(j+1)+' : '+str(df_hr[j])+' hr : '+label_s_2+', '+label_s_3)
    for y_value, x_value in zip(MedianD, DoseX):
        plt.text(x_value, y_value, f'{int(y_value):d}', ha='right')
    j=j+1
plt.xlim([0, max(DoseX_fit)])
plt.ylim([0, 3000])
plt.xlabel('Exposure Dose[uGy]')
plt.ylabel('Mean [DN]')
plt.title('X-ray Response Variation')
plt.grid()
plt.legend()
plt.savefig(os.path.join(folder_path,target_folder)+'/'+str(j)+'_Xray_ResponseCurve_Sum.jpg', bbox_inches='tight')

df_slop['Total Hr']=df_slop['Serise'].cumsum()
df_slop['S_Increase']=df_slop['Slop'].diff().fillna(df_slop['Slop'])
df_slop['Max Median']=max_median

x_min = 0
x_max = df_slop['Total Hr'].max() + (df_slop['Total Hr'].max() * 0.1)
x_reg = np.linspace(x_min, x_max, 100).reshape(-1, 1)

T_hr = df_slop['Total Hr'].values.reshape(-1,1)
S_Increase = df_slop['S_Increase'].values

x_fit_Slop, y_fitting_Slop, model_coef_Slop, model_intercpt_Slop= fitting_tool.polynomialRegression(T_hr,S_Increase, 2)

fig, ax1 = plt.subplots()
ax1.scatter(T_hr, S_Increase, marker='o')
line1, = ax1.plot(x_fit_Slop, y_fitting_Slop, color='royalblue', linestyle='--')#,
ax1.set_xlabel('90C Post Baking Time [hr]')
ax1.set_ylabel('X-ray Response Curve Slope Variation ',color='royalblue')
ax1.set_xlim([0, x_max])
ax1.set_ylim([-1, 4])
ax1.grid()

Max_M = df_slop['Max Median'].values

ax2 = ax1.twinx()
color = 'tab:lightcoral'
x_fit_max, y_fit_max, model_coef_max, model_intercpt_max= fitting_tool.polynomialRegression(T_hr,Max_M, 2)
ax2.scatter(T_hr,Max_M,color='lightcoral',marker='o')
line2, = ax2.plot(x_fit_max, y_fit_max, color='lightcoral', linestyle='--')
ax2.set_ylabel('Maximum Median from X-ray Response ', color='lightcoral')
lines = [line1, line2]
labels = [line.get_label() for line in lines]
ax2.set_xlim([0, x_max])
ax2.set_ylim([min(y_fit_max)*0.9, max(y_fit_max)*1.1])
plt.savefig(os.path.join(folder_path,target_folder)+'/'+str(j)+'_X_Response_Slop_by_Baking.jpg', bbox_inches='tight')
plt.show()




