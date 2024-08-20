'''
    音频管理
    先草pygame.mixer（惩罚），然后草concurrent.futures（奖励）
    
'''
'''
2024/05/20
Fatal Python error: (pygame parachute) Segmentation Fault
Python runtime state: initialized

Current thread 0x0000007fbe700010 (most recent call first):
  File "/home/firefly/Desktop/workplace/python/saveourvedal/workplace/tool.py", line 37 in __mul__
  File "/home/firefly/Desktop/workplace/python/saveourvedal/workplace/def/saveourvedal/evilcore.py", line 360 in set_process
  File "/home/firefly/Desktop/workplace/python/saveourvedal/workplace/def/saveourvedal/annycore.py", line 149 in update_process
  File "/home/firefly/Desktop/workplace/python/saveourvedal/workplace/def/saveourvedal/annycore.py", line 101 in update
  File "/home/firefly/Desktop/workplace/python/saveourvedal/workplace/newcoretiny.py", line 55 in update
  File "main.py", line 37 in update
  File "main.py", line 104 in <module>
fish: “python3 main.py --trigger story…” terminated by signal SIGABRT (Abort)
没复现成功，似乎是小概率事件
'''
import concurrent.futures,evilcore
import resmanager
from local import *
import os,random,time,tinytag,io
from newcoretiny import Runable
import pygame as pg
from tool import dividelst,vector2,trans_time,pointin,tuple2point,printtext,Box


_DEBUG_CONTINUE_RECORD=True
MAX_WORKERS=1


pg.mixer.init(frequency=44100,buffer=65536)

NOSOURCE=pg.Surface((100,100))
NOSOURCE.fill((255,255,255,200))
printtext('No Source',evilcore.xiaoxiongverybig,vector2(2,2),NOSOURCE,color=(255,255,255,255))

def start_record(lst):
    for file in lst:
        if not isinstance(file,str):
            continue
        try:
            file_path = file
            
            if _DEBUG_CONTINUE_RECORD and os.path.exists(trans_wav(file_path)):
                continue
            print('handling:',file_path)
            data, samplerate = sf.read(trans_ogg(file_path))
            sf.write(trans_wav(file_path), data, samplerate,format='wav')
        except sf.LibsndfileError as e:
            print(e)
            os.system(f'ffmpeg -i "{file_path}" "{trans_wav(file_path)}"')

