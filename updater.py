import requests
import time, datetime
import configparser
import click

class Updater:
    version = "0.0.5"

    def __init__(self, config_dir):
        config = configparser.ConfigParser()
        config.read(config_dir)
        if 'github' not in config.sections() or 'yaml' not in config.sections():
            raise Exception("Cannot load config file: missing section(s): 'yaml' / 'github'")
        
        self.github_repository = config['github']['repository']
        self.github_token = config['github']['token']
        self.yaml_path = config['yaml']['path']
        self.yaml_dependency = config['yaml']['dependency']

    def update(self, isProd=False):
        testToken = '[TEST]' if not isProd else ''
        echo("******** %s DISCORD UPDATER V%s %s ********" % (testToken, self.version, testToken))
        
        lines, current_dependency = self.find_current_dependency()
        new_dependency = self.yaml_dependency.replace("${tag}", self.get_latest_tag())
        if current_dependency != new_dependency:
            echo("There is an available update!", 1)
            echo("%s -> %s" % (current_dependency, new_dependency), 2)
            if isProd:
                echo("Writing to the yaml file...", 1)
                self.save_dependency(lines, new_dependency)
                echo("Done!", 1)
        else:
            echo("No updates at this time.", 1)

    # Grabs the tag name using github's api
    def get_latest_tag(self):
        headers = {
            'Accept': "application/vnd.github+json",
            'Authorization': f"Bearer {self.github_token}",
            'X-GitHub-Api-Version': "2022-11-28"
        }
        result = requests.get(f"https://api.github.com/repos/{self.github_repository}/releases/latest", headers=headers)
        tag = result.json().get('tag_name', None)
        if tag is None:
            raise Exception("Could not load the github tag. Do you have a valid github api token in the config?")
        return result.json()['tag_name']

    # Finds the current tag name by reading the yaml config file
    def find_current_dependency(self):
        lines = []
        with open(self.yaml_path, 'r+') as fOd:
            lines = fOd.readlines()
        
        dependency = ""
        for line in lines:
            findDependency = line.find(self.yaml_dependency.replace("${tag}", ""))
            if findDependency != -1:
                dependency = line[findDependency:].replace('\n', '').strip()
                break

        if dependency == "":
            raise Exception("Dependency line could not be found in the given yaml file")            
        return lines, dependency
    
    def save_dependency(self, lines, dependency):
        with open(self.yaml_path, 'w+') as fOd:
            for line in lines:
                findDependency = line.find(self.yaml_dependency.replace("${tag}", ""))
                if findDependency != -1:
                    fOd.write(line[0:findDependency] + dependency + "\n")
                else:
                    fOd.write(line)


@click.group()
@click.option('-c', '--config', default='config.ini', type=click.Path(exists=True))
@click.pass_context
def main(ctx, config):
    ctx.obj = Updater(config)

@main.command(help="Check for an update without changing the yaml file")
@click.pass_obj
def check(obj):
    obj.update()

@main.command(help="Check for an update and change the yaml file")
@click.pass_obj
def update(obj):
    obj.update(True)


# HELPER METHODS
def echo(text, level=0):
    space = '  ' * level
    click.echo('[%s] %s%s' % (datetime.datetime.now(), space, text))

if __name__ == '__main__':
    main()