using SimpleUnityBehaviorTree;
using SimpleUnityBehaviorTree.Nodes;
using SimpleUnityBehaviorTree.Serializations;

namespace DodgeballBT.Nodes
{
    /// <summary>
    /// Check if the agent is holding a specified number or more balls.
    /// </summary>
    [SerializableEvaluator("BallsMoreThanOrEquals")]
    public class BallsMoreThanOrEquals : ConditionEvaluator<Sensory>
    {
        [ConstructorParameter("number")]
        public int number { get; private set; }

        public BallsMoreThanOrEquals(int number)
            : base("BallsMoreThanOrEquals")
        {
            this.number = number;
        }

        public override bool Evaluate(Sensory input, BtInformation btInfo)
        {
            return input.ballsHolding >= number;
        }
    }
}
