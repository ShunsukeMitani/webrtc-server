import asyncio
import websockets
import os
import json

connected_clients = set()

async def signaling_handler(websocket):
    # 新しい端末が接続してきたらリストに追加
    connected_clients.add(websocket)
    print(f"✅ クライアント接続 (現在: {len(connected_clients)}台)")
    try:
        async for message in websocket:
            # 届いたメッセージ(Offer/Answer/ICE)を、自分以外の全員に転送
            for client in connected_clients:
                if client != websocket:
                    try:
                        await client.send(message)
                    except websockets.exceptions.ConnectionClosed:
                        pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # 切断されたらリストから削除
        connected_clients.remove(websocket)
        print(f"❌ クライアント切断 (現在: {len(connected_clients)}台)")

async def main():
    # クラウド(Render)が自動で割り当てるポート番号を取得、なければ8080
    port = int(os.environ.get("PORT", 8080))
    # 0.0.0.0 で起動し、世界中からのアクセスを許可する
    async with websockets.serve(signaling_handler, "0.0.0.0", port):
        print(f"🚀 シグナリングサーバーがポート {port} で起動しました！")
        await asyncio.Future()  # サーバーを永遠に起動し続ける

if __name__ == "__main__":
    asyncio.run(main())
