from ssweb import http
import argparse
import os
import json

cwd = os.getcwd()

config = '%s/vhosts' % cwd
daemonize = False
listens = {}
routes = []

def parse_configs(confdir):
    global listens
    global routes
    for c in os.listdir(confdir):
        if(c.endswith('.json')):
            f = open('%s/%s' % (config, c), "r")
            data = f.read()
            f.close()
            vhost = json.loads(data)
            if vhost['listen'] not in listens.keys():
                listens[vhost['listen']] = []

            for d in vhost['domains']:
                    listens[vhost['listen']].append(d)
            routes.append(vhost)

    http.init(listens, routes)

def main():
    global config
    global cwd
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--test-config', help="Test configuration and exit", action="store_true")
    parser.add_argument('-v', '--version', help="Display version and exit")
    parser.add_argument('-c', '--config', help='Path to directory with vhosts configuration, default: ./vhosts')
    parser.add_argument('-d', '--daemonize', help='Run in daemon mode', action="store_true")
    args = parser.parse_args()

    if args.config:
        config = "%s/%s" % (cwd, args.config)

    parse_configs(config)


if __name__ == '__main__':
    main()
