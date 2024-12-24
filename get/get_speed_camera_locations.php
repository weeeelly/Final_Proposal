<?php
// 引入資料庫連線檔案
include 'db_connection.php';

// 接收來自使用者的查詢參數
$location = $_GET['location'] ?? null;

// SQL 查詢語句，根據 location 篩選資料
$sql = "SELECT RegionName, Address, Longitude, Latitude FROM EnforcementZones";
if ($location) {
    $sql .= " WHERE RegionName LIKE '%$location%' OR Address LIKE '%$location%'";
}

$result = $conn->query($sql);

// 將查詢結果轉換為 JSON 格式返回
$data = array();
if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        $data[] = $row;
    }
    echo json_encode($data);
} else {
    echo "未找到任何測速照相機資料。";
}

$conn->close();
?>
