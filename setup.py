from distutils.core import setup


setup(
    name='rionotes',
    version='0.1.2',
    url='https://github.com/Rioran/rio_notes.git',
    author='Roman Rioran Voronov',
    author_email='voronov_rv@mail.ru',
    description='Compose WAV music using notes.',
    packages=['rionotes'],
    install_requires=[
        'matplotlib >= 3.5.2',
        'numpy >= 1.22.4',
        'scipy >= 1.8.1',
    ],
)