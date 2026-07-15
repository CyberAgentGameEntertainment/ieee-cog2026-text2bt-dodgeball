using SimpleUnityBehaviorTree;
using SimpleUnityBehaviorTree.Nodes;
using SimpleUnityBehaviorTree.Serializations;
using UnityEngine;

namespace DodgeballBT.Nodes
{
    /// <summary>
    /// Check if the target is at the front (within a small angle threshold).
    /// target: "Enemy", "Ally", "BallDropped", "BallThrownByEnemy", "Wall", "Obstacle"
    /// </summary>
    [SerializableEvaluator("AtFront")]
    public class AtFront : ConditionEvaluator<Sensory>
    {
        [ConstructorParameter("target")]
        public string target { get; private set; }

        [ConstructorParameter("distance")]
        public float? distance { get; private set; }

        /// <summary>
        /// Angle threshold (degrees) for "at front" checks (one-sided).
        /// Adjust this value to change how narrow the "front" cone is.
        /// </summary>
        public static float FRONT_ANGLE_THRESHOLD = 10f; // degrees

        public AtFront(string target, float? distance = null)
            : base("AtFront")
        {
            this.target = target;
            this.distance = distance;
        }

        public override bool Evaluate(Sensory input, BtInformation btInfo)
        {
            ObjectInformation? targetObj = GetTargetObject(input, target);

            if (!targetObj.HasValue)
                return false;

            Vector3 targetPos = targetObj.Value.position.ToVector3();
            float angleToTarget = Mathf.Atan2(targetPos.x, targetPos.z) * Mathf.Rad2Deg;

            bool angleCheck = Mathf.Abs(angleToTarget) < FRONT_ANGLE_THRESHOLD;

            if (distance.HasValue)
            {
                float dist = targetPos.magnitude;
                return angleCheck && dist < distance.Value;
            }

            return angleCheck;
        }

        private ObjectInformation? GetTargetObject(Sensory input, string targetName)
        {
            switch (targetName)
            {
                case "Enemy":
                    return input.AtFrontEnemy;
                case "Ally":
                    return input.AtFrontAlly;
                case "BallDropped":
                    return input.AtFrontBallDropped;
                case "BallThrownByEnemy":
                    return input.AtFrontBallThrownByEnemy;
                case "Wall":
                    return input.AtFrontWall;
                case "Obstacle":
                    return input.AtFrontObstacle;
                default:
                    return null;
            }
        }
    }
}
