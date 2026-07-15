using SimpleUnityBehaviorTree.Nodes;
using SimpleUnityBehaviorTree.Serializations;

namespace DodgeballBT.Nodes
{
    /// <summary>
    /// Start turning in the specified direction.
    /// </summary>
    [SerializableNode("StartTurn")]
    public class StartTurn : Action<Sensory, Actions>
    {
        [ConstructorParameter("direction")]
        public string direction { get; private set; }

        [ConstructorParameter("seconds")]
        public float? seconds { get; private set; }

        [ConstructorParameter("maxDegree")]
        public float? maxDegree { get; private set; }

        public StartTurn(string direction, float? seconds, float? maxDegree)
            : base("StartTurn")
        {
            this.direction = direction;
            this.seconds = seconds;
            this.maxDegree = maxDegree;
        }

        protected override Actions TakeAction(Sensory input)
        {
            UnityEngine.Debug.Log($"[BT] StartTurn {direction}");
            Actions action = new Actions();
            action.Reset();
            action.startTurning = true;
            // "left" is anti-clockwise (positive), "right" is clockwise (negative)
            action.startTurningSpeed = direction == "left" ? 360f : -360f;
            action.startTurningDuration = seconds;
            action.startTurningMaxDegree = maxDegree;
            return action;
        }
    }
}
