import os
import sys

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

sys.path.append(os.path.dirname(__file__))
import init_packages


class InitPackagesBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        if init_packages.main() != 0:
            raise Exception('init_packages.py script failed')
