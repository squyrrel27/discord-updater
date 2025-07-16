import requests
import time, datetime
import configparser
import click

class Updater:
    version = "0.0.7"
    github_url = "https://api.github.com/repos/${repo}/releases/latest"

    def __init__(self, config_dir):
        config = configparser.ConfigParser()
        config.read(config_dir)
        if 'github' not in config.sections() or 'yaml' not in config.sections():
            raise Exception("Cannot load config file: missing section(s): 'yaml' / 'github'")
        
        self.github_repository = config['github']['repository']
        self.github_token = config['github']['token']
        self.github_headers = {
            'Accept': "application/vnd.github+json",
            'Authorization': f"Bearer {self.github_token}",
            'X-GitHub-Api-Version': "2022-11-28"
        }
        self.yaml_path = config['yaml']['path']
        self.yaml_dependency = config['yaml']['dependency']
        self.yaml_lines = []
        with open(self.yaml_path, 'r+') as fOd:
            self.yaml_lines = fOd.readlines()

    def update(self, isProd=False):
        testToken = '[TEST]' if not isProd else ''
        echo("******** %s DISCORD UPDATER V%s %s ********" % (testToken, self.version, testToken))
        
        current_tag = self.get_current_tag()
        latest_tag = self.get_latest_tag()
        if current_tag != latest_tag:
            echo("There is an available update! (%s -> %s)" % (current_tag, latest_tag), 0)
            if isProd:
                echo("Writing to the yaml file...", 1)
                self.save_yaml(latest_tag)
                echo("Done!", 1)
        else:
            echo("No updates at this time. (%s latest)" % latest_tag, 0)

    # Grabs the latest tag name using github's api
    def get_latest_tag(self):
        result = requests.get(self.github_url.replace('${repo}', self.github_repository), headers=self.github_headers)
        tag = result.json().get('tag_name', None)
        if tag is None:
            raise Exception("Could not load the github tag. Do you have a valid github api token in the config?")
        return tag

    # Grabs the current tag name by reading the yaml config file
    def get_current_tag(self):
        tag = None
        for line in self.yaml_lines:
            findDependency = line.find(self._replace_tag())
            if findDependency != -1:
                tag = line[findDependency+len(self._replace_tag()):].replace('\n', '').strip()
                break

        if tag is None:
            raise Exception("Current tag could not be found in the given yaml file")            
        return tag

    def save_yaml(self, tag):
        with open(self.yaml_path, 'w+') as fOd:
            for line in self.yaml_lines:
                findDependency = line.find(self._replace_tag())
                if findDependency != -1:
                    fOd.write(line[0:findDependency+len(self._replace_tag())] + tag + "\n")
                else:
                    fOd.write(line)

    def _replace_tag(self, tag=""):
        return self.yaml_dependency.replace("${tag}", tag)


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