from tool import *
import pygame as pg


class Entity:
    def __init__(self,pos:vector2, hitbox:Box, defname:str=None, showdeep=0):
        # defname 
        self.pos = pos
        self.hitbox = hitbox
        self.alive = True
        self.image:pg.Surface = None
        self.defname = defname
        self.interface = None
        self.showdeep = showdeep
        self.isblocked = False

    def update(self, tick=0):
        pass

    def draw(self, scr: pg.Surface, bias : vector2):
        if self.image:
            scr.blit(self.image, (self.get_screenpos(bias))._intlist())

    def set_dead(self):
        self.alive = False

    def get_hitbox_pos(self):
        return self.pos + self.hitbox.pos

    def oninteracted(self, fromentity):
        self.interfunc(self, fromentity)

    def replace_interacted(self, func):
        self.interfunc = func

    def onhited(self, target, nhp, wayp, hittype):
        pass

    def get_screenpos(self, bias):
        return (self.pos + bias, self.deep)

    def get_brightinfo(self):
        # return vector2(0,0),0
        return None
    # hit system

class EntityBlocked(Entity):
    def __init__(self,pos:vector2, hitbox:Box, defname:str=None, showdeep=0):
        super().__init__(pos,hitbox,defname=defname, showdeep=showdeep)
        self.isblocked = True
        self.vel = vector2(0,0)
    def update(self, tick):
        self.pos += self.vel
    def draw(self, scr, bias):
        '''
        pg.draw.rect(scr, (100, 0, 0, 255),
                     (*(self.pos + bias + self.hitbox.pos)._intlist(), *self.hitbox.rect._intlist()), 1)
        '''
        pg.draw.rect(scr, (100, 0, 0, 255),
                     (*(self.pos + bias + self.hitbox.pos)._intlist(), *self.hitbox.rect._intlist()), 1)


class EntityLiving(Entity):
    def __init__(self,pos:vector2, hitbox:Box, defname:str=None, showdeep=0):
        super().__init__(pos,hitbox,defname=defname, showdeep=showdeep)
        self.vel = vector2(0, 0)
    def update(self, tick):
        self.pos += self.vel
    def draw(self, scr, bias):
        pass
        pg.draw.rect(scr, (0, 100, 0, 255), (*(self.pos + bias)._intlist(), *self.hitbox.rect._intlist()), 1)
    def onnothitflag(self):
        pass



class EntityLine:
    def __init__(self):
        self.entityline : list[Entity] = [] 
    def update(self,tick:int):
        rmlst=[]
        for e in self.entityline:
            e.update(tick)
            if not e.alive:
                rmlst.append(e)
        for rme in rmlst:
            self.entityline.remove(rme)
    def eventupdate(self,se:pg.event.Event,camera_pos:vector2):
        for e in self.entityline:
            e.update(se,camera_pos)
    def draw(self,scr:pg.Surface,camera_pos:vector2):
        for e in self.entityline:
            e.draw(scr,camera_pos)
    def __iter__(self):
        return iter(self.entityline)
    def __getitem__(self,key):
        return self.entityline[key]
class WorldEngine:
    def __init__(self):
        self.image_line=[]
        self.living_line=[]
        self.blocked_line=[]
    def update(self,tick):
        pass
    def draw(self,scr):
        pass

