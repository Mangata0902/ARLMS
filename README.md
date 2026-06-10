# 🎓 知己 ScholarMate (ARLMS)

**学术论文 AI 管理与辅助平台** (Academic Research Literature Management System)
基于 Python / PostgreSQL / Vue 构建的全栈平台，深度集成 AI 能力，为科研工作者提供智能化的文献阅读与管理体验。

## ✨ 主要功能 (Features)
- **🤖 AI 导师对话**：基于知识库与上传的文献，深度解析研究方法与结论。
- **📝 大纲生成与论文修改**：快速生成结构化论文大纲，辅助论文润色与 AI 文本检测。
- **📚 智能文献管理**：便捷上传、分类、检索你的专属学术文献库。
- **💬 历史对话追踪**：自动保存与 AI 的学术探讨记录，随时回顾灵感。

<img width="2850" height="1454" alt="image" src="https://github.com/user-attachments/assets/4857cab9-c748-475f-bd38-f62a64371864" />

---

## ⚠️ 极其重要的初始配置 (Important Notice)

> **⛔ 注意：系统没有开放自由注册，首次启动前必须手动创建初始管理员账号！**
> 
> 在完成数据库连接配置后，请务必在你的 `arlms_db` 数据库的 user（用户）表中，插入以下默认账号信息，否则**将无法登录系统主页面**：
> - **默认登录邮箱：** `admin@admin.com`
> - **默认登录密码：** `Admin123456!`

---

## 🚀 快速启动指南 (Getting Started)

### 1. 环境准备 (Prerequisites)
- **Python** 3.9+
- **Node.js** 16+
- **PostgreSQL** 数据库 (需在本地或服务器上手动创建一个名为 `arlms_db` 的空数据库)

## 2. 后端服务启动（Backend Setup）

### 2.1 进入后端目录

```bash
cd backend
```

### 2.2 创建并激活虚拟环境

创建虚拟环境：

```bash
python -m venv venv
```

Windows 系统激活命令：

```bash
venv\Scripts\activate
```

Mac/Linux 系统激活命令：

```bash
source venv/bin/activate
```

### 2.3 安装后端依赖

```bash
pip install -r requirements.txt
```

### 2.4 配置数据库

请修改 `config.py` 或核心配置文件中的数据库连接 URL，使其指向你本地的 `arlms_db`。

### 2.5 启动后端服务

作为模块运行主程序：

```bash
python -m app.main
```

---

## 3. 前端服务启动（Frontend Setup）

### 3.1 进入前端目录

另开一个终端窗口，进入前端目录：

```bash
cd frontend
```

### 3.2 安装前端依赖

```bash
npm install
```

### 3.3 启动开发服务器

```bash
npm run dev
```

---

## 4. 访问系统

服务全部启动后，打开浏览器访问前端终端提示的网址，通常是：

```text
http://localhost:5173
```

输入上方配置好的默认管理员账号与密码，即可开启你的 AI 科研之旅！
