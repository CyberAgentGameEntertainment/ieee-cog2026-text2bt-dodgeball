using SimpleUnityBehaviorTree;
using SimpleUnityBehaviorTree.Nodes;
using SimpleUnityBehaviorTree.Serializations;

namespace DodgeballBT.Nodes
{
    /// <summary>
    /// Check if the agent is currently running.
    /// </summary>
    [SerializableEvaluator("IfRunning")]
    public class IfRunning : ConditionEvaluator<Sensory>
    {
        public IfRunning()
            : base("IfRunning") { }

        public override bool Evaluate(Sensory input, BtInformation btInfo)
        {
            return input.running;
        }
    }
}
