import cv2
import numpy as np
from get_fig_edge import img_to_point_list,img_to_point_list_line
from get_fig_edge import edge_to_data_point
import matplotlib.pyplot as plt

class my_graph_node():#节点类
    def __init__(self,x,y,graph_id,id,beside:np.matrix=np.array([]),beside_id:np.matrix=np.array([])):
        self.x=x
        self.y=y
        self.beside=beside
        self.beside_id=beside_id
        self.graph_id=graph_id
        self.id=id
    def __str__(self) -> str:
        class_type='<class: my_graph_node>'
        xy_point='xy point = ['+str(self.x)+','+str(self.y)+']'
        id='id = '+str(self.id)
        graph_id='graph id = '+str(self.graph_id)
        return class_type+'\n'+xy_point+'\n'+id+'\n'+graph_id
    def add_beside(self,x,y,id):
        beside=np.array([x,y])
        self.beside=np.append(self.beside,beside).reshape(-1,2)
        self.beside_id=np.append(self.beside_id,id)
    def add_beside_(self,beside):
        self.beside=np.append(self.beside,np.array([beside.x,beside.y])).reshape(-1,2)
        self.beside_id=np.append(self.beside_id,beside.id)
    def is_me(self,x,y):
        if x==self.x and y==self.y:
            return True
        else:
            return False
    def is_beside(self,x,y):
        if np.abs(x-self.x)<=1 and np.abs(y-self.y)<=1:
            return True
        else:
            return False
class my_graph():
    def __init__(self,id):
        self.node_list=[]
        self.id=id
        
    def add_node(self,node:my_graph_node):
        self.node_list.append(node)
        
    def add_node_2(self,x,y,beside):
        self.node_list.append(my_graph_node(x,y,beside,self.id))


def matrix_dis(xy_list):#计算距离矩阵
    num=xy_list.shape[0]
    res = np.zeros((num,num))
    for i in range(num):
        for j in range(i+1,num):
            res[i,j] = np.linalg.norm(xy_list[i,:]-xy_list[j,:])
            res[j,i] = res[i,j]
    return res

def test():
    xy_list=img_to_point_list()
    dis_mat=matrix_dis(xy_list=xy_list)
    print(dis_mat.shape)
    
    node_list=[]
    for i in range(xy_list.shape[0]):
        node_list.append(my_graph_node(xy_list[i][0],xy_list[i][1],graph_id=i,id=i))
    node_num=len(node_list)
    for i in range(node_num):
        for j in range(i+1,node_num):
            if node_list[i].is_beside(node_list[j].x,node_list[j].y):
                node_list[i].add_beside_(node_list[j])
                node_list[j].add_beside_(node_list[i])
                node_list[j].graph_id=node_list[i].graph_id
    new_id_list=[0]
    old_id_list=[0]
    for i in range(node_num):
        flag_new_id=True
        for j in range(len(old_id_list)):
            if node_list[i].graph_id==old_id_list[j]:
                node_list[i].graph_id=new_id_list[j]
                flag_new_id=False
                break
        if flag_new_id:
            new_id_list.append(new_id_list[len(new_id_list)-1]+1)
            old_id_list.append(node_list[i].graph_id)
            node_list[i].graph_id=new_id_list[len(new_id_list)-1]
            
    num_graph=len(new_id_list)
    nearlest_mat=np.zeros([num_graph,num_graph])
    nearlest_node_mat=np.zeros([num_graph,num_graph,2])
    for i in range(len(new_id_list)):
        for j in range(node_num):
            if node_list[j].graph_id==new_id_list[i]:
                for k in range(node_num):
                    if not node_list[k].graph_id==new_id_list[i]:
                        if nearlest_mat[new_id_list[i],node_list[k].graph_id]==0 or nearlest_mat[new_id_list[i],node_list[k].graph_id]>dis_mat[j,k]:
                            nearlest_mat[new_id_list[i],node_list[k].graph_id]=dis_mat[j,k]
                            nearlest_node_mat[new_id_list[i],node_list[k].graph_id,0]=j
                            nearlest_node_mat[new_id_list[i],node_list[k].graph_id,1]=k
                            
                            
        
    for i in range(num_graph-1):
        min_dis=0
        for j in range(num_graph):
            for k in range(num_graph):
                if not nearlest_mat[j,k]==0 and (min_dis==0 or min_dis>nearlest_mat[j,k]):
                    min_dis=nearlest_mat[j,k]
                    point=[j,k]
                    
    
    print(node_list[0])
    print(node_list[0].beside)
    for i in range(node_num):
        print(node_list[i].graph_id)
    print(nearlest_mat)


