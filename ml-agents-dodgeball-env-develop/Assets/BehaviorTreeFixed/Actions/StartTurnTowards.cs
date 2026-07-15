using SimpleUnityBehaviorTree.Nodes;
using SimpleUnityBehaviorTree.Serializations;
using UnityEngine;

namespace DodgeballBT.Nodes
{
    /// <summary>
    /// Start turning (continuous) towards the target object.
    /// target: "Enemy", "Ally", "BallDropped", "BallThrownByEnemy", "Wall", "Obstacle"
    /// seconds: duration to turn (null = turn until facing target)
    /// </summary>
    [SerializableNode("StartTurnTowards")]
    public class StartTurnTowards : Action<Sensory, Actions>
    {
        [ConstructorParameter("target")]
        public string target { get; private set; }

        [ConstructorParameter("seconds")]
        public float? seconds { get; private set; }

        public StartTurnTowards(string target, float? seconds)
            : base("StartTurnTowards")
        {
            this.target = target;
            this.seconds = seconds;
        }

        protected override Actions TakeAction(Sensory input)
        {
            UnityEngine.Debug.Log($"[BT] StartTurnTowards {target}");
            Actions action = new Actions();
            action.Reset();

            action.startTurning = true;
            action.turningTarget = target;
            action.startTurningDuration = seconds;
            action.startTurningSpeed = 360f;

            return action;
        }
    }
}
