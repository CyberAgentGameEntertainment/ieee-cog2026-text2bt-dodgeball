/// <summary>
/// Actions that the agent can perform
/// </summary>
public struct Actions
{
    /// <summary>
    /// Start running towards the specified angle (degrees).
    /// Positive angle is anti-clockwise
    /// </summary>
    public bool startRunning;
    public float startRunningAngle;

    /// <summary>
    /// Duration for running in seconds.
    /// null means run indefinitely until stopped.
    /// </summary>
    public float? startRunningDuration;

    /// <summary>
    /// Target object to run towards.
    /// If set, angle will be calculated automatically each frame.
    /// </summary>
    public string runningTarget;

    /// <summary>
    /// Offset angle (degrees) when running towards a target.
    /// </summary>
    public float runningOffsetDegree;

    /// <summary>
    /// Stop running
    /// </summary>
    public bool endRunning;

    /// <summary>
    /// Start turning at the specified angle speed (degrees/second).
    /// Positive speed is anti-clockwise
    /// </summary>
    public bool startTurning;
    public float startTurningSpeed;

    /// <summary>
    /// Duration for turning in seconds.
    /// null means turn indefinitely until stopped.
    /// </summary>
    public float? startTurningDuration;

    /// <summary>
    /// Maximum rotation amount in degrees.
    /// null means no limit on rotation.
    /// </summary>
    public float? startTurningMaxDegree;

    /// <summary>
    /// Target object to turn towards.
    /// If set, turning speed and max degree will be calculated automatically each frame.
    /// </summary>
    public string turningTarget;

    /// <summary>
    /// Stop turning
    /// </summary>
    public bool endTurning;

    /// <summary>
    /// Throw the ball
    /// </summary>
    public bool throwBall;

    /// <summary>
    /// Reset all actions to default (false/0)
    /// </summary>
    public void Reset()
    {
        startRunning = false;
        startRunningAngle = 0f;
        startRunningDuration = null;
        runningTarget = null;
        runningOffsetDegree = 0f;
        endRunning = false;
        startTurning = false;
        startTurningSpeed = 0f;
        startTurningDuration = null;
        startTurningMaxDegree = null;
        turningTarget = null;
        endTurning = false;
        throwBall = false;
    }
}