def mix_graph_neo(node_list,dis_mat,id_list):#高效联通子图
    node_num=len(node_list)
    num_graph=len(id_list)
    nearlest_mat=np.zeros([num_graph,num_graph])
    nearlest_node_mat=np.zeros([num_graph,num_graph,2])
    for i in range(len(id_list)):
        for j in range(node_num):
            if node_list[j].graph_id==id_list[i]:
                for k in range(node_num):
                    if not node_list[k].graph_id==id_list[i]:
                        if nearlest_mat[id_list[i],node_list[k].graph_id]==0 or nearlest_mat[id_list[i],node_list[k].graph_id]>dis_mat[j,k]:
                            nearlest_mat[id_list[i],node_list[k].graph_id]=dis_mat[j,k]
                            nearlest_node_mat[id_list[i],node_list[k].graph_id,0]=j
                            nearlest_node_mat[id_list[i],node_list[k].graph_id,1]=k
    
    observe_set=np.zeros(num_graph)
    
    for i in range(num_graph-1):
        min_dis=0
        for j in range(num_graph):
            for k in range(num_graph):
                if not nearlest_mat[j,k]==0 and (min_dis==0 or min_dis>nearlest_mat[j,k]):
                    min_dis=nearlest_mat[j,k]
                    point=[j,k]
        print(point)
        j=point[0];k=point[1]
        observe_set[j]=1;observe_set[k]=1
        id_0=int(nearlest_node_mat[point[0],point[1],0])
        id_1=int(nearlest_node_mat[point[0],point[1],1])
        nearlest_mat[j,k]=0
        nearlest_mat[k,j]=0
        for m in range(num_graph):
            if nearlest_mat[m,j]==0:
                for n in range(num_graph):
                    if nearlest_mat[n,k]==0:
                        nearlest_mat[m,n]=0
                        nearlest_mat[n,m]=0
            if nearlest_mat[m,k]==0:
                for n in range(num_graph):
                    if nearlest_mat[n,j]==0:
                        nearlest_mat[m,n]=0
                        nearlest_mat[n,m]=0
                
                
        print(id_0,id_1)
        node_list[id_0].add_beside_(node_list[id_1])
        node_list[id_1].add_beside_(node_list[id_0])
    
