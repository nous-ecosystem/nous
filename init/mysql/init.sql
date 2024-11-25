CREATE DATABASE IF NOT EXISTS botdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE botdb;

-- Grant privileges
GRANT ALL PRIVILEGES ON botdb.* TO 'botuser'@'%' IDENTIFIED BY 'botpass';
FLUSH PRIVILEGES;