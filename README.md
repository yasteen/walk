# walk - IN PROGRESS

The program simulates a physics environment with a 2D model. The "creature" (model)
has limbs that it can control. The creature dies if it touches the left wall in
the simulation. Since the ground moves slowly to the left, the creature must learn
how to consistently move itself away from the left wall in order to survive.
The NEAT machine learning algorithm is used to optimize this walking behaviour.


Inspiration and source for NEAT algorithm: https://www.youtube.com/watch?v=qv6UVOQ0F44&ab_channel=SethBling

Required modules: pymunk, pygame, numpy, tkinter

Execute the following in the command line to run the program.
```
python main.py
```

Select the creature to simulate, and run the simulation.
Selecting "Show GUI" gives a visual representation of each individual creature
being processed. Having this unchecked allows for much faster iterations.
