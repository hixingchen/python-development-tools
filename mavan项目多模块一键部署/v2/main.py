import os
import yaml
import shutil
import paramiko
import stat
from file_merge import file_merge

base_url = os.getcwd()[:os.getcwd().find('backup')-1]

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

# 修改文件夹下所有文件取消只读，如果有文件只读 shutil.copytree 方法会报错
def update_file_permissions(path):
    try:
        path = path.replace('\\',os.sep).replace('/',os.sep)
        os.chmod(path,stat.S_IWRITE)
        for root,dirs,files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in config_params['jp_ui_ignore_files']]
            for file in files:
                try:
                    os.chmod(os.path.join(root,file),stat.S_IWRITE)
                except:
                    print(os.path.join(root,file)+'--->文件修改权限失败')
                    break
            for dir in dirs:
                try:
                    os.chmod(os.path.join(root,dir),stat.S_IWRITE)
                except:
                    print(os.path.join(root,dir)+'--->文件夹修改权限失败')
    except:
        print('修改权限失败')

def remove_directory(path):
    path = path.replace('\\',os.sep).replace('/',os.sep)
    print('删除目录'+path)
    try:  
        # 尝试删除整个目录树  
        shutil.rmtree(path)  
        print(f"文件夹 {path} 及其内容已被成功删除。")  
    except FileNotFoundError:  
        print(f"文件夹 {path} 不存在，无需删除。")  
    except PermissionError:  
        print(f"没有权限删除文件夹 {path} 或其内容。")  
    except Exception as e:  
        print(f"删除文件夹 {path} 时发生错误: {e}")   

def copytree(src, dst, symlinks=False, ignore=None): 
    src = src.replace('\\',os.sep).replace('/',os.sep)
    dst = dst.replace('\\',os.sep).replace('/',os.sep) 
    if not os.path.exists(dst):  
        os.makedirs(dst)  
    else:  
        # 如果目标目录已存在，但我们需要覆盖其中的内容（或合并），  
        # 这里我们选择删除目标目录中的同名项（如果需要的话），但通常这不是最佳实践  
        # 因为这可能会意外删除重要文件。更好的方法是逐个检查并覆盖。  
        # 但为了简化，我们在这里不做额外处理，只是确保目标目录存在。  
        pass  
  
    # 定义一个内部函数来处理实际的复制逻辑  
    def _copy(src, dst, ignore=None):  
        for item in os.listdir(src):  
            s = os.path.join(src, item)  
            d = os.path.join(dst, item)  
            if os.path.isdir(s):  
                # 如果源是目录，则递归调用  
                if not os.path.exists(d) and (ignore is None or not ignore(src, [item])):  
                    os.makedirs(d)  
                if ignore is None or not ignore(src, [item]):
                    _copy(s, d, ignore)  
            elif os.path.isfile(s):  
                # 如果源是文件，并且没有被ignore函数指定为要忽略的项  
                if ignore is None or not ignore(src, [item]):  
                    shutil.copy2(s, d)  
  
    # 调用内部函数来执行复制操作  
    _copy(src, dst, ignore)  

def jp_ui_copy():
    print("--------------------开始拷贝jp-ui--------------------")
    for module in config_params['modules']+[config_params['template_module']]:
        src_path = os.path.join(base_url,module,'jp-ui').replace('\\',os.sep).replace('/',os.sep)
        target_path = os.path.join(base_url,config_params['merge_path'],'jp-ui').replace('\\',os.sep).replace('/',os.sep)
        if not os.path.exists(src_path):
            continue
        if os.path.exists(target_path):
            update_file_permissions(target_path)
        def ignore_files(d, files):
            return [f for f in files if f in config_params['jp_ui_ignore_files']]
        print("拷贝jp-ui模块：",module)
        copytree(src_path,target_path,ignore=ignore_files)
    
    print("合并package.json文件...")
    for module in config_params['modules']+[config_params['template_module']]:
        src_path = os.path.join(base_url,module,'jp-ui','package.json').replace('\\',os.sep).replace('/',os.sep)
        target_path = os.path.join(base_url,config_params['merge_path'],'jp-ui','package.json').replace('\\',os.sep).replace('/',os.sep)
        if not os.path.exists(src_path):
            continue
        file_merge.json_merge(src_path,target_path,target_path)
    print("--------------------拷贝jp-ui结束--------------------")

def jp_ui_build():
    print("--------------------开始构建--------------------")
    os.system(f"cd {os.path.join(base_url,config_params['merge_path'],'jp-ui')} && cnpm install")
    print("--------------------构建结束--------------------")
    print("--------------------开始打包前端--------------------")
    os.system(f"cd {os.path.join(base_url,config_params['merge_path'],'jp-ui')} && npm run build")
    print("--------------------打包前端结束--------------------")

