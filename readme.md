# RepoToTextForLLMs

Automates the analysis of GitHub repositories specifically tailored for usage with large context LLMs. This Python script efficiently fetches README files, repository structure, and non-binary file contents. Additionally, it provides structured outputs complete with pre-formatted prompts to guide further analysis of the repository's content.

**This project is a fork of [Doriandarko/RepoToTextForLLMs](https://github.com/Doriandarko/RepoToTextForLLMs).**

## Key Enhancements from Original

- **Web Interface**: Transformed from a CLI tool to a real-time Streamlit web application
- **AI Analysis**: Integrated OpenAI's GPT-4 to provide intelligent insights about repositories

## Features

- **README Retrieval:** Automatically extracts the content of README.md to provide an initial insight into the repository.
- **Structured Repository Traversal:** Maps out the repository's structure through an iterative traversal method, ensuring thorough coverage without the limitations of recursion.
- **Selective Content Extraction:** Retrieves text contents from files, intelligently skipping over binary files to streamline the analysis process.
- **AI-Powered Analysis:** Utilizes GPT-4 to provide detailed analysis of the repository's structure and content.

## Prerequisites

To use **RepoToTextForLLMs**, you'll need:

- Python installed on your system.
- A virtual environment manager (e.g., `venv`, `virtualenv`).
- The following Python packages:
  - `streamlit`
  - `PyGithub`
  - `openai`
  - `re`

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/RepoToTextForLLMs.git
    cd RepoToTextForLLMs
    ```

2. **Set up a virtual environment:**
    ```bash
    python -m venv myenv
    source myenv/bin/activate  # On Windows: myenv\Scripts\activate
    ```

3. **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

    *Note: The `requirements.txt` file contains all necessary dependencies updated from the original project.*

4. **Configure environment variables:**

    - Create a `.env` file in the project root (if not already present) and add your GitHub and OpenAI tokens:

        ```python
        GITHUB_TOKEN = 'YOUR_GITHUB_TOKEN'
        OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'
        ```

## Getting Started

1. **Ensure your virtual environment is activated:**
    ```bash
    source myenv/bin/activate  # On Windows: myenv\Scripts\activate
    ```

2. **Run the application:**
    ```bash
    streamlit run app.py
    ```

3. **Interact with the app:**

    - Open your browser and navigate to the URL provided by Streamlit.
    - Enter the GitHub repository URL you wish to analyze.
    - Click on "Analyze Repository" to initiate the analysis.

## How to Use

1. Clone the repository and set up the environment as described in the **Installation** section.
2. Run the Streamlit application.
3. Input the GitHub repository URL into the provided field.
4. The application will process the repository and display:
    - README content
    - LICENSE information
    - Repository structure
    - File contents (excluding binary files)
    - AI-generated analysis based on the repository's content

## Contributing

Contributions to **RepoToTextForLLMs** are welcomed. Whether it's through submitting pull requests, reporting issues, or suggesting improvements, your input helps make this tool better for everyone. Please see the [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
