<?php
header('Content-Type: application/json');

// Enable error reporting for development
ini_set('display_errors', 1);
error_reporting(E_ALL);

// Handle file upload
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    try {
        // Create uploads directory if it doesn't exist
        $uploadDir = __DIR__ . '/uploads/';
        if (!file_exists($uploadDir)) {
            mkdir($uploadDir, 0777, true);
        }

        // Check if file was uploaded
        if (!isset($_FILES['file'])) {
            throw new Exception('No file uploaded');
        }

        $file = $_FILES['file'];
        $fileName = basename($file['name']);
        $targetPath = $uploadDir . $fileName;

        // Validate file type
        $allowedTypes = ['csv', 'xlsx', 'xls'];
        $fileExtension = strtolower(pathinfo($fileName, PATHINFO_EXTENSION));
        
        if (!in_array($fileExtension, $allowedTypes)) {
            throw new Exception('Invalid file type. Only CSV and Excel files are allowed.');
        }

        // Move uploaded file
        if (move_uploaded_file($file['tmp_name'], $targetPath)) {
            echo json_encode([
                'success' => true,
                'message' => 'File uploaded successfully',
                'filename' => $fileName
            ]);
        } else {
            throw new Exception('Failed to move uploaded file');
        }
    } catch (Exception $e) {
        http_response_code(400);
        echo json_encode([
            'success' => false,
            'message' => $e->getMessage()
        ]);
    }
} else {
    // Serve the dashboard page for GET requests
    include 'templates/dashboard.html';
}
?>
