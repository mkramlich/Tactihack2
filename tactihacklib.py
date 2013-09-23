# tactihacklib.py

import json, zmq # we use 0MQ 3.2.4

SERVER_URL = "tcp://127.0.0.1:9999"

class Thing:
    def __init__(self, name=None, x=None, y=None, weapon=None):
        self.name = name
        self.x = x
        self.y = y
        self.hp = 10
        self.ammo = 15
        self.weapon = weapon
        self.ap = 20
        self.can_move = True
        self.can_fire = True

    def ser_as_dict(self):
        return {'__class__':self.__class__.__name__,
                'name'     :self.name,
                'x'        :self.x,
                'y'        :self.y,
                'hp'       :self.hp,
                'ammo'     :self.ammo,
                'weapon'   :self.weapon,
                'ap'       :self.ap,
                'can_move' :self.can_move,
                'can_fire' :self.can_fire}

    def pop_from_dict(self, d):
        self.name = d['name']
        self.x = d['x']
        self.y = d['y']
        self.hp = d['hp']
        self.weapon = d['weapon']
        self.ammo = d['ammo']
        self.ap = d['ap']
        self.can_move = d['can_move']
        self.can_fire = d['can_fire']

    def status_text(self):
        wtxt = ''
        if self.weapon:
            wtxt = ", %s (%i ammo)" % (self.weapon, self.ammo)
        aptxt = ''
        if self.name in ('hero','buddy','terrorist'): #TODO improper
            aptxt = '%i AP, ' % self.ap
        return "%s: %s%i HP%s" % (self.name, aptxt, self.hp, wtxt)


class Soldier(Thing):
    pass


class Tree(Thing):
    def __init__(self, x=None, y=None):
        Thing.__init__(self,'tree',x,y)
        self.ap = 0
        self.can_move = False
        self.can_fire = False


class MachineGun(Thing):
    def __init__(self, x=None, y=None):
        Thing.__init__(self,'machine gun',x,y)
        self.can_move = False


class TactihackClient:
    def __init__(self):
        # establish communication with the game server
        # where the master instance of world state is held and updated
        context = zmq.Context()
        self.server = context.socket(zmq.REQ)
        self.server.connect(SERVER_URL)

    def send(self, msg):
        print 'sending msg to server: %s' % msg
        self.server.send(msg)
        reply = self.server.recv()
        #print "received reply '%s' for our msg '%s'" % (reply, msg)
        return reply


def jsonthings_to_things(jsonthings):
    thingsnew = []
    for jt in jsonthings:
        clname = jt['__class__']
        thingsubclass = globals()[clname]
        th = thingsubclass()
        th.pop_from_dict(jt)
        thingsnew.append(th)
    return thingsnew

def new_game_reply_to_things(reply):
    jsonresult = reply[5:] # because format was: 'JSON <pickled-things-array>'
    jsonthings = json.loads(jsonresult)
    things = jsonthings_to_things(jsonthings)
    return things

