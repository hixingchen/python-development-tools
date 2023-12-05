import os
import yaml
import shutil
import paramiko
import time
import stat

base_url = os.getcwd()[:os.getcwd().find('\\backup')]

config_params = []

with open('config.yml','r',encoding='utf-8') as file:
    config_params = yaml.safe_load(file)

# 修改文件夹下所有文件取消只读，如果有文件只读 shutil.copytree 方法会报错
def update_file_permissions(path):
    for root,dirs,files in os.walk(path):
        for file in files:
            os.chmod(os.path.join(root,file),stat.S_IWRITE)
            print(os.path.join(root,file))
        for dir in dirs:
            os.chmod(os.path.join(root,dir),stat.S_IWRITE)
            print(os.path.join(root,dir))

def remove_directory(path):
    # 遍历文件夹中的所有文件和子文件夹
    for root, dirs, files in os.walk(path, topdown=False):
        # 删除每个文件
        for file in files:
            os.remove(os.path.join(root, file))
        # 删除每个子文件夹
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    # 删除空文件夹
    os.rmdir(path)

try:
    print("--------------------开始一键部署--------------------")

    if config_params['apis'] is not None:
        print("--------------------开始拷贝api--------------------")
        for url_name in config_params['apis']:
            if os.path.exists(os.path.join(base_url,url_name)):
                target_url = os.path.join(base_url,config_params['merge_path'],'jp-ui\\src\\api',url_name.split('\\')[-1])
                if os.path.exists(target_url):
                    remove_directory(target_url)
                shutil.copytree(os.path.join(base_url,url_name),target_url,dirs_exist_ok = True)
                print(url_name,"--->拷贝完成")
            else:
                print(url_name,"--->路径不存在")
        print("--------------------api拷贝完成--------------------")

    if config_params['views'] is not None:
        print("--------------------开始拷贝view--------------------")
        for url_name in config_params['views']:
            if os.path.exists(os.path.join(base_url,url_name)):
                target_url = os.path.join(base_url,config_params['merge_path'],'jp-ui\\src\\views\\modules',url_name.split('\\')[-1])
                if os.path.exists(target_url):
                    remove_directory(target_url)
                shutil.copytree(os.path.join(base_url,url_name),target_url,dirs_exist_ok = True)
                print(url_name,"--->拷贝完成")
            else:
                print(url_name,"--->路径不存在")
        print("--------------------view拷贝完成--------------------")

    if config_params['jp_ui_package']:
        print("--------------------开始打包前端--------------------")
        if not os.path.exists(os.path.join(base_url,config_params['merge_path'],'webapps')):
            os.makedirs(os.path.join(base_url,config_params['merge_path'],'webapps'))
        print("--------------------开始构建--------------------")
        os.system(f"cd {os.path.join(base_url,config_params['merge_path'])}\\jp-ui && cnpm install")
        print("--------------------构建结束--------------------")
        os.system(f"cd {os.path.join(base_url,config_params['merge_path'])}\\jp-ui && npm run build")
        print("--------------------前端打包结束--------------------")

        print("--------------------开始拷贝前端--------------------")
        target_url = os.path.join(base_url,config_params['merge_path'],'webapps\\ROOT')
        if os.path.exists(target_url):
            remove_directory(target_url)
        shutil.copytree(os.path.join(base_url,config_params['merge_path'],'jp-ui\\dist'),target_url,dirs_exist_ok = True)
        print("--------------------前端拷贝完成--------------------")

    if config_params['modules'] is not None:
        print("--------------------开始打包后端--------------------")
        exceptional_modules = []
        for module_name in config_params['modules']:
            print("开始打包模块--->",module_name)
            os.system(f"cd {os.path.join(base_url,module_name)}\\jp-console && mvn package")
        print("--------------------后端打包完成--------------------")

        print("--------------------开始拷贝后端--------------------")
        for module_name in config_params['modules']:
            if os.path.exists(os.path.join(base_url,module_name,'jp-console\\allright-web\\target\\allright-vue')):
                if os.path.exists(os.path.join(base_url,config_params['merge_path'],'webapps\\allright')):
                    update_file_permissions(os.path.join(base_url,config_params['merge_path'],'webapps\\allright'))
                shutil.copytree(os.path.join(base_url,module_name,'jp-console\\allright-web\\target\\allright-vue'),os.path.join(base_url,config_params['merge_path'],'webapps\\allright'),dirs_exist_ok = True)
                print(module_name,"--->拷贝成功")
            else:
                print(module_name,"--->文件不存在,拷贝失败")
        print("--------------------后端拷贝完成--------------------")

    if config_params['deploy']:
        print("--------------------开始部署--------------------")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=config_params['host_name'], port=config_params['host_port'],username=config_params['user_name'],password=config_params['password'])
        stdin, stdout, stderr = ssh.exec_command(f"ps -ef|grep {config_params['tomcat_name']}")
        stdin.close()
        stdout_infos = stdout.readlines()
        for stdout_info in stdout_infos:
            stdout_info_split = stdout_info.split(' ')
            if stdout_info.find(f"{config_params['tomcat_path']}/{config_params['tomcat_name']}")>0:
                for value in stdout_info_split:
                    if value.isdigit():
                        ssh.exec_command(f"kill -9 {value}")
                        time.sleep(1)
                        break
        sftp = ssh.open_sftp()
        dirname = os.path.join(base_url,config_params['merge_path'],'webapps')
        if os.path.exists(dirname):
            for root,dirs,files in os.walk(dirname):
                for dir in dirs:
                    path = os.path.join(root,dir)
                    path = path.replace(dirname,os.path.join(config_params['tomcat_path'],config_params['tomcat_name'],"webapps")).replace("\\","/")
                    try:
                        sftp.mkdir(path)
                        print(f"创建文件夹--->{dir}")
                    except:
                        continue
                for file in files:
                    path = os.path.join(root,file)
                    path = path.replace(dirname,os.path.join(config_params['tomcat_path'],config_params['tomcat_name'],'webapps')).replace("\\","/")
                    sftp.put(os.path.join(root,file),path)
                    print(f"复制文件--->{path}")

        stdin, stdout, stderr = ssh.exec_command(f"cd {config_params['tomcat_path']}/{config_params['tomcat_name']}/bin;./startup.sh")
        stdin.close()
        stdin, stdout, stderr = ssh.exec_command(f"cd {config_params['tomcat_path']}/{config_params['tomcat_name']}/logs;tail -f catalina.out")
        stdin.close()
        for line in iter(lambda: stdout.readline(2048),""):
            print(line,end="")
            if line.find(config_params['success_remarks'])>0:
                break
        stdout.close()
        sftp.close()
        ssh.close()
        print("--------------------部署结束--------------------")

    print("--------------------一键部署结束--------------------")
    input('按任意键退出：')
except Exception as error:
    print(type(error).__name__)
    input('执行出错！按任意键退出：')