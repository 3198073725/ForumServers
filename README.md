## 目录

1.  项目概述
2.  需求分析
3.  系统架构设计
4.  核心功能模块设计
5.  数据库设计
6.  接口设计
7.  权限管理设计
8.  安全策略
9.  测试计划
10. 部署方案
11. 扩展功能设计
    *   11.1 积分 / 等级系统
    *   11.2 私信聊天功能
    *   11.3 Elasticsearch 全文搜索功能
    *   11.4 日志与审计

---

## 一、项目概述

### 1.1 项目名称

基于 Vue + Django + MySQL 的 PC 端论坛系统

### 1.2 项目背景

随着信息化发展，在线论坛作为用户交流和分享信息的重要平台，广泛应用于各种社区、学校、企业内部。本项目旨在构建一个现代化、响应式、可扩展的 PC 端论坛系统，实现用户注册、发帖、评论、管理等核心功能。

### 1.3 开发技术

*   前端：Vue 3 + Element Plus + Axios + Vue Router + Vuex
*   后端：Django 4.x + Django REST Framework
*   数据库：MySQL 8.x
*   部署：Nginx + Gunicorn + Supervisor + Linux (Ubuntu)

---

## 二、需求分析

### 2.1 用户角色

*   普通用户
*   版主
*   管理员

### 2.2 功能需求

#### 普通用户功能：

*   注册 / 登录 / 退出登录
*   个人信息管理（头像、密码、简介等）
*   查看帖子 / 搜索帖子
*   发帖 / 编辑 / 删除自己的帖子
*   评论 / 回复评论
*   点赞 / 收藏帖子

#### 版主功能：

*   置顶 / 精华帖管理
*   删除违规帖
*   审核举报

#### 管理员功能：

*   用户管理（封禁/解封、角色分配）
*   板块管理（增删改）
*   系统日志查看
*   举报处理

### 2.3 非功能需求

*   系统响应时间小于1s
*   页面支持1080p及以上分辨率
*   支持 Markdown 编辑器
*   RESTful API 设计
*   接口权限控制
*   前后端分离

---

## 三、系统架构设计

### 3.1 架构总览

*   前端：SPA 架构，Vue + Element Plus 构建组件式页面
*   后端：Django 提供 REST API，负责业务逻辑和数据库交互
*   数据库：MySQL 存储用户数据、帖子数据、评论数据等
*   Redis：缓存热帖、热用户、Session（可选）
*   Nginx：负载均衡，静态资源服务
*   Gunicorn：Django WSGI 服务端
*   Supervisor：进程管理

### 3.2 模块分布

*   前端静态资源由 Nginx 提供
*   API 统一由 `/api/` 路径代理至 Django 服务
*   数据分层管理：前端展示、后端逻辑、数据库存储三层清晰

---

## 四、核心功能模块设计

### 4.1 用户模块

*   注册 / 登录 / 注销
*   用户信息查看与修改
*   密码找回与重置

### 4.2 帖子模块

*   发表帖子（支持 Markdown）
*   浏览帖子（分页、搜索、排序）
*   编辑 / 删除自己的帖子
*   点赞 / 收藏
*   浏览统计

### 4.3 评论模块

*   一级评论 / 二级回复
*   删除自己的评论
*   回复通知（被回复时推送通知）

### 4.4 板块模块

*   创建 / 编辑 / 删除板块（管理员）
*   查看各板块帖子列表

### 4.5 举报模块

*   举报帖子 / 评论
*   举报处理（版主 / 管理员）

---

## 五、数据库设计

### 5.1 数据库名称

`forum_db`

### 5.2 主要数据表设计

| 表名            | 描述    |
| ------------- | ----- |
| users         | 用户信息表 |
| posts         | 帖子表   |
| comments      | 评论表   |
| likes         | 点赞表   |
| favorites     | 收藏表   |
| boards        | 板块表   |
| reports       | 举报表   |
| notifications | 通知表   |
| logs          | 系统日志表 |
| private\_messages|私信表|
| user\_points |积分记录表|

### 5.3 各表字段示例及建表语句

#### users

| 表名        | 字段名            | 类型                                       | 约束                                                      | 说明     |
| --------- | -------------- | ---------------------------------------- | ------------------------------------------------------- | ------ |
| **users** | id             | BIGINT(20)                               | PK, AI                                                  | 用户唯一ID |
|           | username       | VARCHAR(50)                              | UNIQUE, NOT NULL                                        | 用户名    |
|           | email          | VARCHAR(100)                             | UNIQUE, NOT NULL                                        | 邮箱     |
|           | password\_hash | VARCHAR(255)                             | NOT NULL                                                | 加密密码   |
|           | nickname       | VARCHAR(50)                              |                                                         | 昵称     |
|           | avatar\_url    | VARCHAR(255)                             |                                                         | 头像URL  |
|           | role           | ENUM('guest','user','moderator','admin') | DEFAULT 'user'                                          | 用户角色   |
|           | created\_at    | DATETIME                                 | DEFAULT CURRENT\_TIMESTAMP                              | 注册时间   |
|           | updated\_at    | DATETIME                                 | DEFAULT CURRENT\_TIMESTAMP ON UPDATE CURRENT\_TIMESTAMP | 更新时间   |
|           | last\_login    | DATETIME                                 |                                                         | 最后登录时间 |

#### posts
| 表名        | 字段名            | 类型                                       | 约束                                                      | 说明     |
| --------- | -------------- | ---------------------------------------- | ------------------------------------------------------- | ------ |
| posts | id | BIGINT(20) | PK, AI | 帖子唯一ID |
| | user_id | BIGINT(20) | FK(users.id), NOT NULL | 发帖用户ID |
| | board_id | BIGINT(20) | FK(boards.id), NOT NULL | 所属板块ID |
| | title | VARCHAR(255) | NOT NULL | 帖子标题 |
| | content | TEXT | NOT NULL | 帖子内容 |
| | views | INT(11) | DEFAULT 0 | 浏览量 |
| | likes_count | INT(11) | DEFAULT 0 | 点赞数 |
| | comments_count | INT(11) | DEFAULT 0 | 评论数 |
| | is_pinned | BOOLEAN | DEFAULT FALSE | 是否置顶 |
| | is_featured | BOOLEAN | DEFAULT FALSE | 是否加精 |
| | created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| | updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

