<?php
// Fallback for PieHost PHP Application runtime
if (file_exists(__DIR__ . '/index.html')) {
    include_once(__DIR__ . '/index.html');
} else {
    echo "BizLens AI Live";
}
?>
