import os
import subprocess
from datetime import datetime

def backup_mysql_xampp(db_name, user, password="", host="localhost", port=3306, table_name=None, output_dir=r"C:\xampp\backups"):
    mysqldump_path = r"C:\xampp\mysql\bin\mysqldump.exe"
    if not os.path.exists(mysqldump_path):
        raise FileNotFoundError("mysqldump not found: C:\\xampp\\mysql\\bin\\mysqldump.exe")
    
    if table_name:
        table_backup_dir = os.path.join(output_dir, table_name)
        os.makedirs(table_backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = os.path.join(table_backup_dir, f"{db_name}_table_{table_name}_backup_{timestamp}.sql")
    else:
        full_backup_dir = os.path.join(output_dir, "full_bd_backup")
        os.makedirs(full_backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = os.path.join(full_backup_dir, f"{db_name}_backup_{timestamp}.sql")
    
    command = [mysqldump_path, "-h", host, "-P", str(port), "-u", user]
    
    if password:
        command.append(f"-p{password}")
    else:
        command.append("-p")
    
    if table_name:
        command.extend([db_name, table_name])
    else:
        command.append(db_name)
    
    with open(output_file, 'wb') as f:
        process = subprocess.Popen(command, stdout=f, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
    
    if process.returncode == 0:
        print(f"Backup successful: {output_file}")
    else:
        print(f"Backup error: {stderr.decode()}")

backup_mysql_xampp(
    db_name="",
    user="",
    password="",  
)

backup_mysql_xampp(
    db_name="",
    user="",
    password="",   
    table_name = "characters"
)