#### comments
| 表名        | 字段名            | 类型                                       | 约束                                                      | 说明     |
| --------- | -------------- | ---------------------------------------- | ------------------------------------------------------- | ------ |
| comments| id | BIGINT(20) | PK, AI | 评论唯一ID |
| | post_id | BIGINT(20) | FK(posts.id), NOT NULL | 所属帖子ID |
| | user_id | BIGINT(20) | FK(users.id), NOT NULL | 评论用户ID |
| | parent_id | BIGINT(20) | FK(comments.id) | 父评论ID（回复的评论） |
| | content | TEXT | NOT NULL | 评论内容 |
| | likes_count | INT(11) | DEFAULT 0 | 点赞数 |
| | created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| | updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

#### likes
| 表名        | 字段名            | 类型                                       | 约束                                                      | 说明     |
| --------- | -------------- | ---------------------------------------- | ------------------------------------------------------- | ------ |
| likes | id | BIGINT(20) | PK, AI | 点赞记录ID |
| | user_id | BIGINT(20) | FK(users.id), NOT NULL | 点赞用户ID |
| | content_type | ENUM('post', 'comment') | NOT NULL | 点赞类型（帖子/评论） |
| | content_id | BIGINT(20) | NOT NULL | 被点赞内容ID |
| | created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 点赞时间 |

#### favorites
| 表名        | 字段名            | 类型                                       | 约束                                                      | 说明     |
| --------- | -------------- | ---------------------------------------- | ------------------------------------------------------- | ------ |
| favorites| id | BIGINT(20) | PK, AI | 收藏记录ID |
| | user_id | BIGINT(20) | FK(users.id), NOT NULL | 收藏用户ID |
| | post_id | BIGINT(20) | FK(posts.id), NOT NULL | 收藏帖子ID |
| | created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 收藏时间 |

#### boards
| 表名        | 字段名            | 类型                                       | 约束                                                      | 说明     |
| --------- | -------------- | ---------------------------------------- | ------------------------------------------------------- | ------ |
| boards | id | BIGINT(20) | PK, AI | 板块唯一ID |
| | name | VARCHAR(100) | NOT NULL, UNIQUE | 板块名称 |
| | description | VARCHAR(255) | | 板块描述 |
| | created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| | updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

#### reports
| 表名        | 字段名            | 类型                                       | 约束                                                      | 说明     |
| --------- | -------------- | ---------------------------------------- | ------------------------------------------------------- | ------ |
| reports | id | BIGINT(20) | PK, AI | 举报唯一ID |
| | reporter_id | BIGINT(20) | FK(users.id), NOT NULL | 举报用户ID |
| | content_type | ENUM('post','comment','user') | NOT NULL | 举报内容类型 |
| | content_id | BIGINT(20) | NOT NULL | 被举报内容ID |
| | reason | VARCHAR(255) | NOT NULL | 举报原因 |
| | status | ENUM('pending','reviewed','dismissed') | DEFAULT 'pending' | 举报状态 |
| | created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 举报时间 |
| | reviewed_by | BIGINT(20) | FK(users.id) | 审核管理员ID |
| | reviewed_at | DATETIME | | 审核时间 |

#### notifications
| 表名        | 字段名            | 类型                                       | 约束                                                      | 说明     |
| --------- | -------------- | ---------------------------------------- | ------------------------------------------------------- | ------ |
| notifications | id | BIGINT(20) | PK, AI | 通知唯一ID |
| | user_id | BIGINT(20) | FK(users.id), NOT NULL | 接收通知用户ID |
| | type | ENUM('like','comment','follow','system') | NOT NULL | 通知类型 |
| | content | VARCHAR(255) | | 通知内容摘要 |
| | is_read | BOOLEAN | DEFAULT FALSE | 是否已读 |
| | created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 通知时间 |

#### logs
| 表名        | 字段名            | 类型                                       | 约束                                                      | 说明     |
| --------- | -------------- | ---------------------------------------- | ------------------------------------------------------- | ------ |
| logs | id | BIGINT(20) | PK, AI | 日志唯一ID |
| | level | ENUM('INFO','WARNING','ERROR','DEBUG') | NOT NULL | 日志等级 |
| | message | TEXT | NOT NULL | 日志消息 |
| | created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 日志时间 |
| | user_id | BIGINT(20) | FK(users.id) | 操作用户ID（可为空） |
| | ip_address | VARCHAR(45) | | 用户IP地址 |

#### private_messages
| 字段名          | 类型         | 约束                     | 说明      |
| ------------ | ---------- | ---------------------- | ------- |
| id           | BIGINT(20) | PK, AI                 | 私信唯一ID  |
| sender\_id   | BIGINT(20) | NOT NULL, FK(users.id) | 发送者用户ID |
| receiver\_id | BIGINT(20) | NOT NULL, FK(users.id) | 接收者用户ID |
| content      | TEXT       | NOT NULL               | 私信内容    |
| is\_read     | BOOLEAN    | NOT NULL, 默认FALSE      | 是否已读    |
| created\_at  | DATETIME   | NOT NULL, 默认当前时间       | 发送时间    |

#### user_points
| 字段名         | 类型         | 约束                   | 说明              |
| ----------- | ---------- | -------------------- | --------------- |
| id          | BIGINT(20) | PK, AI               | 积分记录唯一ID        |
| user\_id    | BIGINT(20) | UNIQUE, FK(users.id) | 用户ID，唯一对应一个积分记录 |
| points      | INT(11)    | NOT NULL, 默认0        | 当前积分总额          |
| updated\_at | DATETIME   | NOT NULL, 自动更新时间     | 积分最后更新时间        |

建表语言：
```mysql
-- 用户表
CREATE TABLE `users` (
	`id` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`username` VARCHAR(50) NOT NULL UNIQUE,
	`email` VARCHAR(100) NOT NULL UNIQUE,
	`password_hash` VARCHAR(255) NOT NULL,
	`nickname` VARCHAR(50) DEFAULT NULL,
	`avatar_url` VARCHAR(255) DEFAULT NULL,
	`role` ENUM('guest', 'user', 'moderator', 'admin') NOT NULL DEFAULT 'user',
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	`last_login` DATETIME DEFAULT NULL,
	PRIMARY KEY (`id`)
) ENGINE = InnoDB CHARSET = utf8mb4;

-- 板块表
CREATE TABLE `boards` (
	`id` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(100) NOT NULL UNIQUE,
	`description` VARCHAR(255) DEFAULT NULL,
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`)
) ENGINE = InnoDB CHARSET = utf8mb4;

