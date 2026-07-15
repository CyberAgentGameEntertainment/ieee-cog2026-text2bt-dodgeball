using SimpleUnityBehaviorTree.Nodes;
using SimpleUnityBehaviorTree.Serializations;

namespace DodgeballBT.Nodes
{
    /// <summary>
    /// Do nothing - return default action
    /// </summary>
    [SerializableNode("DoNothing")]
    public class DoNothing : Action<Sensory, Actions>
    {
        public DoNothing()
            : base("DoNothing") { }

        protected override Actions TakeAction(Sensory input)
        {
            UnityEngine.Debug.Log("[BT] DoNothing");
            Actions action = new Actions();
            action.Reset();
            return action;
        }
    }
}
