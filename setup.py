from setuptools import setup, find_packages


def reqs(*fns):
    return [line for fn in fns for line
            in open('requirements/{}.txt'.format(fn)).readlines()]


setup(name='MyPyFi',
      author='Andrew Edmonds',
      author_email='andrewre@umich.edu',
      description=('My centralized hub for financial analytics.'),
      long_description=('README'),
      version='0.1',
      packages=find_packages(),
      install_requires=reqs('base'),
      tests_require=reqs('base', 'dev'),
      )