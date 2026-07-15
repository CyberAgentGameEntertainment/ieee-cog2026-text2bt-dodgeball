using SimpleUnityBehaviorTree.Nodes;
using SimpleUnityBehaviorTree.Serializations;

namespace DodgeballBT.Nodes
{
    /// <summary>
    /// Stop turning
    /// </summary>
    [SerializableNode("StopTurn")]
    public class StopTurn : Action<Sensory, Actions>
    {
        public StopTurn()
            : base("StopTurn") { }

        protected override Actions TakeAction(Sensory input)
        {
            UnityEngine.Debug.Log("[BT] StopTurn");
            Actions action = new Actions();
            action.Reset();
            action.endTurning = true;
            return action;
        }
    }
}
