import random,math,json,datetime
from functools import lru_cache

RANDOM=None
SEED=None

# 1d = 24h = 24*60 min =24*60*60 s
def trans_time(second:float):
    '''
    将时间按最大可用单位进行处理
    '''

    if second <= 30:
        return (second,'s')
    elif second <= 24*30:
        return  (second/60,'min')
    elif second <= 24*60*30:
        return  (second/3600,'h')
    else:
        return (second/(60*24*60),'d')

def trans_time2(second:float):
    m,s = divmod(second,60)
    h,m = divmod(m,60)
    d,h = divmod(h,24)
    return tuple(zip((d,h,m,s),('d','h','min','s')))
def trans_time3(second:float):
    t = trans_time2(second)
    if t[0][0] == 0:
        return t[1:]
    return t[:-1]


class Timer:
    def __init__(self,time):
        self.time = 0
        self.lasttick = 0
    def tick(self,tick):
        if self.lasttick + self.time < tick:
            return True
        return False



class vector2:
    def __init__(self,x=0,y=0):
        self.x=x
        self.y=y
    def _list(self):
        return (self.x,self.y)
    def _intlist(self):
        return (int(self.x),int(self.y))
    def __int__(self):
        return vector2(int(self.x),int(self.y))
    def copy(self):
        return vector2(self.x,self.y)
    def __add__(self,obj):
        return vector2(self.x+obj.x,self.y+obj.y)
    def __mul__(self,obj):
        # only mul int
        if isinstance(obj,int) or isinstance(obj,float):
            return vector2(self.x*obj,self.y*obj)
        elif isinstance(obj,vector2):
            return vector2(self.x*obj.x,self.y*obj.y)

    def __sub__(self,obj):
        return vector2(self.x-obj.x,self.y-obj.y)
    def __div__(self,obj):
        return vector2(self.x/obj,self.y/obj)
    def __str__(self):
        return '{x:%s,y:%s}' %(self.x,self.y)
    def __eq__(self,obj):
        return self.x==obj.x and self.y==obj.y
    def __truediv__(self,obj):
        return vector2(self.x/obj.x,self.y/obj.y)
    def __matmul__(self,obj):
        return self.x*obj.x + self.y*obj.y
    def __hash__(self):
        return hash(self.__str__())
    def __abs__(self):
        return vector2(abs(self.x),abs(self.y))
    def distance(self,vector):
        return math.sqrt(self.distance_square(vector))
    def distance_square(self,vector):
        return ((self.x-vector.x)**2 + (self.y-vector.y)**2)
    
    
    @staticmethod
    def from_tuple(tup):
        return vector2(*tup)



class vector3:
    def __init__(self,x=0,y=0,z=0):
        self.x = x
        self.y = y
        self.z = z
    def vectormap(self):
        pass
    def copy(self):
        return vector3(self.x,self.y,self.z)
    def __add__(self,obj):
        if isinstance(obj,vector3):
            return vector3(self.x+obj.x,self.y+obj.y,self.z+obj.z)
        elif isinstance(obj,vector2):
            return vector3(self.x+obj.x,self.y+obj.y,self.z)
    def __mul__(self,obj):
        # only mul int
        if isinstance(obj,int) or isinstance(obj,float):
            return vector3(self.x*obj,self.y*obj,self.z*obj)
        elif isinstance(obj,vector3):
            return vector3(self.x*obj.x,self.y*obj.y,self.z*obj.z)
    def __truediv__(self,obj):
        return vector2(self.x/obj,self.y/obj,self.z/obj)
    def __matmul__(self,obj):
        return self.x*obj.x + self.y*obj.y + self.z*obj.z
    def __sub__(self,obj):
        return vector3(self.x-obj.x,self.y-obj.y,self.z-obj.z)
    def __str__(self):
        return '{%f,%f,%f}' % self.x,self.y,self.z
    def __eq__(self,obj):
        return self.x==obj.x and self.y==obj.y and self.z==obj.z
    def __hash__(self):
        return hash(self.__str__())
    def distance(self,vector):
        return math.sqrt(self.distance_square(vector))
    def distance_square(self,vector):
        return ((self.x-vector.x)**2 + (self.y-vector.y)**2 + (self.z-vector.z)**2)
    @staticmethod
    def from_tuple(tup):
        return vector3(*tup)



