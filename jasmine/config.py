from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from .utils import iglob
import os

from jasmine_core import Core


class Config(object):
    def __init__(self, yaml_file, project_path=os.getcwd()):
        self.yaml_file = yaml_file
        self.project_path = project_path
        self._load()

    def _glob_filelist(self, filelist, relative_to, default=[]):
        paths = self.yaml.get(filelist) or default
        paths = [os.path.abspath(os.path.join(self.project_path, relative_to, path)) for path in paths]

        relpaths = [os.path.relpath(absolute, relative_to) for absolute in self._glob_paths(paths)]

        #fix py26 relpath from root bug
        return [relpath[3:] if relpath.startswith("../") else relpath for relpath in relpaths]

    def _glob_paths(self, paths):
        files = []

        for src_glob in paths:
            files.extend([os.path.abspath(x) for x in iglob(src_glob)])

        return list(OrderedDict.fromkeys(files))

    def _load(self):
        with open(self.yaml_file, 'rU') as f:
            self.yaml = load(f, Loader=Loader) or {}

    def reload(self):
        self._load()

    def src_files(self):
        return self._glob_filelist('src_files', self.src_dir())

    def stylesheets(self):
        return self._glob_filelist('stylesheets', self.src_dir())

    def helpers(self):
        default_helpers = os.path.join(self.project_path, self.spec_dir(), 'helpers/**/*.js')

        return self._glob_filelist('helpers', self.spec_dir(), default=[default_helpers])

    def spec_files(self):
        default_spec = os.path.join(self.project_path, self.spec_dir(), "**/*[sS]pec.js")

        return self._glob_filelist('spec_files', self.spec_dir(), default=[default_spec])

    def src_dir(self):
        return self.yaml.get("src_dir") or self.project_path

    def spec_dir(self):
        return self.yaml.get("spec_dir") or 'spec/javascripts'

    def script_urls(self):
        return \
            ["__jasmine__/{0}".format(core_js) for core_js in Core.js_files()] +\
            ["__boot__/{0}".format(boot_file) for boot_file in Core.boot_files()] +\
            ["__src__/{0}".format(src_file) for src_file in self.src_files()] +\
            ["__spec__/{0}".format(helper) for helper in self.helpers()] +\
            ["__spec__/{0}".format(spec_file) for spec_file in self.spec_files()]

    def stylesheet_urls(self):
        return \
            ["__jasmine__/{0}".format(core_css) for core_css in Core.css_files()] +\
            ["__src__/{0}".format(css_file) for css_file in self.stylesheets()]