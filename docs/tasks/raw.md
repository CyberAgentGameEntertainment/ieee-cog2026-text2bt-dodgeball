# **Behavior Tree Task Set**

## **Task 1: Idle Spinner**

Level 1:
```
* Select one movement
  * if not turning  
    * Start rotating to left forever
  * if turning
    * Do nothing
```

Level 2:
```
Keep always rotating leftwards.
```

## **Task 2: Ball Chaser**

Level 1:
```
* Select one movement  
  * if a ball is visible  
    * Start run towards the ball 0 degrees  
  * Stop running
```

Level 2:
```
If you see a ball, run towards it
If you do not see a ball, stop and dont move
```


## **Task 3: Trolling**

Level 1:
```
* Selector  
  * If you can see an enemy
    * Sequence
      * Start turning towards the enemy
      * Start Run towards the enemy
      * if the enemy is at front by 5.0 distance
        * Start running 90 degrees right
  * If running
    * Stop running
  * Start rotate anti-clockwise
```

Level 2:
```
if you see an enemy, keep look and run towards it.
If you see an enemy and the distance is within 5.0, keep run right side relative to the enemy
If not seeing an enemy, dont run and rotate anti-clockwise
```

## **Task 4: Basic Collector**

Level 1:
```
* Select one movement  
  * if a ball is visible  
    * Do these in this sequence.
      * Start run towards the ball
      * Start turn towards the ball
  * if running  
    * Stop running
  * Start rotating left
```

Level 2:
```
If you see a ball, keep look and run towards the ball.
If not seeing a ball, rotate leftwards and dont run.
```

## **Task 5: Standard Bot Strategy**

Level 1:
```
* Select one movement  
  * if holding at least 1 balls AND if enemy is in sight (attack)
    * Do these in order  
      * Rotate towards the enemy  
      * If enemy at front
        * Throw a ball  
  * if a ball is visible AND NOT holding four balls (Collection)
    * Do these in order  
      * Stop rotating
      * Start run towards the ball 0 degrees  
  * Start rotating anti-clockwise (Search)
```

Level 2:
```
If you have at least one ball and you can see the enemy, keep looking at the enemy, then throw the ball if it is at front of you. (attack)
If you can see a ball and you have less than 4 balls, run to the ball. (collect)
If there is nothing to do, rotate anti-clockwise (search)
Priotize attack more than collect.
```

## Task 6: Strafe shooting


Level 1:
```
* Select one movement
  * if enemy is in sight
    * do these in order
      * Start turn towards the enemy
      * Select one movement
        * if have at least 1 ball AND enemy at front
          * Throw a ball
        * Repeat these in this order
          * Start Running towards 90 degrees left for 0.5 seconds
          * Do nothing
          * if not running
            * Start Running forward for 0.5 seconds
          * Do nothing
          * if not running
            * Start Running towards 90 degrees right for 0.5 seconds
          * Do nothing
          * if not running
            * Start Running backwards for 0.5 seconds
          * Do nothing
          * if not running
            * Do nothing
  * if running
    * Stop running
  * Start rotating left
```

Level 2:
```
If you have a ball and the enemy is at front of you, throw the ball. (Attack)
If you can see the enemy, keep looking at the enemy and strafing. Strafing is to move left, forward, right, back 0.5 seconds each.
If you cannot see an enemy, stop running and rotate leftwards.
```

## Task 7: Aggressive Duelist

Level1: 
```
* Select one movement  
  * if enemy is at front by 7.0 AND holding at least 1 ball. 
        * Throw a ball  
  * if holding at least 3 balls AND enemy is in sight (Combat)  
      * Do these in order  
        * Turn towards the enemy
        * Start run towards the enemy 0 degrees
  * if a ball is visible AND NOT holding four balls (Reload)  
    * Do these in order  
      * Turn towards the ball
      * Start run towards the ball 0 degrees
  * if running
    * Stop running
  * Start rotating clockwise (Search Ball or enemy)
```

Level2:
```
If the enemy is at front and the distance is within 7.0 and you have at least a single ball, throw it. (Attack)
If having more or equal to 3 balls and enemy is in sight, keep looking and intercepting at the enemy (Intercept)
If you can see a dropped ball and not having 4 balls, look and go to the ball. (Collection)
if nothing to do, stop running and rotate clockwise (searching)
the priority is "attack > intercept > collection > searching"
```

## Task 8: Tactical Turret

Level 1:
```
* Select one movement  
  * if enemy is at front AND have at least one ball AND not running
    * Throw a ball  
  * if holding more than 3 balls  
    * do these in order  
      * Stop running
      * Start rotating anti-clockwise  
  * if a ball is visible and NOT holding more than 3 balls 
    * Do these in order  
      * Stop rotating
      * Start run towards the ball
  * Do these in order  
    * Stop running
    * Start rotating clockwise
```
  
Level 2:
```
If an enemy is at front and holding any ball and not running, throw it. (Attack)
If holding more than three balls, dont run and rotate anti-clockwise (Turret movement)
If a dropped ball visible and not holding more than 3 balls, run to the ball. (Collection)
If nothing to do, rotate clockwise (Search)
Prioritize attacking first
```

## Task 9: Hit and Run

Level 1:
```
* Selector
  * if enemy is at front by 7.0 distance AND have at least one ball  
    * Throw a ball  
  * if holding at least 2 balls AND enemy is in sight (Hit and Run)
    * sequence
      * Rotate towards the enemy
      * Run towards the enemy
  * If enemy is in sight within 15.0 distance
    * Start run 180 degrees towards the enemy  
  * if a ball is visible AND holding less than four balls (Collection)
    * Do these in order 
      * Stop rotating
      * Start run towards the ball 0 degrees  
  * Start rotating clockwise
```

Level 2:
```
If the enemy is at front within 7.0 and you have a ball, throw it.
If you have at least 2 balls and the enemy visuable, keep look and run at the enemy
if the enemy is visuable and it's near than 15.0 but you dont have more than a single ball, run backwards
if you can see a ball and you are holding less than four balls, go get it
if nothing to do, rotate clockwise
the priority of ball collection is lower than others
```

## Task 10: The Satellite (Orbiter)

Level 1:
```
* Select one movement
  * if enemy at front AND have at least one ball  
    * Throw a ball
  * if holding at least 3 balls AND enemy in sight (Orbit Combat)  
    * Do these in order  
      * Start turn towards the enemy  
      * Start run 90 degrees left relative to the enemy (Circle Strafe)  
  * if a ball is visible AND holding less than four balls (Collection)
    * Do these in order 
      * Stop rotating
      * Start run towards the ball 0 degrees  
  * Start rotating clockwise
```

Level 2:
```
If enemy at fron and you have a ball, throw it. (Attack)
If you have at least 3 balls and the enemy is in sight, go around the enemy leftwards while looking at it. (Orbit movement)
If you can see a dropped ball and have less than 4 balls, run to it. (Collection)
Rotate clockwise (Search)
The priority is Attack > Orbit movement > Collection > Search
```