class WorldEngine:
    def __init__(self):
        # self.frontimages_line=[]
        self.clear_all()
        self.camera_pos = vector2(0, 0)
        self.brightness = []

    def get_blockeds_line(self):
        return self.blockeds_line

    def get_livings_line(self):
        return self.livings_line

    def get_images_line(self):
        return self.images_line

    def clear_all(self):
        self.blockeds_line = EntityLine()
        self.livings_line = EntityLine()
        self.images_line = EntityLine()
        # (box,vel,father,faction)
        self.bullets_line = EntityLine()
    def draw(self, scr):
        for entity in sorted(self.images_line.entityline + self.blockeds_line.entityline + self.livings_line.entityline, key=deepkey):
            entity.draw(scr, self.camera_pos)
    def update(self,tick):
        self.blockeds_line.update(tick)
        self.livings_line.update(tick)
        self.images_line.update(tick)

        for living in self.livings_line:
            hits:list[EntityBlocked] = segment_oneforall(living, self.blockeds_line)
            for hit in hits:
                living_pos1 = living.get_hitbox_pos()
                living_pos2 = living_pos1 + living.hitbox.rect
                blocked_pos1 = hit.get_hitbox_pos()
                blocked_pos2 = blocked_pos1 + hit.hitbox.rect
                livingcentre = get_centre(living)
                blockedcentre = get_centre(hit)
                detla_vel = living.vel-hit.vel
                detla = vector2(
                    abs((living_pos2.x - blocked_pos1.x) if detla_vel.x >= 0 else (living_pos1.x - blocked_pos2.x)),
                    abs((living_pos2.y - blocked_pos1.y) if detla_vel.y >= 0 else (living_pos1.y - blocked_pos2.y))
                    )
                #if living.vel.x==0:detla.x=0
                #if living.vel.y==0:detla.y=0

                nhx = round((hit.hitbox.rect.x / 2 + living.hitbox.rect.x / 2) - abs(blockedcentre.x - livingcentre.x),
                            5)
                nhy = round((hit.hitbox.rect.y / 2 + living.hitbox.rect.y / 2) - abs(blockedcentre.y - livingcentre.y),
                            5)
                
                nohit = vector2(nhx,nhy)
                time = vector2(
                    detla.x / abs(detla_vel.x) if detla_vel.x!=0 else math.nan,
                    detla.y / abs(detla_vel.y) if detla_vel.y!=0 else math.nan
                )
                printtext(f'{detla},{time}', middle_chinese, vector2(50, 75), scr)
                pg.display.update()
                
                if time.x >= time.y or (detla_vel.x==0 and nohit.x!=0):

                    if detla_vel.y > 0:
                        living.vel.y = hit.vel.y
                        living.pos.y -= detla.y
                    
                    elif detla_vel.x < 0:
                        living.vel.y = hit.vel.y
                        living.pos.y += detla.y
                    
                
                elif time.x <= time.y or (detla_vel.y==0 and nohit.y!=0):

                    if (living.vel.x-hit.vel.x) > 0 :
                        living.vel.x = hit.vel.x
                        living.pos.x -= detla.x
                    
                    elif (living.vel.x-hit.vel.x) < 0:
                        living.vel.x = hit.vel.x
                        living.pos.x += detla.x
                

# Example
if __name__ == '__main__':
    pg.init()
    import sys
    WINDOW = vector2(600, 480)
    middle_chinese = pg.font.Font(None, 16)
    from pygame.locals import QUIT, KEYDOWN, K_j, K_a, K_d, K_w,K_s,KEYUP

    scr = pg.display.set_mode(WINDOW._list())
    set_posmap(WINDOW)
    ew = WorldEngine()
    bk=EntityBlocked(vector2(100, 100), Box(vector2(0,0),vector2(300, 300)))
    bk.vel.x=1.1
    bk2=EntityBlocked(vector2(100, 0), Box(vector2(0,0),vector2(400, 80)))
    bk2.vel.x=1
    bk2.vel.y=0.1
    ew.get_blockeds_line().entityline.extend(
        [bk,EntityBlocked(vector2(0, 180), Box(vector2(0,0),vector2(3200, 100))),EntityBlocked(vector2(600, 100), Box(vector2(0,0),vector2(120, 300))),bk2])
    p = EntityLiving(vector2(150, 50), Box(vector2(0, 0), vector2(5, 5)))
    ew.get_livings_line().entityline.extend([p])
    pg.key.stop_text_input()
    fps= pg.time.Clock()
    force=0
    while True:
        fps.tick(100)
        scr.fill((0, 0, 0))
        ew.update(0)
        for evt in pg.event.get():
            if evt.type == QUIT:
                sys.exit()
            elif evt.type == KEYUP:
                key = evt.dict['key']
                if key == K_j:
                    p.vel.y -= force
                    force=0
        keys = pg.key.get_pressed()
        if keys[K_a]: p.vel.x -= 0.08
        if keys[K_d]: p.vel.x += 0.08
        if keys[K_w]: p.vel.y -= 0.08
        if keys[K_s]: p.vel.y += 0.08
        if keys[K_j]: force = min(force+0.1,4)
        p.vel.y+=0.04
        ew.camera_pos = get_centre_u(vector2(0,0)-p.pos, WINDOW)
        ew.draw(scr)
        printtext('{%f,%f},{%f,%f} %f' % (p.pos.x, p.pos.y, p.vel.x, p.vel.y,force), middle_chinese, vector2(100, 55), scr)
        pg.display.update()