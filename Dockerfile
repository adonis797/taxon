# Dockerfile.windows
FROM mcr.microsoft.com/windows/servercore:ltsc2019

# 安装 Python（需要手动下载安装）
# 或者使用预构建的 Python Windows 镜像

# 复制项目文件
COPY . /app
WORKDIR /app

# 安装依赖和 PyInstaller
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 打包
RUN pyinstaller taxon.spec