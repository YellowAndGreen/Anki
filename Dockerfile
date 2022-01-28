FROM alpine:3.13

# 选用国内镜像源以提高下载速度
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tencent.com/g' /etc/apk/repositories \
&& apk add --update --no-cache python3 py3-pip \
&& rm -rf /var/cache/apk/* \
&& apk add zlib1g-dev \
&& apk add liblzo2-dev

# 拷贝当前项目到/app目录下
COPY . /app

# 设定当前的工作目录
WORKDIR /app

# 安装依赖到指定的/install文件夹
# 选用国内镜像源以提高下载速度
RUN pip config set global.index-url http://mirrors.cloud.tencent.com/pypi/simple \
&& pip config set global.trusted-host mirrors.cloud.tencent.com \
&& pip install --upgrade pip \
# pip install scipy 等数学包失败，可使用 apk add py3-scipy 进行， 参考安装 https://pkgs.alpinelinux.org/packages?name=py3-scipy&branch=v3.13
&& pip install --user -r requirements.txt

# 设定对外端口
EXPOSE 80

# 设定启动命令
CMD ["python3", "manage.py", "runserver", "0.0.0.0:80"]