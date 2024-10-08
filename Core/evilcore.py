'''
可是没人爱我

yaheifont = pg.font.Font('yahei.ttf', 15)
qingkongsmall = pg.font.Font('qingkongwan.ttf',19)
xiaoxiongsmall =  pg.font.Font('xiaoxiong.ttf',19)
qingkongverysmall = pg.font.Font('qingkongwan.ttf',15)
qingkongbig = pg.font.Font('qingkongwan.ttf',24)
xiaoxiongbig = pg.font.Font('xiaoxiong.ttf',24)
yaheibig = pg.font.Font('yahei.ttf', 20)
yaheibig2 = pg.font.Font('yahei.ttf', 21)
sounsobig = pg.font.Font('Sounso-Undividedad.ttf', 32)
xiaoxiongverybig = pg.font.Font('xiaoxiong.ttf',32)
liberationmono = pg.font.Font('Liberation Mono.ttf',14)

'''
import sys
sys.path.append(sys.path[0] + '/def/saveourvedal')
from worldcore import *
from tool import *
from local import *
import pygame as pg
import pygame.locals as PGKEY
import resmanager,copy,functools,code
from newcoretiny import Runable,RING3,RING2,RING1,RING0
from itertools import chain
import traceback as tb



sys._stdout = sys.stdout
sys._stderr = sys.stderr

yaheifont = pg.font.Font('yahei.ttf', 15)
yaheiverysmall = pg.font.Font('yahei.ttf', 10)
qingkongsmall = pg.font.Font('qingkongwan.ttf',19)
xiaoxiongsmall =  pg.font.Font('xiaoxiong.ttf',19)
qingkongverysmall = pg.font.Font('qingkongwan.ttf',15)
qingkongbig = pg.font.Font('qingkongwan.ttf',24)
xiaoxiongbig = pg.font.Font('xiaoxiong.ttf',24)
yaheibig = pg.font.Font('yahei.ttf', 20)
yaheibig2 = pg.font.Font('yahei.ttf', 21)
sounsobig = pg.font.Font('Sounso-Undividedad.ttf', 32)
xiaoxiongverybig = pg.font.Font('xiaoxiong.ttf',32)
liberationmono = pg.font.Font('Liberation Mono.ttf',14)
catsmall = pg.font.Font('cat.ttf',15)
catsbig = pg.font.Font('cat.ttf',40)

led1 = pg.font.Font('Digital-Play-St-3.ttf', 40)


for f,name in zip((yaheifont,qingkongsmall,xiaoxiongsmall,yaheibig2,yaheibig,qingkongbig,led1,sounsobig,liberationmono),
                  ('yaheifont','qingkongsmall','xiaoxiongsmall','yaheibig2','yaheibig','qingkongbig','led1','sounsobig','liberationmono')):
    resmanager.DefResourceDomain.add_resource('font.'+name,f)

class effect():
    def __init__(self,pos):
        self.image=None
        self.lasttick=0
        self.alive=True
        self.pos=pos
    def draw(self,scr):
        scr.blit(self.image,self.pos._intlist())
    def set_dead(self):
        self.alive=False

class effect_title(effect):
    def __init__(self,pos,text,fontcolor,lasttime=100,font=None):
        super().__init__(pos)
        self.image = font.render(text, True, fontcolor).convert_alpha()
        self.lasttime=lasttime
    def update(self,tick):
        if self.lasttime > 0:
            self.lasttime-=1
        else:
            return True



class effect_print(effect_title):
    def __init__(self,pos,text,fontcolor,fall_time=20,lasttime=100,font=None):
        super().__init__(pos=pos,text=text,fontcolor=fontcolor,lasttime=lasttime,font=font)
        self.fall_time=fall_time
    def update(self,tick):
        if self.fall_time > 0:
            self.fall_time -= 1
            self.pos.y += 2
        else:
            if self.lasttime > 0:
                self.lasttime -= 1
            else:
                self.set_dead()
                return True



class effect_roll(effect):
    def __init__(self,pos:vector2,text:str,fontcolor:tuple,font=None,fall_vel=0.05,fall_conv=float,bias=vector2(0,30)):
        super().__init__(pos=pos)
        self.stat = 0
        self.text = text
        self.bias = bias
        self.fall_vel = fall_vel
        self.fall_conv = fall_conv
        self.process = 1
        self.set_image(text,fontcolor,font)
    def set_dead(self):
        self.stat=2
    def set_image(self,text,fontcolor,font):
        self.image = font.render(text, True, fontcolor).convert_alpha()
        self.text=text
    def update(self,tick):
        if self.stat==0:
            if self.process<=0:
                self.stat=1
            self.process -= self.fall_vel
        elif self.stat==2:
            if self.process>=1:
                self.set_dead()
                return True
            self.process += self.fall_vel
            
    def draw(self,scr):
        scr.blit(self.image,(self.pos+self.bias*self.fall_conv(self.process))._intlist())


class effect_showline(effect):
    def __init__(self,pos,text,fontcolor,font=None,roll_vel=0.02,start_pos=0,lasttime=50,process=0):
        super().__init__(pos=pos)
        self.text=text
        self.fontcolor=fontcolor
        self.font=font
        self.roll_vel = roll_vel
        self.process = process
        self.lasttime=lasttime
        self.start_pos=start_pos
    def update(self,tick):
        if self.process<=1:
            self.image=self.font.render(self.text[:self.start_pos] + self.text[self.start_pos:int((len(self.text)-self.start_pos)*self.process)+ self.start_pos], True, self.fontcolor).convert_alpha()
            self.process+=self.roll_vel
        else:
            if self.process != 2:
                self.process=2
                self.image = self.font.render(self.text, True, self.fontcolor).convert_alpha()
                self.lasttick=tick
            if self.lasttick+self.lasttime <tick:
                self.set_dead()
                return True

class effect_showline_stand(effect_showline):
    def draw(self,scr):
        scr.blit(self.image,(self.pos-vector2(self.image.get_size()[0]/2,0))._intlist())
        
