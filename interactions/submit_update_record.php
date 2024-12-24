<?php
// 引入資料庫連線檔案
include 'db_connection.php';

// 接收更新記錄的數據
$address = $_POST['address'];
$updateDate = $_POST['updateDate'];
$changesMade = $_POST['changesMade'];

// 插入新的更新記錄
$sql = "INSERT INTO UpdateRecords (Address, UpdateDate, ChangesMade) 
        VALUES ('$address', '$updateDate', '$changesMade')";

if ($conn->query($sql) === TRUE) {
    echo "更新記錄已成功新增。";
} else {
    echo "新增失敗: " . $sql . "<br>" . $conn->error;
}

$conn->close();
?>
