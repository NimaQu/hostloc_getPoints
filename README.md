# skyeysnow_getPoints

从 [hostloc 获取积分](https://github.com/Jox2018/hostloc_getPoints)修改来的：

小鸡自动登录 skyeysnow 获取金币

**第一步**下载下列代码
https://github.com/NimaQu/skyeysnow_getPoints/blob/main/skyeysnow_auto_get_points.py

复制 config.example.py 为 config.py 并填写

```
username = "账户"
password = "密码"
user_agent = "自定义 user_agent"
```

**第三步**上面文件上传到小鸡

**第四步**在小鸡里新建crontab任务

```
crontab -e
```


添加

```shell
10 2 * * * sleep 5;cd /root/hostloc/ && /usr/local/bin/python3 /root/skyeysnow/skyeysnow_auto_get_points.py
```

/root/skyeysnow/为你上传的路径
/usr/local/bin/python3为你小鸡python3的引用路径

**提示**

1.如果提示以下错误

```python
Traceback (most recent call last):
  File "/root/skyeysnow/skyeysnow_auto_get_points.py", line 6, in
   ...
```

请安装request模块

```shell
pip3 install requests
```

2.老哥们可先运行成功以后再添加crontab任务

```shell
cd /root/hostloc/ && /usr/local/bin/python3 /root/hostloc/hostloc_auto_get_points.py
```
