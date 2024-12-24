<?php
// 引入資料庫連線檔案
include 'db_connection.php';

// 接收查詢參數：排序的數量（可選）
$limit = $_GET['limit'] ?? 10; // 默認返回最近 10 筆更新

// 查詢最近更新的區域
$sql = "SELECT Address, UpdateDate, ChangesMade 
        FROM UpdateRecords 
        ORDER BY UpdateDate DESC 
        LIMIT $limit";

$result = $conn->query($sql);

$updates = array();
if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        $updates[] = $row;
    }
    echo json_encode($updates);
} else {
    echo "目前尚無更新記錄。";
}

$conn->close();
?>
