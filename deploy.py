
import ctypes
import sys
import os
import subprocess
import configparser
import shutil


def run_build():
    config = configparser.ConfigParser()
    config.read('settings.ini')

    apps = config.get('Settings', 'Apps', fallback='')
    apps_list = str([app.strip().lower() for app in apps.split(',')])
    password = config.get('Settings', 'Password', fallback='')
    out_name = config.get('Settings', 'OutputName', fallback='').replace(" ", "")

    with open("main.py", "r") as f:
        content = f.read()

    content = content.replace('["REPLACE_APPS"]', apps_list)
    content = content.replace('"REPLACE_PASSWORD"', f'"{password}"')

    with open("temp.py", "w") as f:
        f.write(content)

    print(f"Baking settings into {out_name}.exe...")

    subprocess.run([
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--log-level", "WARN",
        f"--name={out_name}",
        "temp.py"
    ])

    dest_folder = rf"C:\ProgramData\{out_name}"
    os.makedirs(dest_folder, exist_ok=True)
    exe_path = os.path.join(dest_folder, f"{out_name}.exe")
    
    shutil.copy(os.path.join("dist", f"{out_name}.exe"), exe_path)

    print("Registering startup task...")
    ps_script = f"""
    $action = New-ScheduledTaskAction -Execute '{exe_path}'
    $trigger = New-ScheduledTaskTrigger -AtLogon
    $principal = New-ScheduledTaskPrincipal -GroupId "S-1-5-32-545" -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

    Register-ScheduledTask -TaskName "{out_name}" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
    """

    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("PowerShell: Task registered successfully.")
    else:
        print(f"PowerShell Error: {result.stderr}")


    os.remove("temp.py")
    os.remove(f"{out_name}.spec")
    shutil.rmtree("build")
    shutil.rmtree("dist")
    
    config.set('Settings', 'Apps', 'firefox.exe,discord.exe')
    config.set('Settings', 'Password', 'password123')
    config.set("Settings", "OutputName", "WinSystemHost")
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)

    print(f"\nSuccess! {out_name}.exe is now standalone in {dest_folder}.")
    input("Press any key to continue...")


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def request_admin_privileges():
    try:
        script_path = os.path.abspath(sys.argv[0])
        params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
        
        result = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script_path}" {params}', None, 1
        )
        return result > 32  # Success if result > 32
    except Exception as e:
        print("Error:", str(e))
        return False

def admin_check():
    if not is_admin():
        success = request_admin_privileges()
        if success:
            print("Requested admin privileges. Relaunching...")
            sys.exit(0)
        else:
            print("Admin privilege request was denied.")
            input("Press enter to exit...")
            sys.exit(1)
    
    else:
        print("Running with admin privileges!")


if __name__ == "__main__":
    admin_check()
    
    #try:
    run_build()
    #except Exception as e:
    #    print(type(e).__name__, "-", e)




