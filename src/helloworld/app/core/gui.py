import os
import asyncio
import urllib.parse
import toga
from dotenv import load_dotenv

loading_html='''
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport"content="width=device-width, initial-scale=1.0"/><title>Loading Animation</title><style>html,body{overflow:hidden;margin:0;padding:0;width:100%;height:100%}.loader{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:50px;height:50px}.loader::before{content:"";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:20px;height:20px;border-radius:50%;border:3px solid#333;border-top-color:#ffcc00;animation:spin 1s linear infinite}@keyframes spin{0%{transform:translate(-50%,-50%)rotate(0deg)}100%{transform:translate(-50%,-50%)rotate(360deg)}}.svg-style{width:100%;height:100%;display:flex;flex-direction:column;justify-content:center;align-items:center}.text-style{color:white}body{background-color:#383477;width:100vw;height:100vh;display:flex;justify-content:center;align-items:center;overflow:hidden}svg{max-width:100%;max-height:100%;preserveAspectRatio:xMidYMid meet}</style></head><body><div class="svg-style"><svg id="Layer_1"width="100"height="100"data-name="Layer 1"viewBox="0 0 144 144"><defs><clipPath id="clippath-3"><rect x="17.7"y="-60.3671"width="18.1"height="83.6"style="fill: none; stroke-width: 0px"><animate attributeName="y"begin="0s"values="-60.3671;23.23;23.23;106.8334;106.8334"keyTimes="0;0.083;0.5;0.583;1"repeatCount="indefinite"dur="6s"fill="freeze"/></rect></clipPath><clipPath id="clippath-4"><rect x="-90.91"y="72"width="108.6"height="53.87"style="fill: none; stroke-width: 0px"><animate attributeName="x"begin="0s"values="-90.91;-90.91;17.7;17.7;126.3;126.3"keyTimes="0;0.07;0.25;0.54;0.75;1"repeatCount="indefinite"dur="6s"fill="freeze"/></rect></clipPath><clipPath id="clippath-1"><rect x="35.8"y="40.65"width="36.2"height="45.28"style="fill: none; stroke-width: 0px"><animate attributeName="x"begin="0s"values="35.8;35.8;72;72;108.2;108.2"keyTimes="0;0.167;0.25;0.667;0.75;1"repeatCount="indefinite"dur="6s"fill="freeze"/></rect></clipPath><clipPath id="clippath-2"><rect x="126.3"y="51.1"width="30.17"height="38.32"style="fill: none; stroke-width: 0px"><animate attributeName="x"begin="0s"values="126.3;126.3;96.13;96.13;65.9667;65.9667"keyTimes="0;0.25;0.33;0.75;0.833;1"repeatCount="indefinite"dur="6s"fill="freeze"/></rect></clipPath><clipPath id="clippath"><rect x="108.2"y="18.17"width="70.59"height="39.9"style="fill: none; stroke-width: 0px"><animate attributeName="x"begin="0s"values="108.2;108.2;37.61;37.61;-32.98;-32.98"keyTimes="0;0.25;0.4167;0.75;0.9167;1"repeatCount="indefinite"dur="6s"fill="freeze"/></rect></clipPath><linearGradient id="linear-gradient"x1="37.61"y1="72"x2="108.2"y2="72"gradientUnits="userSpaceOnUse"><stop offset="0"stop-color="#66f"/><stop offset=".17"stop-color="#6464fa"/><stop offset=".34"stop-color="#605fee"/><stop offset=".51"stop-color="#5958d9"/><stop offset=".69"stop-color="#4f4dbc"/><stop offset=".87"stop-color="#433f97"/><stop offset="1"stop-color="#383477"/></linearGradient><linearGradient id="linear-gradient-2"x1="96.13"y1="70.26"x2="126.3"y2="70.26"xlink:href="#linear-gradient"/><linearGradient id="linear-gradient-3"x1="17.7"y1="72"x2="126.3"y2="72"gradientUnits="userSpaceOnUse"><stop offset="0"stop-color="#66f"/><stop offset="1"stop-color="#00ced1"/></linearGradient><filter id="X_Shadow_3"x="-200%"y="-200%"width="400%"height="400%"><feDropShadow dx="0"dy="0"flood-color="black"flood-opacity="0.4"stdDeviation="6"/></filter></defs><path d="M126.3,72c0-2.16-1.15-4.15-3.02-5.23-5.03-2.9-10.06-5.81-15.08-8.71v-17.42c0-2.16-1.15-4.15-3.02-5.23-9.05-5.23-18.1-10.45-27.15-15.68-3.73-2.16-8.33-2.16-12.07,0-9.45,5.46-18.9,10.91-28.36,16.37v20.9c9.45-5.46,18.9-10.91,28.36-16.37,3.73-2.16,8.33-2.16,12.07,0,3.13,1.81,11.13,6.42,18.1,10.45-8.04,4.64-16.09,9.29-24.13,13.93v20.9c8.04-4.64,16.09-9.29,24.13-13.93h0l18.1,10.45c-12.07,6.97-24.13,13.93-36.2,20.9-3.73,2.16-8.33,2.16-12.07,0-10.06-5.81-20.11-11.61-30.17-17.42V23.23c-5.03,2.9-10.06,5.81-15.08,8.71-1.87,1.08-3.02,3.07-3.02,5.22v55.73c0,2.16,1.15,4.15,3.02,5.22,15.08,8.71,30.17,17.42,45.25,26.13,3.73,2.16,8.33,2.16,12.07,0,15.08-8.71,30.17-17.42,45.25-26.13,1.87-1.08,3.02-3.07,3.02-5.22v-20.9h0s0,0,0,0Z"style="fill: #fff9; stroke-width: 0px; filter: url(#X_Shadow_3)"/><g style="clip-path: url(#clippath-2)"><path d="M126.3,89.42s0-15.26,0-17.42-1.15-4.15-3.02-5.23c-5.03-2.9-10.06-5.81-15.08-8.71l-12.07-6.97v20.9l30.17,17.42Z"style="fill: #fffe; stroke-width: 0px"/></g><g style="clip-path: url(#clippath)"><path d="M78.03,40.65c-3.73-2.16-8.33-2.16-12.07,0-9.45,5.46-18.9,10.91-28.36,16.37v-20.9c9.45-5.46,18.9-10.91,28.36-16.37,3.73-2.16,8.33-2.16,12.07,0,9.05,5.23,18.1,10.45,27.15,15.68,1.87,1.08,3.02,3.07,3.02,5.23s0,17.42,0,17.42c0,0-24.13-13.93-30.17-17.42Z"style="fill: #fffe; stroke-width: 0px"/></g><g style="clip-path: url(#clippath-1)"><path d="M105.18,66.77c-11.06,6.39-22.12,12.77-33.18,19.16v-20.9c11.06-6.39,22.12-12.77,33.18-19.16,1.87-1.08,3.02-3.07,3.02-5.23v20.9c0,2.16-1.15,4.15-3.02,5.23Z"style="fill: #fffe; stroke-width: 0px"/></g><g style="clip-path: url(#clippath-3)"><path d="M35.8,85.93V23.23c-5.03,2.9-10.06,5.81-15.08,8.71-1.87,1.08-3.02,3.07-3.02,5.22v55.73c0,2.16,1.15,4.15,3.02,5.22,5.03,2.9,10.06,5.81,15.08,8.71v-20.9Z"style="fill: #fffe; stroke-width: 0px"/></g><g style="clip-path: url(#clippath-4)"><path d="M78.03,124.25c15.08-8.71,30.17-17.42,45.25-26.13,1.87-1.08,3.02-3.07,3.02-5.23v-20.9c0,2.16-1.15,4.15-3.02,5.23-15.08,8.71-30.17,17.42-45.25,26.13-3.73,2.16-8.33,2.16-12.07,0-10.06-5.81-48.27-27.87-48.27-27.87,0,0,0-1.16,0,17.42,0,2.16,1.15,4.15,3.02,5.23,15.08,8.71,30.17,17.42,45.25,26.13,3.73,2.16,8.33,2.16,12.07,0Z"style="fill: #fffe; stroke-width: 0px"/></g></svg><span class="text-style">Loading...</span></div><!--<div class="loader"></div>--><script></script></body></html>
'''