def jp_console_merge():
    print("--------------------开始打包后端模块--------------------")
    for module in config_params['modules']+[config_params['template_module']]:
        print("开始打包模块--->",module)
        if os.path.exists(os.path.join(base_url,module,'jp-console')):
            os.system(f"cd {os.path.join(base_url,module,'jp-console')} && mvn package")
    print("--------------------后端模块打包结束--------------------")
    print("--------------------开始拷贝后端--------------------")
    for module in config_params['modules']+[config_params['template_module']]:
        src_path = os.path.join(base_url,module,'jp-console','allright-web','target','allright-vue').replace('\\',os.sep).replace('/',os.sep)
        target_path = os.path.join(base_url,config_params['merge_path'],'allright').replace('\\',os.sep).replace('/',os.sep)
        if os.path.exists(target_path):
            update_file_permissions(target_path)
        print("拷贝后端模块："+module)
        if os.path.exists(src_path):
            copytree(src_path,target_path)
    print("--------------------后端拷贝完成--------------------")
    print("------整合application-development.yml配置文件------")
    for module in config_params['modules']+[config_params['template_module']]:
        src_path = os.path.join(base_url,module,'jp-console','allright-web','target','allright-vue','WEB-INF','classes','application-development.yml').replace('\\',os.sep).replace('/',os.sep)
        target_path = os.path.join(base_url,config_params['merge_path'],'allright','WEB-INF','classes','application-development.yml').replace('\\',os.sep).replace('/',os.sep)
        file_merge.yaml_merge(src_path,target_path,target_path)
    print("--------------------配置文件整合完成--------------------")

def execute_command(ssh,command):
    command = command.replace('\\','/')
    stdin, stdout, stderr = ssh.exec_command(command)
    stdin.close()
    return stdout
def deploy():
    print("--------------------开始部署--------------------")
    ssh = connect_server()
    stdout = execute_command(ssh,f"ps -ef|grep {config_params['tomcat_name']}")
    stdout_infos = stdout.readlines()
    for stdout_info in stdout_infos:
        stdout_info_split = stdout_info.split(' ')
        if stdout_info.find(f"{os.path.join(config_params['tomcat_path'],config_params['tomcat_name'])}")>0:
            for value in stdout_info_split:
                if value.isdigit():
                    execute_command(ssh,f"kill -9 {value}")
                    break
    execute_command(ssh,f"rm -rf {os.path.join(config_params['tomcat_path'],config_params['tomcat_name'],'webapps','ROOT')}")
    execute_command(ssh,f"rm -rf {os.path.join(config_params['tomcat_path'],config_params['tomcat_name'],'webapps','allright')}")
    execute_command(ssh,f"mkdir {os.path.join(config_params['tomcat_path'],config_params['tomcat_name'],'webapps','ROOT')}")
    execute_command(ssh,f"mkdir {os.path.join(config_params['tomcat_path'],config_params['tomcat_name'],'webapps','allright')}")
    sftp = ssh.open_sftp()
    print("测试1")
    remote_cope_dir(os.path.join(base_url,config_params['merge_path'],'jp-ui','dist'),os.path.join(config_params['tomcat_path'],config_params['tomcat_name'],"webapps",'ROOT'),sftp)
    print("测试2")
    remote_cope_dir(os.path.join(base_url,config_params['merge_path'],'allright'),os.path.join(config_params['tomcat_path'],config_params['tomcat_name'],"webapps",'allright'),sftp)
    print("测试3")
    execute_command(ssh,f"cd {os.path.join(config_params['tomcat_path'],config_params['tomcat_name'],'bin')};./startup.sh")
    print("测试4")
    stdout = execute_command(ssh,f"cd {os.path.join(config_params['tomcat_path'],config_params['tomcat_name'],'logs')};tail -f catalina.out")
    print("测试5")
    for line in iter(lambda: stdout.readline(2048),""):
        print("测试6")
        print(line,end="")
        if line.find(config_params['success_remarks'])>0:
            break
    sftp.close()
    ssh.close()
    print("--------------------部署结束--------------------")

def remote_cope_dir(src_path,target_path,sftp):
    src_path = src_path.replace('\\',os.sep).replace('/',os.sep)
    target_path = target_path.replace('\\',os.sep).replace('/',os.sep)
    for root,dirs,files in os.walk(src_path):
        for dir in dirs:
            path = os.path.join(root,dir)
            path = path.replace(src_path,target_path).replace('\\',os.sep).replace('/',os.sep)
            try:
                sftp.mkdir(path)
                print(f"创建文件夹--->{dir}")
            except:
                continue
        for file in files:
            path = os.path.join(root,file)
            path = path.replace(src_path,target_path).replace('\\',os.sep).replace('/',os.sep)
            sftp.put(os.path.join(root,file),path)
            print(f"复制文件--->{path}")

if __name__ == '__main__':
    try:
        if config_params['delete_dist'] and os.path.exists(os.path.join(base_url,config_params['merge_path']).replace('\\',os.sep).replace('/',os.sep)):
            update_file_permissions(os.path.join(base_url,config_params['merge_path']))
            remove_directory(os.path.join(base_url,config_params['merge_path']))
        print("--------------------开始一键部署--------------------")
        if config_params['jp_ui_copy']:
            jp_ui_copy()
        if config_params['jp_ui_package']:
            jp_ui_build()
        if config_params['jp_console_merge']:
            jp_console_merge()
        if config_params['deploy']:
            deploy()
        print("--------------------一键部署结束--------------------")
        if config_params['stop_input']:
            input('按任意键退出：')
    except Exception as error:
        print(error)
        if config_params['stop_input']:
            input('执行出错！按任意键退出：')