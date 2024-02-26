import os

import func_tool
import image_tool
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score

import matplotlib.pyplot as plt
import math
from mpl_toolkits.mplot3d import Axes3D


# Set folder path
folder_path = './'
# folder_list = ['Bright_01','Bright_03','Bright_05','Teeth_05','Resol_05']
target_folder = 'Vadav_Cal\Raw_Data'
width = 1620
height = 2230

file_list = os.listdir(folder_path)
dfs = []
df_hr =[]

df_slop = pd.DataFrame(columns=['Serise', 'Slop', 'Intercept'])
# df_hr = pd.DataFrame(columns=['hr'])

for file in file_list:
    if 'Bright' in file and file.endswith('.xlsx'):
        print(file, file[-9:-7])
        df_each = pd.read_excel(file, engine='openpyxl')
        print (df_each)
        dfs.append(df_each)
        df_hr.append(int(file[-9:-7]))

print(df_hr)
plt.figure()
j = 0
inner_colors = ['royalblue', 'forestgreen', 'goldenrod', 'darkorange','lightcoral','fuchsia','blueviolet']
for df in dfs:
    DoseX = df['Dose'].values.reshape(-1,1)
    MedianD = df['Median'].values

    model = LinearRegression()
    model.fit(DoseX, MedianD)

    x_min = 0
    x_max = DoseX.max() + (DoseX.max() * 0.1)
    x_reg = np.linspace(x_min, x_max, 100).reshape(-1, 1)

    plt.plot(x_reg, model.predict(x_reg), color=inner_colors[j], linestyle='--')
    label_s_2 = f'Y = {model.coef_[0]:.2f}X +( {model.intercept_:.2f} )'
    label_s_3 = f'R2 = {math.floor(r2_score(MedianD, model.predict(DoseX)) * 1000) / 1000}'

    print ( model.coef_[0], model.intercept_ )
    #df.append({'sec': ExposureT[i],
    df_slop = df_slop.append({'Serise':df_hr[j],'Slop':model.coef_[0],'Intercept':model.intercept_},ignore_index=True)

    plt.scatter(DoseX, MedianD, color=inner_colors[j], marker='o', linestyle='-',
                label=str(j+1)+' : '+str(df_hr[j])+' hr : '+label_s_2+', '+label_s_3)

    for y_value, x_value in zip(MedianD, DoseX):
        plt.text(x_value, y_value, f'{int(y_value):d}', ha='right')
    j=j+1
plt.xlim([0, x_max])
plt.ylim([0, 3000])#max(model.predict(x_reg))])
plt.xlabel('Exposure Dose[uGy]')
plt.ylabel('Mean [DN]')
plt.grid()
plt.legend()
plt.savefig(folder_path + 'Sum_Xray_ResponseCurve.jpg', bbox_inches='tight')

print(df_slop)
df_slop['Total Hr']=df_slop['Serise'].cumsum()
df_slop['S_Increase']=df_slop['Slop'].diff().fillna(df_slop['Slop'])
print (df_slop)

plt.figure()

BakingHr = df_slop['Total Hr'].values.reshape(-1, 1)
SlopX = df_slop['S_Increase'].values

poly = PolynomialFeatures(degree=2)
Baking_poly = poly.fit_transform(BakingHr)#[:,np.newaxis])

model = LinearRegression()
model.fit(Baking_poly, SlopX)

# print(model.coef_)

coef = model.coef_

x_min = 0
x_max = BakingHr.max() + (BakingHr.max() * 0.1)
x_reg = np.linspace(x_min, x_max, 100).reshape(-1, 1)

X_fit_poly = poly.transform(x_reg)#[:, np.newaxis])  # 다항 특성 변환
y_fit = model.predict(X_fit_poly)  # 예측값 계산

plt.scatter(BakingHr, SlopX, marker='o')
plt.plot(x_reg, y_fit, color='royalblue', linestyle='--')
         # label=f"{coef[2]:.3f}x^2 + {coef[1]:.3f}x + {coef[0]:.3f}")
plt.xlabel('Baking Time - 90C [Hr]')
plt.ylabel('X-ray Response Curve Slope Variation ')
plt.legend()
plt.xlim([0, x_max])
plt.grid()
plt.show()

    #     if 'Bright' in filename:
    #         print (filename)
#             open_file_path = os.path.join(folder_path,target_folder,filename)
#             print( open_file_path)
#             img = image_tool.open_raw_image(open_file_path,height,width,1)
#             print ( 'STD : ', np.std(img), '  Mean : ', np.mean(img))
#             df = df.append({'Bright':filename[:3],'STD':np.std(img),'Mean':np.mean(img)}, ignore_index=True)
# print(df)
#
# df.to_excel(target_folder + '/Bright_images_STD_Mean.xlsx')

#df_each = pd.read_excel(test_case_folder + '/Median_Signal_Variation.xlsx', engine='openpyxl')
