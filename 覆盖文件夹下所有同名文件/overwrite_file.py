import os
import yaml
import shutil

config_params = []
with open('config.yml','r',encoding='utf-8') as file:
    config_params = yaml.safe_load(file)

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
        if file == config_params['replace_file']:
            file_path = os.path.join(root,file)
            if os.path.isfile(os.path.join(config_params['source_directory'],config_params['replace_file'])):
                shutil.copy2(os.path.join(config_params['source_directory'],config_params['replace_file']),file_path)
