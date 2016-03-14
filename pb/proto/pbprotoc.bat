@echo off
setlocal enabledelayedexpansion
set ParentPath=.\
for /f "delims=" %%a in ('dir /b "%ParentPath%\*.proto"') do (
rem   set str=%%a
rem   set var=!str:~0,-6!  rem -6可替换
protoc.exe  --python_out=..\ %%a
    rem echo %%a
)