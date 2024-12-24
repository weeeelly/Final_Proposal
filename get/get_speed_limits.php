<?php
// 引入資料庫連線檔案
include 'db_connection.php';

// 接收查詢參數：regionName 或 address
$regionName = $_GET['regionName'] ?? null;
$address = $_GET['address'] ?? null;

// SQL 查詢語句
if ($regionName) {
    $sql = "SELECT EnforcementZones.RegionName, SpeedLimits.Address, SpeedLimits.SpeedLimit 
            FROM SpeedLimits 
            INNER JOIN EnforcementZones ON SpeedLimits.Address = EnforcementZones.Address 
            WHERE EnforcementZones.RegionName = '$regionName'";
} elseif ($address) {
    $sql = "SELECT Address, SpeedLimit FROM SpeedLimits WHERE Address = '$address'";
} else {
    echo "請提供 regionName 或 address 作為查詢條件。";
    exit;
}

$result = $conn->query($sql);

// 返回查詢結果
$data = array();
if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        $data[] = $row;
    }
    echo json_encode($data);
} else {
    echo "未找到速限相關資料。";
}

$conn->close();
?>
