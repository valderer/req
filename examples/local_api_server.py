import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class ApiHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/posts/1":
            body = {
                "userId": 1,
                "id": 1,
                "title": "我的第一篇文章",
                "body": "这是本地 HTTP 服务返回的真实 JSON 响应",
            }
            self.send_json(200, body)
            return

        self.send_json(404, {"message": "资源不存在"})

    def send_json(self, status_code, body):
        content = json.dumps(body, ensure_ascii=False).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        print(f"服务器日志：{self.address_string()} - {format % args}")


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8000), ApiHandler)
    print("本地 HTTP 服务已启动：http://127.0.0.1:8000")
    print("按 Control + C 停止服务")
    server.serve_forever()
