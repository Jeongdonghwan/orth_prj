-- MariaDB. 앱이 기동 시 db.create_all() 로 자동 생성하지만, 수동 생성용으로도 둔다.
CREATE DATABASE IF NOT EXISTS ortho CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ortho;
CREATE TABLE IF NOT EXISTS inquiries (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  part VARCHAR(20),
  message TEXT,
  ip VARCHAR(45),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_read TINYINT(1) DEFAULT 0
) CHARACTER SET utf8mb4;
