import time
import re
import textwrap
import requests
import config

from pyaes import AESModeOfOperationCBC
from requests import Session as req_Session


# 使用Python实现防CC验证页面中JS写的的toNumbers函数
def toNumbers(secret: str) -> list:
    text = []
    for value in textwrap.wrap(secret, 2):
        text.append(int(value, 16))
    return text


# 不带Cookies访问论坛首页，检查是否开启了防CC机制，将开启状态、AES计算所需的参数全部放在一个字典中返回
def check_anti_cc() -> dict:
    result_dict = {}
    headers = {
        "user-agent": config.user_agent
    }
    home_page = "https://skyeysnow.com/forum.php"
    res = requests.get(home_page, headers=headers)
    aes_keys = re.findall('toNumbers\("(.*?)"\)', res.text)
    cookie_name = re.findall('cookie="(.*?)="', res.text)

    if len(aes_keys) != 0:  # 开启了防CC机制
        print("检测到防 CC 机制开启！")
        if len(aes_keys) != 3 or len(cookie_name) != 1:  # 正则表达式匹配到了参数，但是参数个数不对（不正常的情况）
            result_dict["ok"] = 0
        else:  # 匹配正常时将参数存到result_dict中
            result_dict["ok"] = 1
            result_dict["cookie_name"] = cookie_name[0]
            result_dict["a"] = aes_keys[0]
            result_dict["b"] = aes_keys[1]
            result_dict["c"] = aes_keys[2]
    else:
        pass

    return result_dict


# 在开启了防CC机制时使用获取到的数据进行AES解密计算生成一条Cookie（未开启防CC机制时返回空Cookies）
def gen_anti_cc_cookies() -> dict:
    cookies = {}
    anti_cc_status = check_anti_cc()

    if anti_cc_status:  # 不为空，代表开启了防CC机制
        if anti_cc_status["ok"] == 0:
            print("防 CC 验证过程所需参数不符合要求，页面可能存在错误！")
        else:  # 使用获取到的三个值进行AES Cipher-Block Chaining解密计算以生成特定的Cookie值用于通过防CC验证
            print("自动模拟计尝试通过防 CC 验证")
            a = bytes(toNumbers(anti_cc_status["a"]))
            b = bytes(toNumbers(anti_cc_status["b"]))
            c = bytes(toNumbers(anti_cc_status["c"]))
            cbc_mode = AESModeOfOperationCBC(a, b)
            result = cbc_mode.decrypt(c)

            name = anti_cc_status["cookie_name"]
            cookies[name] = result.hex()
    else:
        pass

    return cookies


# 登录帐户
def login(username: str, password: str) -> req_Session:
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "origin": "https://skyeysnow.com",
        "referer": "https://skyeysnow.com/forum.php",
    }
    login_url = "https://skyeysnow.com/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1"
    login_data = {
        "fastloginfield": "username",
        "username": username,
        "password": password,
        "quickforward": "yes",
        "handlekey": "ls",
    }

    s = req_Session()
    s.headers.update(headers)
    s.cookies.update(gen_anti_cc_cookies())
    res = s.post(url=login_url, data=login_data)
    res.raise_for_status()
    return s


# 通过抓取用户设置页面的标题检查是否登录成功
def check_login_status(s: req_Session, number_c: int) -> bool:
    check_url = "https://skyeysnow.com/home.php?mod=spacecp"
    res = s.get(check_url)
    res.raise_for_status()
    res.encoding = "utf-8"
    check_title = re.findall("<title>(.*?)<\/title>", res.text)

    if len(check_title) != 0:  # 确保正则匹配到了内容，防止出现数组索引越界的情况
        if check_title[0] != "个人资料 -  天雪 -  Powered by Discuz!":
            print("第", number_c + 1, "个帐户登录失败！")
            return False
        else:
            print("第", number_c + 1, "个帐户登录成功！")
            return True
    else:
        print("无法在用户设置页面找到标题，该页面存在错误或被防 CC 机制拦截！")
        return False


# 抓取并打印输出帐户当前积分
def print_current_points(s: req_Session):
    test_url = "https://skyeysnow.com/forum.php"
    res = s.get(test_url)
    res.raise_for_status()
    res.encoding = "utf-8"
    points = re.findall("Gold: &nbsp;(\d+)", res.text)

    if len(points) != 0:  # 确保正则匹配到了内容，防止出现数组索引越界的情况
        print("帐户当前积分：" + points[0])
    else:
        print("无法获取帐户积分，可能页面存在错误或者未登录！")
    time.sleep(5)


# 打印输出当前ip地址
def print_my_ip():
    api_url = "https://api.ipify.org/"
    try:
        res = requests.get(url=api_url)
        res.raise_for_status()
        res.encoding = "utf-8"
        print("当前使用 ip 地址：" + res.text)
    except Exception as e:
        print("获取当前 ip 地址失败：" + str(e))


if __name__ == "__main__":
    username = config.username
    password = config.password
    # 账户和密码

    # 分割用户名和密码为列表
    user_list = username.split(",")
    passwd_list = password.split(",")

    if not username or not password:
        print("未检测到用户名或密码，请检查环境变量是否设置正确！")
    elif len(user_list) != len(passwd_list):
        print("用户名与密码个数不匹配，请检查环境变量设置是否错漏！")
    else:
        print_my_ip()
        print("共检测到", len(user_list), "个帐户，开始获取金币")
        print("*" * 30)

        # 依次登录帐户获取积分，出现错误时不中断程序继续尝试下一个帐户
        for i in range(len(user_list)):
            try:
                s = login(user_list[i], passwd_list[i])
                if check_login_status(s, i):
                    print_current_points(s)
                    print("*" * 30)
            except Exception as e:
                print("程序执行异常：" + str(e))
                print("*" * 30)
            continue

        print("程序执行完毕，获取积分过程结束")
