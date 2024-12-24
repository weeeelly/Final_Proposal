<?php
// 引入資料庫連線檔案
include 'db_connection.php';

// 接收回饋 ID
$feedbackID = $_POST['feedbackID'];

// 刪除指定的回饋
$sql = "DELETE FROM UserFeedback 
        WHERE FeedbackID = '$feedbackID'";

if ($conn->query($sql) === TRUE) {
    echo "回饋已成功刪除。";
} else {
    echo "刪除失敗: " . $conn->error;
}

$conn->close();
?>
