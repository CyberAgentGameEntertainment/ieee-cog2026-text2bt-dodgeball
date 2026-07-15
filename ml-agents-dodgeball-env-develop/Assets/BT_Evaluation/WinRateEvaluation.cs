using System.Collections.Generic;
using UnityEngine;

public class WinRateEvaluation : MonoBehaviour
{
    public AgentBt agentBt;
    public DodgeBallGameController gameController;
    public List<TextAsset> behaviorTreeFiles;
    public int gamesPerTree = 10;
    public Dictionary<string, float> winRates = new Dictionary<string, float>();

    private int currentTreeIndex = 0;
    private int currentGameCount = 0;
    private int currentWinCount = 0;
    private int agentTeamId;
    private bool evaluationComplete = false;

    void Start()
    {
        // Get the team ID of the agent we're evaluating
        DodgeBallAgent agent = agentBt.GetComponent<DodgeBallAgent>();
        if (agent != null)
        {
            agentTeamId = agent.teamID;
            Debug.Log($"Evaluating agent on Team {agentTeamId}");
        }

        // Subscribe to game end event
        if (gameController != null)
        {
            gameController.OnGameEnded += OnGameEnded;
        }

        // Start first evaluation
        if (behaviorTreeFiles.Count > 0)
        {
            StartNextTree();
        }
    }

    void OnDestroy()
    {
        // Unsubscribe from event
        if (gameController != null)
        {
            gameController.OnGameEnded -= OnGameEnded;
        }
    }

    void StartNextTree()
    {
        if (currentTreeIndex >= behaviorTreeFiles.Count)
        {
            // All trees evaluated
            PrintResults();
            evaluationComplete = true;

            Debug.Log("Evaluation complete. Quitting application...");
            Invoke("QuitApplication", 2.0f);
            return;
        }

        TextAsset btFile = behaviorTreeFiles[currentTreeIndex];
        string treeName = btFile.name;

        Debug.Log(
            $"\n=== Starting evaluation for BT: {treeName} ({currentTreeIndex + 1}/{behaviorTreeFiles.Count}) ==="
        );

        // Set the behavior tree for the agent
        SetBehaviorTree(btFile);

        // Reset counters for this tree
        currentGameCount = 0;
        currentWinCount = 0;
    }

    void OnGameEnded(int winningTeam)
    {
        if (evaluationComplete)
            return;

        currentGameCount++;

        // Record the result
        if (winningTeam == agentTeamId)
        {
            currentWinCount++;
            Debug.Log(
                $"  -> Agent WON! (Game {currentGameCount}/{gamesPerTree}, Total wins: {currentWinCount})"
            );
        }
        else
        {
            Debug.Log(
                $"  -> Agent LOST (Game {currentGameCount}/{gamesPerTree}, Total wins: {currentWinCount})"
            );
        }

        // Check if we've completed all games for this tree
        if (currentGameCount >= gamesPerTree)
        {
            // Calculate and store win rate for this behavior tree
            string treeName = behaviorTreeFiles[currentTreeIndex].name;
            float winRate = (float)currentWinCount / gamesPerTree;
            winRates[treeName] = winRate;

            Debug.Log(
                $"=== Completed evaluation for {treeName}: {winRate * 100:F1}% win rate ({currentWinCount}/{gamesPerTree} wins) ===\n"
            );

            // Move to next tree
            currentTreeIndex++;
            StartNextTree();
        }
    }

    void QuitApplication()
    {
#if UNITY_EDITOR
        UnityEditor.EditorApplication.isPlaying = false;
#else
        Application.Quit();
#endif
    }

    void SetBehaviorTree(TextAsset btFile)
    {
        agentBt.btFile = btFile;
        agentBt.ReadBehaviorTree();
        Debug.Log($"Loaded behavior tree: {btFile.name}");
    }

    void PrintResults()
    {
        Debug.Log("\n" + new string('=', 50));
        Debug.Log("FINAL EVALUATION RESULTS");
        Debug.Log(new string('=', 50));

        foreach (var kvp in winRates)
        {
            Debug.Log(
                $"{kvp.Key}: {kvp.Value * 100:F1}% win rate ({(int)(kvp.Value * gamesPerTree)}/{gamesPerTree} wins)"
            );
        }

        Debug.Log(new string('=', 50) + "\n");
    }
}
