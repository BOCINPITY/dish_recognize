# 创建并且激活虚拟环境
python版本>=3.8.0,版本不要太高
```bash
python -m venv .venv
```
# linux
```bash
source .venv/bin/activate
```

# windows
```bash
.venv/Scripts/activate
```

# 依赖安装
```bash
pip install --upgrade pip && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

# 运行
如果直接python run.py，项目运行起来会在控制台不断打印警告信息，经过排查，是yolov5本身的问题
```bash
PYTHONWARNINGS=ignore::FutureWarning python run.py
```
