using UnityEngine;

/// <summary>
/// Vector struct for representing position and direction
/// </summary>
public struct Vector3D
{
    public float x;
    public float y;
    public float z;

    public Vector3D(float x, float y, float z)
    {
        this.x = x;
        this.y = y;
        this.z = z;
    }

    public Vector3D(Vector3 vector)
    {
        this.x = vector.x;
        this.y = vector.y;
        this.z = vector.z;
    }

    public Vector3 ToVector3()
    {
        return new Vector3(x, y, z);
    }
}

/// <summary>
/// Information about an object in the environment
/// </summary>
public struct ObjectInformation
{
    /// <summary>
    /// Front vector of the object in the player agent's local coordinate space
    /// </summary>
    public Vector3D front;

    /// <summary>
    /// Position vector of the object relative to the player agent's position and orientation
    /// </summary>
    public Vector3D position;

    public ObjectInformation(Vector3D front, Vector3D position)
    {
        this.front = front;
        this.position = position;
    }
}

/// <summary>
/// Sensory information for the agent
/// </summary>
public struct Sensory
{
    /// <summary>
    /// Holds ObjectInformation of the most near objects in sight (between -60 to +60 degrees from the agent).
    /// If none exists, the field is null.
    /// </summary>
    // For InVisual checks (per-side visual field)
    public ObjectInformation? Enemy;
    public ObjectInformation? Ally;
    public ObjectInformation? BallDropped;
    public ObjectInformation? BallThrownByEnemy;
    public ObjectInformation? Wall;
    public ObjectInformation? Obstacle;

    // AtFront fields (for FRONT_ANGLE_THRESHOLD checks per target)
    public ObjectInformation? AtFrontEnemy;
    public ObjectInformation? AtFrontAlly;
    public ObjectInformation? AtFrontBallDropped;
    public ObjectInformation? AtFrontBallThrownByEnemy;
    public ObjectInformation? AtFrontWall;
    public ObjectInformation? AtFrontObstacle;

    /// <summary>
    /// Integer of the balls the agent is holding now
    /// </summary>
    public int ballsHolding;

    /// <summary>
    /// Boolean of whether the agent is running
    /// </summary>
    public bool running;

    /// <summary>
    /// Boolean of whether the agent is turning
    /// </summary>
    public bool turning;

    /// <summary>
    /// Elapsed time (in seconds) since the agent started running.
    /// null if not running.
    /// </summary>
    public float? runningElapsedTime;

    /// <summary>
    /// Elapsed time (in seconds) since the agent started turning.
    /// null if not turning.
    /// </summary>
    public float? turningElapsedTime;

    /// <summary>
    /// Total rotation amount (in degrees) since the agent started turning.
    /// null if not turning.
    /// </summary>
    public float? turningTotalDegrees;
}
