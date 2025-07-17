import re
import requests
import time, datetime
import configparser
import click

class Updater:
    version = "0.0.9"
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
        newLine = '\\n' if config['yaml']['dependency'].endswith('${tag}') else ''
        self.yaml_path = config['yaml']['path']
        self.yaml_pattern = re.compile(re.escape(config['yaml']['dependency']).replace("\\$\\{tag\\}", "(.*)" + newLine))
        with open(self.yaml_path, 'r+') as fOd:
            self.yaml_text = fOd.read()

    def update(self, isProd=False):
        echo("*********** DISCORD UPDATER v%s ***********" % self.version)
        echo("Running update..." if isProd else "Running check...")
        
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
        match = re.search(self.yaml_pattern, self.yaml_text)
        if not match:
            raise Exception("Current tag could not be found in the given yaml file")
        
        return match.group(1)

    # Saves the yaml config file with the new tag substituted in
    def save_yaml(self, tag):
        match = re.search(self.yaml_pattern, self.yaml_text)
        if not match:
            raise Exception("Current tag could not be found in the given yaml file")
        
        with open(self.yaml_path, 'w+') as fOd:
            fOd.write(self.yaml_text.replace(match.group(), match.group().replace(match.group(1), tag)))


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
