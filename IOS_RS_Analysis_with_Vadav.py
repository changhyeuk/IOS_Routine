
import os
import matplotlib.pyplot as plt
import pandas as pd
import func_tool

# Set folder path
folder_path = './'
folder_list = ['Bright_05','Bright_03','Bright_01','Teeth_05','Resol_05']
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