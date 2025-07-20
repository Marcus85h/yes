# 视频交友系统 API 设计文档

## 基础信息
- **基础URL**: `https://api.videodating.com/v1`
- **认证方式**: JWT Token
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证相关

### 1. 用户注册
```
POST /auth/register
```

**请求参数**:
```json
{
    "phone": "13800138001",
    "username": "user123",
    "password": "password123",
    "gender": "M",
    "avatar": "https://example.com/avatar.jpg"
}
```

**响应**:
```json
{
    "code": 200,
    "message": "注册成功",
    "data": {
        "user": {
            "id": 1,
            "username": "user123",
            "phone": "13800138001",
            "gender": "M",
            "avatar": "https://example.com/avatar.jpg",
            "balance": 0.00,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "token": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        }
    }
}
```

### 2. 用户登录
```
POST /auth/login
```

**请求参数**:
```json
{
    "phone": "13800138001",
    "password": "password123"
}
```

**响应**:
```json
{
    "code": 200,
    "message": "登录成功",
    "data": {
        "user": {
            "id": 1,
            "username": "user123",
            "phone": "13800138001",
            "balance": 100.00,
            "is_online": true
        },
        "token": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        }
    }
}
```

### 3. 刷新Token
```
POST /auth/refresh
```

**请求参数**:
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## 用户管理

