# CodeAIdapter-server

## Project Description

CodeAIdapter is a tool designed to help developers solve programming problems more efficiently. We offer the following services:
1. Version conversion
2. Language conversion: conversion between different programming languages
3. Performance optimization
4. Program debugging: compilation errors
5. Program debugging: runtime errors

Whether you are a beginner or an experienced developer, CodeAIdapter can help you tackle various programming challenges more easily!

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management
- [Docker](https://docs.docker.com/get-docker/) for containerization
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) for GCP services

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/CodeAIdapter/CodeAIdapter-server.git
    cd CodeAIdapter-server
    ```

2. Install dependencies:
    ```sh
    poetry install
    ```

3. Create a `.env` file based on the `.env-example` file and fill in the required environment variables:
    ```sh
    cp .env-example .env
    ```

4. Run the application:
    ```sh
    poetry run python app.py
    ```

## Usage Examples

### API Endpoint

The main API endpoint is `/api`, which accepts POST requests with the following JSON payload:

```json
{
    "prompt": "Your prompt here",
    "file": "Your code file content here",
    "filename": "Your code file name here"
}
```

### Example Request

```sh
curl -X POST http://localhost:8080/api -H "Content-Type: application/json" -d '{
    "prompt": "Convert this Python code to Java",
    "file": "print(\"Hello, World!\")",
    "filename": "example.py"
}'
```

### Example Response

```json
{
    "file": "public class Example { public static void main(String[] args) { System.out.println(\"Hello, World!\"); } }",
    "filename": "Example.java",
    "message": "Conversion successful"
}
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
