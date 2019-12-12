import os


LOCAL_IP = '<your_server_ip'
PRIVOXY_CONF_TMP = 'privoxy_tmp.conf'
START_PORT = 6971
SUPERVISOR_BASE_DIR = '/home/user'
SUPERVISOR_CONF_NAME = 'stormproxies.conf'
PRIVOXY_CONFIG_PATH = '/home/user/privoxy_storm'
PRIVOXY_BINARY = '/usr/sbin/privoxy'


def load_tmp_body():
    body = ''
    with open(PRIVOXY_CONF_TMP) as f:
        body = f.read()
    return body


def save_new_conf(name, conf_body):
    with open(name, 'w') as f:
        f.write(conf_body)


def build_conf_files(port, prefix, *proxies):
    conf_tmp = load_tmp_body()
    proxy_list = []
    for p, prx in enumerate(proxies, port):
        new_ip = 'http://{}:{}'.format(LOCAL_IP, p)
        new_conf = conf_tmp.replace('{{ port }}', str(p))
        new_conf = new_conf.replace('{{ proxy }}', prx)
        new_name = '{}_{}.conf'.format(prefix, (p - port + 1))
        save_new_conf(new_name, new_conf)
        proxy_list.append(new_ip)
    return proxy_list


def build_proxy_list(name, *proxies):
    if not name.endswith('.txt'):
        name = name + '.txt'
    with open(name, 'w') as f:
        for prx in proxies:
            f.write('{}\n'.format(prx))

def build_supervisord_conf(*prx_list_names):
    supervisor_conf_body = ''
    for pl_name in prx_list_names:
        m_name = '.'.join(pl_name.split('.')[:-1])
        group_name = 'storm-{}'.format(m_name)
        supervisor_conf_body += '[group:{}]\n'.format(group_name)
        group_programs = []
        proxies = load_proxy_list(pl_name)
        for p_no, _ in enumerate(proxies, 1):
            program_name = 'storm-{}-{}-privoxy'.format(m_name, p_no)
            group_programs.append(program_name)

        supervisor_conf_body += 'programs={}'.format(','.join(group_programs))
        supervisor_conf_body += '\n\n'

        for p_no, p_name in enumerate(group_programs, 1):
            supervisor_conf_body += '[program:{}]\n'.format(p_name)
            supervisor_conf_body += (
                'command={} --no-daemon '
                '{}/{}_{}.conf\n'
                .format(PRIVOXY_BINARY, PRIVOXY_CONFIG_PATH, m_name, p_no))
            supervisor_conf_body += 'directory={}\n'.format(SUPERVISOR_BASE_DIR)
            supervisor_conf_body += 'autostart=true\n'
            supervisor_conf_body += 'autorestart=true\n\n'
    with open(SUPERVISOR_CONF_NAME, 'w') as f:
        f.write(supervisor_conf_body)


def load_proxy_list(name):
    proxy_list = []
    with open(name) as f:
        for l in f:
            prx = l.strip()
            if prx:
                proxy_list.append(prx)
    return proxy_list


def remove_old_conf():
    for f_name in os.listdir('.'):
        if f_name == PRIVOXY_CONF_TMP:
            continue
        if f_name.endswith('.conf'):
            os.unlink(f_name)


def main(*prx_list_names):
    remove_old_conf()
    start_port = START_PORT
    for pl_name in prx_list_names:
        m_name = '.'.join(pl_name.split('.')[:-1])
        proxies = load_proxy_list(pl_name)
        local_proxies = build_conf_files(start_port, m_name, *proxies)
        local_list_name = '{}_local.txt'.format(m_name)
        build_proxy_list(local_list_name, *local_proxies)
        start_port += len(proxies)
    build_supervisord_conf(*prx_list_names)


if __name__ == '__main__':
    main('main.txt', '3min.txt', '15min.txt')
