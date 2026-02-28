
edit settings.ini
run deploy.py to ensure works properly

- must have pip installed and packages pyinstaller, psutil installed. if program not working first try running "pip install pyinstaller psutil" to ensure you have required dependencies.

or uv add pyinstaller



if running for second time with same name ensure old exe is not running before the script is ran to allow it to replace the file.
if different name, will not automatically remove old lock so must manually delete it.

this script can be run by anyone with sufficient privilages so i suggest deleting the source files after completing exe compilation to prevent anyone knowing the script was ran. the password and programs are hidden after deploy is ran but that doesn't stop someone running the script again with the same name to remove it.