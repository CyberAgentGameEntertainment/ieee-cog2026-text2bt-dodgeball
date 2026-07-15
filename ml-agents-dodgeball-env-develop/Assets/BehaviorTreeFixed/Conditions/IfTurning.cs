using SimpleUnityBehaviorTree;
using SimpleUnityBehaviorTree.Nodes;
using SimpleUnityBehaviorTree.Serializations;

namespace DodgeballBT.Nodes
{
    /// <summary>
    /// Check if the agent is currently turning.
    /// </summary>
    [SerializableEvaluator("IfTurning")]
    public class IfTurning : ConditionEvaluator<Sensory>
    {
        public IfTurning()
            : base("IfTurning") { }

        public override bool Evaluate(Sensory input, BtInformation btInfo)
        {
            return input.turning;
        }
    }
}
