using UnityEngine;

public class PlayerController : MonoBehaviour
{
    public float moveSpeed = 5f;
    public float mouseSensitivity = 2f;

    float rotationY;
    CharacterController controller;
    Camera playerCamera;

    void Start()
    {
        controller = gameObject.AddComponent<CharacterController>();
        playerCamera = Camera.main;

        if (playerCamera != null)
        {
            playerCamera.transform.SetParent(transform);
            playerCamera.transform.localPosition = new Vector3(0, 0.7f, 0);
            playerCamera.transform.localRotation = Quaternion.identity;
        }

        Cursor.lockState = CursorLockMode.Locked;
    }

    void Update()
    {
        float x = Input.GetAxis("Horizontal");
        float z = Input.GetAxis("Vertical");

        Vector3 movement = transform.right * x + transform.forward * z;
        controller.SimpleMove(movement * moveSpeed);

        float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
        float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity;

        rotationY -= mouseY;
        rotationY = Mathf.Clamp(rotationY, -80f, 80f);

        transform.Rotate(Vector3.up * mouseX);

        if (playerCamera != null)
            playerCamera.transform.localRotation = Quaternion.Euler(rotationY, 0, 0);

        if (Input.GetKeyDown(KeyCode.Escape))
            Cursor.lockState = CursorLockMode.None;
    }
}
