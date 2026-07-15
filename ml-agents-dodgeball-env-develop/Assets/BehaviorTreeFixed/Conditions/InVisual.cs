using SimpleUnityBehaviorTree;
using SimpleUnityBehaviorTree.Nodes;
using SimpleUnityBehaviorTree.Serializations;
using UnityEngine;

namespace DodgeballBT.Nodes
{
    /// <summary>
    /// Check if the target exists in the visual field (-60 to +60 degrees).
    /// target: "Enemy", "Ally", "BallDropped", "BallThrownByEnemy", "Wall", "Obstacle"
    /// </summary>
    [SerializableEvaluator("InVisual")]
    public class InVisual : ConditionEvaluator<Sensory>
    {
        [ConstructorParameter("target")]
        public string target { get; private set; }

        [ConstructorParameter("distance")]
        public float? distance { get; private set; }

        /// <summary>
        /// Angle threshold (degrees) for visual field checks (one-sided).
        /// Adjust this value to change the agent's visual cone per side (total FOV is twice this value).
        /// </summary>
        public static float VISUAL_ANGLE_THRESHOLD = 60f; // degrees (one-sided)

        public InVisual(string target, float? distance = null)
            : base("InVisual")
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

            bool angleCheck = Mathf.Abs(angleToTarget) <= VISUAL_ANGLE_THRESHOLD;

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
    }
}