def keyattr(attr):
    def warp(obj):
        return getattr(obj, attr)

    return warp

deepkey = keyattr('showdeep')


def get_dictdetla(a,b):
    '''a-b'''
    return {key:a[key]-b[key] for key in a.keys()}

def get_dictdiv(a,b):
    '''a-b'''
    return {a[key]/b[key] for key in a.keys()}

def argstrans(source,default):
    '''用在类里面需要用self中东西的函数的默认参数'''
    return source if source else default

def loadjson(file):
    f = open(file,encoding='utf-8')
    load = json.load(f)
    f.close()
    return load

def str2point(s):
    return vector2(*map(lambda x: float(x), s.split('x'), ))

def dividelst(lst,div,replacement=[]):
    return [lst[i:i+div] for i in range(0,len(lst),div)] if lst else replacement


def tuple2point(t:tuple):
    return vector2(t[0], t[1])

def point2tuple(t:vector2):
    return (int(t.x),int(t.y))
def set_posmap(screen):
    global POSMAP,POSREMAP
    POSMAP,POSREMAP=create_mapper(screen)
def get_posmap():
    global POSMAP,POSREMAP
    return POSMAP,POSREMAP

def printtext(text,font,pt,bs,color=(255,255,255),shadow=0):
    screen = bs
    if shadow:
        image=font.render(text,True,(0,0,0))
        screen.blit(image,(pt.x+shadow,pt.y+shadow))
    image=font.render(text,True,color)
    screen.blit(image,(pt.x,pt.y))
    

def set_global_randomseed(s):
    global RANDOM
    RANDOM=random.Random(s)
    SEED=s
def get_global_randomseed():
    global SEED
    return SEED

class Box:
    def __init__(self, pos, rect):
        self.pos = pos
        self.rect = rect

def smoothmove(now,target,speed=0.1):
    return (target-now)*speed
class Counter():
    def __init__(self,name):
        self.name=name
        self.num=0
    def count(self):
        self.num+=1
    def nextid(self):
        ids=self.name+str(self.num)
        self.count()
        return ids
    def get_count(self):
        return self.num



@lru_cache(64)
def get_distance(pt1,pt2):
    ptd=pt1-pt2
    return math.sqrt(ptd.x**2+ptd.y**2)

@lru_cache(16)
def get_distance_square(pt1,pt2):
    ptd=pt1-pt2
    return ptd.x**2+ptd.y**2
@lru_cache(16)
def get_vec(der):
    rad=math.radians(der-180)
    return vector2(math.cos(rad),math.sin(rad))
@lru_cache(16)
def get_targetrad(pt1,pt2):
    dx=pt1.x-pt2.x
    dy=pt1.y-pt2.y
    return math.degrees(math.atan2(dy,dx))

def pointin(pt,rectpt,rect):
    # handle singal point check
    if rect.x==0 and rect.y==0 and pt==rectpt:
        return True
    if pt.x<rectpt.x or pt.y<rectpt.y or pt.x>rectpt.x+rect.x or pt.y>rectpt.y+rect.y:
        return False
    return True

def pointin_bybox(pt,box:Box):
    return pointin(pt,box.pos,box.rect)

def create_mapper(screen):
    @lru_cache(32)
    def posmap(realpos,deep,k=0.001):
        temppos=realpos
        return vector2(temppos.x/(screen.x+screen.x*k*deep) * screen.x,temppos.y/(screen.y+screen.y*k*deep) * screen.y)
    def posremap(realpos,deep,k=0.001):
        return vector2(realpos.x/screen.x*(screen.x+screen.x*k*deep),realpos.y/screen.y*(screen.y+screen.y*k*deep))
    return posmap,posremap
# get_centre_u(p.pos,point(0,0)-WINDOW)-get_posmap()[0](self.pos,self.deep)
def get4pos_bybox(box):
    left=box.pos
    right=vector2(left.x+box.rect.x,left.y)
    downleft=vector2(left.x,left.y+box.rect.y)
    downright=left+box.rect
    return left,right,downleft,downright
