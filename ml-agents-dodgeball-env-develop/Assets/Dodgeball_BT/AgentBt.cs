using System;
using MLAgents;
using SimpleUnityBehaviorTree;
using SimpleUnityBehaviorTree.Nodes;
using SimpleUnityBehaviorTree.Serializations;
using UnityEngine;

public class AgentBt : MonoBehaviour
{
    // Inner classes for state management
    private class RunningState
    {
        public bool IsActive { get; set; }
        public float Angle { get; set; }
        public float ElapsedTime { get; set; }
        public float? Duration { get; set; }
        public string Target { get; set; }
        public float OffsetDegree { get; set; }

        public void Reset()
        {
            IsActive = false;
            Angle = 0f;
            ElapsedTime = 0f;
            Duration = null;
            Target = null;
            OffsetDegree = 0f;
        }
    }

    private class TurningState
    {
        public bool IsActive { get; set; }
        public float Speed { get; set; }
        public float ElapsedTime { get; set; }
        public float TotalDegrees { get; set; }
        public float? Duration { get; set; }
        public float? MaxDegree { get; set; }
        public string Target { get; set; }

        public void Reset()
        {
            IsActive = false;
            Speed = 0f;
            ElapsedTime = 0f;
            TotalDegrees = 0f;
            Duration = null;
            MaxDegree = null;
            Target = null;
        }
    }

    public TextAsset btFile;

    public BehaviorTree<Sensory, Actions> behaviorTree { get; private set; }

    private DodgeBallAgent agent;
    private AgentCubeMovement movement;

    // Sensory and Actions
    public Sensory sensory = new Sensory();
    public Actions actions = new Actions();

    // State for continuous actions
    private readonly RunningState runningState = new RunningState();
    private readonly TurningState turningState = new TurningState();

    [SerializeField]
    private float fieldOfViewAngle = 60f; // -60 to +60 degrees

    [SerializeField]
    private float maxTurnSpeed = 360f; // deg/sec upper limit for continuous turning

    [SerializeField]
    private bool showDebugRays = true; // Toggle to show/hide debug rays

    [SerializeField]
    private float rayDistance = 10f; // Distance to draw debug rays

    private void Start()
    {
        agent = GetComponent<DodgeBallAgent>();
        movement = GetComponent<AgentCubeMovement>();
        behaviorTree = ReadBehaviorTree();
    }

    public void ResetStates()
    {
        runningState.Reset();
        turningState.Reset();
    }

    // Check if target is within the front angle (one-sided)
    private bool IsInFrontAngle(Transform target, float frontAngleDeg)
    {
        Vector3 directionToTarget = target.position - transform.position;
        float angleToTarget = Mathf.Abs(Vector3.Angle(transform.forward, directionToTarget));
        return angleToTarget <= frontAngleDeg;
    }

    private void Update()
    {
        // Don't run behavior tree during countdown or when stunned
        if (Time.timeScale == 0 || agent.Stunned)
        {
            return;
        }

        // Update sensory information
        UpdateSensory();

        // Tick behavior tree
        if (behaviorTree != null)
        {
            actions = behaviorTree.Tick(sensory);
        }

        // Execute actions
        ExecuteActions();
    }

    private void UpdateSensory()
    {
        ResetSensoryData();
        PopulateInsights();
        UpdateSensoryState();
    }

    private void ResetSensoryData()
    {
        // Reset insights (for InVisual)
        sensory.Enemy = null;
        sensory.Ally = null;
        sensory.BallDropped = null;
        sensory.BallThrownByEnemy = null;
        sensory.Wall = null;
        sensory.Obstacle = null;

        // Reset AtFront fields
        sensory.AtFrontEnemy = null;
        sensory.AtFrontAlly = null;
        sensory.AtFrontBallDropped = null;
        sensory.AtFrontBallThrownByEnemy = null;
        sensory.AtFrontWall = null;
        sensory.AtFrontObstacle = null;
    }

    private void UpdateSensoryState()
    {
        sensory.ballsHolding = agent.currentNumberOfBalls;
        sensory.running = runningState.IsActive;
        sensory.turning = turningState.IsActive;
        sensory.runningElapsedTime = runningState.IsActive
            ? runningState.ElapsedTime
            : (float?)null;
        sensory.turningElapsedTime = turningState.IsActive
            ? turningState.ElapsedTime
            : (float?)null;
        sensory.turningTotalDegrees = turningState.IsActive
            ? turningState.TotalDegrees
            : (float?)null;
    }

