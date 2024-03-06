import matplotlib.pyplot as plt
import numpy as np
import cv2

def open_raw_image(file_path, H, W, Mask):
    if Mask == 0 :
        with open(file_path, 'rb') as f:
            # RAW 파일을 numpy 배열로 읽기
            raw_data = np.frombuffer(f.read(), dtype=np.int16)

        # image reshape
        image_raw = raw_data.reshape((H, W))

        return image_raw
    elif Mask == 1:
        with open(file_path, 'rb') as f:
            # RAW 파일을 numpy 배열로 읽기
            raw_data = np.frombuffer(f.read(), dtype=np.int16)
        # image reshape
        image_raw = raw_data.reshape((H, W))
        # Poly Mask Generation
        mask = np.zeros((H, W), dtype=np.uint8)
        mask_pts = np.array([[0,0], [0, 1950], [280, 2229],[1340, 2229], [1619, 1950],[1619,0]], dtype=np.int32)
        cv2.fillPoly(mask, [mask_pts], 1)
        # Mask apply to Raw Image
        masked_img = cv2.bitwise_and(image_raw,image_raw,mask = mask)
        return masked_img

def save_bmp_image(file_path, img, DynamicRange, DisplaySize):
    # Masked image Display Range Selection
    # print ( DynamicRange[0], DynamicRange[1] )
    clipped_image = np.clip(img, int(DynamicRange[0]), int(DynamicRange[1]))
    # Data Normalization to display
    scaled_image = cv2.normalize(clipped_image, None, 0, 255, cv2.NORM_MINMAX)
    # Image Resize to display
    resized_i = cv2.resize(scaled_image.astype(np.uint16), (DisplaySize[0], DisplaySize[1]))
    #cv2.imwrite(file_path +'_'+ str(DynamicRange[0])+'_'+ str(DynamicRange[1]) + '_py.bmp', resized_i)
    cv2.imwrite(file_path +'_'+ str(DynamicRange[0])+'_'+ str(DynamicRange[1]) + '_py.bmp', scaled_image[::4,::4])

def save_simple_bmp(file_path, img, DynamicRange):
    #plt.imsave(file_path +'_'+ str(DynamicRange[0])+'_'+ str(DynamicRange[1]) + '_py.bmp', img, cmap='gray', vmin=DynamicRange[0], vmax=DynamicRange[1])
    norm_image = ( ( np.clip(img,DynamicRange[0],DynamicRange[1]) ) / DynamicRange[1]) * 256
    cv2.imwrite(file_path +'_'+ str(DynamicRange[0])+'_'+ str(DynamicRange[1]) + '_py.bmp', norm_image)
    
def save_raw_image(file_path, raw_image):
    with open(file_path, 'wb') as f:
        f.write(raw_image.astype(np.uint16).tobytes())

def onclick(event, array):
    x = event.xdata
    y = event.ydata
    array.append((x, y))
    #print(f"Click Location : x={x}, y={y}")

def digit_points(array):
    point_data = np.round(array)
    i_point = point_data[0,:]
    e_point = point_data[1,:]
    width = point_data[1,0] - point_data[0, 0]
    height = point_data[1,1] - point_data[0, 1]
    return i_point, e_point, width, height