# 要改
def get4pos(one):
    left=one.get_hitbox_pos()
    right=vector2(left.x+one.hitbox.rect.x,left.y)
    downleft=vector2(left.x,left.y+one.hitbox.rect.y)
    downright=left+one.hitbox.rect
    return left,right,downleft,downright
def uncom_segment_oneforone_part_bybox(left,right,downleft,downright,anotherbox : Box):
    epos=anotherbox.pos
    if pointin(left,epos,anotherbox.rect) or pointin(right,epos,anotherbox.rect) or \
                                           pointin(downleft,epos,anotherbox.rect) or \
                                           pointin(downright,epos,anotherbox.rect):
        return anotherbox
def uncom_segment_oneforone_part(left,right,downleft,downright,another):
    epos=another.get_hitbox_pos()
    if pointin(left,epos,another.hitbox.rect) or pointin(right,epos,another.hitbox.rect) or \
                                           pointin(downleft,epos,another.hitbox.rect) or \
                                           pointin(downright,epos,another.hitbox.rect):
        return another
#第1个是“小”（待检测）对象
def segment_oneforone_part(one,another):
    return uncom_segment_oneforone_part(*get4pos(one),another)
def segment_oneforone(one,another):
    return uncom_segment_oneforone_part(*get4pos(one),another) or uncom_segment_oneforone_part(*get4pos(another),one)
def segment_oneforall(one,alls:list)-> list:
    left,right,downleft,downright=get4pos(one)
    ret=[]
    for e in alls:
        if uncom_segment_oneforone_part(left,right,downleft,downright,e) or uncom_segment_oneforone_part(*get4pos(e),one):
            ret.append(e)
    return ret

def get_entity_bypos_circle(pos,search_list,d=0):
    ret=[]
    dsq=d**2
    for e in search_list:
        if get_distance_square(get_centre(e),pos)<=dsq:
            ret.append(e)
    return ret
def get_entity_bypos(entitys,pos,search_width=0):
    ret=[]
    for e in entitys:
        if pointin(e.pos,pos,vector2(search_width,search_width)):
            ret.append(e)
    return ret
def get_entity_byname(entitys,name):
    ret=[]
    for e in entitys:
        if e.name==name:ret.append(e)
    return ret
def get_entity_bydefname(entitys,defname):
    ret=[]
    for e in entitys:
        if e.defname==defname:ret.append(e)
    return ret
def get_centre(one):
    return get_centre_u(one.get_hitbox_pos(),one.hitbox.rect)
def get_centre_u(pos,rect):
    return vector2((pos.x+rect.x/2),(pos.y+rect.y/2))
def poop(x):
    return 5**x*math.sin(2*10*x*math.pi+math.pi/2)
def random_point(fropt,rectpt):
    global RANDOM
    x1=fropt.x
    x2=rectpt.x+x1
    y1=fropt.y
    y2=rectpt.y+y1
    return vector2(RANDOM.randint(x1,x2),RANDOM.randint(y1,y2))
def random_point_float(fropt,rectpt):
    global RANDOM
    x1=fropt.x
    x2=rectpt.x+x1
    y1=fropt.y
    y2=rectpt.y+y1
    return vector2(RANDOM.random()*(x2-x1)+x1,RANDOM.random()*(y2-y1)+y1)
@lru_cache(12)
def get_circle_dist(radius1,radius2,dist):
    return (radius1+radius2-dist)
# <0:no segment >=0:segment

def segment_circle(radius1,radius2,dist):
    ret=get_circle_dist(radius1,radius2,dist)
    return 0 if ret<0 else ret
def random_circle_point(midpt,radius):
    newpt=random_point(midpt-vector2(radius,radius),vector2(radius*2,radius*2))
    while get_distance(newpt,midpt)>radius:
        newpt=random_point(midpt-vector2(radius,radius),vector2(radius*2,radius*2))
    return newpt

def fast_to_slow(x):
    return -x**2+2*x

def slow_to_fast(x,_pow=3):
    return x**_pow

