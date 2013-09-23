#!/usr/bin/env python2.7

# Tactihack's Pygame Client, using 0MQ REQ

game_title = 'TactiHack Pygame'

import sys, time, json, pickle
import pygame
from tactihacklib import *

width = None
height = None
ANIMATE_EVENT = pygame.USEREVENT

class ThingView:
    char = '?'
    color = 'white'

    def __init__(self, thing):
        self.thing = thing

    def draw_thing(self, surface):
        c = colors[self.color]
        ch = self.char
        if self.thing.hp <= 0:
            ch = '%'
        ts = font.render(ch, antialias, c) #TODO cache this surf and reuse
        surface.blit(ts, ((self.thing.x*fs)+fs/8,
                          (self.thing.y*fs),      fs, fs))


class SoldierView(ThingView):
    char = '@'

    def __init__(self, thing):
        ThingView.__init__(self,thing)
        if self.thing.name == 'terrorist':
            self.color = 'red'


class TreeView(ThingView):
    char = 'T'
    color = 'green'


class MachineGunView(ThingView):
    char = 'G'
    color = 'gray'


class Mode:
    def event_handle(self, event):
        print event

        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == ANIMATE_EVENT:
            if TreeView.char == 'T': TreeView.char = 't'
            else: TreeView.char = 'T'
            return

        if event.type == pygame.KEYDOWN:
            keyname = pygame.key.name(event.key)
            print keyname

            if keyname == 'q':   sys.exit()

            if keyname == 'tab': cycle_actor()
            if keyname == 't':   cycle_target()

            if keyname == 'j':   move(0,1)
            if keyname == 'k':   move(0,-1)
            if keyname == 'h':   move(-1,0)
            if keyname == 'l':   move(1,0)
            if keyname == 'y':   move(-1,-1)
            if keyname == 'u':   move(1,-1)
            if keyname == 'n':   move(1,1)
            if keyname == 'b':   move(-1,1)

            if keyname == 'f':   fire()

    def draw(self):
        screen.fill( colors['black'])
        #blit_hcentered(screen, surfs['title'], 100)
        for i in range(len(things)):
            th = things[i]
            thv = thingviews[i]
            if actor > -1 and th == things[actor]: continue
            thv.draw_thing(screen)
        ml = 20
        if actor >= 0:
            a = things[actor]
            av = thingviews[actor]
            draw_text(a.status_text(), (ml,0), screen)
            # draw actor indicator circle
            av.draw_thing(screen)
            pygame.draw.circle(screen, colors['blue'], ((a.x*fs)+(fs/2), (a.y*fs)+(fs/2)), (2*fs)/3, 1) # indicate focused

        if target > -1: # draw target indicator square
            e = things[target]
            #ev = thingviews[target]
            draw_text(e.status_text(), (ml,fs), screen, 'red')
            pygame.draw.rect(screen, colors['red'], (e.x*fs,e.y*fs,fs,fs), 1)

        y = 50
        pygame.draw.line(screen, colors['white'], (0,y), (width,y))
        y = height - fs*3 - 5
        pygame.draw.line(screen, colors['white'], (0,y), (width,y))

        fby = height - fs*3
        for fb in fbs[-3:]:
            draw_text(fb, (ml, fby), screen)
            fby += fs


def blit_hcentered(dest, src, y):
    dest.blit(src, ((dest.get_width() - src.get_width()) / 2, y))

def draw_text(txt, pos, surf, color=None):
    c = colors['white']
    if color:
        c = colors[color]
    ts = font.render(txt, antialias, c)
    surf.blit(ts, pos)

def fb(txt): # TODO purge old entries so doesn't leak
    fbs.append(txt)

def cycle_actor():
    global actor, target

    if len(things) < 1:
        actor = -1
    actor += 1
    if actor >= len(things):
        actor = 0
    if target == actor:
        target = -1

def cycle_target():
    global actor, target

    if len(things) < 1:
        target = -1
        return
    target += 1
    if target == actor:
        target += 1 # cannot target self so we'll advance past
    if target >= len(things):
        target = 0
    if target == actor:
        target = -1
        return

def move(xd, yd):
    if actor < 0:
        fb('nobody selected')
        return

    a = things[actor]

    if a.hp <= 0:
        fb('you (%s) are dead so cannot move' % a.name)
        return

    if not a.can_move:
        fb('this type of thing cannot move')
        return

    if a.ap < 1:
        fb('you (%s) cannot move due to not enough AP left' % a.name)
        return

    msg = 'move %i %i %i' % (actor, xd, yd)
    reply = client.send(msg) # assume reply is '<result-in-JSON>'
    resultjson = reply[5:] # because format was: 'JSON <json>'
    r = json.loads(resultjson) # afterward we have a dict
    s = r['s']
    m = r['m']
    if s: # success; whether requested move happened or not
        a.ap = r['ap']
        a.x = r['x']
        a.y = r['y']
    fb(m)

def fire():
    if actor < 0:
        fb('nobody selected')
        return

    a = things[actor]

    if not a.can_fire:
        fb('this type of thing cannot fire')
        return

    if target < 0:
        fb('no target')
        return

    e = things[target]

    if a.hp <= 0:
        fb('you (%s) are dead so cannot fire' % a.name)
        return

    if a.ap < 1:
        fb('you (%s) cannot fire because not enough AP left' % a.name)
        return

    if a.ammo <= 0:
        fb('you (%s) are out of ammo' % a.name)
        return

    msg = 'fire %i %i' % (actor, target)
    reply = client.send(msg) # assume reply is '<result-in-JSON>'
    resultjson = reply[5:] # because format was: 'JSON <json>'
    r = json.loads(resultjson) # afterward we have a dict
    s = r['s']
    m = r['m']
    if s: # success; whether requested fire happened or not
        a.ap = r['ap']
        a.ammo = r['ammo']
        e.hp = r['hp']
    fb(m)


things = None
thingviews = None
fbs = None
surfs = None
colors = None
screen = None
fs = None
font = None
actor = None
target = None
antialias = True
client = None


def main():
    global size, width, height, things, thingviews, surfs, fbs, colors, screen, fs, font, actor, target, client

    print game_title

    pygame.init()
    pygame.font.init()

    size = width, height = 800, 500
    screen = pygame.display.set_mode(size)

    colors = {}
    colors['black'] = (  0,  0,  0)
    colors['white'] = (255,255,255)
    colors['red'] =   (255,  0,  0)
    colors['blue'] =  (  0,  0,255)
    colors['green'] = (  0,255,  0)
    colors['title'] = ( 80,110,150)
    colors['gray'] =  ( 80, 80, 80)

    fs = 24
    font = pygame.font.Font('Bitstream-Vera-Sans-Mono-VeraMono.ttf',fs)

    actor = 0 # when user gives keyboard commands, they are orders for him
    target = 2 # who the acting entity is currently targeting for combat/info

    surfs = {}
    surfs['title'] = font.render(game_title, antialias, colors['title'])

    fbs = []

    mode = Mode()
    #pygame.time.set_timer(ANIMATE_EVENT, 100) 

    client = TactihackClient()
    reply = client.send('new_game')
    things = new_game_reply_to_things(reply)

    thing2view_map = {
        Thing      : ThingView,
        Soldier    : SoldierView,
        Tree       : TreeView,
        MachineGun : MachineGunView}

    thingviews = []
    for th in things:
        viewclass = thing2view_map[th.__class__]
        thingviews.append( viewclass(th))

    while True:
        event = pygame.event.wait()
        mode.event_handle(event)
        mode.draw()
        pygame.display.flip()


if __name__ == '__main__':
    main()