def start_mulitprocess(handlelst=None,max_workers=2):
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        div=max(len(handlelst)//max_workers,max_workers)
        workers=[]
        for content in dividelst(handlelst,div):
            workers.append(executor.submit(start_record,content))
        for i,w in enumerate(workers):
            loclogger.info(resmanager.NameResourceDomain.get_resource('info.transogg_2').format(worker_info=i))
            w.result()


class EntityStatImage_Special(evilcore.EntityStatImage):
    def __init__(self, pos, boxpos, image, func=None,alpha=255, deep=0, defname=None, showdeep=0):
        super().__init__(pos, boxpos, image, alpha, deep, defname, showdeep)
        self.func=func
    def eventupdate(self, se, bias):
        if se.type == pg.locals.MOUSEBUTTONDOWN and pointin(tuple2point(se.dict['pos']),
                                                                              self.get_hitbox_pos() + bias,
                                                                              self.hitbox.rect):
            self.func(self.defname)
        return super().eventupdate(se, bias)
# 用pygame.mixer播放NeuroV3的歌曲明显变慢,还有其他问题，所以我用simpleaudio播放wav
def get_duringtick(source):
    return int(len(source.audio_data)/(source.bytes_per_sample*source.num_channels*source.sample_rate)*50)
class MusicCoreRunable_Base(Runable):
    def __init__(self):
        super().__init__()
        self.play_list = dict()
        self.detla = 10*50
        self.timer = self.detla
        self.original_time = 0
        self.allow_next = True
        self.nowplay = None

        # 电台界面
        def next(defname):
            self.play_action('playnow next')
        window = get_world().window
        detectboxa=Box(vector2(window.x-150,0),vector2(150,100))
        detectboxb=Box(vector2(window.x-330,0),vector2(330,110))
        self.info_frame = evilcore.EntitySlideFrame(vector2(window.x,100+5-40,),vector2(210,40),posB=vector2(get_world().window.x-215,100+5-40),detectboxA=detectboxa,detectboxB=detectboxb,defname='musiccorerunable_info_frame')
        self.coverimage_frame = evilcore.EntitySlideFrame(vector2(window.x,5),vector2(100,100),posB=vector2(get_world().window.x-330,5),detectboxA=detectboxa,detectboxB=detectboxb,defname='musiccorerunable_coverimage_frame')
        self._process = evilcore.EntityProcess(vector2(0,0),vector2(0,0),vector2(200,30),defname='process')
        self._nowplay = evilcore.EntityLabel(vector2(0,0),vector2(0,0),'None',evilcore.yaheifont,(0,0,0,0),(255,255,255,190),defname='nowplay')
        self._cover = EntityStatImage_Special(vector2(0,0),vector2(0,0),None,func=next,defname='cover')
        self._stat = evilcore.EntityLabel(vector2(2,22),vector2(0,0),'None',evilcore.yaheiverysmall,(0,0,0,0),(255,255,255,190),defname='stat')
        self.coverimage_frame.add_control(self._cover)
        self.info_frame.add_control(self._process)
        self.info_frame.add_control(self._nowplay)
        self.info_frame.add_control(self._stat)
        self.update_process(0)
        self.update_nowplay(None)
        self.update_stat('stop')

        self.show = False
    def update(self, tick, world):
        if self.lasttick+self.timer<=tick and self.play_list and self.allow_next:
            self._play(
                source=self.play_list[random.choice(tuple(self.play_list.keys()))]
                )
            self.lasttick=tick
        self.update_process(tick)
        self.info_frame.update(tick)
    def eventupdate(self,se):
        self.info_frame.eventupdate(se,vector2(0,0))
        self.coverimage_frame.eventupdate(se,vector2(0,0))
    def _play(self,source):
        pass
    def _stop(self):
        self.nowplay = None
    def get_musictype(self):
        def null(*args,**kwargs):
            return None
        return null
    def play_action(self,action='stop',**kwargs):
        if action=='stop':
            self._stop()
            self.allow_next = False
            self.update_stat('stop')
        elif action=='resume':
            self.allow_next = True
            self.timer = 100
            self.update_stat('play')
        elif action=='replace play_list':
            #random.shuffle(self.play_list)
            self.play_list = dict(kwargs['play_list'])
        elif action=='replace detla':
            self.detla = kwargs['detla']
        elif action=='playnow source':
            self._play(source=kwargs['source'])
            self.update_stat('play')
        elif action=='get musictype':
            return self.get_musictype()
        elif action=='playnow name':
            self.update_stat('play')
            return self._play(self.play_list[kwargs['name']])
        elif action=='playnow next':
            self.update_stat('play')
            self.allow_next = True
            self.timer = 0
        
    def draw(self,bs):
        self.info_frame.draw(bs,bias=vector2(0,0))
        self.coverimage_frame.draw(bs,bias=vector2(0,0))
    def update_stat(self,stat : str):
        classname = self.__class__.__name__.split('_')[-1]
        self._stat.change_text(text = f'{classname} {stat} (allow_next:{self.allow_next})')
    def update_process(self,tick):
        if self.nowplay:
            self._process.set_process((tick-self.lasttick)/self.timer)
        else:
            self._process.set_process()

    def update_nowplay(self,name):
        self.nowplay = name
        if name is not None:
            tag = tinytag.TinyTag.get(name,image=True)
            loclogger.debug(tag)
            
            nowtime = trans_time(tag.duration if tag.duration else 0)
            music_info = f'{tag.title}' if tag.title else name.split('/')[0]
            self._nowplay.change_text(f'{music_info} ({nowtime[0]:.2f}{nowtime[1]})')
            # 专辑图片
            cover = tag.get_image()
            if cover:
                image = pg.transform.smoothscale(pg.image.load(io.BytesIO(cover)),self.coverimage_frame.hitbox.rect._intlist()).convert()
                image.set_alpha(180)
                self._cover.change_image(image)
            else:
                self._cover.change_image(NOSOURCE)

class MusicCoreRunable_Simpleaudio(MusicCoreRunable_Base):
    def __init__(self):
        super().__init__()
        self.process=None

        start_time = time.time()
        get_loadprocesser()(resmanager.NameResourceDomain.get_resource('info.transogg').format(max_workers=MAX_WORKERS),tick=start_time)
    def _play(self,source):
        self._stop()
        if isinstance(source,str):
            source = self.get_musictype()(source)
        self.process = source.play()

        tick = get_duringtick(source)
        self.timer = tick + self.detla*(12+random.random()*12)
        self.original_time = tick
        self.update_nowplay(source.name)
        return True
    def _stop(self):
        if self.process:
            self.process.stop()
            super()._stop()
    
    def get_musictype(self):
        def f(x):
            wave = SA.WaveObject.from_wave_file(trans_wav(x))
            setattr(wave,'name',x)
            return wave
        return f



class MusicCoreRunable_Pygame_Mixer(MusicCoreRunable_Base):
    def __init__(self):
        super().__init__()
        self.channel=pg.mixer.find_channel(True)
        pg.mixer.music.set_endevent(pg.locals.USEREVENT)
        self.active=True
    def eventupdate(self,event):
        MusicCoreRunable_Base.eventupdate(self,event)
        if event.type==pg.locals.USEREVENT and self.active:
            # 启动计时器
            self.timer=self.detla*(0.5+random.random())
            self.allow_next=True
    def _play(self,source):
        if isinstance(source,str):
            self.allow_next=False
            pg.mixer.music.stop()
            pg.mixer.music.load(source)
            pg.mixer.music.play()
            self.update_nowplay(source.name)
            self.timer = 0
        else:
            self.channel.fadeout(4500)
            self.channel.play(source)
    def _stop(self):
        self.allow_next=False
        self.channel.fadeout(4500)
        pg.mixer.music.stop()
        super()._stop()
    def get_musictype(self):
        return pg.mixer.Sound




soundpath=dotpath+'resource/sound/'




def load_singlesound(respath:str):
    '''加载单首歌，转换至”real“+respath上'''
    mcr = MCO_target(resmanager.DefResourceDomain.get_resource('MusicCoreRunableType'))
    dtype=mcr.get_musictype()
    
    loclogger.debug(f'dtype:{dtype} {resmanager.DefResourceDomain.get_resource(respath)}')
    start_mulitprocess([resmanager.DefResourceDomain.get_resource(respath)])
    resmanager.DefResourceDomain.add_resource('real'+respath,dtype(resmanager.DefResourceDomain.get_resource(respath)))
def load_mutlisound(respath:str):
    mcr = MCO_target(resmanager.DefResourceDomain.get_resource('MusicCoreRunableType'))
    dtype=mcr.get_musictype()
    loclogger.debug(f'dtype:{dtype} {resmanager.DefResourceDomain.get_resource(respath)}')
    start_mulitprocess(resmanager.DefResourceDomain.get_resource(respath))
    resmanager.DefResourceDomain.add_resource('real'+respath,list(map(lambda x:x,resmanager.DefResourceDomain.get_resource(respath))))

def load_mutlisound_bypath(respath:str):
    mcr = MCO_target(resmanager.DefResourceDomain.get_resource('MusicCoreRunableType'))
    dtype=mcr.get_musictype()
    path = resmanager.DefResourceDomain.get_resource(respath)

    loclogger.debug(f'dtype:{dtype} {path}')
    processed_list = list(map(lambda x:os.path.join(path,x),
        filter(lambda x: os.path.isfile(os.path.join(path,x)) and get_lastname(x) == 'mp3',os.listdir(path))
        ))
    start_mulitprocess(processed_list)
    play_list = {name:dtype(name) for name in processed_list}
    
    resmanager.DefResourceDomain['real'+respath] = play_list



def trans_wav(source):
    return get_mainname(source)+'.wav'
def trans_ogg(source):
    return get_mainname(source)+'.ogg'
def get_mainname(source):
    return ''.join(source.split('.')[:-1])
def get_lastname(source):
    return source.split('.')[-1]




def check_modules(mutype):
    if mutype=='Simpleaudio':
        if not sf:
            raise ModuleNotFoundError(resmanager.NameResourceDomain.get_resource('error.needmodule').replace('[module]','pysoundfile(import soundfile as sf)'))
        if not SA:
            raise ModuleNotFoundError(resmanager.NameResourceDomain.get_resource('error.needmodule').replace('[module]','Simpleaudio(import Simpleaudio as SA)'))
    if not numpy:
        raise ModuleNotFoundError(resmanager.NameResourceDomain.get_resource('error.needmoudle').replace('[moudle]','numpy(import numpy)'))
    if not psutil:
        raise ModuleNotFoundError(resmanager.NameResourceDomain.get_resource('error.needmoudle').replace('[moudle]','psutil(import psutil)'))


ALL={'Pygame_Mixer':MusicCoreRunable_Pygame_Mixer,'Simpleaudio':MusicCoreRunable_Simpleaudio,'Base':MusicCoreRunable_Base}
TRANS={'Pygame_Mixer':trans_ogg,'Simpleaudio':trans_wav,'Base':trans_wav}