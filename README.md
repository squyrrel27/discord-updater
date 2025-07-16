# discord-updater

discord-updater allows our discord music bot to grab the latest youtube plugin version.

---

## Installation
- Pull in the git repo
    ```
    git clone https://github.com/squyrrel27/discord-updater.git
    cd discord-updater
    git fetch origin
    git tag -l                                              # lists all tags
    git checkout tags/{tag_name}
    ```
- requirements.txt contains all the python packages that are needed. run with:  
    ```
    pip install --upgrade pip  
    pip install -r requirements.txt

    # If moving to a new server/environment, please check 
    # the requirements.txt for any package updates needed
    ```
- Copy `config-default.ini` -> `config.ini`, open `config.ini` and replace the appropriate values


## Starting the processes
- Run the program:  
    ```
    # Check for an update without changing the yaml file
    $ python3 updater.py check  

    # Check for an update and change the yaml file
    $ python3 updater.py update

    # Config defaults to ./config.ini. Use the following 
    # if you need an absolute path:
    $ python3 updater.py --config /where/ever/custom.ini test
    ```
## Automating the processes
- Run from crontab:  
    ```
    # Customize time entries from every hour to needed interval
    # Update /path/to/program to path of git clone
    # Update /where/ever to configuration directory path
    0 * * * * /usr/bin/python3 /path/to/program/updater.py -c /where/ever/config.ini run >/dev/null 2>&1
    ```
