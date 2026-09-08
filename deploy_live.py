import paramiko
import time

hostname = '93.188.81.158'
port = 2231
username = 'devuser'
password = "9XM61r'b9!\"!i^E&2i&Sr."

def run():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostname, port=port, username=username, password=password, timeout=15)
    print("Ulandi!")

    # Deploy steps
    stdin, stdout, stderr = client.exec_command(
        'cd /home/devuser/apps/architect-edu/Tift_ojs_journal && '
        'git fetch origin && '
        'git reset --hard origin/main && '
        './venv/bin/python populate_editorial_board.py && '
        './venv/bin/python manage.py makemigrations && '
        './venv/bin/python manage.py migrate && '
        './venv/bin/python manage.py collectstatic --noinput && '
        './venv/bin/python update_pages.py'
    )
    print("DEPLOY OUT:", stdout.read().decode().strip())
    if stderr:
        err = stderr.read().decode().strip()
        if err:
            print("DEPLOY ERR:", err)

    # Restart service
    channel = client.get_transport().open_session()
    channel.get_pty()
    channel.exec_command('sudo systemctl restart tift-journal.service')
    time.sleep(1)
    channel.send(password + '\n')
    time.sleep(3)
    exit_status = channel.recv_exit_status()
    print("Restart exit:", exit_status)

    # Check
    stdin, stdout, stderr = client.exec_command('systemctl is-active tift-journal.service')
    print("Status:", stdout.read().decode().strip())

    client.close()
    print("Deploy yakunlandi!")

if __name__ == '__main__':
    run()