    private void PopulateInsights()
    {
        ProcessAgents();
        ProcessDodgeBalls();
        ProcessWalls();
        ProcessObstacles();
    }

    private void ProcessAgents()
    {
        float nearestEnemyDist = float.MaxValue;
        float nearestAllyDist = float.MaxValue;
        float nearestFrontEnemyDist = float.MaxValue;
        float nearestFrontAllyDist = float.MaxValue;

        DodgeBallAgent[] allAgents = FindObjectsOfType<DodgeBallAgent>();
        foreach (DodgeBallAgent otherAgent in allAgents)
        {
            if (otherAgent == agent || !otherAgent.gameObject.activeInHierarchy)
                continue;

            if (!IsInFieldOfView(otherAgent.transform, out float distance))
                continue;

            bool isEnemy = otherAgent.teamID != agent.teamID;
            bool isInFront = IsInFrontAngle(
                otherAgent.transform,
                DodgeballBT.Nodes.AtFront.FRONT_ANGLE_THRESHOLD
            );

            if (isEnemy)
            {
                UpdateNearestObject(
                    distance,
                    ref nearestEnemyDist,
                    ref sensory.Enemy,
                    otherAgent.transform
                );
                if (isInFront)
                    UpdateNearestObject(
                        distance,
                        ref nearestFrontEnemyDist,
                        ref sensory.AtFrontEnemy,
                        otherAgent.transform
                    );
            }
            else
            {
                UpdateNearestObject(
                    distance,
                    ref nearestAllyDist,
                    ref sensory.Ally,
                    otherAgent.transform
                );
                if (isInFront)
                    UpdateNearestObject(
                        distance,
                        ref nearestFrontAllyDist,
                        ref sensory.AtFrontAlly,
                        otherAgent.transform
                    );
            }
        }
    }

    private void ProcessDodgeBalls()
    {
        float nearestBallDroppedDist = float.MaxValue;
        float nearestBallThrownDist = float.MaxValue;
        float nearestFrontBallDroppedDist = float.MaxValue;
        float nearestFrontBallThrownDist = float.MaxValue;

        DodgeBall[] allBalls = FindObjectsOfType<DodgeBall>();
        foreach (DodgeBall ball in allBalls)
        {
            if (!IsInFieldOfView(ball.transform, out float distance))
                continue;

            bool isInFront = IsInFrontAngle(
                ball.transform,
                DodgeballBT.Nodes.AtFront.FRONT_ANGLE_THRESHOLD
            );

            if (ball.inPlay && ball.TeamToIgnore != agent.teamID)
            {
                ProcessThrownBall(
                    ball,
                    distance,
                    ref nearestBallThrownDist,
                    ref nearestFrontBallThrownDist,
                    isInFront
                );
            }
            else if (!ball.inPlay)
            {
                UpdateNearestObject(
                    distance,
                    ref nearestBallDroppedDist,
                    ref sensory.BallDropped,
                    ball.transform
                );
                if (isInFront)
                    UpdateNearestObject(
                        distance,
                        ref nearestFrontBallDroppedDist,
                        ref sensory.AtFrontBallDropped,
                        ball.transform
                    );
            }
        }
    }

    private void ProcessThrownBall(
        DodgeBall ball,
        float distance,
        ref float nearestDist,
        ref float nearestFrontDist,
        bool isInFront
    )
    {
        if (distance < nearestDist)
        {
            nearestDist = distance;
            Rigidbody ballRb = ball.GetComponent<Rigidbody>();
            Vector3 ballVelocity = ballRb != null ? ballRb.velocity.normalized : Vector3.zero;
            sensory.BallThrownByEnemy = CreateObjectInformationWithFront(
                ball.transform,
                ballVelocity
            );
        }

        if (isInFront && distance < nearestFrontDist)
        {
            nearestFrontDist = distance;
            Rigidbody ballRb = ball.GetComponent<Rigidbody>();
            Vector3 ballVelocity = ballRb != null ? ballRb.velocity.normalized : Vector3.zero;
            sensory.AtFrontBallThrownByEnemy = CreateObjectInformationWithFront(
                ball.transform,
                ballVelocity
            );
        }
    }

    private void ProcessWalls()
    {
        ProcessGameObjectsByTag("wall", ref sensory.Wall, ref sensory.AtFrontWall);
    }

    private void ProcessObstacles()
    {
        ProcessGameObjectsByTag("bush", ref sensory.Obstacle, ref sensory.AtFrontObstacle);
    }

