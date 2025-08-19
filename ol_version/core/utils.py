from pathlib import Path
from typing import Optional, Union
from .commons import QIcon

def set_app_icon(app, icon_path: Optional[Union[str, Path]] = None):
    if icon_path is None:
        icon_path = Path("assets/icons/favicon.ico")
        
    if isinstance(icon_path, str):
        icon_path = Path(icon_path)
        
    if not icon_path.exists():
        raise FileNotFoundError(f"Le fichier d'icône {icon_path} n'existe pas")

    app.setWindowIcon(QIcon(str(icon_path)))