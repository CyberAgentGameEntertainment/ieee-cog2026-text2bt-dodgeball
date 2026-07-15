using SimpleUnityBehaviorTree.Nodes;
using SimpleUnityBehaviorTree.Serializations;
using UnityEngine;

namespace DodgeballBT.Nodes
{
    /// <summary>
    /// Start running towards the target object with an offset angle.
    /// target: "Enemy", "Ally", "BallDropped", "BallThrownByEnemy", "Wall", "Obstacle"
    /// degree: offset angle from the target direction (anti-clockwise)
    /// </summary>
    [SerializableNode("StartRunTowards")]
    public class StartRunTowards : Action<Sensory, Actions>
    {
        [ConstructorParameter("target")]
        public string target { get; private set; }

        [ConstructorParameter("degree")]
        public float degree { get; private set; }

        [ConstructorParameter("seconds")]
        public float? seconds { get; private set; }

        public StartRunTowards(string target, float degree, float? seconds)
            : base("StartRunTowards")
        {
            this.target = target;
            this.degree = degree;
            this.seconds = seconds;
        }

        protected override Actions TakeAction(Sensory input)
        {
            UnityEngine.Debug.Log($"[BT] StartRunTowards {target} with offset {degree} degrees");
            Actions action = new Actions();
            action.Reset();

            action.startRunning = true;
            action.runningTarget = target;
            action.runningOffsetDegree = degree;
            action.startRunningDuration = seconds;

            return action;
        }
    }
}
