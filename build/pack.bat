if exist build\output rd /s/Q build\output
if exist dist rd /s/Q dist
mkdir dist

pyinstaller --noconfirm ^
    --specpath="build" ^
    --distpath="build\output" ^
    --workpath="build\workpath" ^
    --onedir ^
    --noconsole ^
    "app.py"

Xcopy /E /I /Y tables build\output\app\tables
rename build\output\app\app.exe ekalappai.exe
"C:\Program Files (x86)\Inno Setup 6\iscc" build\pack.iss