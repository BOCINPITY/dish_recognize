import asyncio
import websockets
import torch
import cv2
import time
from database.Dishes import Dishes
import json

class DishDetector:
    def __init__(self):
        # 推理参数
        self.confidence_threshold = 0.85
        self.iou_threshold = 0.45
        # 加载模型
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path='./model/best0107.pt')
        self.model.conf = self.confidence_threshold
        self.model.iou = self.iou_threshold
        self.cap = cv2.VideoCapture(2) #机器摄像头设备
        self.prev_result = None
        self.start_time = None
        self.dishes = Dishes()

    def parse_detection_results(self, detection_df):
        count_dict = {}
        for _, row in detection_df.iterrows():
            class_id = row["class"]
            if class_id in count_dict:
                count_dict[class_id] += 1
            else:
                count_dict[class_id] = 1

        result = []
        for class_id, number in count_dict.items():
            result.append({"id": class_id, "number": number})
        return result

    # 结果校验
    def detect_valid(self, valid_data):
        current_time = time.time()
        if self.prev_result is None:
            self.start_time = current_time
            self.prev_result = valid_data

        if current_time - self.start_time >= 1:
            if self.prev_result == valid_data:
                self.start_time = current_time
                return valid_data
            else:
                self.start_time = current_time
                self.prev_result = valid_data

        return None

    async def detection_loop(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("无法获取摄像头画面，可能摄像头已断开连接。")
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.model(frame_rgb)
            detections = results.pandas().xyxy[0]
            parse_res = self.parse_detection_results(detections)
            valid_result = self.detect_valid(parse_res)
            if valid_result:
                result_set = []
                for dish in valid_result:
                    dish_id = dish["id"]
                    dish_number = dish["number"]
                    dish_info = self.dishes.get_dish_by_id(dish_id)
                    if dish_info:
                        dish_info["price"] = float(dish_info["price"])
                        temp_dict = {
                            "dish_info": dish_info,
                            "number": dish_number
                        }
                        result_set.append(temp_dict)
                yield result_set
            await asyncio.sleep(0.01)

    async def handle_receive(self, websocket):
        try:
            peer_info = websocket.remote_address
            print(f"客户端 {peer_info} 已连接")
            try:
                while True:
                    client_message = await websocket.recv()
                    print(f"Received from client {peer_info}: {client_message}")
            except websockets.exceptions.ConnectionClosed:
                print(f"客户端 {peer_info} 已断开连接")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error receiving client message: {e}")
        finally:
            await websocket.close()

    async def send_data(self, websocket, path):
        receive_task = asyncio.create_task(self.handle_receive(websocket))
        try:
            async for result_set in self.detection_loop():
                data_to_send = json.dumps(result_set)
                print(data_to_send)
                await websocket.send(data_to_send)
        except Exception as e:
            print(f"WebSocket 数据发送异常: {e}")
        finally:
            receive_task.cancel()
            await websocket.close()

    def run(self):
        try:
            start_server = websockets.serve(self.send_data, "localhost", 8765)
            asyncio.get_event_loop().run_until_complete(start_server)
            asyncio.get_event_loop().run_forever()
        except Exception as e:
            print(f"程序运行出现异常: {e}")
        finally:
            cv2.destroyAllWindows()
            self.cap.release()
            self.dishes.close()


if __name__ == "__main__":
    detector = DishDetector()
    detector.run()