-- 帖子表
CREATE TABLE `posts` (
	`id` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`user_id` BIGINT(20) NOT NULL,
	`board_id` BIGINT(20) NOT NULL,
	`title` VARCHAR(255) NOT NULL,
	`content` TEXT NOT NULL,
	`views` INT(11) NOT NULL DEFAULT 0,
	`likes_count` INT(11) NOT NULL DEFAULT 0,
	`comments_count` INT(11) NOT NULL DEFAULT 0,
	`is_pinned` BOOLEAN NOT NULL DEFAULT false,
	`is_featured` BOOLEAN NOT NULL DEFAULT false,
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`),
	INDEX `idx_user`(`user_id`),
	INDEX `idx_board`(`board_id`),
	CONSTRAINT `fk_posts_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
	CONSTRAINT `fk_posts_board` FOREIGN KEY (`board_id`) REFERENCES `boards` (`id`) ON DELETE CASCADE
) ENGINE = InnoDB CHARSET = utf8mb4;

-- 评论表
CREATE TABLE `comments` (
	`id` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`post_id` BIGINT(20) NOT NULL,
	`user_id` BIGINT(20) NOT NULL,
	`parent_id` BIGINT(20) DEFAULT NULL,
	`content` TEXT NOT NULL,
	`likes_count` INT(11) NOT NULL DEFAULT 0,
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`),
	INDEX `idx_post`(`post_id`),
	INDEX `idx_user`(`user_id`),
	INDEX `idx_parent`(`parent_id`),
	CONSTRAINT `fk_comments_post` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE,
	CONSTRAINT `fk_comments_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
	CONSTRAINT `fk_comments_parent` FOREIGN KEY (`parent_id`) REFERENCES `comments` (`id`) ON DELETE SET NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

-- 点赞表
CREATE TABLE `likes` (
	`id` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`user_id` BIGINT(20) NOT NULL,
	`content_type` ENUM('post', 'comment') NOT NULL,
	`content_id` BIGINT(20) NOT NULL,
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`),
	INDEX `idx_user`(`user_id`),
	INDEX `idx_content`(`content_type`, `content_id`),
	CONSTRAINT `fk_likes_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE = InnoDB CHARSET = utf8mb4;

-- 收藏表
CREATE TABLE `favorites` (
	`id` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`user_id` BIGINT(20) NOT NULL,
	`post_id` BIGINT(20) NOT NULL,
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`),
	UNIQUE KEY `uniq_user_post` (`user_id`, `post_id`),
	INDEX `idx_user`(`user_id`),
	INDEX `idx_post`(`post_id`),
	CONSTRAINT `fk_favorites_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
	CONSTRAINT `fk_favorites_post` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE
) ENGINE = InnoDB CHARSET = utf8mb4;

-- 举报表
CREATE TABLE `reports` (
	`id` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`reporter_id` BIGINT(20) NOT NULL,
	`content_type` ENUM('post', 'comment', 'user') NOT NULL,
	`content_id` BIGINT(20) NOT NULL,
	`reason` VARCHAR(255) NOT NULL,
	`status` ENUM('pending', 'reviewed', 'dismissed') NOT NULL DEFAULT 'pending',
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`reviewed_by` BIGINT(20) DEFAULT NULL,
	`reviewed_at` DATETIME DEFAULT NULL,
	PRIMARY KEY (`id`),
	INDEX `idx_reporter`(`reporter_id`),
	INDEX `idx_reviewer`(`reviewed_by`),
	CONSTRAINT `fk_reports_reporter` FOREIGN KEY (`reporter_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
	CONSTRAINT `fk_reports_reviewer` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

-- 通知表
CREATE TABLE `notifications` (
	`id` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`user_id` BIGINT(20) NOT NULL,
	`type` ENUM('like', 'comment', 'follow', 'system') NOT NULL,
	`content` VARCHAR(255) DEFAULT NULL,
	`is_read` BOOLEAN NOT NULL DEFAULT false,
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`),
	INDEX `idx_user`(`user_id`),
	CONSTRAINT `fk_notifications_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE = InnoDB CHARSET = utf8mb4;

-- 日志表
CREATE TABLE `logs` (
	`id` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`level` ENUM('INFO', 'WARNING', 'ERROR', 'DEBUG') NOT NULL,
	`message` TEXT NOT NULL,
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`user_id` BIGINT(20) DEFAULT NULL,
	`ip_address` VARCHAR(45) DEFAULT NULL,
	PRIMARY KEY (`id`),
	INDEX `idx_user`(`user_id`),
	CONSTRAINT `fk_logs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

-- 积分表 (User Points)
CREATE TABLE `user_points` (
	`id` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`user_id` BIGINT(20) NOT NULL,
	`points` INT(11) NOT NULL DEFAULT 0,
	`updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`),
	UNIQUE KEY `uniq_user` (`user_id`),
	CONSTRAINT `fk_user_points_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE = InnoDB CHARSET = utf8mb4;

-- 私信表 (Private Messages)
CREATE TABLE `private_messages` (
	`id` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`sender_id` BIGINT(20) NOT NULL,
	`receiver_id` BIGINT(20) NOT NULL,
	`content` TEXT NOT NULL,
	`is_read` BOOLEAN NOT NULL DEFAULT false,
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`),
	INDEX `idx_sender`(`sender_id`),
	INDEX `idx_receiver`(`receiver_id`),
	CONSTRAINT `fk_pm_sender` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
	CONSTRAINT `fk_pm_receiver` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE = InnoDB CHARSET = utf8mb4;
```

---

## 六、接口设计

### 6.1 接口规范

*   RESTful 风格
*   所有接口前缀：`/api/v1/`
*   响应格式统一（status, data, msg）

### 6.2 接口鉴权机制

*   JWT 令牌机制：前端登录后保存 token，请求时在 Header 中携带 `Authorization: Bearer <token>`。后端通过中间件校验 token 的有效性、是否过期等。

### 6.3 主要接口定义（示例）

#### 用户认证接口
*   `POST /api/v1/auth/register/`：用户注册
*   `POST /api/v1/auth/login/`：用户登录，返回 token 和用户信息
*   `POST /api/v1/auth/logout/`：用户登出 (后端可使 token 失效或前端清除 token)
*   `POST /api/v1/auth/password/reset/`：请求重置密码 (如发送邮件)
*   `POST /api/v1/auth/password/reset/confirm/`：确认重置密码

#### 用户管理接口
*   `GET /api/v1/users/me/`：获取当前登录用户信息
*   `PUT /api/v1/users/me/`：修改当前登录用户信息
*   `PUT /api/v1/users/me/password/`：修改当前登录用户密码
*   `GET /api/v1/users/{user_id}/`：获取指定用户信息 (管理员/版主权限)
*   `PUT /api/v1/users/{user_id}/`：修改指定用户信息 (管理员权限)

#### 帖子接口
*   `GET /api/v1/posts/`：获取帖子列表 (支持板块筛选 `board_id`, 关键词搜索 `keyword`, 分页 `page`, `page_size`, 排序 `ordering`)
*   `POST /api/v1/posts/`：发布新帖子 (需登录)
*   `GET /api/v1/posts/{post_id}/`：获取帖子详情
*   `PUT /api/v1/posts/{post_id}/`：编辑帖子 (作者或管理员/版主权限)
*   `DELETE /api/v1/posts/{post_id}/`：删除帖子 (作者或管理员/版主权限)
*   `POST /api/v1/posts/{post_id}/like/`：点赞/取消点赞帖子 (需登录)
*   `POST /api/v1/posts/{post_id}/favorite/`：收藏/取消收藏帖子 (需登录)
*   `PUT /api/v1/posts/{post_id}/pin/`：置顶/取消置顶帖子 (版主/管理员权限)
*   `PUT /api/v1/posts/{post_id}/feature/`：加精/取消加精帖子 (版主/管理员权限)

#### 评论接口
*   `GET /api/v1/posts/{post_id}/comments/`：获取帖子下的评论列表 (支持分页)
*   `POST /api/v1/posts/{post_id}/comments/`：发表评论 (需登录)
*   `GET /api/v1/comments/{comment_id}/`：获取评论详情 (较少使用，但可预留)
*   `PUT /api/v1/comments/{comment_id}/`：编辑评论 (作者或管理员/版主权限)
*   `DELETE /api/v1/comments/{comment_id}/`：删除评论 (作者或管理员/版主权限)
*   `POST /api/v1/comments/{comment_id}/like/`：点赞/取消点赞评论 (需登录)

#### 板块接口
*   `GET /api/v1/boards/`：获取板块列表
*   `POST /api/v1/boards/`：创建新板块 (管理员权限)
*   `GET /api/v1/boards/{board_id}/`：获取板块详情
*   `PUT /api/v1/boards/{board_id}/`：修改板块信息 (管理员权限)
*   `DELETE /api/v1/boards/{board_id}/`：删除板块 (管理员权限)

#### 举报接口
*   `POST /api/v1/reports/`：提交举报 (需登录，参数：`content_type`, `content_id`, `reason`)
*   `GET /api/v1/reports/`：获取举报列表 (版主/管理员权限，支持状态筛选)
*   `PUT /api/v1/reports/{report_id}/status/`：处理举报 (版主/管理员权限，参数：`status` ['reviewed', 'dismissed'])

### 6.4 接口文档格式模板 (RESTful 示例)
```python
接口名称: 用户登录
请求方式: POST
请求地址: /api/v1/auth/login/

请求参数 (application/json):
{
  "username": "testuser",
  "password": "password123"
}

请求头:
Content-Type: application/json

成功返回参数 (200 OK):
{
  "status": 0,
  "msg": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user_info": {
      "id": 1,
      "username": "testuser",
      "nickname": "Test User",
      "email": "test@example.com",
      "role": "user",
      "avatar_url": "http://example.com/avatar.jpg"
    }
  }
}

