import os
import yaml

config_params = []
with open('config.yml','r',encoding='utf-8') as file:
    config_params = yaml.safe_load(file)

cmd = f"netsh interface ip set address name={config_params['name']} static {config_params['ip']} {config_params['mask']} {config_params['gateway']}"

if __name__ == "__main__":
    os.system(cmd)