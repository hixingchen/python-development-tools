import yaml
import psutil
import subprocess
import time

config_params = []
with open('config.yml','r',encoding='utf-8') as file:
    config_params = yaml.safe_load(file)

def is_port_in_use(port):
    # 获取所有当前活跃的连接
    connections = psutil.net_connections()
    for conn in connections:
        # 检查是否有连接使用了指定的端口
        if conn.laddr.port == port:
            return True
    return False

if __name__ == '__main__':
    while True:
        for i in range(len(config_params['ports'])):
            if not is_port_in_use(config_params['ports'][i]):
                print(f"端口{config_params['ports'][i]}未被占用，启动程序--->{config_params['exe_path'][i]}")
                try:
                    subprocess.Popen(config_params['exe_path'][i])
                except Exception as e:
                    print(e)
        time.sleep(60)