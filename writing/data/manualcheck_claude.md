# **Behavior Tree Task Set**

## **Task 1: Idle Spinner**

1

```
o Keep always rotating leftwards.
```

## **Task 2: Ball Chaser**

```
o If you see a ball, run towards it
o If you do not see a ball, stop and dont move
```

```
o If you see a ball, run towards it
o If you do not see a ball, stop and dont move
```

## **Task 3: Trolling**

```
o if you see an enemy, keep look and run towards it.
o If you see an enemy and the distance is within 5.0, keep run right side relative to the enemy
o If not seeing an enemy, dont run and rotate anti-clockwise
```

```
o if you see an enemy, keep look and run towards it.
o If you see an enemy and the distance is within 5.0, keep run right side relative to the enemy
o If not seeing an enemy, dont run and rotate anti-clockwise
```

```
o if you see an enemy, keep look and run towards it.
o If you see an enemy and the distance is within 5.0, keep run right side relative to the enemy
o If not seeing an enemy, dont run and rotate anti-clockwise
```

```
o if you see an enemy, keep look and run towards it.
o If you see an enemy and the distance is within 5.0, keep run right side relative to the enemy
o If not seeing an enemy, dont run and rotate anti-clockwise
```

## **Task 4: Basic Collector**

```
o If you see a ball, keep look and run towards the ball.
o If not seeing a ball, rotate leftwards and dont run.
```

```
o If you see a ball, keep look and run towards the ball.
o If not seeing a ball, rotate leftwards and dont run.
```

## **Task 5: Standard Bot Strategy**

malfunction

```
o If you have at least one ball and you can see the enemy, keep looking at the enemy, then throw the ball if it is at front of you. (attack)
o If you can see a ball and you have less than 4 balls, run to the ball. (collect)
o If there is nothing to do, rotate anti-clockwise (search)
o Priotize attack more than collect.
```

```
o If you have at least one ball and you can see the enemy, keep looking at the enemy, then throw the ball if it is at front of you. (attack)
o If you can see a ball and you have less than 4 balls, run to the ball. (collect)
o If there is nothing to do, rotate anti-clockwise (search)
o oPriotize attack more than collect.
```

```
o If you have at least one ball and you can see the enemy, keep looking at the enemy, then throw the ball if it is at front of you. (attack)
o If you can see a ball and you have less than 4 balls, run to the ball. (collect)
o If there is nothing to do, rotate anti-clockwise (search)
o Priotize attack more than collect.
```

```
o If you have at least one ball and you can see the enemy, keep looking at the enemy, then throw the ball if it is at front of you. (attack)
o If you can see a ball and you have less than 4 balls, run to the ball. (collect)
o If there is nothing to do, rotate anti-clockwise (search)
o Priotize attack more than collect.
```

## Task 6: Strafe shooting

```
o If you have a ball and the enemy is at front of you, throw the ball. (Attack)
x If you can see the enemy, keep looking at the enemy and strafing. Strafing is to move left, forward, right, back 0.5 seconds each.
o If you cannot see an enemy, stop running and rotate leftwards.
```

missunderstanding of sequencing

```
o If you have a ball and the enemy is at front of you, throw the ball. (Attack)
x If you can see the enemy, keep looking at the enemy and strafing. Strafing is to move left, forward, right, back 0.5 seconds each.
o If you cannot see an enemy, stop running and rotate leftwards.
```

```
o If you have a ball and the enemy is at front of you, throw the ball. (Attack)
x If you can see the enemy, keep looking at the enemy and strafing. Strafing is to move left, forward, right, back 0.5 seconds each.
o If you cannot see an enemy, stop running and rotate leftwards.
```

missunderstanding of sequencing

```
o If you have a ball and the enemy is at front of you, throw the ball. (Attack)
x If you can see the enemy, keep looking at the enemy and strafing. Strafing is to move left, forward, right, back 0.5 seconds each.
o If you cannot see an enemy, stop running and rotate leftwards.
```

## Task 7: Aggressive Duelist

```
o If the enemy is at front and the distance is within 7.0 and you have at least a single ball, throw it. (Attack)
o If having more or equal to 3 balls and enemy is in sight, keep looking and intercepting at the enemy (Intercept)
o If you can see a dropped ball and not having 4 balls, look and go to the ball. (Collection)
o if nothing to do, stop running and rotate clockwise (searching)
o the priority is "attack > intercept > collection > searching"
```

```
o If the enemy is at front and the distance is within 7.0 and you have at least a single ball, throw it. (Attack)
o If having more or equal to 3 balls and enemy is in sight, keep looking and intercepting at the enemy (Intercept)
o If you can see a dropped ball and not having 4 balls, look and go to the ball. (Collection)
o if nothing to do, stop running and rotate clockwise (searching)
o the priority is "attack > intercept > collection > searching"
```

