import streamlit as st 
from github import Github 
import re
from openai import OpenAI 
from typing import Optional
from config import GITHUB_TOKEN, OPENAI_API_KEY

def get_readme_content(repo):
    """Fetch and decode the README.md file from the repository"""
    readme_files = ["README.md", "README", "readme.md", "readme"]
    
    try:
        for readme_name in readme_files:
            try:
                readme = repo.get_contents(readme_name)
                content = readme.decoded_content.decode('utf-8')
                
                # Get repository details
                repo_full_name = repo.full_name
                default_branch = repo.default_branch
                
                # Convert relative image paths to absolute GitHub raw URLs
                content = content.replace(
                    'src="./', 
                    f'src="https://raw.githubusercontent.com/{repo_full_name}/{default_branch}/'
                )
                content = content.replace(
                    'src="/', 
                    f'src="https://raw.githubusercontent.com/{repo_full_name}/{default_branch}/'
                )
                
                # Handle paths without ./ or /
                content = re.sub(
                    r'src="(?!http[s]?://|/)(.*?)"',
                    f'src="https://raw.githubusercontent.com/{repo_full_name}/{default_branch}/\\1"',
                    content
                )
                
                return content
            except:
                continue
        return "README not found."
    except:
        return "README not found."

def get_license_content(repo):
    """Fetch and decode the LICENSE file from the repository"""
    license_files = ["LICENSE", "LICENSE.md", "license", "license.md"]
    
    try:
        for license_name in license_files:
            try:
                license_file = repo.get_contents(license_name)
                return license_file.decoded_content.decode('utf-8')
            except:
                continue
        return "LICENSE not found."
    except:
        return "LICENSE not found."

def traverse_repository(repo, process_content_fn):
    """
    Base function to traverse repository
    @param repo: GitHub repository object
    @param process_content_fn: Function to process each content item
    @return: Result of processing (string)
    """
    result = ""
    dirs_to_visit = [("", repo.get_contents(""))]
    dirs_visited = set()

    while dirs_to_visit:
        path, contents = dirs_to_visit.pop()
        dirs_visited.add(path)
        for content in contents:
            if content.type == "dir":
                if content.path not in dirs_visited:
                    dirs_to_visit.append((f"{path}/{content.name}", repo.get_contents(content.path)))
            # Process content using the provided function
            result += process_content_fn(path, content)
            
    return result

def traverse_repo_iteratively(repo):
    """Creates a tree-like structure of the repository contents"""
    def process_structure(path, content):
        if content.type == "dir":
            return f"{path}/{content.name}/\n"
        return f"{path}/{content.name}\n"

    with st.spinner('Traversing repository structure...'):
        return traverse_repository(repo, process_structure)