def fast_print(info,pos=None,fontcolor=(180,255,220,200),font=resmanager.DefResourceDomain.get_resource('font.qingkongbig')):
    if not pos:
        window = get_world().window
        pos = vector2(window.x*0.4,window.y*0.05)
    get_world().effects.append(effect_print(pos,info,fontcolor,font=font))

def print_dialog(talkname:str,content:list):
    window = get_world().window
    effect = effect_showline_stand(
                        pos=vector2(window.x*0.5,window.y*0.9-10),
                        text=('[%s]:' % talkname)+''.join(content),
                        fontcolor=(255,235,245,255),
                        roll_vel=0.03,
                        lasttime=len(''.join(content))*3+40,
                        font=resmanager.DefResourceDomain.get_resource('font.qingkongbig'),
                        start_pos=len(talkname)+3
                        )
    get_world().effects.append(effect)
    return effect



class RollControlRunable(Runable):
    def __init__(self,control,targetpos,startpos=None,rolling=slow_to_fast,vel=0.01):
        super().__init__()
        self.control=control
        self.targetpos=targetpos
        self.rolling=rolling
        
        if startpos:
            self.control.pos = startpos.copy()
            self.startpos=startpos
        else:
            self.startpos = self.control.pos.copy()
        self.detla=self.targetpos-self.startpos
        self.process = 0
        self.vel = vel
    def update(self,tick,master):
        self.control.pos = self.startpos+self.detla * self.rolling(self.process)
        self.process += self.vel
        if self.process>=1:
            return True



