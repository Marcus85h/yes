-- 视频交友系统数据库表结构
-- 基于ER图设计

-- 创建数据库
CREATE DATABASE IF NOT EXISTS video_dating_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE video_dating_db;

-- 1. 用户表 (users)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone VARCHAR(15) UNIQUE,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    role ENUM('user', 'host', 'admin', 'moderator') DEFAULT 'user',
    gender ENUM('M', 'F', 'O'),
    avatar VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 扩展字段
    balance DECIMAL(10,2) DEFAULT 0.00,
    is_online BOOLEAN DEFAULT FALSE,
    last_seen TIMESTAMP NULL,
    
    INDEX idx_phone (phone),
    INDEX idx_username (username),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at)
);

-- 2. 房间表 (rooms)
CREATE TABLE rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    host_id INT NOT NULL,
    status ENUM('waiting', 'active', 'ended', 'cancelled') DEFAULT 'waiting',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 扩展字段
    name VARCHAR(100),
    description TEXT,
    max_participants INT DEFAULT 2,
    
    FOREIGN KEY (host_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_host_id (host_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- 3. 通话会话表 (call_sessions)
CREATE TABLE call_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    caller_id INT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NULL,
    duration INT DEFAULT 0 COMMENT '通话时长（秒）',
    quality ENUM('low', 'medium', 'high', 'hd') DEFAULT 'medium',
    
    -- 扩展字段
    is_active BOOLEAN DEFAULT TRUE,
    total_cost DECIMAL(10,2) DEFAULT 0.00,
    
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (caller_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_room_id (room_id),
    INDEX idx_caller_id (caller_id),
    INDEX idx_start_time (start_time),
    INDEX idx_is_active (is_active)
);

-- 4. 礼物表 (gift)
CREATE TABLE gift (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price INT NOT NULL COMMENT '价格（分）',
    icon VARCHAR(500) NOT NULL,
    animation_url VARCHAR(500),
    
    -- 扩展字段
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    category VARCHAR(50),
    
    INDEX idx_name (name),
    INDEX idx_price (price),
    INDEX idx_category (category),
    INDEX idx_is_active (is_active)
);

-- 5. 礼物交易表 (gift_transactions)
CREATE TABLE gift_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gift_id INT NOT NULL,
    session_id INT NOT NULL,
    sender_id INT NOT NULL,
    price_at_time INT NOT NULL COMMENT '当时价格（分）',
    
    -- 扩展字段
    quantity INT DEFAULT 1,
    total_amount INT NOT NULL COMMENT '总金额（分）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (gift_id) REFERENCES gift(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES call_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_gift_id (gift_id),
    INDEX idx_session_id (session_id),
    INDEX idx_sender_id (sender_id),
    INDEX idx_created_at (created_at)
);

-- 6. 计费记录表 (billing_records)
CREATE TABLE billing_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    amount_charged INT NOT NULL COMMENT '计费金额（分）',
    billed_at TIMESTAMP NOT NULL,
    
    -- 扩展字段
    billing_type VARCHAR(20) DEFAULT 'per_minute',
    rate_per_minute INT DEFAULT 100 COMMENT '每分钟费率（分）',
    
    FOREIGN KEY (session_id) REFERENCES call_sessions(id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_billed_at (billed_at)
);

-- 7. 用户行为日志表 (user_behavior_logs)
CREATE TABLE user_behavior_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    ip VARCHAR(45) NOT NULL,
    action_type VARCHAR(50) NOT NULL COMMENT 'login_fail, screen_record_attempt, api_abuse, etc.',
    user_agent TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 扩展字段
    details JSON,
    severity ENUM('info', 'warning', 'error') DEFAULT 'info',
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_action_type (action_type),
    INDEX idx_created_at (created_at),
    INDEX idx_severity (severity)
);

-- 8. 用户黑名单表 (user_blacklist)
CREATE TABLE user_blacklist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    reason TEXT NOT NULL,
    banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- 扩展字段
    banned_by INT,
    duration INT COMMENT '封禁时长（小时），NULL表示永久',
    expires_at TIMESTAMP NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (banned_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_is_active (is_active),
    INDEX idx_banned_at (banned_at)
);

