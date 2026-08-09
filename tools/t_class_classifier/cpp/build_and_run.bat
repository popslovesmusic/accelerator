@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"

echo Compiling t_class_classifier_cpp...
cl /O2 /EHsc /I. ^
    main.cpp ingest.cpp sanitize.cpp feature_extract.cpp t_signature.cpp classify.cpp distribution.cpp audit.cpp ^
    /Fe:t_class_classifier_cpp.exe

if %ERRORLEVEL% EQU 0 (
    echo Compilation successful.
) else (
    echo Compilation failed.
)
