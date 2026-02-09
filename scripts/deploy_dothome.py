import os
import ftplib
import getpass
from pathlib import Path

# Configuration
LOCAL_DIR = Path("forkast-web-ui/dist")
REMOTE_DIR = "/html" # Dothome's public folder is usually /html

def upload_files():
    print("="*40)
    print("      Dothome FTP Auto-Uploader")
    print("="*40)
    
    # 1. Get Credentials
    import sys
    if len(sys.argv) > 2:
        username = sys.argv[1]
        password = sys.argv[2]
        print(f"Connecting to forkast.dothome.co.kr as {username}...")
    else:
        print("Connecting to forkast.dothome.co.kr...")
        username = input("FTP ID (default: forkast): ").strip() or "forkast"
        password = getpass.getpass("FTP Password: ")

    host = "forkast.dothome.co.kr"

    try:
        # 2. Connect
        ftp = ftplib.FTP(host)
        ftp.login(user=username, passwd=password)
        ftp.encoding = "utf-8"
        print(f"✅ Connected to {host}")
        
        # 3. Change to Target Directory
        try:
            ftp.cwd(REMOTE_DIR)
            print(f"📂 Changed directory to {REMOTE_DIR}")
        except ftplib.error_perm:
            print(f"❌ Error: Could not find remote directory '{REMOTE_DIR}'. Check your Dothome structure.")
            return

        # 4. Walk and Upload
        for root, dirs, files in os.walk(LOCAL_DIR):
            # Calculate relative path from LOCAL_DIR
            rel_path = Path(root).relative_to(LOCAL_DIR)
            
            # Determine remote path corresponding to this local root
            if rel_path == Path('.'):
                remote_root = ""
            else:
                remote_root = str(rel_path).replace(os.sep, '/')
            
            # Create remote directories if they don't exist
            # Note: We need to ensure parent dirs exist. 
            # Simple approach: Mirror directory structure
            for d in dirs:
                remote_dir = (Path(remote_root) / d).as_posix()
                try:
                    ftp.mkd(remote_dir)
                    print(f"📁 Created remote directory: {remote_dir}")
                except ftplib.error_perm:
                    # Ignore if exists
                    pass

            # Upload Files
            for f in files:
                if f.startswith('.') and f != '.htaccess': continue # Skip hidden files except .htaccess
                
                local_file = Path(root) / f
                
                if remote_root:
                    remote_file = f"{remote_root}/{f}"
                else:
                    remote_file = f
                
                print(f"⬆️  Uploading {f} ...", end='\r')
                with open(local_file, 'rb') as fp:
                    ftp.storbinary(f'STOR {remote_file}', fp)
                print(f"✅ Uploaded {remote_file}    ")

        print("\n🎉 Deployment Complete!")
        print(f"👉 Check your site: http://{username}.dothome.co.kr")
        
        ftp.quit()

    except ftplib.all_errors as e:
        print(f"\n❌ FTP Error: {e}")

if __name__ == "__main__":
    if not LOCAL_DIR.exists():
        print(f"❌ Error: Local export directory '{LOCAL_DIR}' not found. Run export_static.py first.")
    else:
        upload_files()
