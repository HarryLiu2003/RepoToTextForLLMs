# Import required libraries
import streamlit as st  # Web app framework
from github import Github  # GitHub API wrapper
from tqdm import tqdm  # Progress bar utility
import base64  # For encoding download content

def get_readme_content(repo):
    """Fetch and decode the README.md file from the repository"""
    try:
        readme = repo.get_contents("README.md")
        return readme.decoded_content.decode('utf-8')
    except:
        return "README not found."

def traverse_repo_iteratively(repo):
    """
    Create a tree-like structure of the repository contents
    Uses iteration instead of recursion to handle large repositories
    """
    structure = ""
    # Initialize with root directory
    dirs_to_visit = [("", repo.get_contents(""))]
    dirs_visited = set()  # Track visited directories to avoid cycles

    with st.spinner('Traversing repository structure...'):
        while dirs_to_visit:
            path, contents = dirs_to_visit.pop()
            dirs_visited.add(path)
            for content in contents:
                if content.type == "dir":
                    # If directory hasn't been visited, add to structure and queue
                    if content.path not in dirs_visited:
                        structure += f"{path}/{content.name}/\n"
                        dirs_to_visit.append((f"{path}/{content.name}", repo.get_contents(content.path)))
                else:
                    # Add file to structure
                    structure += f"{path}/{content.name}\n"
    return structure

def get_file_contents_iteratively(repo):
    """
    Fetch contents of all text files in the repository
    Skips binary files and handles encoding issues
    """
    file_contents = ""
    dirs_to_visit = [("", repo.get_contents(""))]
    dirs_visited = set()
    
    # Comprehensive list of binary file extensions to skip
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

    with st.spinner('Fetching file contents...'):
        while dirs_to_visit:
            path, contents = dirs_to_visit.pop()
            dirs_visited.add(path)
            for content in contents:
                if content.type == "dir":
                    # Process subdirectories
                    if content.path not in dirs_visited:
                        dirs_to_visit.append((f"{path}/{content.name}", repo.get_contents(content.path)))
                else:
                    # Handle file content
                    if any(content.name.endswith(ext) for ext in binary_extensions):
                        # Skip binary files
                        file_contents += f"File: {path}/{content.name}\nContent: Skipped binary file\n\n"
                    else:
                        # Process text files
                        file_contents += f"File: {path}/{content.name}\n"
                        try:
                            if content.encoding is None or content.encoding == 'none':
                                file_contents += "Content: Skipped due to missing encoding\n\n"
                            else:
                                try:
                                    # Attempt to decode content with UTF-8
                                    decoded_content = content.decoded_content.decode('utf-8')
                                    # Format content with markdown code block and language hint
                                    file_contents += f"Content:\n```{content.name.split('.')[-1]}\n{decoded_content}\n```\n\n"
                                except UnicodeDecodeError:
                                    file_contents += "Content: Skipped due to encoding issues\n\n"
                        except:
                            file_contents += "Content: Skipped due to access error\n\n"
    return file_contents

def download_button(object_to_download, download_filename, button_text):
    """
    Create a custom styled download button using HTML/CSS
    Converts content to base64 for browser download
    """
    try:
        # Encode content for download
        b64 = base64.b64encode(object_to_download.encode()).decode()
        button_uuid = f"download_{download_filename}"
        
        # Custom CSS for button styling
        custom_css = f"""
            <style>
                #{button_uuid} {{
                    background-color: rgb(255, 255, 255);
                    color: rgb(38, 39, 48);
                    padding: 0.25em 0.38em;
                    position: relative;
                    text-decoration: none;
                    border-radius: 4px;
                    border-width: 1px;
                    border-style: solid;
                    border-color: rgb(230, 234, 241);
                    border-image: initial;
                }}
                #{button_uuid}:hover {{
                    border-color: rgb(246, 51, 102);
                    color: rgb(246, 51, 102);
                }}
            </style>
        """
        # Create download link with custom styling
        dl_link = custom_css + f'<a download="{download_filename}" id="{button_uuid}" href="data:text/plain;base64,{b64}">{button_text}</a><br/><br/>'
        return dl_link
    except Exception as e:
        return str(e)

def main():
    """Main application function"""
    # Set up the main page
    st.title("GitHub Repository Analyzer")
    st.markdown("Analyze GitHub repositories and prepare them for LLM processing")

    # Configure sidebar
    with st.sidebar:
        st.header("Configuration")
        # Input fields for GitHub token and repository URL
        github_token = st.text_input("GitHub Token", type="password")
        repo_url = st.text_input("Repository URL", placeholder="https://github.com/username/repo")
        analyze_button = st.button("Analyze Repository")
        
        # Visual separator in sidebar
        st.markdown("---")

    # Main analysis logic
    if analyze_button:
        # Validate inputs
        if not github_token or not repo_url:
            st.error("Please provide both GitHub token and repository URL")
            return

        try:
            # Initialize GitHub API and get repository
            g = Github(github_token)
            repo = g.get_repo(repo_url.replace('https://github.com/', ''))
            
            # Create tabbed interface for different sections
            readme_tab, structure_tab, contents_tab = st.tabs(["README", "Structure", "Contents"])
            
            # README tab
            with readme_tab:
                st.header("README")
                readme_content = get_readme_content(repo)
                st.markdown(readme_content)

            # Structure tab
            with structure_tab:
                st.header("Repository Structure")
                structure = traverse_repo_iteratively(repo)
                st.code(structure)

            # Contents tab
            with contents_tab:
                st.header("File Contents")
                file_contents = get_file_contents_iteratively(repo)
                st.markdown(file_contents)

            # Create download button for complete analysis
            full_content = f"# Analysis of {repo_url}\n\n## README\n{readme_content}\n\n## Structure\n```\n{structure}\n```\n\n## Contents\n{file_contents}"
            with st.sidebar:
                st.markdown(download_button(full_content, "repo_analysis.txt", "Download Full Analysis"), unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Entry point of the application
if __name__ == "__main__":
    main()