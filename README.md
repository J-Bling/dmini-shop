# Mini Shop API

一个基于 Python FastAPI 构建的轻量电商后端 API 项目，用于学习和实践后端开发。

## 技术栈

| 技术 | 用途 |
|------|------|
| **Python 3.11+** | 运行语言 |
| **FastAPI** | Web 框架 |
| **SQLAlchemy 2.x** | ORM 数据库操作 |
| **SQLite** | 数据库（开发环境，可无缝切换 MySQL） |
| **JWT** | 用户认证（python-jose） |
| **bcrypt** | 密码加密 |
| **Alembic** | 数据库迁移（预留） |

## 项目结构

```
mini_shop/
├── app/
│   ├── main.py              # 应用入口
│   ├── config.py             # 配置
│   ├── database.py           # 数据库连接
│   ├── models/               # 数据模型
│   │   ├── user.py           # 用户
│   │   ├── product.py        # 商品 + 分类
│   │   ├── cart.py           # 购物车
│   │   ├── order.py          # 订单
│   │   └── payment.py        # 支付记录
│   ├── schemas/              # 请求/响应数据校验
│   ├── routers/              # API 路由
│   ├── services/             # 业务逻辑
│   │   └── payment/          # 支付系统（策略模式）
│   │       ├── base.py       # 支付渠道基类
│   │       └── channels/     # 各支付渠道实现
│   └── core/                 # 核心工具
│       ├── security.py       # JWT + 密码
│       ├── dependencies.py   # 依赖注入
│       └── logging_config.py # 日志配置
├── logs/                     # 日志文件
├── venv/                     # Python 虚拟环境
├── requirements.txt
└── README.md
```

## 快速开始

```bash
# 1. 进入项目目录
cd mini_shop

# 2. 创建虚拟环境（如已存在则跳过）
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Mac / Linux:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 启动服务
uvicorn app.main:app --reload --port 8000

# 6. 打开浏览器访问
# API 文档: http://127.0.0.1:8000/docs
# 健康检查: http://127.0.0.1:8000/health
```

## API 接口一览

### 用户
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/users/register` | 注册 |
| POST | `/api/users/login` | 登录（返回 JWT） |
| GET | `/api/users/me` | 获取当前用户信息 |
| PUT | `/api/users/me` | 修改个人信息 |

### 分类
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/categories` | 创建分类 |
| GET | `/api/categories` | 分类列表 |
| GET | `/api/categories/{id}` | 分类详情 |
| PUT | `/api/categories/{id}` | 修改分类 |
| DELETE | `/api/categories/{id}` | 删除分类 |

### 商品
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/products` | 创建商品 |
| GET | `/api/products` | 商品列表（支持分类筛选、关键词搜索、分页） |
| GET | `/api/products/{id}` | 商品详情 |
| PUT | `/api/products/{id}` | 修改商品 |
| DELETE | `/api/products/{id}` | 删除商品 |

### 购物车
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/cart/items` | 添加商品 |
| GET | `/api/cart` | 查看购物车 |
| PUT | `/api/cart/items/{id}` | 修改数量 |
| DELETE | `/api/cart/items/{id}` | 删除商品 |
| DELETE | `/api/cart` | 清空购物车 |

### 订单
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/orders` | 创建订单（从购物车生成） |
| GET | `/api/orders` | 订单列表 |
| GET | `/api/orders/{id}` | 订单详情 |
| POST | `/api/orders/{id}/cancel` | 取消订单 |
| POST | `/api/orders/{id}/pay` | 发起支付 |

### 支付
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/pay/orders/{id}` | 发起支付（选择渠道） |
| POST | `/api/pay/callback/{channel}` | 支付回调入口 |
| GET | `/api/pay/{pay_no}/status` | 查询支付状态 |

## 核心设计

### 订单状态流转

```
pending → paid → shipped → delivered → completed
pending → cancelled
```

### 支付系统设计（策略模式）

```
PaymentService（统一入口）
    ├── MockPayChannel（模拟支付，当前使用）
    ├── AlipayChannel（预留）
    └── WeChatChannel（预留）
```

扩展新支付方式只需新增一个 Channel 类并注册一行代码。

### 价格单位

所有金额以 **分** 为单位存储（`int`），避免浮点数精度问题。

## 日志

服务器日志自动滚动存储于 `logs/app.log`，每个文件最大 5MB，保留最近 5 份。

```log
[2026-06-03 15:34:39] INFO  app.main | GET /health → 200 (2ms)
[2026-06-03 15:35:26] INFO  app.main | POST /api/users/register → 200 (792ms)
```

## License

MIT
