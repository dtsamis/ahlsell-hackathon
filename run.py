import argparse
import sys
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="FloorCAD YOLOv8n FastAPI & Web Visualizer")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port number (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable automatic reload on code changes")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  [FloorCAD YOLOv8n] CAD Floor Plan Detection Service")
    print("=" * 60)
    print(f"  * Web UI:      http://{args.host}:{args.port}/")
    print(f"  * API Docs:    http://{args.host}:{args.port}/docs")
    print(f"  * Healthcheck: http://{args.host}:{args.port}/api/health")
    print("=" * 60 + "\n")

    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)

if __name__ == "__main__":
    main()
