# walk - IN PROGRESS
Uses the NEAT algorithm to optimize walking behaviour on various "creatures".
The program simulates a physics environment with a 2D model. The creature (model)
has limbs that it can control. The creature dies if it touches the left wall in
the simulation. Since the ground moves slowly to the left, the creature must learn
how to move itself away from the left in order to survive.


Inspiration and source for NEAT algorithm: https://www.youtube.com/watch?v=qv6UVOQ0F44&ab_channel=SethBling

Required modules: pymunk, pygame, numpy, tkinter

Execute the following in the command line to run the program.
```
python main.py
```

Select the creature to simulate, and run the simulation.
Selecting "Show GUI" gives a visual representation of each individual creature
being processed. Having this unchecked allows for much faster iterations.
