Tactihack2

This is a work-in-progress snapshot. It's not a finished/polished or fully playable product. We assume the user is a programmer or sufficiently technical.

To play:
    ./tactihackd
    ./tactihackcg

There is also a CLI client which is not needed by players and exists purely to show and ensure that multiple clients and client types can work, and to be the platform upon which an admin tool can be built in the future. Currently it just prints some simple stats about the state of the world.

Introduction

This is a stab at re-writing/re-inventing an older unpublished game of mine, TactiHack, from scratch, except with some difference architectural and development process choices. The original was in C using curses and wsa a lot of fun to play, though the complete vision was not built out. This version uses Pygame. We'll start by implementing the core gameplay, the core fun part of movement and combat and exploration of a map, and won't add campaigns/scenarios/recruiting/etc until much much later in the project life. (Think a cross between XCOM and GI Joe.)  Another goal is to give it a client/server architecture from the start; and to use ZeroMQ, somewhat as an excuse to gain more experience using it; another goal is we're going to publish the source to this in my public GitHub account as a career feather-in-cap.

This uses zeromq 3.2.4 for the client/server communication so you'll need to have that installed plus the Python zmq module.

Play Controls:

TAB to cycle selected unit
t to cycle current fire target
f to make selected unit fire at current target 
vi/Rogue-like keys to move selected unit in that direction (hjkl yu bn)
q to quit

some units cannot fire, some cannot move
the selected unit must have AP left to move or fire
ammo is required to fire

You can control all factions at the moment, while under development. AP never refreshes because the turn advance code is not written yet.

