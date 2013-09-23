#!/usr/bin/env python2.7

import collections
from tactihacklib import *

def main():
    print "Tactihack CLI client"
    #print "sending 'get_things' to server and reply is: "
    client = TactihackClient()
    #reply = client.send('new_game')
    reply = client.send('get_things')
    things = new_game_reply_to_things(reply)
    print "things qty %i" % len(things)

    def zero(): return 0
    counts = collections.defaultdict(zero)
    for t in things:
        if t.name == 'terrorist':
            if t.hp > 0: counts['terr_alive'] += 1
            else: counts['terr_dead'] += 1
        if isinstance(t,Soldier) and t.name != 'terrorist':
            if t.hp > 0: counts['team_alive'] += 1
            else: counts['team_dead'] += 1
        if isinstance(t,Tree):
            counts['trees'] += 1
    for k in ('team_alive','team_dead','terr_alive','terr_dead','trees'):
        print "%s = %i" % (k, counts[k])

if __name__ == '__main__':
    main()
