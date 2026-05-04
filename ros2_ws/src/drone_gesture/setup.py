from setuptools import find_packages, setup

package_name = 'drone_gesture'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', [
            'launch/gesture_system.launch.py',
            'launch/gesture_test.launch.py',
        ]),
        ('share/' + package_name + '/config', [
            'config/gesture_params.yaml',
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='dev@example.com',
    description='无人机手势识别控制系统',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'gesture_recognizer = drone_gesture.gesture_recognizer:main',
            'gesture_commander = drone_gesture.gesture_commander:main',
        ],
    },
)
