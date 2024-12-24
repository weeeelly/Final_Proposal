<?php
// 引入資料庫連線檔案
include 'db_connection.php';

// 接收使用者 ID
$userID = $_GET['userID'];

// 查詢該使用者的所有回饋
$sql = "SELECT FeedbackID, Address, FeedbackType, FeedbackText, DateSubmitted 
        FROM UserFeedback 
        WHERE UserID = '$userID'
        ORDER BY DateSubmitted DESC";

$result = $conn->query($sql);

$data = array();
if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        $data[] = $row;
    }
    echo json_encode($data);
} else {
    echo "尚無任何回饋資料。";
}

$conn->close();
?>