class UIApp(toga.App):
    
    def init_env(self):
        '''配置环境'''
        app_root = self.paths.app.parent.parent #需要注意，根据代码结构调整
        envfile = app_root.joinpath("resources", ".env")
        load_dotenv(envfile)
        self.paths.data.mkdir(parents=True, exist_ok=True)
        os.environ['DATA_PATH'] = str(self.paths.data)
        self.paths.logs.mkdir(parents=True, exist_ok=True)
        os.environ['LOG_PATH'] = str(self.paths.logs)
        os.environ['GUI_PATH'] = str(app_root.joinpath("resources", "dist"))

        self.HOST = "127.0.0.1"
        self.PORT = int(os.getenv("PORT", 9090))
        self.CHECK_INTERVAL = 0.5    # 检查间隔(秒)
        self.MAX_ATTEMPTS = 60       # 最大尝试次数 (30秒超时)
        self.WEBVIEW_URL = f"http://{self.HOST}:{self.PORT}"
        self.HEALTH_CHECK_PATH = "/iot/health"

        os.environ['APP_ENV'] = "OK"

    def startup(self):
        """初始化主窗口和加载页面"""
        # 设置环境变量
        self.init_env()
        
        # 创建加载页面
        # loading_html = "<h1>Loading...</h1>"  # 假设已有loading_html定义
        encoded_html = urllib.parse.quote(loading_html) if toga.platform.current_platform == "android" else loading_html
        
        loading_view = toga.WebView()
        
        if toga.platform.current_platform == "android":
            loading_view._impl.settings.setSupportZoom(False)
            loading_view._impl.settings.setBuiltInZoomControls(False)
            loading_view._impl.native.clearCache(True)
            

        loading_view.set_content(
            "http://loading",
            encoded_html,
        )

        # 设置窗口内容
        self.main_window = toga.Window()
        # self.main_window.title = "Application Loader"
        self.main_window.size = (1024, 768)
        self.main_window.content = loading_view
        self.main_window.show()

    async def check_server_health(self):
        """带超时的健康检查"""
        for attempt in range(1, self.MAX_ATTEMPTS+1):
            try:
                # 使用上下文管理器管理连接
                reader, writer = await asyncio.open_connection(
                    self.HOST, 
                    self.PORT
                )
                
                try:
                    # 构造标准HTTP请求
                    request = (
                        f"GET {self.HEALTH_CHECK_PATH} HTTP/1.1\r\n"
                        f"Host: {self.HOST}\r\n"
                        "\r\n"
                    ).encode()
                    
                    writer.write(request)
                    await writer.drain()

                    # 读取响应
                    response = await reader.readuntil(b"\r\n\r\n")
                    headers = response.decode().split('\r\n')
                    
                    # 解析状态码
                    status_line = headers[0]
                    status_code = int(status_line.split()[1])
                    
                    if status_code == 200:
                        return True
                finally:
                    writer.close()
                    await writer.wait_closed()

            except (ConnectionError, TimeoutError, asyncio.IncompleteReadError) as e:
                print(f"Attempt {attempt} failed: {str(e)}")
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                raise

            await asyncio.sleep(self.CHECK_INTERVAL)
        return False

    async def on_running(self, **kwargs):
        """当应用运行时检测服务"""
        if await self.check_server_health():
            # 创建主WebView并切换
            app_view = toga.WebView(url=self.WEBVIEW_URL)
            if toga.platform.current_platform == "android":
                app_view._impl.settings.setSupportZoom(False)
                app_view._impl.settings.setBuiltInZoomControls(False)
                # app_view._impl.settings.setCacheMode(2)
                  
            self.main_window.content = app_view
        else:
            # 处理服务启动失败
            error_box = toga.Box(
                children=[
                    toga.Label("服务启动失败，请重试"),
                    toga.Button("退出", on_press=lambda _: self.exit())
                ]
            )
            self.main_window.content = error_box



def foreground_ui_app():
    app = UIApp('xplay', 'com.adveco.xplay')
    app.main_loop()