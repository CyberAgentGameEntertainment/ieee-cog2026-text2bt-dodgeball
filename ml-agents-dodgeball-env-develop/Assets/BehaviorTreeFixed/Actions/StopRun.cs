using SimpleUnityBehaviorTree.Nodes;
using SimpleUnityBehaviorTree.Serializations;

namespace DodgeballBT.Nodes
{
    /// <summary>
    /// Stop running
    /// </summary>
    [SerializableNode("StopRun")]
    public class StopRun : Action<Sensory, Actions>
    {
        public StopRun()
            : base("StopRun") { }

        protected override Actions TakeAction(Sensory input)
        {
            UnityEngine.Debug.Log("[BT] StopRun");
            Actions action = new Actions();
            action.Reset();
            action.endRunning = true;
            return action;
        }
    }
}