class EntityButton(Entity):
    def __init__(self, pos, boxpos, boxrect, text, font, bottomcolor, fontcolor, definedfunction, deep=0, defname=None,
                 showdeep=0):
        # boxpos一般取pos对吧
        super().__init__(pos, boxpos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.active = False
        self.definedfunction = definedfunction
        # 预先绘制图像以提高性能
        self.surface = pg.Surface(point2tuple(self.hitbox.rect)).convert_alpha()
        self.surface.fill(bottomcolor)
        printtext(text, font, vector2(self.hitbox.rect.x // len(text) - 4, self.hitbox.rect.y // 2 - 6), self.surface,
                  fontcolor)
        self.press = pg.Surface(point2tuple(self.hitbox.rect)).convert_alpha()
        self.press.fill(fontcolor)
        printtext(text, font, vector2(self.hitbox.rect.x // len(text) - 4, self.hitbox.rect.y // 2 - 6), self.press,
                  bottomcolor)

        self.image = self.surface

    def eventupdate(self, evt, bias):
        # 超我之前写的代码

        if evt.type in (PGKEY.MOUSEBUTTONDOWN, PGKEY.MOUSEMOTION) and pointin(tuple2point(evt.dict['pos']),
                                                                              self.get_hitbox_pos() + bias,
                                                                              self.hitbox.rect):
            if evt.type == PGKEY.MOUSEBUTTONDOWN and self.active:

                self.active = False
                self.image = self.surface
                if self.defname:
                    self.definedfunction(self.defname)
                else:
                    self.definedfunction()
            elif (evt.type == PGKEY.MOUSEMOTION):
                self.active = True
                self.image = self.press
        else:
            self.active = False
            self.image = self.surface




class EntityButtonImmerse(Entity):
    def __init__(self, pos, boxpos, boxrect, text, font, bottomcolor, fontcolor, definedfunction, press_speed=0.05,deep=0, defname=None,fill_bottom=True,showdeep=0):
        # boxpos一般取pos对吧
        super().__init__(pos, boxpos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.definedfunction = definedfunction

        self.surface = pg.Surface(point2tuple(self.hitbox.rect)).convert_alpha()
        if fill_bottom:self.surface.fill((0,0,0,0))
        pg.draw.rect(self.surface,bottomcolor,(0,0,*point2tuple(self.hitbox.rect)),5)
        printtext(text, font, vector2(self.hitbox.rect.x // len(text) - 4, self.hitbox.rect.y // 2 - 6), self.surface,
                  fontcolor)

        self.image = self.surface
        self.press = 0.0
        self.active = True
        self.press_speed = press_speed
        self.fontcolor=fontcolor
    def eventupdate(self, evt, bias):
        pass
    def draw(self,scr,bias):
        # 因为害怕性能问题，没准备根据tick运行的update，只好在draw里更新了QAQ 
        super().draw(scr,bias)
        # 超我之前写的代码
        if pg.mouse.get_pressed()[0] and pointin(tuple2point(pg.mouse.get_pos()),self.get_hitbox_pos() + bias,self.hitbox.rect):
            self.press+=self.press_speed
            if self.press>=1:
                if self.defname:
                    self.definedfunction(self.defname)
                else:
                    self.definedfunction()
                self.press=0
        else:
            self.press=0
        if self.press>0:
            pg.draw.rect(scr,self.fontcolor,
                     (*point2tuple(self.get_hitbox_pos() + bias),self.press*self.hitbox.rect.x,self.hitbox.rect.y),0)




class EntitySwitch(Entity):
    def __init__(self, pos, boxpos, boxrect, font, bottomcolor, fontcolor, stateenum, deep=0, defname=None,
                 showdeep=0):
        # boxpos一般取pos对吧
        super().__init__(pos, boxpos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.active = False
        self.stateenum = stateenum
        self.statenum = -1
        # 预先绘制图像以提高性能
        self.bottomcolor = bottomcolor
        self.font = font
        self.fontcolor = fontcolor
        self.next_state()
        self.image = self.surface
        

    def next_state(self):
        self.statenum = (self.statenum+1) % len(self.stateenum)
        # Reset Image
        text = self.stateenum[self.statenum]
        self.surface = pg.Surface(point2tuple(self.hitbox.rect)).convert_alpha()
        self.surface.fill(self.bottomcolor)
        printtext(text, self.font, vector2(self.hitbox.rect.x // len(text) - 4, self.hitbox.rect.y // 2 - 6), self.surface,
                  self.fontcolor)
        self.press = pg.Surface(point2tuple(self.hitbox.rect)).convert_alpha()
        self.press.fill(self.fontcolor)
        printtext(text, self.font, vector2(self.hitbox.rect.x // len(text) - 4, self.hitbox.rect.y // 2 - 6), self.press,
                  self.bottomcolor)
    def eventupdate(self, evt, bias):
        # 超我之前写的代码
        if evt.type in (PGKEY.MOUSEBUTTONDOWN, PGKEY.MOUSEMOTION) and pointin(tuple2point(evt.dict['pos']),
                                                                              self.get_hitbox_pos() + bias,
                                                                              self.hitbox.rect):
            if evt.type == PGKEY.MOUSEBUTTONDOWN and self.active:

                self.active = False
                self.image = self.surface
                self.next_state()
            elif (evt.type == PGKEY.MOUSEMOTION):
                self.active = True
                self.image = self.press
        else:
            self.active = False
            self.image = self.surface



class EntityLabel(Entity):
    def __init__(self, pos, boxpos, text, font, bottomcolor, fontcolor, deep=0, defname=None, showdeep=0):
        super().__init__(pos, boxpos, boxrect=vector2(0, 0), deep=deep, defname=defname, showdeep=showdeep)
        
        self.text=text
        self.font=font
        self.bottomcolor=bottomcolor
        self.fontcolor=fontcolor
        self.hitbox.rect = tuple2point(self.change_text(text, font, bottomcolor, fontcolor).get_size())
    def change_text(self, text=None, font=None, bottomcolor=None, fontcolor=None):
        '''
        改变EntityLabel的显示内容.

        不修改的值将采用之前设定的默认值.
        '''
        self.text = argstrans(text,self.text)
        self.font = argstrans(font,self.font)
        self.bottomcolor = argstrans(bottomcolor,self.bottomcolor)
        self.fontcolor = argstrans(fontcolor,self.fontcolor)

        image = self.font.render(self.text, True, self.fontcolor).convert_alpha()
        self.image = pg.Surface(image.get_size()).convert_alpha()
        self.image.fill(self.bottomcolor)
        self.image.blit(image, (0, 0))
        return self.image

    def eventupdate(self, evt, bias):
        pass



class EntityProcess(Entity):
    def __init__(self, pos, boxpos, boxrect, process_color=(110,120,250,120),deep=0, defname=None, showdeep=0):
        super().__init__(pos, boxpos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.process=0.0
        self.process_color= process_color
        self.image = pg.Surface(boxrect._intlist()).convert_alpha()
    def set_process(self,process=0):
        self.process=process
        self.image.fill((0,0,0,0))
        pg.draw.rect(self.image, self.process_color, (0,0, *(self.hitbox.rect*vector2(self.process,1))._intlist()), 0)
    def eventupdate(self,se,bias):
        pass



class EntityStatImage(Entity):
    def __init__(self, pos, boxpos, image, alpha=255, deep=0, defname=None, showdeep=0):
        super().__init__(pos, boxpos, boxrect=vector2(0, 0), deep=deep, defname=defname, showdeep=showdeep)
        self.change_image(image,alpha)
    def change_image(self,image,alpha=255):
        if alpha != 255:
            self.image = image.convert()
            self.image.set_alpha(alpha)
        else:
            self.image=image
        if self.image:
            self.hitbox.rect=tuple2point(self.image.get_size())
    def eventupdate(self,se,bias):
        pass



class EntityTextEditer(Entity):
    def __init__(self, pos, boxpos, boxrect, font, bottomcolor, fontcolor, deep=0, defname=None, showdeep=0):
        super().__init__(pos, boxpos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.active=False
        self.font=font
        self.image = pg.Surface(point2tuple(boxrect)).convert_alpha()
        self.image.fill(bottomcolor)
        pg.draw.rect(self.image,fontcolor,(0,0,*point2tuple(self.hitbox.rect)),3)
        self.fontcolor=fontcolor
        self.text=''
        self.change_text()
    def eventupdate(self,evt,bias):
        if evt.type ==PGKEY.MOUSEBUTTONDOWN and pointin(tuple2point(evt.dict['pos']),
                                                                              self.get_hitbox_pos() + bias,
                                                                              self.hitbox.rect):
            if self.active:
                self.active = False
                self.change_text()
            else:
                self.active = True
                self.change_text()
        elif self.active and evt.type in (PGKEY.KEYDOWN,PGKEY.KEYUP):
            if evt.type==PGKEY.KEYDOWN:
                if evt.dict['key']!=PGKEY.K_BACKSPACE:
                    self.text+=evt.dict['unicode']
                else:
                    self.text=self.text[:-1]
                self.change_text()
    def change_text(self):
        self.textimage=self.font.render((self.text if not self.active else self.text+'_'), True, self.fontcolor).convert_alpha()
    def draw(self,scr,bias):
        super().draw(scr,bias)
        scr.blit(self.textimage,point2tuple(self.get_hitbox_pos() + bias+vector2(3,3)))
        


class EntityFrame(Entity):
    def __init__(self, pos, boxrect, bottomcolor=(20, 40, 50, 50), deep=0, defname='', showdeep=0):
        super().__init__(pos, boxpos=vector2(0, 0), boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        # sid -> frame id
        # boxrect的功能令人迷惑，日后再说
        self.controllst = []
        self.bottomcolor = bottomcolor
        self.surface = pg.Surface(point2tuple(boxrect)).convert_alpha()
        self.surface.fill(bottomcolor)

    def draw(self, scr, bias):
        scr.blit(self.surface, point2tuple((self.get_hitbox_pos() + bias)))
        for c in self.controllst:
            c.draw(scr, bias+self.pos)

    def add_control(self, lastcontrol):
        lastcontrol.pos
        self.controllst.append(lastcontrol)
        return lastcontrol

    def eventupdate(self, evt, bias):
        mousepos = pg.mouse.get_pos()
        if pointin(tuple2point(mousepos), self.get_hitbox_pos()+bias, self.hitbox.rect):
        #if True:
            for c in self.controllst:
                c.eventupdate(evt, bias+self.pos)

    def get_control(self, defname):
        for c in self.controllst:
            if c.defname == defname: return c
    def remove_control(self, defname):
        for c in self.controllst:
            if c.defname == defname:
                self.controllst.remove(c)
                return c
    def update(self,tick):
        super().update(tick)
        #for c in self.controllst:
        #    c.update(tick)

class EntityFrameUpdated(EntityFrame):
    def update(self,tick):
        super().update(tick)
        for c in self.controllst:
            c.update(tick)

def middle_label_mirror(object_,pos,rect):
    # (partname,resname)
    return EntityLabel(pos,
                        vector2(0, 0),
                        object_[0], yaheifont,
                        (10, 10, 10, 50),(141, 193, 178, 250),
                        deep=0, defname=object_[1], showdeep=0)
def left_button_mirror(object_,pos,rect):
    # (partname,resname,func)
    return EntityButton(pos,
                        vector2(0, 0), vector2(rect.x-10,22),
                        object_[0], yaheifont,
                        (10, 10, 10, 50),(141, 193, 178, 250), definedfunction=object_[2],
                        deep=0, defname=object_[1], showdeep=0)

def launch_button_mirror(object_,pos,rect):
    # (partname,resname,func)
    return EntityButton(pos,
                        vector2(0, 0), vector2(rect.x-10,22),
                        object_[0], yaheifont,
                        (160,167,188,30),(250, 250, 250, 100), definedfunction=object_[2],
                        deep=0, defname=object_[1], showdeep=0)
TABLE_WIDTH=10




class EntityTable(EntityFrame):
    def __init__(self, pos, boxrect, mirror, bottomcolor=(20, 40, 50, 50), deep=0, defname='', showdeep=0):
        super().__init__(pos=pos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.bias = vector2(0,0)
        self.table = []
        self.def_mirror = mirror
        self.next_pos = vector2(1,2)
        pg.draw.rect(self.surface,bottomcolor,(0,0,*point2tuple(self.hitbox.rect)),4)
    def list_append(self,object_):
        self.table.append(object_)
        ret = self.def_mirror(object_, self.next_pos, self.hitbox.rect)
        self.next_pos.y += (ret.hitbox.rect.y + TABLE_WIDTH)
        self.add_control(ret)
    def list_pop(self,num):
        try:
            self.table.pop(num)
        except IndexError:
            fast_print('已经没有东西了！')
            return
        self.next_pos.y -= (self.controllst.pop(num).hitbox.rect.y + TABLE_WIDTH)
    def list_clear(self):
        self.table = []
        self.controllst = []
        self.next_pos=vector2(1,2)


DIALOG_WIDTH = 400
def PlayText(debateframe,talker,text,titlefont,textfont,toward):
    def warp(eventrunner):
        add_dialog(debateframe,talker,text,titlefont,textfont,toward)
    return warp
def add_dialog(debateframe,talker,text,titlefont,textfont,toward):
    debateframe.add_control(EntityDialog(debateframe.next_pos,vector2(DIALOG_WIDTH,100),talker,text,
                                                     resmanager.DefResourceDomain.get_resource(titlefont),resmanager.DefResourceDomain.get_resource(textfont),toward))
    debateframe.next_pos.y+=110


class EntityFrameDebate(EntityFrame):
    def __init__(self, pos, boxrect, bottomcolor=(20, 40, 50, 50), deep=0, defname='', showdeep=0):
        super().__init__(pos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.bias=vector2(0,0)
        self.bias_target=vector2(0,boxrect.y*0.8)
        self.next_pos=copy.copy(self.bias_target)
        self.dialog_capacity=boxrect.y//100-1
        self.lasttick=0
        self.left_stall=None
        self.right_stall=None
    def eventupdate(self,se,bias):
        super().eventupdate(se,bias+self.bias)
        if (se.type==PGKEY.MOUSEBUTTONDOWN or se.type==PGKEY.KEYDOWN) and pointin(tuple2point(pg.mouse.get_pos()) + bias, self.get_hitbox_pos(), self.hitbox.rect):
            #下一条
            get_world().eventrunner.trigger('nexttext')
            
    def draw(self,scr,bias):
        scr.blit(self.surface, point2tuple(self.get_hitbox_pos() + bias))
        for c in self.controllst:
            c.draw(scr, bias + self.bias)
        if self.left_stall:scr.blit(self.left_stall,(0,380))
        if self.right_stall:scr.blit(self.right_stall,(600,400))
    def update(self,tick):
        if len(self.controllst) > 0 :
            bias = self.controllst[-1].pos - self.bias_target - self.bias
            speed = 25
            self.bias.y = (self.bias.y+speed if bias.y>=speed else self.bias.y+bias.y)
            if len(self.controllst) >= self.dialog_capacity +1:
                self.controllst.pop(0)
    def add_control(self,ct):
        super().add_control(ct)
        if isinstance(ct,EntityDialog):
            if ct.toward==TOWARDRIGHT:
                self.left_stall=resmanager.DefResourceDomain.get_resource('texture.stall.'+ct.talker)
            elif ct.toward==TOWARDLEFT:
                self.right_stall=resmanager.DefResourceDomain.get_resource('texture.stall.'+ct.talker)
                
    def clear_all(self):
        self.controllst=[]
        self.bias=vector2(0,0)
        self.next_pos=vector2(0,0)



# text -> tuple
TOWARDLEFT=1
TOWARDRIGHT=0
class EntityDialog(Entity):
    def __init__(self, pos,boxrect,talker, text, titlefont=yaheibig,textfont=qingkongsmall,toward=TOWARDRIGHT,deep=0, defname='', showdeep=0):
        super().__init__(pos, boxpos=vector2(0, 0), boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.talker = talker
        self.text = text
        self.talkname = resmanager.NameResourceDomain.get_resource('name.talker.'+talker)
        bottomcolor = resmanager.DefResourceDomain.get_resource('color.talker.'+talker)
        talkerhead = resmanager.DefResourceDomain.get_resource('texture.talker.'+talker)
        self.surface=pg.Surface(point2tuple(boxrect)).convert_alpha()
        
        self.surface.fill(bottomcolor)
        # normal: 100*100
        # normal: 100*600
        if toward==TOWARDRIGHT:
            self.surface.blit(titlefont.render(self.talkname, True, (200,200,255,255)).convert_alpha(), (102, 2))
            start_pos=vector2(102,24)
            self.surface.blit(talkerhead, (0, 0))
        else:
            temp=titlefont.render(self.talkname, True, (200,200,255,255)).convert_alpha()
            self.surface.blit(temp, (DIALOG_WIDTH-talkerhead.get_size()[0]-temp.get_size()[0]-2, 2))
            start_pos=vector2(2,24)
            self.surface.blit(talkerhead, (DIALOG_WIDTH-talkerhead.get_size()[0], 0))
        self.toward=toward
        for line in text:
            self.surface.blit(textfont.render(line, True, (200,200,255,255)).convert_alpha(),point2tuple(start_pos))
            start_pos.y+=17
        self.image=self.surface
        
    def eventupdate(sel,se,bias):
        pass


class EntitySlideFrame(EntityFrame):
    def __init__(self, pos, boxrect, detectboxA:Box,posB:vector2,detectboxB=None,bottomcolor=(20, 40, 50, 50), deep=0, defname='', showdeep=0):
        super().__init__(pos, boxrect=boxrect, bottomcolor=bottomcolor,deep=deep, defname=defname, showdeep=showdeep)
        self.detectboxA = detectboxA
        self.detectboxB = argstrans(detectboxB,Box(posB,boxrect))
        self.posA = pos
        self.posB = posB
        self.active=False
        self.detectbox = detectboxA
    def eventupdate(self,se,bias):
        super().eventupdate(se,bias)
        if se.type == PGKEY.MOUSEMOTION:
            mpos = vector2.from_tuple(se.dict['pos'])
            isin = pointin_bybox(mpos,self.detectbox)
            if not self.active and isin:
                self.detectbox = self.detectboxB
                self.active = True
                get_world().eventrunner.Runables[RING3].append(RollControlRunable(self,self.posB,rolling=fast_to_slow,vel=0.02))
            elif self.active and not isin:
                self.detectbox = self.detectboxA
                self.active = False
                get_world().eventrunner.Runables[RING3].append(RollControlRunable(self,self.posA,rolling=fast_to_slow,vel=0.02))
        


class FrameManager():
    def __init__(self):
        self.mxlst = []
        self.controllst = []
        self.hide = []

    def draw(self, scr, bias):
        for c in sorted(self.controllst, key=deepkey):
            if c.defname not in self.hide: c.draw(scr, bias)

    def get_show_controls(self):
        result = []
        for c in self.controllst:
            if c.defname not in self.hide: result.append(c)
        return result

    def get_control(self, sid):
        for c in self.controllst:
            if c.defname == sid: return c

    def add_control(self, lastcontrol, mux=False):
        if mux:
            # mux -> don't open frame again
            if self.isin(lastcontrol.defname):
                return False
            self.mxlst.append(lastcontrol.defname)
        self.controllst.append(lastcontrol)
        return True

    def eventupdate(self, evt, bias):
        for c in self.controllst:
            if c.defname not in self.hide: c.eventupdate(evt, bias)
    def update(self,tick):
        for c in self.controllst:
            if c.defname not in self.hide: c.update(tick)
    def remove_control(self, defname):
        for c in self.controllst:
            if c.defname == defname:
                self.controllst.remove(c)
                if defname in self.mxlst:
                    self.mxlst.remove(c.defname)
                if defname in self.hide:
                    self.hide.remove(c.defname)
                return
    def switch_control(self,defname):
        if defname in self.hide:
            self.show_control(defname)
        else:
            self.hide_control(defname)
        return True
        
    def isin(self, defname):
        return defname in self.mxlst

    def hide_control(self, defname):
        self.hide.append(defname)

    def show_control(self, defname):
        self.hide.remove(defname)

    def hide_all(self):
        self.hide = ['']
        for control in self.controllst:
            if control.defname:
                self.hide.append(control.defname)



class EntityTouchPad(EntityFrame):
    def __init__(self, pos, boxrect, bottomcolor=(20, 40, 50, 50), deep=0, defname='', showdeep=0):
        super().__init__(pos=pos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.bias = vector2(0, 0)
        self.press = False

    def eventupdate(self, evt, bias):
        super().eventupdate(evt, bias + self.bias)
        if evt.type == PGKEY.MOUSEBUTTONDOWN and pointin(vector2(evt.pos[0], evt.pos[1]), self.get_hitbox_pos() + bias,
                                                         self.hitbox.rect):
            self.press = True
        elif evt.type == PGKEY.MOUSEMOTION and self.press:
            self.bias += tuple2point(evt.dict['rel'])
        elif evt.type == PGKEY.MOUSEBUTTONUP:
            self.press = False

    def draw(self, scr, bias):
        scr.blit(self.surface, point2tuple(self.get_hitbox_pos() + bias))
        for c in self.controllst:
            # c可能会到外面去，这是特性，因为做两矩形检测又麻烦又耗时
            c.draw(scr, bias + self.bias)


'''
0 1 TER_DONNOTDRAWPANCEL : Stop Window from craeting titlebar
0 2 TER_COURSE           : None
0 4 TER_SWITCH_DRAWORDER : SWITCH the order of drawing controls and textlines
0 8
0 16
'''
WIND_DONNOTDRAWPANCEL = 1
WIND_COURSE = 2
TER_SWITCH_DRAWORDER = 4

def check_flags(bits,flag):
    return bits & flag
class EntityWindow(EntityFrame):
    def __init__(self, pos, boxrect, title, font, bottomcolor=(12, 12, 23, 50), titlefontcolor=(220,220,230,220),titlecolor=(37,151,148,220), flags=0, deep=0, defname='', showdeep=0):
        super().__init__(pos=pos,boxrect=boxrect,bottomcolor=bottomcolor,deep=deep,defname=defname,showdeep=showdeep)
        self.title = title
        self.titlecolor = titlecolor
        self.titlefontcolor = titlefontcolor
        self.font = font
        self.flags = flags
        self.flush_window()
        
    def flush_window(self):
        if check_flags(self.flags,WIND_DONNOTDRAWPANCEL):
            return
        
        titletext = self._get_text((self.title,self.titlefontcolor))
        size = vector2.from_tuple(titletext.get_size()) + vector2(10,0)
        self.hitbox = Box(vector2(0,-size.y),size)
        # Title Bar
        self.titlecache = pg.Surface(size._intlist()).convert_alpha()
        self.titlecache.fill((0,0,0,0))
        pg.draw.polygon(self.titlecache,self.titlecolor,((0,0),(size.x-10,0),(size.x,size.y),(0,size.y)),0)
        self.titlecache.blit(titletext,(3,0))
        # Bottom
        self.surface.fill(self.bottomcolor)
        bottomsize = self.surface.get_size()
        pg.draw.rect(self.surface,self.titlecolor,pg.Rect(0,0,*bottomsize),2)
    def draw(self,scr,bias):
        super().draw(scr,bias)
        temppos = self.pos + bias
        scr.blit(self.titlecache,point2tuple(temppos+self.hitbox.pos))


class EntityTerminal(EntityWindow):
    '''
    ## EntityTerminal

    由于EntityWindow使用hitbox存储titlebar数据以应对未来可能的开发,EntityTerminal的boxpos和boxrect都有不同的含义

    **boxpos** -> 终端位置偏移量

    **boxrect** -> 终端surface大小
    '''
    def __init__(self, pos, boxpos, boxrect, title, font, bottomcolor=(12, 12, 23, 50), titlefontcolor=(220,220,230,220),titlecolor=(37,151,148,220), shape=vector2(10,20), flags=0, deep=0, defname='', showdeep=0):
        super().__init__(pos=pos,boxrect=boxrect,title=title,font=font,bottomcolor=bottomcolor,titlefontcolor=titlefontcolor,titlecolor=titlecolor,deep=deep,defname=defname,showdeep=showdeep)
        # _boxpos 为偏移量
        self._boxpos = boxpos
        # _boxrect 为surface大小
        self._boxrect = boxrect
        
        self.shape = shape
        self.flags=flags
        self.screen = []
        # screen内部为 (Text, Color)
        self.hash = []
        self.screencache=[]
        
        self.flush_transdefault()
        self.flush_window()
        self.flush()
    def flush_transdefault(self):
        # transdefault 用来存储write等函数的默认操作列表
        self.transdefault = self.screen
    def flush(self):
        self.screen = self.screen[max(len(self.screen)-self.shape.y,0):]
        self.hash = self.hash[max(len(self.hash)-self.shape.y,0):]
        
        for i in range(len(self.screen)):
            if i>=len(self.hash):
                #print('E:hash not sync',self.screen[i])
                self.hash.append(hash(self.screen[i]))
            # update cache
            if i>=len(self.screencache):
                self.screencache.append(self._get_text(self.screen[i]))
            if hash(self.screen[i])!=self.hash[i]:
                self.screencache[i]=(self._get_text(self.screen[i]))
                self.hash[i]=hash(self.screen[i])
                #print('hash')
        
        if len(self.hash)>len(self.screen):
            #print('E:hash not sync 2',file=sys._stderr)
            #self.hash=self.hash[max(len(self.hash)-len(self.screen),0):]
            pass
        if len(self.screencache)>len(self.screen):
            pass
            #print('E:sc not sync')
            #self.screencache=self.screencache[max(len(self.screencache)-len(self.screen),0):]
        #self.screencache=[]
        #for screen in self.screen:
        #    self.screencache.append(self._get_text(screen))
        self.flush_transdefault()
    def write_lines(self,lines,source=None,_hash=True):
        source=argstrans(source,self.transdefault)
        newlines=[]
        while len(lines)>0:
            element=lines.pop(0)
            temp=tuple(dividelst(element[0],self.shape.x,replacement=('',)))
            newlines.extend([(x,element[1]) for x in temp])
        source.extend(newlines)
        self.flush()
    def write(self,*args,color=(255,255,255,255),source=None,_hash=True):
        source=argstrans(source,self.transdefault)
        temp = (' '.join(args)).split('\n')
        color = tuple(color)
        if len(source)==0:
            temp=list(chain.from_iterable(map(lambda x:dividelst(x,self.shape.x,replacement=('',)),temp)))
            self.write_lines(list(zip(temp,[color for i in temp])),source=source,_hash=_hash)
        else:
            source[-1] = (source[-1][0]+temp[0],source[-1][1])
            if source[-1][0]:
                newlines=list(map(lambda x:(x,color),dividelst(source[-1][0],self.shape.x,replacement=('',))))
                source.pop(-1)
                source.extend(newlines)
            nextlines=temp[1:]
            self.write_lines(list(zip(chain.from_iterable(map(lambda x:tuple(dividelst(x,self.shape.x,replacement=('',))),nextlines)),[color for i in nextlines]))
                             ,source=source,_hash=_hash)
    def pop(self,linenum):
        self.screen.pop(linenum)
        self.hash.pop(linenum)
        self.screencache.pop(linenum)
    def clear_all(self):
        self.screen = []
        self.hash = []
        self.screencache=[]
        #这个很重要,要不然之后的第一个write会写到那个已经没有引用的list上
        self.flush_transdefault()
    
    @functools.lru_cache(16)
    def _get_text(self,textcolor):
        return self.font.render(textcolor[0], True, textcolor[1]).convert_alpha()
    
    def draw(self,scr,bias):
        temppos = self.pos + bias
        scr.blit(self.surface, temppos._intlist())
        scr.blit(self.titlecache, (temppos + self.hitbox.pos)._intlist())
        start_pos=(temppos + bias+self._boxpos)
        if check_flags(self.flags,TER_SWITCH_DRAWORDER):
            for c in self.controllst:
                c.draw(scr, bias+self.pos)
            for cache in self.screencache:
                scr.blit(cache,start_pos._intlist())
                start_pos.y+=cache.get_size()[1]+1
        else:
            for cache in self.screencache:
                scr.blit(cache,start_pos._intlist())
                start_pos.y+=cache.get_size()[1]+1
            for c in self.controllst:
                c.draw(scr, bias+self.pos)
            
        
        




PROMPT_COLOR=(220,220,225,230)
class EntityTerminalPrompt(EntityTerminal):
    def __init__(self, pos, boxpos, boxrect, title, font, bottomcolor=(12, 12, 23, 200), titlefontcolor=(220,220,230,220),titlecolor=(37,151,148,220), shape=vector2(10,20), flags=0, deep=0, defname='', showdeep=0):
        self.history=[]
        super().__init__(pos=pos,boxpos=boxpos,boxrect=boxrect,title=title,font=font,bottomcolor=bottomcolor,titlefontcolor=titlefontcolor,shape=shape,flags=flags,deep=deep,defname=defname,showdeep=showdeep)
        self.prompt=''
        self.active=False
        self.flush_transdefault()
    def flush_transdefault(self):
        self.transdefault = self.history
    def screen_flush(self):
        self.screen = self.history[max(len(self.history)-self.shape.y,0):]
        self.write(self.prompt,color=PROMPT_COLOR,source=self.screen)
        if self.active:
            self.write('_',color=PROMPT_COLOR,source=self.screen)
        self.flush()
    def handle_prompt(self,prompt):
        pass
    def eventupdate(self,evt,bias):
        if evt.type ==PGKEY.MOUSEBUTTONDOWN and pointin(tuple2point(evt.dict['pos']),
                                                                    self.pos + bias,
                                                                    self._boxrect):
            if self.active:
                self.active = False
            else:
                self.active = True
            self.screen_flush()
        
        elif self.active and evt.type in (PGKEY.KEYDOWN,PGKEY.KEYUP):
            if evt.type==PGKEY.KEYDOWN:
                if evt.dict['key'] == PGKEY.K_RETURN:
                    self.write(self.prompt+'\n',source=self.history,color=PROMPT_COLOR)
                    self.handle_prompt(self.prompt)
                    self.prompt=''
                elif evt.dict['key']!=PGKEY.K_BACKSPACE:
                    self.prompt+=evt.dict['unicode']
                else:
                    self.prompt = self.prompt[:-1]
            self.screen_flush()

# 能用
ERROR_COLOR=(222,40,72,220)
class Err_mirror:
    def __init__(self,we):
        self.write = we
class EntityTerminalDebug(EntityTerminalPrompt):
    def __init__(self, pos, boxpos, boxrect, title, font, bottomcolor=(20, 40, 50, 200), titlefontcolor=(220,220,230,220),titlecolor=(37,151,148,220), shape=vector2(10,20), flags=0, deep=0, defname='', showdeep=0):
        super().__init__(pos, boxpos, boxrect, title, font, bottomcolor, titlefontcolor,titlecolor, shape, flags, deep, defname, showdeep)
        self.err_mirror=Err_mirror(self.err_write)
        
        sys._stdout=sys.stdout
        sys.stdout=self
        sys._stderr=sys.stderr
        sys.stderr=self.err_mirror
        
        self.console=code.InteractiveConsole(locals=globals())
        self.console.write=self.err_write
        
        self.ps1='>> '
        self.ps2='.. '
        self.more = 0
        self.banner()
        
        self.prompt_back()
        self.screen_flush()
    def banner(self):
        cprt='Type "help", "copyright", "credits" or "license" for more information.\n\nI love you Neurosama heart heart heart'
        helps= '...Type get_world() to get main.World object...'
        self.write("Python %s on %s\n%s\n\n%s\n\n(console is %s)\n" %
                       (sys.version, sys.platform, cprt,helps,
                        self.__class__.__name__))
    def err_write(self,data):
        self.write(data,color=ERROR_COLOR,source=self.history)
    def prompt_back(self):
        self.write(self.ps2 if self.more else self.ps1,color=PROMPT_COLOR,source=self.history)
    def handle_prompt(self,prompt):
        try:
            self.more = self.console.push(prompt)
        except Exception as e:
            self.write('\n',source=self.history)
            self.console.showtraceback()
        self.prompt_back()
        self.flush()

class EntityScreen(Entity):
    def __init__(self, pos,boxpos,boxrect,deep=0, defname=None, showdeep=0,info=''):
        super().__init__(pos, boxpos=boxpos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep,info=info)
        self.image = pg.Surface(point2tuple(boxrect)).convert_alpha()
    def eventupdate(self,se,bias):
        pass

try:
    import hiyoricore as hiyori
    class EntityCanvas(EntityScreen):
        def __init__(self, pos,boxpos,boxrect,scalx:int,rgbbase=None,rgbbottom=None,alpha=255,deep=0, defname=None, showdeep=0,info=''):
            super().__init__(pos=pos, boxpos=boxpos, boxrect=boxrect*scalx, deep=deep, defname=defname, showdeep=showdeep,info=info)
            self.image = self.image.convert()
            self.image.set_alpha(alpha)
            self.image_array = numpy.zeros(boxrect._intlist(),dtype='float16')
            self.drawer =  numpy.array([[0.8,0.8,0.8],[0.8,1,0.8],[0.8,1,0.8]]) / 4
            RGBbase = rgbbase if rgbbase is not None else numpy.full((boxrect.x*scalx,boxrect.y*scalx,3),255).astype('float16')
            self.RGBbottom = (rgbbottom if rgbbottom is not None else numpy.full((boxrect.x*scalx,boxrect.y*scalx,3),0).astype('float16'))
            self.RGBdetla = RGBbase - self.RGBbottom
            self.drawer_rect = vector2(*self.drawer.shape)
            self.scalx = scalx
            self.image.set_colorkey(((0,0,0)))
            self.rel=vector2(0,0)
        def draw(self,scr,bias):
            super().draw(scr,bias)
            mouse,button = tuple2point(pg.mouse.get_pos())+bias,pg.mouse.get_pressed()
            force = get_d_square(mouse-self.rel,vector2(0,0)) / 10
            self.rel = mouse
            if pointin(mouse,self.pos,self.hitbox.rect):
                if any(button):
                    rel_pos = ((mouse-self.pos) * (1/self.scalx)).__int__()
                    view = hiyori.subarray(self.image_array,rel_pos,self.drawer_rect)
                    if button[0]:
                        view[:]= numpy.minimum(view+self.drawer[:view.shape[0],:view.shape[1]]*force,1)
                    elif button[2]:
                        view[:,:] = 0
                    self.update_image()
        def update_image(self):
            w = pg.surfarray.pixels3d(self.image)
            w[:]= ((hiyori.scalx_array(self.image_array,self.scalx).T*self.RGBdetla.T).T+self.RGBbottom).astype('int8')
            
except ImportError:
    pass




def create_textlines(frame,textlines,font,start_pos,bias_y,bottomcolor,fontcolor,mode='left'):
    '''
    Use to add Labels to frame.
    mode='left' / 'right' / 'centre' 
    '''
    for line in textlines:
        tempLabel=EntityLabel(start_pos,vector2(0,0),line,font,bottomcolor,fontcolor)
        if mode=='centre':
            tempLabel.pos.x -= tempLabel.hitbox.rect.x//2
        elif mode=='right':
            tempLabel.pos.x -= tempLabel.hitbox.rect.x
        frame.add_control(tempLabel)
        start_pos.y+=bias_y+tempLabel.hitbox.rect.y



LASTTIME = 0 # 秒
BACKIMAGES=['texture.paccha_entiy1','texture.paccha_entiy2','texture.paccha_entiy3']
BACKIMAGE=resmanager.DefResourceDomain.get_resource(random.choice(BACKIMAGES))
SENTENCE=random.choice(resmanager.NameResourceDomain.get_resource('sentences.normal1'))

def resentence(open_sentence='sentences.normal1'):
    global SENTENCE
    SENTENCE = random.choice(resmanager.NameResourceDomain.get_resource(open_sentence))

def _load_process_old(text,textcolor=(200,210,200,220),bgimageres=None,bottomcolor=(15,16,40,200),open_sentence='sentences.normal1',tick=0):
    global LASTTIME,SENTENCE,BACKIMAGES,BACKIMAGE
    if LASTTIME + 20 < tick:
        BACKIMAGE=resmanager.DefResourceDomain.get_resource(random.choice(BACKIMAGES))
        LASTTIME = tick
        resentence(open_sentence)

    bgimage = resmanager.DefResourceDomain.get_resource(bgimageres) if bgimageres else BACKIMAGE
    if bgimage:get_world().surface.blit(bgimage,(0,0))
    
    text = yaheifont.render(text[:50], True, textcolor).convert_alpha()
    textsize = text.get_size()
    image = pg.Surface((textsize[0]+80,45)).convert_alpha()
    image.fill(bottomcolor)
    size=tuple2point(image.get_size())
    top=get_centre_u(vector2(-size.x//2,-size.y//2),get_world().window)
    fonttop=get_centre_u(vector2(-textsize[0]/2,-textsize[1]//2),size)
    image.blit(text,fonttop._intlist())
    if open_sentence:
        #temp=resmanager.NameResourceDomain.get_resource(open_sentence)
        sentence=yaheifont.render(SENTENCE,True, (200,210,200,220)).convert_alpha()
        sentencesize=tuple2point(sentence.get_size())
        sentencebottom=pg.Surface(sentence.get_size()).convert_alpha()
        sentencebottom.fill(bottomcolor)
        sentencetop=get_centre_u(vector2(-sentencesize.x//2,-sentencesize.y//2),get_world().window)+vector2(0,45+15)
        sentencebottom.blit(sentence,(0,0))
        get_world().surface.blit(sentencebottom,sentencetop._intlist())
    get_world().surface.blit(image,point2tuple(top))
    pg.display.update()



def _load_process_(text,textcolor=(200,210,200,220),bgimageres=None,open_sentence='sentences.normal1',tick=0):
    global LASTTIME,SENTENCE,BACKIMAGES,BACKIMAGE
    if LASTTIME + 1 > tick:
        BACKIMAGE=resmanager.DefResourceDomain.get_resource(random.choice(BACKIMAGES))
        LASTTIME = tick
        resentence(open_sentence)
    
    window = get_world().window

    bgimage = resmanager.DefResourceDomain.get_resource(bgimageres) if bgimageres else BACKIMAGE
    if bgimage:
        bgimage_centre = get_centre_u(vector2(0,0),vector2.from_tuple(bgimage.get_size()))
        get_world().surface.blit(bgimage,(window*0.5-bgimage_centre)._intlist())
    
    text = catsbig.render(text[:50], True, textcolor).convert_alpha()
    get_world().surface.blit(text,vector2(8,window.y-text.get_size()[1]-30)._intlist())
    if open_sentence:
        sentence=xiaoxiongsmall.render(SENTENCE,True, (200,210,200,220)).convert_alpha()
        get_world().surface.blit(sentence,vector2(1,window.y-25)._intlist())

    pg.display.update()

HISTORY=[]
def _load_process_text(text,textcolor=(255,255,255,240),bgimageres=None,bottomcolor=(15,16,40,200),open_sentence='sentences.normal1',tick=0):
    global HISTORY
    HISTORY.append(yaheifont.render(text[:100], True, textcolor).convert_alpha())
    get_world().surface.fill((0,0,0,255))
    start_pos = vector2(2,2)
    bias_y = 18
    HISTORY = HISTORY[max(len(HISTORY)-28,0):]
    for text in HISTORY:
        if text:
            get_world().surface.blit(text,point2tuple(start_pos))
        start_pos.y += bias_y
    pg.display.update()

LOAD_PROCESS = {'GUI':_load_process_,'text':_load_process_text}