失败返回参数 (400 Bad Request / 401 Unauthorized):
{
  "status": 1, // 或其他错误码
  "msg": "Incorrect username or password" // 或 "Username is required"
}

失败返回参数 (500 Internal Server Error):
{
  "status": 500,
  "msg": "An unexpected error occurred."
}

```

---

## 七、权限管理设计

### 7.1 权限模型

采用基于角色的访问控制（RBAC）模型。系统预设几个核心角色（普通用户、版主、管理员），每个角色对应一组权限。用户的权限由其被分配的角色决定。

### 7.2 角色与权限映射

*   **普通用户 (user)**：
    *   浏览所有公开板块和帖子。
    *   注册、登录、登出、修改个人信息（头像、昵称、简介、密码）。
    *   发表新帖子、编辑和删除自己的帖子。
    *   发表评论、回复评论、删除自己的评论。
    *   点赞/取消点赞帖子和评论。
    *   收藏/取消收藏帖子。
    *   举报帖子、评论或用户。
    *   查看个人通知、积分、私信。
    *   发送和接收私信。
*   **版主 (moderator)**：
    *   拥有普通用户的所有权限。
    *   管理其负责板块内的帖子：置顶/取消置顶、加精/取消加精。
    *   删除其负责板块内的违规帖子和评论。
    *   审核和处理其负责板块相关的举报（标记为已处理或驳回）。
*   **管理员 (admin)**：
    *   拥有版主的所有权限（通常对所有板块生效）。
    *   用户管理：查看用户列表、查看用户详情、修改用户信息（如角色分配）、封禁/解封用户。
    *   板块管理：创建新板块、编辑板块信息、删除板块。
    *   系统配置管理（如积分规则、敏感词等）。
    *   查看系统日志。
    *   处理所有类型的举报。

### 7.3 接口权限控制

后端将使用装饰器或中间件对每个需要权限的 API 接口进行校验。
*   对于需要登录的接口，检查请求头中 JWT token 的有效性。
*   对于需要特定角色的接口（如版主操作、管理员操作），在校验 token 后，进一步检查用户角色是否满足要求。
*   例如：
    *   `POST /api/v1/posts/`：需要 `user` 或以上角色。
    *   `PUT /api/v1/posts/{post_id}/pin/`：需要 `moderator` (且是该板块版主) 或 `admin` 角色。
    *   `POST /api/v1/boards/`：需要 `admin` 角色。
    *   对于编辑/删除自己内容的操作，除了角色外，还需验证操作者是否为内容所有者。

### 7.4 页面级权限控制

前端根据用户登录后获取的角色信息，动态控制页面元素的显示和可操作性。
*   未登录用户只能看到登录/注册按钮，不能进行发帖、评论等操作。
*   普通用户登录后，可以看到发帖按钮、评论框等，但看不到管理后台入口或版主操作按钮。
*   版主登录后，在其管理的板块下，帖子旁边会显示置顶、加精、删除等操作按钮。
*   管理员登录后，可以看到管理后台入口，并能进行用户管理、板块管理等操作。
*   路由守卫 (Vue Router navigation guards) 用于控制未授权用户访问特定页面（如管理后台页面）。

---

## 八、安全策略

### 8.1 接口安全

*   所有接口限制访问频率（例如使用 `django-ratelimit` 或 Redis 计数），防止暴力破解和DDoS攻击。
*   所有敏感接口（如修改密码、查看个人信息、管理操作）必须在登录后（通过JWT验证）才能访问。
*   所有写操作（创建、修改、删除）统一使用 `POST/PUT/DELETE` HTTP 方法，避免使用 `GET` 方法进行状态变更，防止 CSRF 漏洞利用（尽管JWT本身有一定CSRF防护能力）。
*   对用户输入进行严格校验和清洗，防止恶意数据。

### 8.2 前端安全

*   **防止 XSS (跨站脚本攻击)**：
    *   Vue 默认会对 `{{ }}` 插值进行 HTML 转义。
    *   对于使用 `v-html` 指令输出的内容，确保来源可靠或进行严格的 XSS过滤（如使用 `DOMPurify`）。
    *   用户输入的 Markdown 内容在后端渲染为 HTML 时，使用安全的 Markdown 库并配置适当的过滤规则。
*   **防止 CSRF (跨站请求伪造)**：
    *   JWT token 机制本身通过将 token 存储在 localStorage/sessionStorage 或 HttpOnly Cookie 中，并在请求头中携带，可以有效防止传统基于 Session Cookie 的 CSRF 攻击。
    *   确保后端正确验证 `Authorization` 头。
*   **输入校验**：前端对用户输入进行初步校验（如长度、格式），减轻后端压力，但最终校验必须在后端进行。
*   **HTTPS**：全站使用 HTTPS 保证数据传输过程中的加密。

### 8.3 后端安全

*   **SQL 注入防护**：Django ORM 默认使用参数化查询，能有效防止 SQL 注入。避免直接拼接 SQL 字符串。
*   **权限验证**：在每个需要权限的视图/接口处进行严格的权限检查，确保用户只能访问其被授权的资源和操作。
*   **密码安全**：用户密码使用强哈希算法（如 Django 默认的 PBKDF2，或 Argon2）加盐存储，不存储明文密码。
*   **敏感信息保护**：配置文件中的密钥、数据库密码等敏感信息不应硬编码在代码中，使用环境变量或专门的 secrets 管理工具。
*   **依赖库安全**：定期检查并更新项目依赖的第三方库，修复已知的安全漏洞。
*   **日志记录**：详细记录用户关键操作日志（如登录、修改密码、重要数据操作）、系统错误日志、安全事件日志，便于审计和问题排查。配置异常告警机制。
*   **错误处理**：避免向客户端暴露详细的错误栈信息，返回通用的错误提示。

---

## 九、测试计划

### 9.1 测试环境

*   **开发环境**：开发人员本地环境，使用独立的开发数据库。
*   **测试服务器**：与生产环境配置尽可能一致的独立服务器，部署最新的测试版本。
*   **测试数据库**：使用生产数据库的脱敏副本或专门生成的测试数据集，确保数据隔离和测试的真实性。

### 9.2 测试分类

*   **单元测试 (Unit Testing)**：
    *   针对后端 Django 的 Models, Views (逻辑部分), Services, Utils 等独立函数或类方法。
    *   使用 Django 自带的 `unittest` 模块或 `pytest-django`。
    *   前端 Vue 组件的 props 传递、方法调用、事件触发等，可使用 `Vue Test Utils` 结合 `Jest` 或 `Vitest`。
*   **接口测试 (API Testing)**：
    *   针对后端 RESTful API 进行测试，验证请求参数、响应数据、状态码、权限控制等。
    *   工具：Postman, Insomnia, 或者使用 Python 的 `requests` 库编写自动化脚本。
    *   Swagger/OpenAPI 自动生成的客户端也可用于辅助测试。
*   **UI 测试 / E2E 测试 (End-to-End Testing)**：
    *   模拟真实用户操作流程，从前端界面进行测试，验证整体功能的正确性和用户体验。
    *   初期以人工测试为主，覆盖核心用户场景。
    *   可考虑引入自动化 UI 测试框架，如 Selenium, Cypress, Playwright。
*   **集成测试 (Integration Testing)**：
    *   测试多个模块或服务协同工作的正确性，例如前端调用后端API，后端与数据库的交互。
*   **性能测试 / 压力测试 (Performance/Stress Testing)**：
    *   评估系统在高并发、大数据量情况下的响应时间、吞吐量、资源利用率和稳定性。
    *   工具：Apache JMeter, Locust, k6。
    *   重点测试登录、帖子列表、发帖等高频接口。
*   **安全测试 (Security Testing)**：
    *   检查常见的安全漏洞，如 XSS, SQL注入, CSRF, 权限绕过等。
    *   可借助自动化扫描工具 (如 OWASP ZAP) 和人工渗透测试。
*   **兼容性测试**：
    *   测试前端在不同主流浏览器（Chrome, Firefox, Edge, Safari）和不同分辨率下的显示和功能。

### 9.3 测试内容

*   **功能正确性**：
    *   所有用户故事和功能需求是否按预期实现。
    *   正常流程和异常流程的覆盖。
*   **接口返回正确性**：
    *   请求参数合法/非法时，接口是否返回正确的状态码和数据。
    *   分页、排序、筛选等参数是否按预期工作。
*   **权限控制**：
    *   不同角色的用户是否只能访问其被授权的功能和数据。
    *   未登录用户是否无法访问受限资源。
    *   越权操作是否被正确阻止。
*   **数据校验**：
    *   前端和后端对用户输入的校验是否有效（如必填项、格式、长度、边界值）。
    *   对非法输入的处理是否得当。
*   **异常流程测试**：
    *   Token 过期、无效 Token 的处理。
    *   网络错误、服务器内部错误的处理。
    *   数据库连接失败等场景。
*   **用户体验**：
    *   页面加载速度、响应时间。
    *   交互是否流畅、提示信息是否清晰。
*   **非功能需求满足度**：
    *   系统响应时间是否小于1s。
    *   页面是否支持1080p及以上分辨率。
    *   Markdown 编辑器功能是否正常。

---

## 十、部署方案

### 10.1 前端部署 (Vue)

1.  **构建项目**：
    *   在前端项目根目录下执行 `npm run build` (或 `yarn build`)。
    *   这会在 `dist/` 目录下生成优化和压缩后的静态资源文件 (HTML, CSS, JavaScript, 图片等)。
2.  **Nginx 配置**：
    *   将 `dist/` 目录下的所有文件上传到服务器的指定静态资源目录 (例如 `/var/www/forum_frontend`)。
    *   配置 Nginx 作为静态资源服务器，并处理前端路由（SPA应用的History模式）。
    ```nginx
    server {
        listen 80;
        server_name your_domain.com; # 替换为你的域名或IP
    
        root /var/www/forum_frontend; # 前端文件存放路径
        index index.html;
    
        location / {
            try_files $uri $uri/ /index.html; # 处理Vue Router的History模式
        }
    
        # API 代理 (详见后端部署)
        location /api/ {
            proxy_pass http://127.0.0.1:8000; # Gunicorn 运行的地址和端口
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    
        # 可选：其他静态资源优化，如gzip压缩、缓存控制
        location ~* \.(?:css|js|jpg|jpeg|gif|png|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1M; # 缓存1个月
            add_header Cache-Control "public";
        }
    }
    ```

### 10.2 后端部署 (Django)

1.  **环境准备**：
    *   在 Linux (Ubuntu) 服务器上安装 Python, pip, virtualenv。
    *   创建并激活虚拟环境：
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   安装项目依赖：`pip install -r requirements.txt`
    *   安装 Gunicorn 和 Supervisor：`pip install gunicorn supervisor`
2.  **Gunicorn 配置**：
    *   Gunicorn 是一个 Python WSGI HTTP Server，用于运行 Django 应用。
    *   启动 Gunicorn 的命令示例 (通常通过 Supervisor 管理)：
        ```bash
        gunicorn project_name.wsgi:application \
            --workers 3 \
            --bind 0.0.0.0:8000 \
            --chdir /path/to/your/django_project
        ```
        *   `project_name.wsgi:application`: Django 项目的 WSGI 应用路径。
        *   `--workers`: Gunicorn worker 进程数量，通常设置为 `2 * CPU核心数 + 1`。
        *   `--bind`: Gunicorn 监听的地址和端口，Nginx 会将请求代理到这里。
        *   `--chdir`: Django 项目的根目录。
3.  **Supervisor 配置**：
    *   Supervisor 是一个进程管理工具，用于监控和控制 Gunicorn 进程（如自动重启）。
    *   创建 Supervisor 配置文件 (例如 `/etc/supervisor/conf.d/forum_backend.conf`):
        ```ini
        [program:forum_backend]
        command=/path/to/your/venv/bin/gunicorn project_name.wsgi:application --workers 3 --bind 127.0.0.1:8000 --chdir /path/to/your/django_project
        directory=/path/to/your/django_project
        user=your_user # 运行 Gunicorn 的用户
        autostart=true
        autorestart=true
        stderr_logfile=/var/log/supervisor/forum_backend_err.log
        stdout_logfile=/var/log/supervisor/forum_backend_out.log
        environment=DJANGO_SETTINGS_MODULE="project_name.settings.production" # 指定生产环境配置
        ```
    *   加载并启动 Supervisor 配置：
        ```bash
        sudo supervisorctl reread
        sudo supervisorctl update
        sudo supervisorctl start forum_backend
        ```
4.  **Nginx 代理**：
    *   如 10.1 中 Nginx 配置所示，将 `/api/` 路径下的请求代理到 Gunicorn 监听的地址和端口。
    *   Nginx 同时处理静态资源（Django 的 `collectstatic` 收集的静态文件，如 admin 后台样式）和媒体文件（用户上传的文件）。
        ```nginx
        # (在 server block 中添加)
        location /static/ { # Django collectstatic 后的静态文件
            alias /path/to/your/django_project/staticfiles/;
        }
        
        location /media/ { # 用户上传的媒体文件
            alias /path/to/your/django_project/media/;
        }
        ```
5.  **Django 配置**：
    *   确保 `settings.py` (或生产环境的 `settings_production.py`) 配置正确：
        *   `DEBUG = False`
        *   `ALLOWED_HOSTS = ['your_domain.com', 'www.your_domain.com']`
        *   配置数据库连接到生产数据库。
        *   配置 `STATIC_URL`, `STATIC_ROOT`, `MEDIA_URL`, `MEDIA_ROOT`。
    *   运行数据库迁移：`python manage.py migrate`
    *   收集静态文件：`python manage.py collectstatic`

### 10.3 数据库配置 (MySQL)

1.  **安装与配置**：
    *   在服务器上安装 MySQL 8.x。
    *   创建 `forum_db` 数据库和专用用户，并授予权限。
        ```sql
        CREATE DATABASE forum_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        CREATE USER 'forum_user'@'localhost' IDENTIFIED BY 'your_strong_password';
        GRANT ALL PRIVILEGES ON forum_db.* TO 'forum_user'@'localhost';
        FLUSH PRIVILEGES;
        ```
    *   如果 Django 应用和数据库不在同一台服务器，需要允许远程访问（修改 `bind-address` 为 `0.0.0.0` 或特定IP，并确保防火墙允许对应端口）。
2.  **定期备份**：
    *   设置定时任务 (如 cron job) 使用 `mysqldump` 定期备份数据库到安全的位置。
    *   示例备份脚本：
        ```bash
        #!/bin/bash
        DB_USER="forum_user"
        DB_PASS="your_strong_password"
        DB_NAME="forum_db"
        BACKUP_DIR="/path/to/backups"
        DATE=$(date +"%Y-%m-%d_%H-%M-%S")
        FILENAME="$BACKUP_DIR/$DB_NAME-$DATE.sql.gz"
        
        mysqldump -u $DB_USER -p$DB_PASS $DB_NAME | gzip > $FILENAME
        # 可选：删除旧备份，例如只保留最近7天的
        find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +7 -delete
        ```
3.  **性能优化**：
    *   根据服务器资源调整 MySQL 配置参数 (如 `innodb_buffer_pool_size`)。
    *   定期分析和优化慢查询。

---

## 十一、扩展功能设计

### 11.1 积分 / 等级系统

**说明：**

1.  用户通过在论坛的积极行为（如发帖、回帖、帖子被点赞等）获得积分。
2.  积分累计到一定阈值后，用户等级自动提升。
3.  管理员或系统可以配置积分获取和扣除的规则。

**功能：**

1.  **等级与积分显示**：在用户信息区域（如个人主页、帖子作者信息旁）显示用户的当前等级图标和积分数。
2.  **积分变动记录**：用户可以查看自己的积分获取和消费历史记录，了解每次积分变动的原因和数量。
3.  **后台积分规则配置**：管理员可以在后台管理界面设置不同行为对应的积分值（增加或减少），以及等级晋升所需的积分阈值。
4.  **等级权益** (可选)：不同等级的用户可以拥有不同的特权，如每日发帖上限、特殊徽章、访问特定板块等。

**示例积分规则：**

| 行为          | 积分变动 | 备注                               |
| ------------- | -------- | ---------------------------------- |
| 每日登录      | +1       | 每日首次登录                       |
| 发表帖子      | +10      |                                    |
| 发表回复      | +2       |                                    |
| 帖子被他人回复 | +1       | 每条有效回复，作者获得             |
| 帖子被他人点赞 | +2       | 每个赞，作者获得                   |
| 评论被他人点赞 | +1       | 每个赞，评论者获得                 |
| 帖子被设为精华 | +50      | 作者获得                           |
| 帖子被置顶    | +20      | 作者获得，按天或一次性             |
| 举报被采纳    | +5       | 举报者获得                         |
| 帖子被删除(违规)| -20      | 作者被扣除                         |
| 评论被删除(违规)| -5       | 评论者被扣除                       |

**数据库表关联：** `user_points` 表（已在数据库设计章节中定义）用于存储用户的总积分。积分变动记录可以设计新表 `point_logs` (user\_id, change\_amount, reason, created\_at)。

### 11.2 私信聊天功能

**功能说明：**

1.  **点对点私信**：允许注册用户之间进行一对一的私密文字聊天。
2.  **消息列表**：用户拥有一个私信列表，按最近联系人或最近消息时间排序，显示联系人昵称、头像、最后一条消息摘要以及未读消息数。
3.  **聊天界面**：点击消息列表中的联系人进入与该用户的聊天界面，可以发送新消息，并以对话气泡形式展示聊天记录（滚动加载历史消息）。
4.  **消息状态管理**：标记消息的已读/未读状态。当用户打开与某人的聊天界面时，该对话的未读消息应自动标记为已读。
5.  **实时推送 (可选增强)**：新消息到达时，可以通过 WebSocket 实现实时推送到接收方客户端，并在界面上给出提示（如小红点、桌面通知）。若不使用 WebSocket，则通过轮询或用户主动刷新获取新消息。

**核心页面：**

1.  **私信列表页 (`/messages/`)**：
    *   展示所有有过私信往来的对话列表。
    *   每个对话项显示对方用户名、头像、最后一条消息内容摘要、最后消息时间、未读消息数。
    *   按最后消息时间降序排列。
2.  **聊天详情页 (`/messages/{user_id}/` 或 `/chat/{conversation_id}/`)**：
    *   顶部显示聊天对象的用户名。
    *   中间区域显示聊天记录，支持向上滚动加载更多历史消息。
    *   底部为文本输入框和发送按钮。

**后端建议：**

1.  **数据库表**：`private_messages` 表（已在数据库设计章节中定义）。
2.  **索引优化**：
    *   在 `private_messages` 表的 `sender_id` 和 `receiver_id` 上建立联合索引或各自建立索引，以优化查询特定两人之间的聊天记录。
    *   例如：`INDEX idx_conversation (LEAST(sender_id, receiver_id), GREATEST(sender_id, receiver_id), created_at)` 可以高效查询两人对话并按时间排序。
    *   `INDEX idx_receiver_read (receiver_id, is_read)` 用于快速查询用户的未读消息。
3.  **未读消息数缓存**：用户的总未读消息数或每个对话的未读消息数可以考虑使用 Redis 缓存，以减少数据库查询压力，特别是在消息列表页。当发送新消息或用户已读消息时更新缓存。
4.  **API 设计**：
    *   `GET /api/v1/messages/conversations/`：获取当前用户的对话列表。
    *   `GET /api/v1/messages/conversations/{user_id}/`：获取与特定用户的聊天记录（分页）。
    *   `POST /api/v1/messages/conversations/{user_id}/`：向特定用户发送消息。
    *   `PUT /api/v1/messages/conversations/{user_id}/read/`：标记与特定用户的消息为已读。

### 11.3 Elasticsearch 全文搜索功能

**功能目标：**

1.  **广泛搜索范围**：支持对论坛内的帖子标题、帖子正文内容、评论内容进行快速、准确的全文关键词搜索。
2.  **实时/准实时同步**：MySQL 中的帖子和评论数据发生变更（创建、更新、删除）时，能够较快地同步到 Elasticsearch 索引中，保证搜索结果的时效性。
3.  **高级搜索特性**：
    *   **关键词高亮**：在搜索结果中高亮显示匹配的关键词。
    *   **相关度排序**：搜索结果默认按与关键词的相关度进行排序。
    *   **结果摘要**：展示包含关键词的上下文片段。
    *   **(可选)** 按时间、板块等条件过滤和排序搜索结果。

**技术路径：**

1.  **Elasticsearch (ES)**：选择合适的 Elasticsearch 版本并部署。
2.  **Django-ES 集成库**：使用 `django-elasticsearch-dsl` 库，它简化了 Django Models 与 Elasticsearch 索引之间的映射和同步。
3.  **定义索引 (Document)**：
    *   为 `Post` Model 创建一个对应的 `PostDocument`，指定需要索引的字段：
        *   `title` (帖子标题)
        *   `content` (帖子正文，可能需要处理 HTML 或 Markdown)
        *   `author_username` (发帖用户名，用于按作者搜索)
        *   `board_name` (所属板块名称，用于按板块过滤)
        *   `created_at` (创建时间，用于按时间排序/过滤)
    *   (可选) 为 `Comment` Model 创建 `CommentDocument`，索引 `content`, `author_username`, `post_id`。
4.  **数据同步策略**：
    *   **信号 (Signals)**：监听 Django Model 的 `post_save` 和 `post_delete` 信号。当帖子或评论被创建、更新或删除时，自动触发相应的 ES 索引更新操作。这是比较实时的方案。
    *   **定时任务 (Celery/Cron)**：定期执行脚本，扫描数据库中自上次同步以来发生变化的数据，并批量更新到 ES。适用于对实时性要求不高或数据量非常大的场景。
    *   **首次数据导入**：提供管理命令将现有数据库中的所有相关数据导入到 ES 索引中。

**搜索接口：**

*   **请求方式**: `GET`
*   **请求地址**: `/api/v1/search/`
*   **请求参数**:
    *   `q` (string, required): 搜索关键词。
    *   `type` (string, optional, default='post'): 搜索类型，如 `post`, `comment`, `all`。
    *   `board_id` (integer, optional): 按板块ID过滤 (如果 `type` 包含 `post`)。
    *   `page` (integer, optional, default=1): 分页页码。
    *   `page_size` (integer, optional, default=10): 每页数量。
    *   `sort_by` (string, optional, default='relevance'): 排序方式，如 `relevance`, `newest`, `oldest`。
*   **返回示例 (搜索帖子)**:
    ```json
    {
      "status": 0,
      "msg": "Search successful",
      "data": {
        "total_hits": 120,
        "page": 1,
        "page_size": 10,
        "results": [
          {
            "id": 101,
            "title": "关于 <mark>Django</mark> 性能优化的几点建议",
            "content_snippet": "...本文将探讨几种提升 <mark>Django</mark> 应用性能的实用方法...",
            "author_username": "expert_user",
            "board_name": "技术分享",
            "created_at": "2023-10-26T10:00:00Z",
            "views": 1500,
            "likes_count": 80,
            "comments_count": 15,
            "url": "/posts/101/" // 前端跳转链接
          },
          // ... more results
        ]
      }
    }
    ```

**搜索结果展示字段（前端考虑）：**

*   帖子标题（高亮匹配的关键词）。
*   内容摘要（截取包含关键词的部分正文，并高亮关键词）。
*   作者用户名、发布时间。
*   所属板块。
*   帖子的浏览量、点赞数、评论数。
*   指向原帖子/评论的链接。

### 11.4 日志与审计

**日志类型：**

1.  **用户操作日志 (User Activity Logs)**：
    *   记录普通用户在前端执行的关键操作。
    *   **示例**：用户登录、用户注册、用户登出、发表帖子、编辑帖子、删除帖子、发表评论、删除评论、点赞、收藏、举报、修改个人资料、修改密码。
    *   **包含信息**：操作用户ID/用户名、操作时间、操作类型、操作对象ID（如帖子ID）、用户IP地址、User-Agent。
2.  **管理后台操作日志 (Admin Action Logs)**：
    *   记录版主和管理员在后台管理系统中执行的操作。
    *   **示例**：管理员登录后台、用户封禁/解封、角色分配、板块创建/修改/删除、帖子置顶/加精/删除（管理员操作）、举报处理。
    *   **包含信息**：操作管理员ID/用户名、操作时间、操作类型、操作对象ID/描述、操作参数、IP地址。Django Admin 自带 `LogEntry` 模型可用于此。
3.  **系统运行日志 (Application Logs)**：
    *   记录应用程序运行时的状态信息、警告和错误。
    *   **级别**：DEBUG, INFO, WARNING, ERROR, CRITICAL。
    *   **示例**：服务启动/停止、数据库连接状态、第三方服务调用情况、未捕获的异常堆栈信息、性能瓶颈警告。
    *   通常由 Django 的 logging 模块配置输出到文件或日志管理系统。
4.  **API 请求日志 (Access Logs)**：
    *   记录所有对后端 API 的请求。
    *   **示例**：Nginx 或 Gunicorn 的访问日志。
    *   **包含信息**：请求时间、请求方法、请求URL、状态码、响应时间、客户端IP、User-Agent、Referer。

**审计用途：**

1.  **系统问题溯源**：
    *   当系统出现故障或异常行为时，通过分析错误日志和系统运行日志，快速定位问题原因和发生点。
    *   追踪特定请求的处理流程，排查数据不一致等问题。
2.  **安全事件分析与违规行为定位**：
    *   通过用户操作日志和管理后台操作日志，追踪可疑操作，如未授权访问尝试、批量恶意注册、恶意发帖等。
    *   在发生安全事件（如账户被盗、数据泄露）后，提供调查线索，确定影响范围。
    *   对用户举报的违规行为，结合操作日志进行核实和处理。
3.  **合规性与责任认定**：
    *   对于敏感操作（如数据删除、用户封禁），日志可以作为操作凭证，明确操作责任人。
    *   满足特定行业或法律法规对日志记录和审计的要求。
4.  **系统优化与行为分析**：
    *   通过分析 API 请求日志和用户操作日志，了解用户行为模式、高频操作、系统瓶颈，为系统优化和功能改进提供数据支持。
    *   统计用户活跃度、功能使用频率等。

**实现考虑：**

*   **日志存储**：
    *   小型系统可直接存入数据库（如 `logs` 表，已在数据库设计中定义）。
    *   中大型系统建议使用专门的日志管理系统，如 ELK Stack (Elasticsearch, Logstash, Kibana) 或 Graylog，便于集中存储、查询和分析。
*   **日志格式**：采用结构化日志格式（如 JSON），方便机器解析和查询。
*   **日志级别**：合理配置日志级别，确保在生产环境中不会记录过多不必要的 DEBUG 信息，同时能捕获所有重要的 WARNING 和 ERROR 信息。
*   **敏感信息处理**：日志中避免记录明文密码、Token 等高度敏感信息，或进行脱敏处理。
*   **日志轮转与归档**：配置日志文件的自动轮转 (log rotation) 和定期归档，防止日志文件过大占用过多磁盘空间。