def mix_graph(node_list,dis_mat,id_list):#联通子图
    node_num=len(node_list)
    num_graph=len(id_list)
    nearlest_mat=np.zeros([num_graph,num_graph])
    nearlest_node_mat=np.zeros([num_graph,num_graph,2])
    for i in range(len(id_list)):
        for j in range(node_num):
            if node_list[j].graph_id==id_list[i]:
                for k in range(node_num):
                    if not node_list[k].graph_id==id_list[i]:
                        if nearlest_mat[id_list[i],node_list[k].graph_id]==0 or nearlest_mat[id_list[i],node_list[k].graph_id]>dis_mat[j,k]:
                            nearlest_mat[id_list[i],node_list[k].graph_id]=dis_mat[j,k]
                            nearlest_node_mat[id_list[i],node_list[k].graph_id,0]=j
                            nearlest_node_mat[id_list[i],node_list[k].graph_id,1]=k
                            
    min_dis=0                    
    for j in range(num_graph):
        for k in range(num_graph):
            if not nearlest_mat[j,k]==0 and (min_dis==0 or min_dis>nearlest_mat[j,k]):
                min_dis=nearlest_mat[j,k]
                point=[j,k]
    id_0=int(nearlest_node_mat[point[0],point[1],0])
    id_1=int(nearlest_node_mat[point[0],point[1],1])
    print(id_0,id_1)
    node_list[id_0].add_beside_(node_list[id_1])
    node_list[id_1].add_beside_(node_list[id_0])
    new_id=node_list[id_0].graph_id
    old_id=node_list[id_1].graph_id
    
    for i in range(node_num):
        if node_list[i].graph_id==old_id:
            node_list[i].graph_id=new_id
    
    '''new_id_list=[]
    for i in range(len(id_list)):
        if id_list[i]==old_id:
            continue
        else:
            new_id_list.append(id_list[i])'''
    
    new_id_list=[0]
    old_id_list=[node_list[0].graph_id]
    for i in range(node_num):
        flag_new_id=True
        for j in range(len(old_id_list)):
            if node_list[i].graph_id==old_id_list[j]:
                node_list[i].graph_id=new_id_list[j]
                flag_new_id=False
                break
        if flag_new_id:
            new_id_list.append(new_id_list[len(new_id_list)-1]+1)
            old_id_list.append(node_list[i].graph_id)
            node_list[i].graph_id=new_id_list[len(new_id_list)-1]
    return new_id_list

def test2():#主函数
    fig_path='picachu.jpg'
    xy_list,edge=img_to_point_list_line(fig_path,100,100)#生成线稿
    '''edge=np.array(cv2.imread(fig_path,0))
    print(edge.shape)
    xy_list=edge_to_data_point(edge)'''
    dis_mat=matrix_dis(xy_list=xy_list)
    print(dis_mat.shape)
    
    #加载节点
    node_list=[]
    for i in range(xy_list.shape[0]):
        node_list.append(my_graph_node(xy_list[i][0],xy_list[i][1],graph_id=i,id=i))
    node_num=len(node_list)
    #生成子联通图
    for i in range(node_num):
        for j in range(i+1,node_num):
            if node_list[i].is_beside(node_list[j].x,node_list[j].y):
                node_list[i].add_beside_(node_list[j])
                node_list[j].add_beside_(node_list[i])
                node_list[j].graph_id=node_list[i].graph_id
    print('creat nodes completed!')
    new_id_list=[0]
    old_id_list=[0]
    for i in range(node_num):
        flag_new_id=True
        for j in range(len(old_id_list)):
            if node_list[i].graph_id==old_id_list[j]:
                node_list[i].graph_id=new_id_list[j]
                flag_new_id=False
                break
        if flag_new_id:
            new_id_list.append(new_id_list[len(new_id_list)-1]+1)
            old_id_list.append(node_list[i].graph_id)
            node_list[i].graph_id=new_id_list[len(new_id_list)-1]
            
    '''while(len(new_id_list)>1):
        print(len(new_id_list))
        new_id_list=mix_graph(node_list=node_list,dis_mat=dis_mat,id_list=new_id_list)'''
    #合并连通图
    mix_graph_neo(node_list=node_list,dis_mat=dis_mat,id_list=new_id_list)
    
    '''for i in range(node_num):
        print(node_list[i].beside_id)'''
    
    #深度优先遍历，规划路径    
    rote=deep_observe(node_list)
    print(rote)
    
    #绘图，归一化位置，储存图片与数据点
    x=[]
    y=[]
    xy_list=np.zeros(len(rote)*2)
    for i in range(len(rote)):
        x.append(node_list[rote[i]].y)
        y.append(-node_list[rote[i]].x)
        xy_list[i*2]=node_list[rote[i]].y
        xy_list[i*2+1]=-node_list[rote[i]].x
    xy_list.reshape(-1,2)
    x=np.array(x)
    y=np.array(y)
    np.save(fig_path+'.npy',xy_list)
    plt.plot(x,y)
    plt.savefig(fig_path+'graph.png',dpi=400)
    plt.show()
    plt.cla()
    x,y=xy_to_place(x_list=x,y_list=y,x=10,y=10,img=edge.T)
    plt.plot(x,y)
    plt.savefig(fig_path+'graph_to_1.png',dpi=400)
    for i in range(len(rote)):
        xy_list[i*2]=x[i]
        xy_list[i*2+1]=y[i]
    xy_list.reshape(-1,2)
    np.save(fig_path+'_to_1.npy',xy_list)
    
    
