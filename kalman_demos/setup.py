from setuptools import setup

package_name = 'kalman_demos'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Kalman Robotics',
    maintainer_email='kalmanrobotics@gmail.com',
    description='Demos en Python para el Kit-Kalman de Kalman Robotics',
    license='Apache License, Version 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'cuadrado        = kalman_demos.cuadrado:main',
            'espiral         = kalman_demos.espiral:main',
            'evitar_obstaculos = kalman_demos.evitar_obstaculos:main',
            'explorador      = kalman_demos.explorador:main',
            'seguidor_paredes = kalman_demos.seguidor_paredes:main',
            'control_p       = kalman_demos.control_p:main',
            'antivuelco      = kalman_demos.antivuelco:main',
            'telemetria_live = kalman_demos.telemetria_live:main',
            'radar           = kalman_demos.radar:main',
        ],
    },
)
