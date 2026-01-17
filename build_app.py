import PyInstaller.__main__
import os
import shutil
import time
from PyInstaller.utils.hooks import collect_data_files

# --- CONFIGURATION ---
APP_NAME = "ReFlow"
MAIN_FILE = "main.py"
ICON_FILE = "icon.ico"    # Make sure this exists!
SPLASH_FILE = "splash.png" # Make sure this exists!

# 1. FORCE KILL OLD PROCESSES
print(f"--- STARTING BUILD: {APP_NAME} ---")
print("   > Killing old processes to free up files...")
os.system(f"taskkill /F /IM {APP_NAME}.exe 2>nul")
os.system("taskkill /F /IM ffmpeg.exe 2>nul")
time.sleep(2)

# 2. CLEANUP
if os.path.exists("dist"): shutil.rmtree("dist")
if os.path.exists("build"): shutil.rmtree("build")

# 3. COLLECT DATA (Profanity Filter)
print("   > Collecting data files...")
profanity_datas = collect_data_files('better_profanity')
data_args = []
for source, dest in profanity_datas:
    data_args.append(f'--add-data={source};{dest}')

# 4. BUILD COMMAND
cmd = [
    MAIN_FILE,
    f'--name={APP_NAME}',
    '--onedir',
    '--windowed',
    '--clean',
    '--noconfirm',
]

# Add Icon if exists
if os.path.exists(ICON_FILE):
    print(f"   > Using Icon: {ICON_FILE}")
    cmd.append(f'--icon={ICON_FILE}')
else:
    print("   [WARNING] icon.ico not found. Using default.")

# Add Splash if exists
if os.path.exists(SPLASH_FILE):
    print(f"   > Using Splash: {SPLASH_FILE}")
    cmd.append(f'--splash={SPLASH_FILE}')
else:
    print("   [WARNING] splash.png not found. Skipping.")

# Add Data Files
cmd.extend(data_args)

# Add Imports & Excludes
cmd.extend([
    # --- CRITICAL AI HOOKS ---
    '--hidden-import=torch',
    '--hidden-import=transformers',
    '--hidden-import=TTS',
    '--hidden-import=scipy.special.cython_special',
    '--hidden-import=sklearn.utils._typedefs',
    '--hidden-import=sklearn.neighbors._partition_nodes',
    '--hidden-import=scipy.spatial.transform._rotation_groups',
    '--hidden-import=nudenet',
    '--hidden-import=expecttest',
    '--hidden-import=better_profanity',
    
    # --- EXCLUSIONS ---
    '--exclude-module=matplotlib',
    '--exclude-module=ipython',
])

PyInstaller.__main__.run(cmd)

print("\n--- BUILD COMPLETE ---")

# 5. POST-BUILD SETUP
dist_folder = os.path.join("dist", APP_NAME)
ffmpeg_src = "ffmpeg.exe" 

if os.path.exists(ffmpeg_src):
    print(f"   > Copying {ffmpeg_src}...")
    shutil.copy(ffmpeg_src, os.path.join(dist_folder, "ffmpeg.exe"))
else:
    print("   [WARNING] ffmpeg.exe not found! App will not function.")

os.makedirs(os.path.join(dist_folder, "Outputs"), exist_ok=True)

print(f"\nSUCCESS! {APP_NAME} is ready at:\n{os.path.abspath(dist_folder)}")