    private void ProcessGameObjectsByTag(
        string tag,
        ref ObjectInformation? sensoryField,
        ref ObjectInformation? atFrontField
    )
    {
        float nearestDist = float.MaxValue;
        float nearestFrontDist = float.MaxValue;

        GameObject[] objects = GameObject.FindGameObjectsWithTag(tag);
        foreach (GameObject obj in objects)
        {
            if (!IsInFieldOfView(obj.transform, out float distance))
                continue;

            UpdateNearestObject(distance, ref nearestDist, ref sensoryField, obj.transform);

            if (IsInFrontAngle(obj.transform, DodgeballBT.Nodes.AtFront.FRONT_ANGLE_THRESHOLD))
                UpdateNearestObject(
                    distance,
                    ref nearestFrontDist,
                    ref atFrontField,
                    obj.transform
                );
        }
    }

    private void UpdateNearestObject(
        float distance,
        ref float nearestDist,
        ref ObjectInformation? sensoryField,
        Transform objTransform
    )
    {
        if (distance < nearestDist)
        {
            nearestDist = distance;
            sensoryField = CreateObjectInformation(objTransform);
        }
    }

    private bool IsInFieldOfView(Transform target, out float distance)
    {
        Vector3 directionToTarget = target.position - transform.position;
        distance = directionToTarget.magnitude;

        // Check if within field of view angle
        float angleToTarget = Mathf.Abs(Vector3.Angle(transform.forward, directionToTarget));
        if (angleToTarget > fieldOfViewAngle)
            return false;

        return true;
    }

    private ObjectInformation CreateObjectInformation(Transform objTransform)
    {
        // Calculate relative position (translated so agent's position is origin and rotated)
        Vector3 relativePos = transform.InverseTransformPoint(objTransform.position);

        // Calculate relative front direction (rotated)
        Vector3 relativeFront = transform.InverseTransformDirection(objTransform.forward);

        return new ObjectInformation(new Vector3D(relativeFront), new Vector3D(relativePos));
    }

    private ObjectInformation CreateObjectInformationWithFront(
        Transform objTransform,
        Vector3 frontDirection
    )
    {
        // Calculate relative position
        Vector3 relativePos = transform.InverseTransformPoint(objTransform.position);

        // Calculate relative front direction (use provided direction)
        Vector3 relativeFront = transform.InverseTransformDirection(frontDirection);

        return new ObjectInformation(new Vector3D(relativeFront), new Vector3D(relativePos));
    }

    private void ExecuteActions()
    {
        HandleActionCommands();
        UpdateContinuousActions();
        ApplyContinuousActions();
    }

    private void HandleActionCommands()
    {
        if (actions.startRunning)
        {
            StartRunning();
            actions.startRunning = false;
        }

        if (actions.endRunning)
        {
            runningState.Reset();
            actions.endRunning = false;
        }

        if (actions.startTurning)
        {
            StartTurning();
            actions.startTurning = false;
        }

        if (actions.endTurning)
        {
            turningState.Reset();
            actions.endTurning = false;
        }

        if (actions.throwBall)
        {
            agent.ThrowTheBall();
            actions.throwBall = false;
        }
    }

    private void StartRunning()
    {
        runningState.IsActive = true;
        runningState.Angle = actions.startRunningAngle;
        runningState.ElapsedTime = 0f;
        runningState.Duration = actions.startRunningDuration;
        runningState.Target = actions.runningTarget;
        runningState.OffsetDegree = actions.runningOffsetDegree;
    }

    private void StartTurning()
    {
        turningState.IsActive = true;
        turningState.Speed = Mathf.Clamp(actions.startTurningSpeed, -maxTurnSpeed, maxTurnSpeed);
        turningState.ElapsedTime = 0f;
        turningState.TotalDegrees = 0f;
        turningState.Duration = actions.startTurningDuration;
        turningState.MaxDegree = actions.startTurningMaxDegree;
        turningState.Target = actions.turningTarget;
    }

    private void UpdateContinuousActions()
    {
        if (runningState.IsActive)
        {
            UpdateRunningState();
        }

        if (turningState.IsActive)
        {
            UpdateTurningState();
        }
    }

    private void UpdateRunningState()
    {
        runningState.ElapsedTime += Time.deltaTime;

        if (
            runningState.Duration.HasValue
            && runningState.ElapsedTime >= runningState.Duration.Value
        )
        {
            runningState.Reset();
        }
    }

