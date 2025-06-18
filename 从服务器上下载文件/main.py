import os
import yaml
import paramiko
import stat

with open('config.yml','r',encoding='utf-8') as file:
    config_params = yaml.safe_load(file)

# 连接服务器
def connect_server():
    try:
        # 创建SSH对象
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if config_params['login_mode'] == 'pem':
            private_key = paramiko.RSAKey.from_private_key_file(config_params['pem_path'])
            # 连接服务器
            ssh.connect(hostname=config_params['host_name'], port=config_params['port'], username=config_params['user_name'], pkey=private_key)
        else:
            ssh.connect(hostname=config_params['host_name'], port=config_params['port'], username=config_params['user_name'], password=config_params['password'])
        return ssh
    except:
        print('连接服务器失败')

def download_from_server(remote_path, local_path, sftp):
    """
    从服务器下载文件或目录到本地
    :param remote_path: 服务器上的路径
    :param local_path: 本地目标路径
    :param sftp: SFTP连接对象
    """
    remote_path = remote_path  # 统一服务器路径格式
    local_path = local_path # 统一本地路径格式
    
    # 检查远程路径是文件还是目录
    try:
        file_attr = sftp.stat(remote_path)
    except IOError:
        print(f"远程路径不存在: {remote_path}")
        return
    
    if stat.S_ISDIR(file_attr.st_mode):
        # 如果是目录
        if not os.path.exists(local_path):
            os.makedirs(local_path)
            print(f"创建本地目录: {local_path}")
        
        # 遍历远程目录
        for item in sftp.listdir(remote_path):
            remote_item = f"{remote_path}/{item}"
            local_item = os.path.join(local_path, item)
            download_from_server(remote_item, local_item, sftp)
    else:
        # 如果是文件
        try:
            sftp.get(remote_path, local_path)
            print(f"下载文件: {remote_path} -> {local_path}")
        except Exception as e:
            print(f"下载文件失败: {remote_path}, 错误: {str(e)}")

if __name__ == '__main__':
    ssh = connect_server()
    sftp = ssh.open_sftp()
    
    # 从服务器下载文件到本地
    download_from_server(
        config_params['server_download_path'],  # 服务器上要下载的路径
        config_params['local_save_path'],       # 本地保存路径
        sftp
    )
    
    sftp.close()
    ssh.close()