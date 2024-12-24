<?php
// db_connection.php
$host = 'localhost';
$username = 'root';
$password = 'willy0310';
$database = 'final';

$conn = new mysqli($host, $username, $password, $database);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>
