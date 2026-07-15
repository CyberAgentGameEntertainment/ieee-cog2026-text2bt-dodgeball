using SimpleUnityBehaviorTree;
using SimpleUnityBehaviorTree.Nodes;
using SimpleUnityBehaviorTree.Serializations;
using UnityEngine;

namespace DodgeballBT.Nodes
{
    /// <summary>
    /// Check if an enemy ball is incoming towards the agent.
    /// The ball must be in the visual field (-60 to +60 degrees) and
    /// heading towards the agent (within 10 degrees deviation).
    /// </summary>
    [SerializableEvaluator("EnemyBallIncoming")]
    public class EnemyBallIncoming : ConditionEvaluator<Sensory>
    {
        private const float VISUAL_ANGLE_THRESHOLD = 60f; // degrees
        private const float HEADING_ANGLE_THRESHOLD = 10f; // degrees

        public EnemyBallIncoming()
            : base("EnemyBallIncoming") { }

        public override bool Evaluate(Sensory input, BtInformation btInfo)
        {
            if (!input.BallThrownByEnemy.HasValue)
                return false;

            ObjectInformation ball = input.BallThrownByEnemy.Value;

            // Check if ball is in visual field
            Vector3 ballPos = ball.position.ToVector3();
            float angleToBall = Mathf.Atan2(ballPos.x, ballPos.z) * Mathf.Rad2Deg;

            if (Mathf.Abs(angleToBall) > VISUAL_ANGLE_THRESHOLD)
                return false;

            // Check if ball is heading towards the agent
            // The front vector represents the direction the ball is thrown
            Vector3 ballDirection = ball.front.ToVector3();

            // Calculate angle between ball's direction and direction from ball to agent
            Vector3 ballToAgent = -ballPos.normalized;
            float dotProduct = Vector3.Dot(ballDirection.normalized, ballToAgent);
            float headingAngle = Mathf.Acos(dotProduct) * Mathf.Rad2Deg;

            return headingAngle <= HEADING_ANGLE_THRESHOLD;
        }
    }
}
