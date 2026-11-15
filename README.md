# LogLens

LogLens is a lightweight, dependency-minimal application log analyzer designed for Python 3.12+.

## Features

- Parse standard application logs (`YYYY-MM-DD HH:MM:SS LEVEL METHOD /endpoint STATUS_CODE`)
- Categorize by severity (`INFO`, `WARNING`, `ERROR`)
- Analyze HTTP status codes and error rates (`overall`, `client 4xx`, `server 5xx`)
- Identify problematic API endpoints
- Generate JSON reports and Markdown summary reports
