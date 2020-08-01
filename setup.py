from setuptools import setup, find_packages

setup(
  name='toybox',
  version='0.1.3',
  packages=find_packages(exclude=["test"]),
  package_data={'interventions': ['resources/game_template.py']}
)
