<?php
// 引入資料庫連線檔案
include 'db_connection.php';

// 接收查詢參數：地址 Address
$address = $_GET['address'] ?? null;

if (!$address) {
    echo "請提供區域的地址（Address）以查詢回饋資料。";
    exit;
}

// 查詢該地址的回饋資料
$sql = "SELECT FeedbackID, UserID, FeedbackType, FeedbackText 
        FROM UserFeedback 
        WHERE Address = '$address'";

$result = $conn->query($sql);

$feedbacks = array();
if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        $feedbacks[] = $row;
    }
    echo json_encode($feedbacks);
} else {
    echo "該區域尚無任何回饋資料。";
}

$conn->close();
?>
