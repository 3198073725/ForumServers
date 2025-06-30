@echo off
chcp 65001 > nul
echo 正在启动论坛系统...

REM 激活虚拟环境
call venv_new\Scripts\activate

REM 启动 Django API 服务器
start cmd /c "cd ForumBackend && python manage.py runserver"

REM 启动前端开发服务器
start cmd /c "cd ForumFrontend && npm run serve"

echo 服务器启动完成！
echo API 服务器运行地址：http://localhost:8000
echo 前端页面访问地址：http://localhost:8080
echo.
echo 请保持这些终端窗口开启。关闭它们将会停止相关服务。
echo.
pause 