from setuptools import setup


with open("VERSION.txt") as ver:
    VERSION = ver.read().strip()


def readme():
    with open("README.txt") as rm:
        return rm.read()


setup(name="pbar",
      version=VERSION,
      description="Simple console progress bar widget",
      long_description=readme(),
      url=None,
      author="Will Stokes",
      author_email="william.stokes@zf.com",
      license="MIT",
      packages=["pbar"],
      install_requires=[],
      entry_points={
          "console_scripts": []
      },
      zip_safe=True,
      include_package_data=True,
      classifiers=[
          "Programming Language :: Python :: 3",
          "Operation System :: Windows"])