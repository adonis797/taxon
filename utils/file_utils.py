import logging


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    return logger

def get_file_category(extension: str) -> str:
    cate_rules = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.md'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'audio': ['.mp3', '.wav', '.flac', '.aac'],
        'video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv'],
        'code': ['.py', '.js', '.html', '.css', '.java', '.cpp'],
        'executables': ['.exe', '.msi', '.dmg', '.pkg', '.deb']
    }

    extension = extension.lower()
    for category, extensions in cate_rules.items():
        if extension in extensions:
            return category
    
    return 'others'

