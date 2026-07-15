using SimpleUnityBehaviorTree.Nodes;
using SimpleUnityBehaviorTree.Serializations;

namespace DodgeballBT.Nodes
{
    /// <summary>
    /// Start running towards the specified angle (degrees) from the player's forward direction.
    /// Positive angle is anti-clockwise.
    /// </summary>
    [SerializableNode("StartRun")]
    public class StartRun : Action<Sensory, Actions>
    {
        [ConstructorParameter("degree")]
        public float degree { get; private set; }

        [ConstructorParameter("seconds")]
        public float? seconds { get; private set; }

        public StartRun(float degree, float? seconds)
            : base("StartRun")
        {
            this.degree = degree;
            this.seconds = seconds;
        }

        protected override Actions TakeAction(Sensory input)
        {
            UnityEngine.Debug.Log("[BT] StartRun");
            Actions action = new Actions();
            action.Reset();
            action.startRunning = true;
            action.startRunningAngle = degree;
            action.startRunningDuration = seconds;
            return action;
        }
    }
}
