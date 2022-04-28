# Simple Socket-based Webserver in Python3

### SSWeb is standalone webserver built in Python3.

### Key features:

- Running without any custom third-party libraries. Written entirely on basic Python sockets.
- Can run multiple vhosts defined in YAML.
- Static/dynamic routes.
- Routes backend files separated from configuration, which makes it easier to write and read.
-	Caching static files under assets/ directory.
-	Pretty fast.


### Currently working on:
- Logging with 3 levels: debug, warning, errors.
- Template system, actual simply replaces ((variables)) with values in HTML files. Need to work on lists, functions etc.
- SSL
- Arguments from test.py file. For now they are just placeholders.


### Planned in the future:
- Documentation, after 1.0 version is released.


### If you want to test it
1. Clone repository to your system.
2. Edit vhosts/test.lab.yml with your options(or leave it like it is), I think their names are pretty clear.
3. Run python3 test.py and access the website.
