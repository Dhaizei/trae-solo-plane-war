# 飞机大战游戏

这是一个使用Python和Pygame开发的简单飞机大战游戏。

## 游戏说明

在游戏中，玩家控制一架飞机在屏幕底部移动，躲避敌机并射击它们。每击落一架敌机可以获得10分。玩家有3条生命，被敌机撞击后会失去一条生命，当生命值为0时游戏结束。

## 操作方法

- 方向键：控制飞机移动
- 空格键：发射子弹/开始游戏
- ESC键：退出游戏

## 安装与运行

本项目推荐使用 `uv` 进行环境管理，它是一个快速的Python包管理器。

### 方法一：使用 uv（推荐）

#### 1. 安装 uv

如果您还没有安装 uv，请访问 [uv官网](https://docs.astral.sh/uv/) 或使用以下命令安装：

```bash
# 在 Linux/macOS 上
curl -LsSf https://astral.sh/uv/install.sh | sh

# 在 Windows 上
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或者使用 pip 安装
pip install uv
```

#### 2. 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境（会自动使用 .python-version 中指定的Python版本）
uv venv

# 激活虚拟环境
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 安装项目依赖
uv pip install -e .

# 或者直接同步依赖（推荐）
uv sync
```

#### 3. 运行游戏

```bash
# 在激活的虚拟环境中运行
python main.py

# 或者使用 uv 直接运行
uv run python main.py
```

#### 4. 安装可选依赖

```bash
# 安装音频处理相关依赖
uv pip install -e ".[audio]"

# 安装开发依赖
uv pip install -e ".[dev]"
```

### 方法二：使用传统 pip

#### 安装依赖

```bash
pip install pygame numpy

# 可选：安装音频处理依赖
pip install scipy
```

#### 运行游戏

```bash
python main.py
```

## 游戏特性

- 玩家飞机可以上下左右移动
- 敌机随机生成并向下移动
- 玩家可以发射子弹击落敌机
- 击落敌机后有爆炸效果
- 玩家被敌机撞击后有短暂的无敌时间
- 游戏有分数和生命系统

## 开发说明

### 开发环境设置

```bash
# 安装开发依赖
uv sync --extra dev

# 代码格式化
uv run black .

# 代码检查
uv run flake8 .

# 类型检查
uv run mypy .

# 运行测试
uv run pytest
```

### uv 常用命令

```bash
# 添加新依赖
uv add package-name

# 添加开发依赖
uv add --dev package-name

# 更新依赖
uv lock --upgrade

# 查看依赖树
uv tree

# 运行脚本
uv run python script.py
```

## 文件结构

- `main.py`: 游戏主程序和主循环
- `sprites.py`: 游戏中的各种精灵类（玩家飞机、敌机、子弹等）
- `sounds.py`: 音效管理系统
- `create_resources.py`: 创建游戏资源的脚本
- `pyproject.toml`: 项目配置文件（依赖、元数据、工具配置）
- `.python-version`: 指定Python版本
- `resources/`: 游戏资源目录
  - `images/`: 游戏图像资源
  - `sounds/`: 游戏音效资源