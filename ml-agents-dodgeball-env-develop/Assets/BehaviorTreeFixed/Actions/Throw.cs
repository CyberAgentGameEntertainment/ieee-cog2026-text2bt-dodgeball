using SimpleUnityBehaviorTree.Nodes;
using SimpleUnityBehaviorTree.Serializations;

namespace DodgeballBT.Nodes
{
    /// <summary>
    /// Throw the ball
    /// </summary>
    [SerializableNode("Throw")]
    public class Throw : Action<Sensory, Actions>
    {
        public Throw()
            : base("Throw") { }

        protected override Actions TakeAction(Sensory input)
        {
            UnityEngine.Debug.Log("[BT] Throw");
            Actions action = new Actions();
            action.Reset();
            action.throwBall = true;
            return action;
        }
    }
}
