import ping3
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=100)
result = []
def ping(ip):
    temp = 0
    for i in range(3):
        response_time = ping3.ping(ip,timeout=1)
        if type(response_time) == float:
            temp += 1
    if temp >= 2:
        result.append(ip+"---成功")
    else:
        result.append(ip+"---失败")
def my_key_func(value):
    return int(value.split(".")[-1].split("---")[0])

if __name__ == "__main__":
    print("开始测试。。。")
    for i in range(1,256):
        ip = f'192.168.1.{i}'
        executor.submit(ping,ip)
    executor.shutdown()
    result.sort(key=my_key_func)
    for name in result:
        print(name)
    input("测试结束！")
