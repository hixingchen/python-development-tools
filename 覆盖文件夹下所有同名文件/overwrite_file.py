import os
import yaml
import shutil

config_params = []
with open('config.yml','r',encoding='utf-8') as file:
    config_params = yaml.safe_load(file)

if __name__ == "__main__":
    try:
        for root, dirs, files in os.walk(config_params['target_directory']):
            # source_path = os.path.join(source_directory, file)
            # target_path = os.path.join(target_directory, file)
            
            # # 判断源文件是否为文件而非目录
            # if os.path.isfile(source_path):
            #     shutil.copy2(source_path, target_path)
            for skip_directory in config_params['skip_directorys']:
                if skip_directory in dirs:
                    dirs.remove(skip_directory)
            for file in files:
                if file == config_params['target_file']:
                    file_path = os.path.join(root,file)
                    if os.path.isfile(os.path.join(config_params['source_directory'],config_params['source_file'])):
                        print("正在拷贝"+file_path)
                        os.chmod(file_path, 0o777)# 修改权限，有些只读文件覆盖会报错
                        shutil.copy2(os.path.join(config_params['source_directory'],config_params['source_file']),file_path)
        print("拷贝完成-------")
    except Exception as e:
        print(e)
    finally:
        input('按任意键退出!')