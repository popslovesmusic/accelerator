@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"
cl /O2 /arch:AVX2 /openmp /EHsc /LD agent_capi.cpp AgentEngineAVX2.cpp /Fe:agent_capi.dll
