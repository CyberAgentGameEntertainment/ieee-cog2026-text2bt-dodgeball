## Schema
### Vector
x, y, z

### ObjectInformation
- front
    - front Vector of the object rotated as the front vector of the player agent is (0,0,0)
- position
    - position Vector of the object translated as the front vector of the player agent is (0,0,0)

## Fields in sensory struct
- insights
    - holds ObjectInformation of the objects below. The most near among the objects in sight (exist between -60 - +60 from the agent). If none exists, `null`
    - Enemy
    - Ally
    - BallDropped
    - BallThrownByEnemy
        - front vector is the direction thrown
    - Wall
    - Obstacle

- ballsHolding
    - integer of the balls the agent holding now

- running
    - boolean of whether the agent is running 

- turning
    - boolean of whether the agent is turning