def guess(leq):
    global RANDOM
    rnum=RANDOM.random()
    if rnum<=leq:return True
    return False
def max_up(num,mnum):
    if num<=mnum:
        return num if num>=0 else 0
    return mnum
def cross(p1,p2,p3):
    x1=p2.x-p1.x
    y1=p2.y-p1.y
    x2=p3.x-p1.x
    y2=p3.y-p1.y
    return x1*y2-x2*y1
def segment(p1,p2,p3,p4):
    # Rect check 
    if(max(p1.x,p2.x)>=min(p3.x,p4.x) and max(p3.x,p4.x)>=min(p1.x,p2.x) and max(p1.y,p2.y)>=min(p3.y,p4.y) and max(p3.y,p4.y)>=min(p1.y,p2.y)):
        if (cross(p1,p2,p3)*cross(p1,p2,p4)<=0 and cross(p3,p4,p1)*cross(p3,p4,p2)<=0):
            return 1
    return 0
def segment_circle_and_line(p1,p2,pO,r):
    '''
    计算圆和直线的交点坐标 取离p1最近的交点
    '''
    if r<=0:return None
    # choose the farthest point as p1
    detla = p1-p2
    # get Ax+By+C=0
    if detla.x == 0:
        A = 1
        B = 0
        C = -p1.x
    elif detla.y == 0:
        A = 0
        B = 1
        C = -p1.y
    else:
        A = p1.y-p2.y
        B = p2.x-p1.x
        C = p1.x*p2.y - p1.y*p2.x
    # 圆心与线距离
    dist1 = (abs(A * pO.x + B * pO.y+C)**2) / (A**2 + B**2)
    t_check = r**2 - dist1
    if t_check < 0:
        return None
    E = math.sqrt(t_check)
    dist2 = get_distance_square(pO,p1)
    dist3 = math.sqrt(dist2 - dist1)
    S = dist3 - E
    if S <= 0:
        return None
    F = get_vec(get_targetrad(p1,p2)) * S + p1
    t_d1 = dist2
    t_d2 = get_distance_square(p2,pO)
    if t_d2 > t_d1:
        p1,p2 = p2,p1
    if get_distance_square(F,p1) > get_distance_square(p1,p2):
        return None
    
    return F
    
# A* path finder
class node:
    def __init__(self,pos,father):
        self.pos=pos
        self.father=father
def find_node_bypos(nodes,pos):
    for n in nodes:
        if n.pos==pos:
            return n
def avenage(nums):
    return sum(nums)/len(nums)

def astar_findpath(start_pos,end_pos,func_getnear,func_H):
    path=[]
    close_pos=[]
    close_F=[]
    open_pos=[start_pos]
    open_F=[0]
    open_G=[0]
    
    flag_success=False
    while len(open_F)>=1:
        min_cost=min(open_F)
        min_pop=open_F.index(min_cost)
        min_pos=open_pos[min_pop]
        min_G=open_G[min_pop]
        # remove now node
        open_F.pop(min_pop)
        open_pos.pop(min_pop)
        open_G.pop(min_pop)
        close_F.append(min_cost)
        close_pos.append(min_pos)
        children=func_getnear(min_pos)
        # start search
        for childpos in children:
            if childpos in close_pos:
                continue
            H=func_H(childpos)
            G=min_G+1
            F=H+G
            
            if childpos in open_pos:
                target_pos=open_pos.index(childpos)
                if open_F[target_pos]<F:
                    # update a better node
                    open_F[target_pos]=F
                    open_G[target_pos]=G
                    update_node=find_node_bypos(path,childpos)
                    path[path.index(update_node)]=node(childpos,find_node_bypos(path,min_pos))
            else:
                open_pos.append(childpos)
                open_F.append(F)
                open_G.append(G)
                path.append(node(childpos,find_node_bypos(path,min_pos)))
        if end_pos in children:
            flag_success=True
            break
    if not flag_success:
        return []
    build_path=[end_pos]
    now_node=path[-1]
    while not now_node.father is None:
        now_node=now_node.father
        build_path.append(now_node.pos)
    build_path.reverse()
    return build_path