def xy_to_place(x_list,y_list,x,y,img:np.matrix):#依据墙壁将点位置归一化
    x_list=(x_list+0.5)*x/img.shape[0]-x/2
    y_list=(y_list+0.5)*y/img.shape[1]+y/2
    return x_list,y_list

def deep_observe(node_list):#深度优先遍历
    node_num=len(node_list)
    observe_set=np.zeros(node_num+1)
    rote=[]
    father_node_stack=[]
    sub_node_stack=[]
    sub_rote_stack=[]
    start_point=0
    point_now=start_point
    while observe_set[node_num]<node_num:
        #print(point_now)
        print(observe_set[node_num],node_num)
        if observe_set[point_now]==0:
            observe_set[point_now]=1
            observe_set[node_num]+=1
            sub_rote_stack.append(point_now)
            rote.append(point_now)
            if get_beside(node_list[point_now],observe_set,sub_node_stack):
                sub_node=sub_node_stack.pop()
                point_last=point_now
                point_now=sub_node.pop()
                if len(sub_node)>0:
                    sub_node_stack.append(sub_node)
                    father_node_stack.append(point_last)
                elif len(father_node_stack)>0:
                    if point_last==father_node_stack[-1]:
                        father_node_stack.pop()
            else:
                if len(father_node_stack)==0:
                    break
                point_last=father_node_stack[-1]
                flag_circel=False
                for i in range(len(node_list[point_now].beside_id)):
                    if node_list[point_now].beside_id[i]==father_node_stack[-1]:
                        flag_circel=True
                        break
                if flag_circel:
                    point_temp=-1
                    while not point_temp==father_node_stack[-1]:
                        point_temp=sub_rote_stack.pop()
                    sub_rote_stack.append(point_temp)
                    rote.append(father_node_stack[-1])
                    sub_node=sub_node_stack.pop()
                    point_now=sub_node.pop()
                    if len(sub_node)>0:
                        sub_node_stack.append(sub_node)
                    else:
                        father_node_stack.pop()
                else:
                    point_temp=-1
                    while not point_temp==father_node_stack[-1]:
                        point_temp=sub_rote_stack.pop()
                        rote.append(point_temp)
                    sub_rote_stack.append(point_temp)
                    sub_node=sub_node_stack.pop()
                    point_now=sub_node.pop()
                    if len(sub_node)>0:
                        sub_node_stack.append(sub_node)
                    else:
                        father_node_stack.pop()
        else:
            if len(father_node_stack)==0:
                break
            if point_last==father_node_stack[-1]:
                sub_node=sub_node_stack.pop()
                point_now=sub_node.pop()
                if len(sub_node)>0:
                    sub_node_stack.append(sub_node)
                else:
                    father_node_stack.pop()
            else:
                point_temp=-1
                rote.pop()
                while not point_temp==father_node_stack[-1]:
                    point_temp=sub_rote_stack.pop()
                    rote.append(point_temp)
                sub_rote_stack.append(point_temp)
                sub_node=sub_node_stack.pop()
                point_last=point_now
                point_now=sub_node.pop()
                if len(sub_node)>0:
                    sub_node_stack.append(sub_node)
                else:
                    father_node_stack.pop()
    return rote

        

def get_beside(node:my_graph_node,observe_set,sub_node_stack):#得到未探索子节点
    sub_stack=[]
    for i in range(node.beside_id.shape[0]):
        if observe_set[int(node.beside_id[i])]==0:
            sub_stack.append(int(node.beside_id[i]))
    if len(sub_stack)>0:
        sub_node_stack.append(sub_stack)
        return True
    else:
        return False
    
def test3():
    p=[1,2,3]
    p.pop()
    print(p[-2])
if __name__=="__main__":
    test2()