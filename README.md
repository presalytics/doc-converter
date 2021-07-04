# Presalytics Doc Converter

Convert PowerPoint, Google Slides and Libreoffice files to images (.png), thumbnails and Scaleable Vector Graphics (.svg) files with simple api calls over HTTP.

## Table of Contents

1. [Getting Started](#Getting)
2. [About](#About)
3. [Development](#Development)
4. [Next Steps](#TODOs)
5. [Contributing](#Contributing)

## Getting started

To run a local version of the application, clone this repo and use the [docker-compose](https://docs.docker.com/compose/install/) command from the command line or your version of [Docker Desktop](https://docs.docker.com/desktop/).

From the command line, the commands:

````bash
git clone https://github.com/presalytics/doc-converter.git
docker-compose up
````

will get the application running.  Sample .png and .svg can be created by running the integration tests by running the commands below in a new terminal:

````bash
python3 -m venv venv
. venv/bin/activate
pip intall -U pip
pip install -r requirements.txt -r requirements.debug.txt
python -m unittest test.integration_test
````

After these commands complete, the sample files `Rectanagle.png` and `Rectangle.svg` will be located the `out/` directory in the current folder.

To convert you own files locally, you can create a directory named `in` in the root directory of your clone repo.  Place your files in the directory you created and run the command:

````bash
python run.py <convert_type>
````

where `<convert_type>` is either `svg` or `png`, depending upon the type of output file that you need.  This argument defautls to `png`.

## Development

To run a debug configuration, run the command:

````bash
docker-compose -f docker-compose-debug.yml up
````

You can attach your debugger using the `debugpy` package or by launch the `api-debug-attach` and `worker-debug-attach` configurations from vscode.

This project's code linted using the mypy and flake8 linters. Ensure to install the required mypy types with the command `mypy --intall-types` from your virtual environment.

### About this project

This project was created to create any easy, langauage-agnositic way convert office documents (e.g., PowerPoint, Google Slides, Libreoffice) to images for display and editing over the web.  This helps business sales analytics quickly turn around and contributed to client-side development and applications.  This is also a convenient thumbnail server for file types that are typically hard proview without 3rd party libraries.  and Previous solutions are platform- or language-dependent (e.g., requires VBA or Google Scripts). For api documentation, please visit [https://api.presalytics.io/doc-converter/docs](https://api.presalytics.io/doc-converter/docs).

Image processing jobs are managed on a [celery queue](https://docs.celeryproject.org/en/stable/).  The image conversation handled on a subprocess by calling into the uno apis developed by the [Libreoffice project](https://www.libreoffice.org/).  The API webserver is implemented using the [FastApi project](https://fastapi.tiangolo.com/).  Many thnks to all the these open source contributors whose work is conbimed to build this point solution.

## TODOs: Next steps

- [ ] Add websocket support
- [ ] Reduce built docker image sizes
- [ ] Add https paths and worker tasks for output image (.png) scaling

## Contributing

We'd love your contributions!  Please either open an issue, or better yet, write a PR.  And, of course, don't be a jerk.
