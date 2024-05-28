"""
Setup for pypi releases of llm_analyst
"""
from setuptools import setup, find_packages
from pathlib import Path


# Read the contents of README.md for the long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read the contents of requirements.txt for install_requires
requirements_path = this_directory / "requirements.txt"
install_requires = requirements_path.read_text().splitlines()


setup(name='llm_analyst',
      version='0.1.0',
      description='LLL Research tool',
      long_description_content_type="text/markdown",
      long_description=long_description,

      url='https://github.com/DanHUMassMed/llm_analyst.git',
      author='Dan Higgins',
      author_email='daniel.higgins@yahoo.com',
      license='MIT',

      packages=find_packages(),
      install_requires=install_requires,
      include_package_data=True,
      zip_safe=False)