    private void UpdateTurningState()
    {
        float deltaRotation = turningState.Speed * Time.deltaTime;
        turningState.ElapsedTime += Time.deltaTime;
        turningState.TotalDegrees += Mathf.Abs(deltaRotation);

        bool durationReached =
            turningState.Duration.HasValue
            && turningState.ElapsedTime >= turningState.Duration.Value;
        bool maxDegreeReached =
            turningState.MaxDegree.HasValue
            && turningState.TotalDegrees >= turningState.MaxDegree.Value;

        if (durationReached || maxDegreeReached)
        {
            turningState.Reset();
        }
    }

    private void ApplyContinuousActions()
    {
        if (runningState.IsActive)
        {
            ApplyRunning();
        }

        if (turningState.IsActive)
        {
            ApplyTurning();
        }
    }

    private void ApplyRunning()
    {
        if (!string.IsNullOrEmpty(runningState.Target))
        {
            UpdateRunningAngleTowardsTarget();
        }

        Vector3 runDirection = Quaternion.Euler(0, runningState.Angle, 0) * transform.forward;
        movement.RunOnGround(runDirection);
    }

    private void UpdateRunningAngleTowardsTarget()
    {
        ObjectInformation? targetObj = GetTargetObject(sensory, runningState.Target);
        if (targetObj.HasValue)
        {
            Vector3 targetPos = targetObj.Value.position.ToVector3();
            float angleToTarget = Mathf.Atan2(targetPos.x, targetPos.z) * Mathf.Rad2Deg;
            runningState.Angle = angleToTarget + runningState.OffsetDegree;
        }
    }

    private void ApplyTurning()
    {
        if (string.IsNullOrEmpty(turningState.Target))
        {
            float rotateDegree = turningState.Speed * Time.deltaTime;
            transform.Rotate(0, rotateDegree, 0);
        }
        else
        {
            ApplyTurningTowardsTarget();
        }
    }

    private void ApplyTurningTowardsTarget()
    {
        ObjectInformation? targetObj = GetTargetObject(sensory, turningState.Target);
        if (targetObj.HasValue)
        {
            Vector3 targetPos = targetObj.Value.position.ToVector3();
            float angleToTarget = Mathf.Atan2(targetPos.x, targetPos.z) * Mathf.Rad2Deg;
            float rotateDegree =
                Mathf.Min(Mathf.Abs(angleToTarget), Mathf.Abs(turningState.Speed * Time.deltaTime))
                * Mathf.Sign(angleToTarget);

            transform.Rotate(0, rotateDegree, 0);
        }
    }

    private ObjectInformation? GetTargetObject(Sensory input, string targetName)
    {
        switch (targetName)
        {
            case "Enemy":
                return input.Enemy;
            case "Ally":
                return input.Ally;
            case "BallDropped":
                return input.BallDropped;
            case "BallThrownByEnemy":
                return input.BallThrownByEnemy;
            case "Wall":
                return input.Wall;
            case "Obstacle":
                return input.Obstacle;
            default:
                return null;
        }
    }

    public BehaviorTree<Sensory, Actions> ReadBehaviorTree()
    {
        if (btFile == null)
        {
            Debug.LogError("Behavior Tree file is not assigned.");
            return null;
        }
        Node<Sensory, Actions> rootNode = Deserializer<Sensory, Actions>.ReadNodeJson(btFile.text);
        behaviorTree = new BehaviorTree<Sensory, Actions>("DodgeballBT", rootNode);

        return behaviorTree;
    }

    private void OnDrawGizmos()
    {
        if (!showDebugRays)
            return;

        // Draw InVisual range (fieldOfViewAngle: ±60 degrees)
        DrawFieldOfViewRays(fieldOfViewAngle, Color.green);

        // Draw AtFront range (FRONT_ANGLE_THRESHOLD: ±10 degrees)
        DrawFieldOfViewRays(DodgeballBT.Nodes.AtFront.FRONT_ANGLE_THRESHOLD, Color.red);
    }

    private void DrawFieldOfViewRays(float angle, Color color)
    {
        // Draw left boundary ray
        Vector3 leftBoundary = Quaternion.Euler(0, -angle, 0) * transform.forward;
        Debug.DrawRay(transform.position, leftBoundary * rayDistance, color);

        // Draw right boundary ray
        Vector3 rightBoundary = Quaternion.Euler(0, angle, 0) * transform.forward;
        Debug.DrawRay(transform.position, rightBoundary * rayDistance, color);
    }
}