```
o If the enemy is at front and the distance is within 7.0 and you have at least a single ball, throw it. (Attack)
o If having more or equal to 3 balls and enemy is in sight, keep looking and intercepting at the enemy (Intercept)
o If you can see a dropped ball and not having 4 balls, look and go to the ball. (Collection)
o if nothing to do, stop running and rotate clockwise (searching)
o the priority is "attack > intercept > collection > searching"
```

```
o If the enemy is at front and the distance is within 7.0 and you have at least a single ball, throw it. (Attack)
o If having more or equal to 3 balls and enemy is in sight, keep looking and intercepting at the enemy (Intercept)
o If you can see a dropped ball and not having 4 balls, look and go to the ball. (Collection)
o if nothing to do, stop running and rotate clockwise (searching)
o the priority is "attack > intercept > collection > searching"
```

## Task 8: Tactical Turret

state control

```
x If an enemy is at front and holding any ball and not running, throw it. (Attack)
o If holding more than three balls, dont run and rotate anti-clockwise (Turret movement)
o If a dropped ball visible and not holding more than 3 balls, run to the ball. (Collection)
o If nothing to do, rotate clockwise (Search)
o Prioritize attacking first
```

```
o If an enemy is at front and holding any ball and not running, throw it. (Attack)
x If holding more than three balls, dont run and rotate anti-clockwise (Turret movement)
o If a dropped ball visible and not holding more than 3 balls, run to the ball. (Collection)
o If nothing to do, rotate clockwise (Search)
Prioritize attacking first
```

```
x If an enemy is at front and holding any ball and not running, throw it. (Attack)
x If holding more than three balls, dont run and rotate anti-clockwise (Turret movement)
x If a dropped ball visible and not holding more than 3 balls, run to the ball. (Collection)
o If nothing to do, rotate clockwise (Search)
o Prioritize attacking first
```

```
o If an enemy is at front and holding any ball and not running, throw it. (Attack)
o If holding more than three balls, dont run and rotate anti-clockwise (Turret movement)
o If a dropped ball visible and not holding more than 3 balls, run to the ball. (Collection)
o If nothing to do, rotate clockwise (Search)
o Prioritize attacking first
```

## Task 9: Hit and Run

```
o If the enemy is at front within 7.0 and you have a ball, throw it.
o If you have at least 2 balls and the enemy visuable, keep look and run at the enemy
o if the enemy is visuable and it's near than 15.0 but you dont have more than a single ball, run backwards
o if you can see a ball and you are holding less than four balls, go get it
o if nothing to do, rotate clockwise
o the priority of ball collection is lower than others
```

```
o If the enemy is at front within 7.0 and you have a ball, throw it.
o If you have at least 2 balls and the enemy visuable, keep look and run at the enemy
o if the enemy is visuable and it's near than 15.0 but you dont have more than a single ball, run backwards
o if you can see a ball and you are holding less than four balls, go get it
o if nothing to do, rotate clockwise
o the priority of ball collection is lower than others
```

```
o If the enemy is at front within 7.0 and you have a ball, throw it.
o If you have at least 2 balls and the enemy visuable, keep look and run at the enemy
o if the enemy is visuable and it's near than 15.0 but you dont have more than a single ball, run backwards
o if you can see a ball and you are holding less than four balls, go get it
o if nothing to do, rotate clockwise
o the priority of ball collection is lower than others
```

```
o If the enemy is at front within 7.0 and you have a ball, throw it.
o If you have at least 2 balls and the enemy visuable, keep look and run at the enemy
o if the enemy is visuable and it's near than 15.0 but you dont have more than a single ball, run backwards
o if you can see a ball and you are holding less than four balls, go get it
o if nothing to do, rotate clockwise
o the priority of ball collection is lower than others
```

## Task 10: The Satellite (Orbiter)

```
o If enemy at fron and you have a ball, throw it. (Attack)
o If you have at least 3 balls and the enemy is in sight, go around the enemy leftwards while looking at it. (Orbit movement)
o If you can see a dropped ball and have less than 4 balls, run to it. (Collection)
o Rotate clockwise (Search)
o The priority is Attack > Orbit movement > Collection > Search
```

```
o If enemy at fron and you have a ball, throw it. (Attack)
o If you have at least 3 balls and the enemy is in sight, go around the enemy leftwards while looking at it. (Orbit movement)
o If you can see a dropped ball and have less than 4 balls, run to it. (Collection)
o Rotate clockwise (Search)
o The priority is Attack > Orbit movement > Collection > Search
```

```
o If enemy at fron and you have a ball, throw it. (Attack)
o If you have at least 3 balls and the enemy is in sight, go around the enemy leftwards while looking at it. (Orbit movement)
o If you can see a dropped ball and have less than 4 balls, run to it. (Collection)
o Rotate clockwise (Search)
o The priority is Attack > Orbit movement > Collection > Search
```

```
o If enemy at fron and you have a ball, throw it. (Attack)
o If you have at least 3 balls and the enemy is in sight, go around the enemy leftwards while looking at it. (Orbit movement)
o If you can see a dropped ball and have less than 4 balls, run to it. (Collection)
o Rotate clockwise (Search)
o The priority is Attack > Orbit movement > Collection > Search
```