### 4. 获取用户信息
```
GET /users/profile
Authorization: Bearer <token>
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "id": 1,
        "username": "user123",
        "phone": "13800138001",
        "gender": "M",
        "avatar": "https://example.com/avatar.jpg",
        "balance": 100.00,
        "is_online": true,
        "last_seen": "2024-01-01T12:00:00Z",
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

### 5. 更新用户信息
```
PUT /users/profile
Authorization: Bearer <token>
```

**请求参数**:
```json
{
    "username": "newusername",
    "gender": "F",
    "avatar": "https://example.com/new-avatar.jpg"
}
```

### 6. 搜索用户
```
GET /users/search?keyword=user&gender=M&online_only=true
Authorization: Bearer <token>
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "users": [
            {
                "id": 2,
                "username": "host1",
                "gender": "F",
                "avatar": "https://example.com/avatar2.jpg",
                "is_online": true,
                "role": "host",
                "price_per_minute": 1.00
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 20
    }
}
```

## 房间管理

### 7. 创建房间
```
POST /rooms
Authorization: Bearer <token>
```

**请求参数**:
```json
{
    "name": "我的房间",
    "description": "欢迎来到我的房间",
    "max_participants": 2
}
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "id": 1,
        "name": "我的房间",
        "host_id": 1,
        "status": "waiting",
        "created_at": "2024-01-01T12:00:00Z"
    }
}
```

### 8. 获取房间列表
```
GET /rooms?status=waiting&page=1&page_size=20
Authorization: Bearer <token>
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "rooms": [
            {
                "id": 1,
                "name": "我的房间",
                "host": {
                    "id": 1,
                    "username": "user123",
                    "avatar": "https://example.com/avatar.jpg"
                },
                "status": "waiting",
                "participants_count": 1,
                "created_at": "2024-01-01T12:00:00Z"
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 20
    }
}
```

### 9. 加入房间
```
POST /rooms/{room_id}/join
Authorization: Bearer <token>
```

**响应**:
```json
{
    "code": 200,
    "message": "成功加入房间",
    "data": {
        "room_id": 1,
        "webrtc_config": {
            "ice_servers": [
                {"urls": "stun:stun.l.google.com:19302"}
            ]
        }
    }
}
```

## 通话管理

### 10. 开始通话
```
POST /calls/start
Authorization: Bearer <token>
```

**请求参数**:
```json
{
    "room_id": 1,
    "caller_id": 1,
    "quality": "hd"
}
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "call_id": 1,
        "room_id": 1,
        "start_time": "2024-01-01T12:00:00Z",
        "webrtc_config": {
            "ice_servers": [
                {"urls": "stun:stun.l.google.com:19302"}
            ],
            "signaling_server": "wss://signaling.videodating.com"
        }
    }
}
```

### 11. 结束通话
```
POST /calls/{call_id}/end
Authorization: Bearer <token>
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "call_id": 1,
        "duration": 300,
        "total_cost": 5.00,
        "end_time": "2024-01-01T12:05:00Z"
    }
}
```

## 礼物系统

### 12. 获取礼物列表
```
GET /gifts
Authorization: Bearer <token>
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "gifts": [
            {
                "id": 1,
                "name": "玫瑰",
                "price": 100,
                "icon": "https://example.com/rose.png",
                "animation_url": "https://example.com/rose.gif",
                "category": "flower"
            }
        ]
    }
}
```

### 13. 发送礼物
```
POST /gifts/send
Authorization: Bearer <token>
```

**请求参数**:
```json
{
    "gift_id": 1,
    "session_id": 1,
    "quantity": 1
}
```

**响应**:
```json
{
    "code": 200,
    "message": "礼物发送成功",
    "data": {
        "transaction_id": 1,
        "total_amount": 100,
        "sender_balance": 99.00
    }
}
```

## 计费系统

### 14. 充值
```
POST /billing/recharge
Authorization: Bearer <token>
```

**请求参数**:
```json
{
    "amount": 5000,
    "method": "alipay"
}
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "recharge_id": 1,
        "amount": 5000,
        "payment_url": "https://alipay.com/pay/...",
        "status": "pending"
    }
}
```

### 15. 获取充值记录
```
GET /billing/recharges?page=1&page_size=20
Authorization: Bearer <token>
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "recharges": [
            {
                "id": 1,
                "amount": 5000,
                "method": "alipay",
                "status": "completed",
                "recharged_at": "2024-01-01T12:00:00Z"
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 20
    }
}
```

### 16. 获取消费记录
```
GET /billing/records?page=1&page_size=20
Authorization: Bearer <token>
```

## 消息系统

### 17. 发送消息
```
POST /messages
Authorization: Bearer <token>
```

**请求参数**:
```json
{
    "room_id": 1,
    "content": "你好！",
    "message_type": "text"
}
```

### 18. 获取消息历史
```
GET /messages?room_id=1&page=1&page_size=50
Authorization: Bearer <token>
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "messages": [
            {
                "id": 1,
                "content": "你好！",
                "sender": {
                    "id": 1,
                    "username": "user123",
                    "avatar": "https://example.com/avatar.jpg"
                },
                "message_type": "text",
                "sent_at": "2024-01-01T12:00:00Z"
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 50
    }
}
```

## WebSocket 接口

### 19. 连接WebSocket
```
WebSocket: wss://api.videodating.com/ws
```

**连接参数**:
```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "room_id": 1
}
```

### 20. 消息类型

#### 聊天消息
```json
{
    "type": "chat_message",
    "data": {
        "message_id": 1,
        "content": "你好！",
        "sender_id": 1,
        "sent_at": "2024-01-01T12:00:00Z"
    }
}
```

#### 礼物消息
```json
{
    "type": "gift_message",
    "data": {
        "gift_id": 1,
        "gift_name": "玫瑰",
        "sender_id": 1,
        "animation_url": "https://example.com/rose.gif"
    }
}
```

#### 用户状态更新
```json
{
    "type": "user_status",
    "data": {
        "user_id": 1,
        "is_online": true,
        "last_seen": "2024-01-01T12:00:00Z"
    }
}
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 响应格式

所有API响应都遵循以下格式：

```json
{
    "code": 200,
    "message": "操作成功",
    "data": {
        // 具体数据
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

错误响应格式：

```json
{
    "code": 400,
    "message": "参数错误",
    "errors": [
        {
            "field": "phone",
            "message": "手机号格式不正确"
        }
    ],
    "timestamp": "2024-01-01T12:00:00Z"
}
``` 