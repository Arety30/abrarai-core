import os
import zipfile
import logging

class IngestionPipeline:
    """
    Parses structural workspace contents, unpacking compressed workspace bundles 
    and consolidating text blocks into contextual layouts for model consumption.
    """
    def __init__(self, allowed_extensions=None):
        self.allowed_extensions = allowed_extensions or [".py", ".json", ".md", ".txt", ".lua"]

    def process_directory_tree(self, root_directory):
        """Recursively scrapes a workspace folder, filtering extensions into a standard code document vector."""
        workspace_manifest = {}
        if not os.path.exists(root_directory):
            logging.error(f"Ingestion cancelled: Target workspace path '{root_directory}' does not exist.")
            return workspace_manifest

        for base_path, _, filenames in os.walk(root_directory):
            for filename in filenames:
                file_extension = os.path.splitext(filename)[1].lower()
                if file_extension in self.allowed_extensions:
                    absolute_filepath = os.path.join(base_path, filename)
                    try:
                        with open(absolute_filepath, 'r', encoding='utf-8', errors='ignore') as source_file:
                            workspace_manifest[absolute_filepath] = source_file.read()
                    except Exception as error:
                        logging.warning(f"Bypassing data ingestion for file '{filename}' due to capture failure: {error}")
        
        logging.info(f"Ingestion cycle completed. Successfully parsed {len(workspace_manifest)} assets.")
        return workspace_manifest

    def extract_compressed_payload(self, bundle_path, output_workspace):
        """Safely decompresses raw zip payload structures directly into target run containers."""
        try:
            with zipfile.ZipFile(bundle_path, 'r') as package:
                package.extractall(output_workspace)
            logging.info(f"Successfully unpackaged project structure into targeted array: {output_workspace}")
            return True
        except zipfile.BadZipFile:
            logging.error("Ingestion failed: Target payload is not a valid compressed format or contains broken binary fragments.")
            return False
