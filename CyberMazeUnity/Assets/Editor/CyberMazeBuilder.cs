using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;

public class CyberMazeBuilder
{
    [MenuItem("Cyber Maze/Build Level 1")]
    public static void BuildLevel()
    {
        if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
            return;

        var root = new GameObject("CYBER FOREST LEVEL 1");

        Material floorMat = MakeMat("Forest Floor", new Color(0.12f, 0.18f, 0.14f));
        Material wallMat = MakeMat("Cyber Walls", new Color(0.08f, 0.16f, 0.22f));
        Material playerMat = MakeMat("Player", Color.cyan);
        Material keyMat = MakeMat("Golden Keys", Color.yellow);
        Material enemyMat = MakeMat("Enemy", Color.red);

        GameObject floor = GameObject.CreatePrimitive(PrimitiveType.Cube);
        floor.name = "Maze Floor";
        floor.transform.SetParent(root.transform);
        floor.transform.position = new Vector3(7, -0.5f, 7);
        floor.transform.localScale = new Vector3(16, 1, 16);
        floor.GetComponent<Renderer>().sharedMaterial = floorMat;

        string[] map =
        {
            "###############",
            "#P....#.......#",
            "#.##..#.###...#",
            "#....##...#...#",
            "###......##...#",
            "#......#......#",
            "#.####.#.###..#",
            "#....#.#......#",
            "#.K..#...K....#",
            "#.##...####...#",
            "#......#......#",
            "#.###..#.###..#",
            "#....E........#",
            "#.....K.......#",
            "###############"
        };

        for (int z = 0; z < map.Length; z++)
        {
            for (int x = 0; x < map[z].Length; x++)
            {
                char cell = map[z][x];

                if (cell == '#')
                {
                    GameObject wall = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    wall.name = "Cyber Wall";
                    wall.transform.SetParent(root.transform);
                    wall.transform.position = new Vector3(x, 1, z);
                    wall.transform.localScale = new Vector3(1, 2, 1);
                    wall.GetComponent<Renderer>().sharedMaterial = wallMat;
                }

                if (cell == 'P')
                {
                    GameObject player = GameObject.CreatePrimitive(PrimitiveType.Capsule);
                    player.name = "Player";
                    player.transform.SetParent(root.transform);
                    player.transform.position = new Vector3(x, 1, z);
                    player.GetComponent<Renderer>().sharedMaterial = playerMat;
                }

                if (cell == 'K')
                {
                    GameObject key = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                    key.name = "Golden Key";
                    key.transform.SetParent(root.transform);
                    key.transform.position = new Vector3(x, 0.8f, z);
                    key.transform.localScale = Vector3.one * 0.45f;
                    key.GetComponent<Renderer>().sharedMaterial = keyMat;
                }

                if (cell == 'E')
                {
                    GameObject enemy = GameObject.CreatePrimitive(PrimitiveType.Capsule);
                    enemy.name = "Forest Enemy";
                    enemy.transform.SetParent(root.transform);
                    enemy.transform.position = new Vector3(x, 1, z);
                    enemy.GetComponent<Renderer>().sharedMaterial = enemyMat;
                }
            }
        }

        GameObject lightObject = new GameObject("Forest Lighting");
        lightObject.transform.SetParent(root.transform);

        Light sun = lightObject.AddComponent<Light>();
        sun.type = LightType.Directional;
        sun.intensity = 1.2f;
        lightObject.transform.rotation = Quaternion.Euler(50, -30, 0);

        GameObject cameraObject = new GameObject("Player Camera");
        cameraObject.transform.position = new Vector3(7, 17, -5);
        cameraObject.transform.rotation = Quaternion.Euler(65, 0, 0);
        cameraObject.AddComponent<Camera>();

        Camera.main?.gameObject.SetActive(false);

        Selection.activeGameObject = root;

        EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
        EditorSceneManager.SaveScene(
            EditorSceneManager.GetActiveScene(),
            "Assets/Scenes/CyberForest_Level1.unity"
        );

        Debug.Log("Cyber Forest Level 1 created successfully!");
    }

    static Material MakeMat(string name, Color color)
    {
        Shader shader = Shader.Find("Standard");
        Material mat = new Material(shader);
        mat.name = name;
        mat.color = color;
        return mat;
    }
}
