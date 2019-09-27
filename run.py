"""
Run file for debug configuration.

For reference - vscode launch.json config:
{
    "name": "run",
    "type": "python",
    "request": "launch",
    "envFile": "${workspaceFolder}/../.env",
    "program": "${workspaceRoot}/run.py"

}
"""
from doc_converter.app import app as application

if __name__ == '__main__':
    application.run(port=8080, debug=True, use_reloader=False, threaded=False)