-- 9. 充值记录表 (recharges)
CREATE TABLE recharges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    amount INT NOT NULL COMMENT '充值金额（分）',
    method ENUM('alipay', 'wechat', 'bank_card', 'apple_pay', 'google_pay') NOT NULL,
    recharged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 扩展字段
    status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    transaction_id VARCHAR(100) UNIQUE,
    description VARCHAR(200),
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_method (method),
    INDEX idx_status (status),
    INDEX idx_recharged_at (recharged_at)
);

-- 10. 消息表 (messages)
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    content TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 扩展字段
    sender_id INT NOT NULL,
    message_type ENUM('text', 'image', 'audio', 'video') DEFAULT 'text',
    is_deleted BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_room_id (room_id),
    INDEX idx_sender_id (sender_id),
    INDEX idx_sent_at (sent_at),
    INDEX idx_message_type (message_type)
);

-- 创建视图：活跃用户统计
CREATE VIEW active_users_stats AS
SELECT 
    COUNT(*) as total_users,
    SUM(CASE WHEN is_online = 1 THEN 1 ELSE 0 END) as online_users,
    SUM(CASE WHEN role = 'host' THEN 1 ELSE 0 END) as total_hosts,
    SUM(CASE WHEN role = 'host' AND is_online = 1 THEN 1 ELSE 0 END) as online_hosts
FROM users;

-- 创建视图：房间统计
CREATE VIEW room_stats AS
SELECT 
    COUNT(*) as total_rooms,
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_rooms,
    SUM(CASE WHEN status = 'waiting' THEN 1 ELSE 0 END) as waiting_rooms,
    AVG(CASE WHEN status = 'ended' THEN TIMESTAMPDIFF(SECOND, created_at, NOW()) ELSE NULL END) as avg_room_duration
FROM rooms;

-- 创建视图：收入统计
CREATE VIEW revenue_stats AS
SELECT 
    SUM(amount_charged) as total_revenue,
    COUNT(*) as total_billing_records,
    AVG(amount_charged) as avg_billing_amount,
    DATE(billed_at) as billing_date
FROM billing_records 
WHERE billed_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(billed_at);

-- 插入示例数据

-- 插入示例用户
INSERT INTO users (phone, username, password, role, gender, avatar) VALUES
('13800138001', 'user1', 'password123', 'user', 'M', 'https://example.com/avatar1.jpg'),
('13800138002', 'host1', 'password123', 'host', 'F', 'https://example.com/avatar2.jpg'),
('13800138003', 'admin1', 'password123', 'admin', 'M', 'https://example.com/avatar3.jpg');

-- 插入示例礼物
INSERT INTO gift (name, price, icon, animation_url, description, category) VALUES
('玫瑰', 100, 'https://example.com/rose.png', 'https://example.com/rose.gif', '美丽的玫瑰花', 'flower'),
('爱心', 50, 'https://example.com/heart.png', 'https://example.com/heart.gif', '表达爱意', 'emotion'),
('皇冠', 500, 'https://example.com/crown.png', 'https://example.com/crown.gif', '尊贵皇冠', 'premium');

-- 创建触发器：更新用户余额
DELIMITER //
CREATE TRIGGER after_recharge_complete
AFTER UPDATE ON recharges
FOR EACH ROW
BEGIN
    IF NEW.status = 'completed' AND OLD.status = 'pending' THEN
        UPDATE users 
        SET balance = balance + (NEW.amount / 100)
        WHERE id = NEW.user_id;
    END IF;
END//
DELIMITER ;

-- 创建触发器：记录用户行为日志
DELIMITER //
CREATE TRIGGER after_user_login
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    IF NEW.last_seen != OLD.last_seen THEN
        INSERT INTO user_behavior_logs (user_id, ip, action_type, user_agent, severity)
        VALUES (NEW.id, '127.0.0.1', 'login_success', 'Mozilla/5.0', 'info');
    END IF;
END//
DELIMITER ; 