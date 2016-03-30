#!/usr/local/bin/python
import shlex
import psutil
import subprocess
from subprocess import Popen
from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello! I am healthy. Are you?'


@app.route('/cpu/<int:percent>', methods=['GET', 'POST'])
def cpu(percent):
    run_stress(cpulimit_percent=percent)
    return "Your requested CPU load percentage is %d" % percent


@ app.route('/mem/<int:memory_size>', methods=['GET', 'POST'])
def mem(memory_size):
    run_stress(stress_cmd='stress -m 1 --vm-hang 1 --vm-bytes %dM' %
               memory_size)
    return "Your requested memory size is %d MB" % memory_size


@app.route('/stats')
def stats():
    ps_cmd = Popen("ps -o pid -C stress", shell=True, stdout=subprocess.PIPE)
    stress_pids = [pid.decode("utf-8")
                   for pid in ps_cmd.stdout.read().strip().split()[2:]]
    print (stress_pids)
    if len(stress_pids) < 1:
        return "No stress process running"
    else:
        stress_pids = filter_zombies(stress_pids)
    return print_stats(stress_pids)


def print_stats(stress_pids):
    output = ""
    cpu_total = 0.0
    mem_total = 0
    for stress_pid in stress_pids:
        process = psutil.Process(int(stress_pid))
        cpu = process.cpu_percent(interval=1)
        mem = process.memory_info()[0]/1048576
        output = output +\
            "PID: %d CPU: %f Memory: %d MB <br/>" % (int(stress_pid), cpu, mem)
        cpu_total = cpu_total + cpu
        mem_total = mem_total + mem
    output = output + "<br/>Total CPU: %f Memory: %d MB" % (cpu_total,
                                                            mem_total)
    return output


def filter_zombies(stress_pids):
    filtered_pids = []
    for pid in stress_pids:
        if not zombie(pid):
            filtered_pids.append(pid)
    return filtered_pids


def zombie(pid):
    zombie_cmd = Popen("ps f --pid " + pid + " | grep -o Z",
                       shell=True, stdout=subprocess.PIPE)
    zombie_found = zombie_cmd.stdout.read().strip().decode("utf-8")
    if len(zombie_found) > 0:
        return True
    else:
        return False


@app.route('/reset')
def reset():
    Popen(shlex.split('killall -q -s 9 -r stress cpulimit'))
    return "Killed all instances of stress"


def run_stress(stress_cmd=None, cpulimit_percent=None):
    Popen(shlex.split('killall -q -s 9 -r stress cpulimit'))
    if not cpulimit_percent:
        Popen(shlex.split(stress_cmd))
        return
    p = Popen(shlex.split("stress -c %d" % ((cpulimit_percent/100) + 1)))
    ps_cmd = Popen("ps -o pid --ppid %d --noheaders" % p.pid, shell=True,
                   stdout=subprocess.PIPE)
    stress_pids = [pid.decode("utf-8")
                   for pid in ps_cmd.stdout.read().strip().split()]
    for stress_pid in stress_pids:
        percent = min(cpulimit_percent, 100)
        Popen(['cpulimit', '-p', stress_pid, '-l', str(cpulimit_percent)])
        cpulimit_percent = cpulimit_percent - percent

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
