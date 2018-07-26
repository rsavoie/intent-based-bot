from setuptools import setup

setup(
	name='intentbasedbot',
	packages=['intentbasedbot'],
	include_package_data=True,
	install_requires=[
    	'flask', 'requests', 'ansicolors', 'rfc3339', 'pymessenger', 'pandas','numpy', 'keras', 'scikit-learn', 'tensorflow'
	],
)