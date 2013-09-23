#!/usr/bin/env python2.7

# Tactihack 2's Server, using 0MQ REP

import json, pickle, zmq # we use 0MQ 3.2.4
from tactihacklib import *

things = None

def get_things():
    return [th.ser_as_dict() for th in things]

def new_game():
    global things

    things = [
        Soldier('hero',     10,10,weapon='Glock'),
        Soldier('buddy',     9,11,weapon='AR-15'),
        Soldier('terrorist',10, 7,weapon='9mm Uzi'),
        Soldier('terrorist',11, 7,weapon='9mm Uzi'),
        Soldier('terrorist', 6, 5,weapon='9mm Uzi'),
        Tree(3,10),
        Tree(4,10),
        Tree(6,11),
        MachineGun(15,11)]

    things2 = []
    for th in things:
        d = th.ser_as_dict()
        things2.append(d)
    return things2

def move(msg):
    r = {'s':False} # s means success, whether requested action happened/denied
    toks = msg.split(' ') # assumes format: move <actorid> <xd> <yd>
    actor = int(toks[1])
    a = things[actor] #TODO what if actor is invalid #?
    xd = int(toks[2])
    yd = int(toks[3])
    if a.hp <= 0:
        r['m'] = 'you (%s) are dead so cannot move' % a.name
    elif not a.can_move:
        r['m'] = 'this type of thing cannot move'
    elif a.ap < 1:
        r['m'] = 'you (%s) cannot move due to not enough AP left' % a.name
    else:
        #TODO check whether can move into the target XY because maybe blocked
        a.ap -= 1
        a.x += xd
        a.y += yd
        m = 'you (%s) moved' % a.name
        r.update({'s':True, 'm':m, 'ap':a.ap, 'x':a.x, 'y':a.y})
        # m means message, for the playing user to read explaining result
    return r

def fire(msg):
    r = {'s':False}
    toks = msg.split(' ') # assumes format: fire <actorid> <targetid>
    actor = int(toks[1])
    a = things[actor] #TODO what if actor is invalid #?
    target = int(toks[2])
    e = things[target] #TODO what if target is invalid #?
    if not a.can_fire:
        r['m'] = 'this type of thing cannot fire'
    elif a.hp <= 0:
        r['m'] = 'you (%s) are dead so cannot fire' % a.name
    elif a.ap < 1:
        r['m'] = 'you (%s) cannot fire because not enough AP left' % a.name
    elif a.ammo <= 0:
        r['m'] = 'you (%s) are out of ammo' % a.name
    else:
        r['s'] = True
        a.ap -= 1
        a.ammo -= 1
        e = things[target]
        r['m'] = 'you (%s) fired at %s' % (a.name,e.name)
        if e.hp > 0:
            e.hp -= 1
        if e.hp <= 0:
            r['m'] += ' and he died'
        r['ap'] = a.ap
        r['ammo'] = a.ammo
        r['hp'] = e.hp
    return r

def json_reply(result):
    resultjson = json.dumps(result)
    reply = 'JSON %s' % resultjson
    return reply

def pickled_reply(result):
    resultpickled = pickle.dumps(result)
    reply = 'PICK ' + resultpickled
    return reply

def main():
    print 'Tactihack Server starting on %s' % SERVER_URL
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(SERVER_URL)

    while True:
        print 'server waiting for msg'
        msg = socket.recv()
        print "received msg: %s" % msg
        reply = None
        if msg.startswith('new_game'):
            reply = json_reply( new_game())
            print 'replying: ' + reply
        elif msg.startswith('get_things'):
            reply = json_reply( get_things())
            print 'replying: ' + reply
        if msg.startswith('move'):
            reply = json_reply( move(msg))
            print 'replying: ' + reply
        elif msg.startswith('fire'):
            reply = json_reply( fire(msg))
            print 'replying: ' + reply
        socket.send(reply)

if __name__ == '__main__':
    main()

