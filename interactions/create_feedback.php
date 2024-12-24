<?php
// 引入資料庫連線檔案
include 'db_connection.php';

// 接收回饋資料
$userID = $_POST['userID'];
$address = $_POST['address'];
$feedbackType = $_POST['feedbackType'];
$feedbackText = $_POST['feedbackText'];

// 插入回饋資料
$sql = "INSERT INTO UserFeedback (UserID, Address, FeedbackType, FeedbackText) 
        VALUES ('$userID', '$address', '$feedbackType', '$feedbackText')";

if ($conn->query($sql) === TRUE) {
    echo "回饋已成功提交。";
} else {
    echo "提交失敗: " . $conn->error;
}

$conn->close();
?>
