# ibmcli
Command line tool on top of ibmcloud cli to do some more advanced stuff.

# install

git clone ...
cd pycli/ibmcli
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
which ibmcli

# usage
```
$ ibmcli --help
Usage: ibmcli [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  help    generate help for commands and children
  plugin

$ ibmcli plugin
Usage: ibmcli plugin [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  install    install all plugins
  uninstall  uninstall all plugins

$ ibmcli help --help
Usage: ibmcli help [OPTIONS] [TOP]...

  generate help for commands and children

Options:
  --help  Show this message and exit.

# Getting started
I use:

python3 -m venv virt
source ./virt/bin/activate
pip install -e .

