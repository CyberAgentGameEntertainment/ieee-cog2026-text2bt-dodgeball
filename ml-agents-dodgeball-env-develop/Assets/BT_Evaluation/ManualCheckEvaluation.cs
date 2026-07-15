using System.Collections.Generic;
using UnityEngine;

public class ManualCheckEvaluation : MonoBehaviour
{
    public AgentBt agentBt;
    public DodgeBallGameController gameController;
    public List<TextAsset> behaviorTreeFiles;

    private int currentTreeIndex = 0;
    private bool gameInProgress = true;
    private bool spaceKeyPressed = false;

    void Start()
    {
        // Subscribe to game end event
        if (gameController != null)
        {
            gameController.OnGameEnded += OnGameEnded;
        }

        // Load the first behavior tree
        if (behaviorTreeFiles.Count > 0)
        {
            LoadBehaviorTree(currentTreeIndex);
        }
        else
        {
            Debug.LogWarning("No behavior tree files assigned to ManualCheckEvaluation");
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

    void Update()
    {
        // Check for space key press
        if (Input.GetKeyDown(KeyCode.Space))
        {
            spaceKeyPressed = true;
            Debug.Log("Space key pressed. Will change behavior tree after current game ends.");
        }

        // If space was pressed and game is not in progress, change the tree
        if (spaceKeyPressed && !gameInProgress)
        {
            ChangeToNextTree();
            spaceKeyPressed = false;
        }
    }

    void OnGameEnded(int winningTeam)
    {
        gameInProgress = false;
        Debug.Log($"Game ended. Team {winningTeam} won. Ready for next behavior tree change.");
    }

    void ChangeToNextTree()
    {
        currentTreeIndex++;

        if (currentTreeIndex >= behaviorTreeFiles.Count)
        {
            currentTreeIndex = 0; // Loop back to the first tree
            Debug.Log("Reached end of behavior tree list. Looping back to first tree.");
        }

        LoadBehaviorTree(currentTreeIndex);
        gameInProgress = true; // New game will start after tree change
    }

    void LoadBehaviorTree(int index)
    {
        if (index < 0 || index >= behaviorTreeFiles.Count)
        {
            Debug.LogError($"Invalid behavior tree index: {index}");
            return;
        }

        TextAsset btFile = behaviorTreeFiles[index];
        agentBt.btFile = btFile;
        agentBt.ReadBehaviorTree();

        Debug.Log(
            $"=== Loaded behavior tree [{index + 1}/{behaviorTreeFiles.Count}]: {btFile.name} ==="
        );
    }
}
