from cirrus.cli import component


class CoreTask(component.ComponentBase):
    enable_cli = False
    user_extendable = False
    python = component.ComponentFile(filename='task.py', content_fn=lambda x: '')
    definition = component.ComponentFile(filename='definition.yml', content_fn=lambda x: '')
    # make this optional once we have them
    readme = component.ComponentFile(filename='README.md', optional=True)
    requirements = component.ComponentFile(filename='requirements.txt', optional=True)