def get_file_contents_iteratively(repo):
    """Fetches contents of all text files in the repository"""
    binary_extensions = [
        # Compiled executables and libraries
        '.exe', '.dll', '.so', '.a', '.lib', '.dylib', '.o', '.obj',
        # Compressed archives
        '.zip', '.tar', '.tar.gz', '.tgz', '.rar', '.7z', '.bz2', '.gz', '.xz', '.z', '.lz', '.lzma', '.lzo', '.rz', '.sz', '.dz',
        # Application-specific files
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',
        # Media files (less common)
        '.png', '.jpg', '.jpeg', '.gif', '.mp3', '.mp4', '.wav', '.flac', '.ogg', '.avi', '.mkv', '.mov', '.webm', '.wmv', '.m4a', '.aac',
        # Virtual machine and container images
        '.iso', '.vmdk', '.qcow2', '.vdi', '.vhd', '.vhdx', '.ova', '.ovf',
        # Database files
        '.db', '.sqlite', '.mdb', '.accdb', '.frm', '.ibd', '.dbf',
        # Java-related files
        '.jar', '.class', '.war', '.ear', '.jpi',
        # Python bytecode and packages
        '.pyc', '.pyo', '.pyd', '.egg', '.whl',
        # Other potentially important extensions
        '.deb', '.rpm', '.apk', '.msi', '.dmg', '.pkg', '.bin', '.dat', '.data',
        '.dump', '.img', '.toast', '.vcd', '.crx', '.xpi', '.lockb', 'package-lock.json', '.svg' ,
        '.eot', '.otf', '.ttf', '.woff', '.woff2',
        '.ico', '.icns', '.cur',
        '.cab', '.dmp', '.msp', '.msm',
        '.keystore', '.jks', '.truststore', '.cer', '.crt', '.der', '.p7b', '.p7c', '.p12', '.pfx', '.pem', '.csr',
        '.key', '.pub', '.sig', '.pgp', '.gpg',
        '.nupkg', '.snupkg', '.appx', '.msix', '.msp', '.msu',
        '.deb', '.rpm', '.snap', '.flatpak', '.appimage',
        '.ko', '.sys', '.elf',
        '.swf', '.fla', '.swc',
        '.rlib', '.pdb', '.idb', '.pdb', '.dbg',
        '.sdf', '.bak', '.tmp', '.temp', '.log', '.tlog', '.ilk',
        '.bpl', '.dcu', '.dcp', '.dcpil', '.drc',
        '.aps', '.res', '.rsrc', '.rc', '.resx',
        '.prefs', '.properties', '.ini', '.cfg', '.config', '.conf',
        '.DS_Store', '.localized', '.svn', '.git', '.gitignore', '.gitkeep',
    ]

    # Files to exclude from contents (matching the above functions)
    excluded_files = [
        "README.md", "README", "readme.md", "readme",
        "LICENSE", "LICENSE.md", "license", "license.md"
    ]

    def process_content(path, content):
        # Skip excluded files (case-insensitive)
        if content.name.lower() in [f.lower() for f in excluded_files]:
            return ""
        
        if content.type == "dir":
            return ""
            
        if any(content.name.endswith(ext) for ext in binary_extensions):
            return f"File: {path}/{content.name} (skipped binary file)\n\n"
            
        result = f"File: {path}/{content.name}\n"
        try:
            if content.encoding is None or content.encoding == 'none':
                return f"File: {path}/{content.name} (skipped due to missing encoding)\n\n"
                
            try:
                decoded_content = content.decoded_content.decode('utf-8')
                return result + f"```{content.name.split('.')[-1]}\n{decoded_content}\n```\n\n"
            except UnicodeDecodeError:
                return f"File: {path}/{content.name} (skipped due to encoding issues)\n\n"
        except:
            return f"File: {path}/{content.name} (skipped due to access error)\n\n"

    with st.spinner('Fetching file contents...'):
        return traverse_repository(repo, process_content)

class RepositoryAnalysisPrompt:
    """Handles creation and formatting of repository analysis prompts"""
    
    @staticmethod
    def get_instructions(repo_url: str) -> str:
        """Generate the analysis instructions prompt"""
        instructions = f"Prompt: Analyze the {repo_url} repository to understand its structure, purpose, and functionality. Follow these steps to study the codebase:\n\n"
        instructions += "1. Read the README file to gain an overview of the project, its goals, and any setup instructions.\n\n"
        instructions += "2. Examine the repository structure to understand how the files and directories are organized.\n\n"
        instructions += "3. Identify the main entry point of the application (e.g., main.py, app.py, index.js) and start analyzing the code flow from there.\n\n"
        instructions += "4. Study the dependencies and libraries used in the project to understand the external tools and frameworks being utilized.\n\n"
        instructions += "5. Analyze the core functionality of the project by examining the key modules, classes, and functions.\n\n"
        instructions += "6. Look for any configuration files (e.g., config.py, .env) to understand how the project is configured and what settings are available.\n\n"
        instructions += "7. Investigate any tests or test directories to see how the project ensures code quality and handles different scenarios.\n\n"
        instructions += "8. Review any documentation or inline comments to gather insights into the codebase and its intended behavior.\n\n"
        instructions += "9. Identify any potential areas for improvement, optimization, or further exploration based on your analysis.\n\n"
        instructions += "10. Provide a summary of your findings, including the project's purpose, key features, and any notable observations or recommendations.\n\n"
        instructions += "Use the files and contents provided below to complete this analysis:\n\n"
        return instructions

    @staticmethod
    def create_combined_prompt(
        repo_url: str,
        readme_content: str,
        license_content: str,
        structure: str,
        file_contents: str
    ) -> str:
        """Create the combined prompt for analysis"""
        instructions = RepositoryAnalysisPrompt.get_instructions(repo_url)
        return f"{instructions}\n# Analysis of {repo_url}\n\n## README\n{readme_content}\n\n## LICENSE\n{license_content}\n\n## Structure\n```\n{structure}\n```\n\n## Contents\n{file_contents}"

