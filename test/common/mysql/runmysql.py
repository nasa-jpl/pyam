import subprocess
import sys
import os
import signal

cmd = os.path.join(sys.argv[1], "mysql", "completesql.bash")  # "./completesql.bash"
arg = " -s " + "'" + os.path.join(sys.argv[1], "mysql", "example_yam_for_import.sql") + "'"
fullcmd = cmd + arg


def runmysql():
    # print("mysql cmd",fullcmd)
    # Commenting line below as it was deemded as high risk. Uncomment at your own discretion. 
    # popen = subprocess.Popen(fullcmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True, preexec_fn=os.setsid)
    port = None
    # second line of program is the port number so save that
    # popen.stdout.readline()
    # port = int(popen.stdout.readline())
    while True:
        line = popen.stdout.readline().strip("\n ")
        if line.isnumeric():
            port = int(line)
            # print("FOUND PORT")
            break

    # print("PID for mysql",popen.pid)

    # kill the server subprocess
    # os.killpg(os.getpgid(popen.pid), signal.SIGTERM)
    # return [id of process, port that it is running on]
    print(popen.pid, port)
    return popen.pid, port


if __name__ == "__main__":
    runmysql()
