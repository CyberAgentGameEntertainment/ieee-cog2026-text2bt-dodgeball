using UnityEngine;
using UnityEditor;

[CustomEditor(typeof(AgentBt))]
public class AgentBtEditor : Editor
{
    public override void OnInspectorGUI()
    {
        // Draw the default inspector
        DrawDefaultInspector();

        // Add some space
        EditorGUILayout.Space();

        // Get reference to the AgentBt component
        AgentBt agentBt = (AgentBt)target;

        // Create the button
        if (GUILayout.Button("ReadBehaviorTree"))
        {
            // Execute ReadBehaviorTree
            agentBt.ReadBehaviorTree();
            Debug.Log("ReadBehaviorTree executed.");
        }
    }
}
