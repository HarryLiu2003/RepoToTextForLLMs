import streamlit as st
from github import Github
from tqdm import tqdm
import base64

def get_readme_content(repo):
    try:
        readme = repo.get_contents("README.md")
        return readme.decoded_content.decode('utf-8')
    except:
        return "README not found."

def traverse_repo_iteratively(repo):
    structure = ""
    dirs_to_visit = [("", repo.get_contents(""))]
    dirs_visited = set()

    with st.spinner('Traversing repository structure...'):
        while dirs_to_visit:
            path, contents = dirs_to_visit.pop()
            dirs_visited.add(path)
            for content in contents:
                if content.type == "dir":
                    if content.path not in dirs_visited:
                        structure += f"{path}/{content.name}/\n"
                        dirs_to_visit.append((f"{path}/{content.name}", repo.get_contents(content.path)))
                else:
                    structure += f"{path}/{content.name}\n"
    return structure

def get_file_contents_iteratively(repo):
    # Using the same binary_extensions list from your original code
    # Reference to the original file for binary_extensions
    binary_extensions = ['.exe', '.dll', '.so', '.pdf', '.jpg', '.png']  # Shortened for brevity
    
    file_contents = ""
    dirs_to_visit = [("", repo.get_contents(""))]
    dirs_visited = set()

    with st.spinner('Fetching file contents...'):
        while dirs_to_visit:
            path, contents = dirs_to_visit.pop()
            dirs_visited.add(path)
            for content in contents:
                if content.type == "dir":
                    if content.path not in dirs_visited:
                        dirs_to_visit.append((f"{path}/{content.name}", repo.get_contents(content.path)))
                else:
                    if any(content.name.endswith(ext) for ext in binary_extensions):
                        file_contents += f"File: {path}/{content.name}\nContent: Skipped binary file\n\n"
                    else:
                        file_contents += f"File: {path}/{content.name}\n"
                        try:
                            if content.encoding is None or content.encoding == 'none':
                                file_contents += "Content: Skipped due to missing encoding\n\n"
                            else:
                                try:
                                    decoded_content = content.decoded_content.decode('utf-8')
                                    file_contents += f"Content:\n{decoded_content}\n\n"
                                except UnicodeDecodeError:
                                    file_contents += "Content: Skipped due to encoding issues\n\n"
                        except:
                            file_contents += "Content: Skipped due to access error\n\n"
    return file_contents

def download_button(object_to_download, download_filename, button_text):
    try:
        b64 = base64.b64encode(object_to_download.encode()).decode()
        button_uuid = f"download_{download_filename}"
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
        dl_link = custom_css + f'<a download="{download_filename}" id="{button_uuid}" href="data:text/plain;base64,{b64}">{button_text}</a><br/><br/>'
        return dl_link
    except Exception as e:
        return str(e)

def main():
    st.title("GitHub Repository Analyzer")
    st.markdown("Analyze GitHub repositories and prepare them for LLM processing")

    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        github_token = st.text_input("GitHub Token", type="password")
        repo_url = st.text_input("Repository URL", placeholder="https://github.com/username/repo")

    if st.sidebar.button("Analyze Repository"):
        if not github_token or not repo_url:
            st.error("Please provide both GitHub token and repository URL")
            return

        try:
            g = Github(github_token)
            repo = g.get_repo(repo_url.replace('https://github.com/', ''))
            
            # Create tabs for different sections
            readme_tab, structure_tab, contents_tab = st.tabs(["README", "Structure", "Contents"])
            
            with readme_tab:
                st.header("README")
                readme_content = get_readme_content(repo)
                st.markdown(readme_content)

            with structure_tab:
                st.header("Repository Structure")
                structure = traverse_repo_iteratively(repo)
                st.text(structure)

            with contents_tab:
                st.header("File Contents")
                file_contents = get_file_contents_iteratively(repo)
                st.text(file_contents)

            # Create download button for full analysis
            full_content = f"# Analysis of {repo_url}\n\n## README\n{readme_content}\n\n## Structure\n{structure}\n\n## Contents\n{file_contents}"
            st.markdown(download_button(full_content, "repo_analysis.txt", "Download Full Analysis"), unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()