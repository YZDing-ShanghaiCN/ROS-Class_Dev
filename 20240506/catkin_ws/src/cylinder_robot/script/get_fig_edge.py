import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def test():
    img=cv2.imread('./535833.jpg',0)
    sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=5)
    sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=5)
    sobelxy=cv2.Sobel(img, cv2.CV_64F, 1, 1, ksize=5)
    edges =	cv2.Canny(img ,80,150,(5,5))


    plt.subplot(1, 4, 1), plt.imshow(img, cmap = 'gray')
    plt.title('Original'), plt.xticks([]), plt.yticks([])
    plt.subplot(1, 4, 2), plt.imshow(sobelx, cmap = 'gray')
    plt.title('Sobel X'), plt.xticks([]), plt.yticks([])
    plt.subplot(1, 4, 3),plt.imshow(sobely, cmap = 'gray')
    plt.title('Sobel Y'), plt.xticks([]), plt.yticks([])
    plt.subplot(1, 4, 4),plt.imshow(edges, cmap = 'gray')
    plt.title('edge'), plt.xticks([]), plt.yticks([])
    plt.show()
    plt.cla()
    plt.imshow(edges, cmap = 'gray')
    plt.savefig('edge.png',dpi=400)
    plt.cla()

def img_to_egde(img_path='./flag1.png',n1=80,n2=150):
    img=cv2.imread(img_path,0)
    edges =	cv2.Canny(img ,n1,n2,(5,5))
    plt.imshow(edges, cmap = 'gray')
    plt.savefig(img_path+'_edge.png',dpi=400)
    edges=np.array(edges)
    print(edges.shape)
    return edges

def img_to_egde_line(img_path='./flag1.png',n1=80,n2=150):#提取线稿
    img=cv2.imread(img_path,0)
    edges =	cv2.Canny(img ,n1,n2,(5,5))
    plt.imshow(edges, cmap = 'gray')
    plt.savefig(img_path+'_edge.png',dpi=400)
    edges=np.array(edges)
    img=np.array(img)
    edges_line=np.zeros([img.shape[0],img.shape[1]])
    x_beside=np.array([0,0,1,1,1,-1,-1,-1],dtype=int)
    y_beside=np.array([1,-1,0,1,-1,0,1,-1],dtype=int)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i,j]<30:
                x_b=x_beside+i
                y_b=y_beside+j
                for k in range(8):
                    if x_b[k]<0 or x_b[k]>=edges.shape[0] or y_b[k]<0 or y_b[k]>=edges.shape[1]:
                        continue
                    else:
                        if edges[x_b[k],y_b[k]]>200:
                            edges_line[i,j]=225
                            break
    plt.cla()
    plt.imshow(edges_line, cmap = 'gray')
    plt.savefig(img_path+'_edge_line.png',dpi=400)
    plt.cla()
    print(edges.shape)
    return edges_line


def edge_to_data_point(edge):
    shape=edge.shape
    xy_list=[]
    for i in range(shape[0]):
        for j in range(shape[1]):
            if edge[i,j]>20:
                xy_list.append(i)
                xy_list.append(j)
    xy_list=np.array(xy_list).reshape(-1,2)
    return xy_list

def img_to_point_list(img_path='./flag1.png',n1=80,n2=150):
    edge=img_to_egde(img_path=img_path,n1=n1,n2=n2)
    xy_list=edge_to_data_point(edge)
    return xy_list,edge


def img_to_point_list_line(img_path='./flag1.png',n1=80,n2=150):
    edge=img_to_egde_line(img_path=img_path,n1=n1,n2=n2)
    xy_list=edge_to_data_point(edge)
    return xy_list,edge

def test3():
    img=cv2.imread('./flag1.png',0)
    print(img)

def test4():
    img_path='picachu.jpg'
    edges=img_to_egde_line(img_path=img_path,n1=80,n2=80)

    
if __name__=='__main__':
    test4()
    '''edge=img_to_egde()
    xy_list=edge_to_data_point(edge)
    print(xy_list)'''