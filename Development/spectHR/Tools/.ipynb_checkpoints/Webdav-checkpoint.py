import easywebdav
import os
from pathlib import Path
from spectHR.Tools.Logger import logger

def initWebdav():
    webdav = easywebdav.connect(
        host='unishare.rug.nl',  # Only the hostname
        username=os.environ['USER'],
        password=os.environ['webdavpass'],
        protocol='https',  # Specify the protocol explicitly
        path=os.environ['unishare'] + '/XDFData'  # The path on the server
    )
    return(webdav)

def copyWebdav(fullname):
    datadir = os.path.dirname(fullname)
    filename = os.path.basename(fullname)
    fullname = os.path.join(datadir, filename)
        
    logger.info(f'Loading "{filename}"')     
    file_path = Path(fullname)
    if not file_path.exists():
        logger.info(f'get {filename} not in local storage')
        webdav = initWebdav()
        remotes = webdav.ls()
        # Use list comprehension to filter .xdf files and directly assign it to xdf_files
        xdf_files = [os.path.basename(remote.name) for remote in remotes if remote.name.endswith('.xdf')]
        if filename in xdf_files:
            logger.info(f'copy {filename} to local ({datadir}) storage')
            webdav.download(filename, fullname)
