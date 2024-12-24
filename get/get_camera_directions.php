<?php
// 引入資料庫連線檔案
include 'db_connection.php';

// 接收查詢參數：地址 Address
$address = $_GET['address'] ?? null;

if (!$address) {
    echo "請提供測速照相機的地址（Address）。";
    exit;
}

// 查詢方向資訊
$sql = "SELECT Direction FROM SpeedLimits WHERE Address = '$address'";
$result = $conn->query($sql);

$directions = array();
if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        $directions[] = $row;
    }
    echo json_encode($directions);
} else {
    echo "未找到該地址的方向資訊。";
}

$conn->close();
?>
