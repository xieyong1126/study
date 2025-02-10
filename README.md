# study
启动supervisord管理的所有进程    supervisorctl restart all
supervisorctl start all
停止supervisord管理的所有进程
supervisorctl stop all
启动supervisord管理的某一个特定进程
supervisorctl start program-name // program-name为[program:xx]中的xx
停止supervisord管理的某一个特定进程
supervisorctl stop program-name  // program-name为[program:xx]中的xx
重启所有进程或所有进程
supervisorctl restart all // 重启所有supervisorctl reatart program-name // 重启某一进程，program-name为[program:xx]中的xx
查看supervisord当前管理的所有进程的状态
supervisorctl status

fuser -v -n tcp 端口号   查看占用端口的进程

切换到远程新分支
sudo git pull
sudo git checkout -b develop_v3.1.9 origin/develop_v3.1.9


控制台:document.body.contentEditable='true' 复制
virtualenv C:\Users\admin\Desktop\venv\ten    新建Python虚拟环境
virtualenv C:\Users\admin\Desktop\venv\ten --python=/path/to/python3.8
net start mysql  启动本地Mysql

日志，控制台debug模式，查看sql语句
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'propagate': True,
            'level':'DEBUG',
        },
    }
}


free -m 查看内存
df -m 查看磁盘(MB)
cat /proc/cpuinfo 查看cpu
cat filename | tail -n 10     显示文件最后10行
cat filename | head -n 10  显示文件前面10行
#cat filename | tail -n 10  从10行开始显示，显示10行以后的所有行
cat filename | head -n 50 | tail -n 10  前50的后10行，即40行到50行

grep -E "INFO|ERROR"
grep -W "INFO|ERROR"
stat filepath  查看文件大小
tree -h | grep exec


# 可以直接基于这两个文件构建自定义镜像并管理
docker-compose -f 指定配置文件 up -d
# 如果自定义镜像不存在，会帮助我们创建，如果已经存在会直接运行这个镜像
# 如果想重新构建
docker-compose build
# 运行时重新构建
docker-compose up -d --build
# 1. 使用yml文件启动管理的容器
docker-compose up -d
# 2. 关闭并删除容器
docker-compose down
# 3. 开启|关闭|重启由yml维护的容器
docker-compose start|stop|restart
# 4. 查看yml管理的容器
docker-compose ps
# 5. 查看日志
docker-compose logs -f


# 先构建
docker-compose build
# 再重启生效
docker-compose restart

sz  下载文件  上传rz
# tar -czvf test.tar.gz a.c   //压缩 a.c文件为test.tar.gz
# tar -xzvf test.tar.gz 


复制
javascript:document.body.contentEditable='true';document.designMode='on'; void 0

查找文件
find ./ -name henginex_manager -type d

目录大小
du -sh ./xxx  xxx目录大小
du -sh ./*    当前目录下所有目录大小

pychram
 ctrl + r   替换
 ctrl + shift + f  全局搜索文本
 
 find / -name xxx.sh -type f
 
 
git merge --abort 取消合并
git reflog  git reset --hard ae5244a8退回
 
1.git log //找到你的日志commit号为22dfbf1f907764c5ae70381b8191104f9af21d8c
2.git checkout 22dfbf1f907764c5ae70381b8191104f9af21d8c //切换到这个commit下
3.git checkout -b dev_2.0 22dfbf1f907764c5ae70381b8191104f9af21d8c //在本地新建一个dev_2.0分支
4.git branch //查看分支
5.git push --set-upstream origin dev_2.0 //将本地dev_2.0分支推到远程

回退
# 查看当前的提交历史
git log
# 执行回退操作，将代码回退到指定的commit
git reset <commit>
# 将回退后的代码推送到远程仓库
git push origin <branch> --force


apt-get update
apt-get install -y git
mkdir -p video-plugins/shared-envs
pip install virtualenv
virtualenv video-shot-algo-static
./bin/pip3 install ./../../../video_complex_algos-1.0.0.tar.gz

git clone -b 分支名 地址

liunx 定时任务
crontab -l  查看任务
crontab -e   添加任务
*/2 * * * * LANG_ALL=zh_cn.UTF-8 /usr/local/bin/python /data/webapp/ten-backstage/manage.py runcrons >> /tmp/ten-crontab.log 2>&1
*/2 * * * * export TAAS_ENV="Test"; /usr/local/bin/python /data/webapp/ten-backstage/manage.py runcrons >> /tmp/ten-crontab.log 2>&1
*/2 * * * * export TAAS_ENV="Prd"; /usr/local/bin/python /data/webapp/ten-backstage/manage.py runcrons >> /tmp/ten-crontab.log 2>&1


查看文件夹大小
du -sh dir_path
nproc  查看cpu核心数


mysql
查看binlog
.\bin\mysqlbinlog --no-defaults --base64-output=decode-rows -v   .\data\binlog.000066
加上时间过滤
mysqlbinlog --no-defaults --base64-output=decode-rows -v --start-datetime='2024-04-20 13:20:00' --stop-datetime='2024-04-20 15:00:00'   ../data/mysql-bin.000002 



要将Docker镜像推送到Sonatype Nexus Repository Manager，你可以按照以下步骤进行操作：
登录到Nexus Repository Manager：首先，使用你的浏览器访问Nexus Repository Manager的Web界面，并使用你的凭据登录。
创建Docker仓库：如果尚未创建Docker仓库，你需要在Nexus Repository Manager中创建一个用于存储Docker镜像的仓库。在Nexus的界面中，找到仓库管理部分，按照指引创建一个Docker仓库。
登录Docker Registry：在本地环境中，使用docker login命令登录到Nexus Repository Manager的Docker Registry。命令格式如下：
docker login <nexus-registry-url> -u <username> -p <password>
其中<nexus-registry-url>是Nexus Repository Manager的Docker Registry地址，<username>和<password>是你在Nexus Repository Manager中的凭据。
打标签（Tag）镜像：在本地环境中，使用docker tag命令为你的Docker镜像打上Nexus Repository Manager中仓库的标签。命令格式如下：
docker tag <local-image> <nexus-registry-url>/<repository-name>/<image-name>:<tag>
其中<local-image>是本地镜像的名称，<nexus-registry-url>是Nexus Repository Manager的Docker Registry地址，<repository-name>是你在Nexus Repository Manager中创建的Docker仓库名称，<image-name>是你想要为镜像指定的名称，<tag>是标签。
推送镜像：使用docker push命令将标记的镜像推送到Nexus Repository Manager的Docker Registry。命令格式如下：
docker push <nexus-registry-url>/<repository-name>/<image-name>:<tag>
这将会将你的Docker镜像推送到Nexus Repository Manager的Docker仓库中。
