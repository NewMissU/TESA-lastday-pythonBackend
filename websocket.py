import asyncio
import websockets
import paho.mqtt.client as mqtt

CONNECTIONS = set()

# Callback function สำหรับ MQTT เมื่อได้รับข้อความ
def on_mqtt_message(client, userdata, msg):
    message = msg.payload.decode()  # แปลง payload จาก byte เป็น string
    print(f"Received message from MQTT: {message}")
    # ส่งข้อความไปยังทุก WebSocket client ที่เชื่อมต่ออยู่
    for websocket in CONNECTIONS:
        asyncio.run_coroutine_threadsafe(websocket.send(message), asyncio.get_running_loop())

async def message_handle(websocket):
    async for message in websocket:  # รับข้อความจาก WebSocket client (ถ้ามี)
        for connection in CONNECTIONS:
            if connection is not websocket:
                await connection.send(message)  # ส่งต่อข้อความไปยัง WebSocket clients อื่น ๆ

async def handle(websocket):
    CONNECTIONS.add(websocket)
    try:
        await message_handle(websocket)
        await websocket.wait_closed()  # รอจนกว่าจะปิดการเชื่อมต่อ
    finally:
        CONNECTIONS.remove(websocket)

async def main():
    # เริ่มต้น WebSocket server
    async with websockets.serve(handle, "localhost", 5678):
        # รัน MQTT client ใน background
        mqtt_client = mqtt.Client()
        mqtt_client.on_message = on_mqtt_message
        mqtt_client.connect("localhost", 1884)  # กำหนด broker และพอร์ตที่ต้องการเชื่อมต่อ
        mqtt_client.subscribe("rasppi/a")  # กำหนด topic ที่ต้องการรับข้อความ
        mqtt_client.loop_start()  # รัน MQTT client loop
        
        await asyncio.Future()  # run forever เพื่อให้ฟังก์ชันไม่จบการทำงาน

if __name__ == "__main__":
    asyncio.run(main())
