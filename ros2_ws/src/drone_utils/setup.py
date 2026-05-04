from setuptools import setup

package_name = 'drone_utils'

setup(
    name=package_name,
    version='0.1.0',
    packages=[],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', [
            'launch/mavros_sitl.launch.py',
            'launch/drone_sim.launch.py',
        ]),
        ('share/' + package_name + '/scripts', [
            'scripts/drone_takeoff.py',
            'scripts/drone_land.py',
            'scripts/drone_status.py',
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='dev@example.com',
    description='无人机仿真和控制工具包',
    license='MIT',
    entry_points={},
)