def analyze_with_gpt4(content: str, api_key: str) -> Optional[str]:
    """Analyze the repository content using GPT-4-Turbo"""
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4-1106-preview", 
            messages=[
                {"role": "system", "content": "You are a skilled software engineer analyzing a GitHub repository."},
                {"role": "user", "content": content}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        if "context_length_exceeded" in str(e):
            # If still too long, we could try to truncate or summarize the content
            return ("Error: Repository content is too large for analysis. ")
        return f"Error during GPT-4 analysis: {str(e)}"

def main():
    """Main application function"""
    st.title("GitHub Repository Analyzer")
    st.markdown("Analyze GitHub repositories, ready for LLM processing")

    # Configure sidebar
    with st.sidebar:
        st.header("Configuration")
        # github_token = st.text_input("GitHub Token", type="password")
        repo_url = st.text_input("Repository URL", placeholder="https://github.com/username/repo")
        analyze_button = st.button("Analyze Repository")
        # st.markdown("---")
        # openai_key = st.text_input("OpenAI API Key", type="password")
        st.markdown("---")

    if analyze_button:
        if not repo_url:
            st.error("Please provide a repository URL")
            return

        try:
            g = Github(GITHUB_TOKEN)
            repo = g.get_repo(repo_url.replace('https://github.com/', ''))
            
            # Create tabbed interface
            readme_tab, license_tab, structure_tab, contents_tab, analysis_tab = st.tabs(
                ["README", "LICENSE", "Structure", "Contents", "AI Analysis"]
            )
            
            with readme_tab:
                st.header("README")
                readme_content = get_readme_content(repo)
                st.markdown(readme_content, unsafe_allow_html=True)

            with license_tab:
                st.header("LICENSE")
                license_content = get_license_content(repo)
                st.markdown(license_content)

            with structure_tab:
                st.header("Repository Structure")
                structure = traverse_repo_iteratively(repo)
                st.code(structure)

            with contents_tab:
                st.header("File Contents")
                file_contents = get_file_contents_iteratively(repo)
                st.markdown(file_contents)

            # Create combined prompt
            combined_prompt = RepositoryAnalysisPrompt.create_combined_prompt(
                repo_url,
                readme_content,
                license_content,
                structure,
                file_contents
            )
            
            # Add AI Analysis tab content
            with analysis_tab:
                st.header("AI Analysis")
                with st.spinner("Analyzing repository with GPT-4..."):
                    analysis = analyze_with_gpt4(combined_prompt, OPENAI_API_KEY)
                    st.markdown(analysis)

            # Show download button for raw data after everything is done
            with st.sidebar:
                st.download_button(
                    label="Download Raw Data",
                    data=combined_prompt,
                    file_name="repo_raw_data.txt",
                    mime="text/plain",
                    type="tertiary"
                )

        except Exception as e:
            if "404" in str(e):
                st.error("Repository not found. Please enter a valid and public repository URL.")
            else:
                st.error(f"An error occurred: {str(e)}")

# Entry point of the application
if __name__ == "__main__":
    main()