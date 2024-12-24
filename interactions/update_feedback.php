<?php
// 引入資料庫連線檔案
include 'db_connection.php';

// 接收更新資料
$feedbackID = $_POST['feedbackID'];
$feedbackText = $_POST['feedbackText'];

// 更新指定的回饋
$sql = "UPDATE UserFeedback 
        SET FeedbackText = '$feedbackText' 
        WHERE FeedbackID = '$feedbackID'";

if ($conn->query($sql) === TRUE) {
    echo "回饋已成功更新。";
} else {
    echo "更新失敗: " . $conn->error;
}

$conn->close();
?>
