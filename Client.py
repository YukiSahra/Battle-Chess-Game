#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Battle Chess Client - Game Client
Nhóm 13
"""

import socket
import json
import threading
import time
from typing import List, Dict, Any

class GameClient:
    
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.available_champions = []
        self.selected_team = []
        self.in_battle = False
    
    def connect_to_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            
            print(f"✅ Đã kết nối đến server {self.host}:{self.port}")
            
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Không thể kết nối đến server: {e}")
            return False
    
    def receive_messages(self):
        while self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                message = json.loads(data.decode('utf-8'))
                self.handle_server_message(message)
                
            except Exception as e:
                if self.connected:
                    print(f"❌ Lỗi khi nhận tin nhắn: {e}")
                    print(f"❌ Lỗi khi nhận tin nhắn: {data}")
                break
        
        self.connected = False
        print("🔌 Kết nối đã bị ngắt")
    
    def handle_server_message(self, message: Dict[str, Any]):
        """Xử lý tin nhắn từ server"""
        msg_type = message.get('type')
        
        if msg_type == 'welcome':
            self.handle_welcome(message)
        elif msg_type == 'team_confirmed':
            self.handle_team_confirmed(message)
        elif msg_type == 'waiting':
            self.handle_waiting(message)
        elif msg_type == 'battle_start':
            self.handle_battle_start(message)
        elif msg_type == 'battle_result':
            self.handle_battle_result(message)
        elif msg_type == 'error':
            self.handle_error(message)
        else:
            print(f"📩 Tin nhắn từ server: {message}")
    
    def handle_welcome(self, message: Dict[str, Any]):
        print(f"🎉 {message['message']}")
        self.available_champions = message['champions']
    def handle_team_confirmed(self, message: Dict[str, Any]):
        print(f"✅ {message['message']}")
        self.show_team_info(message['team'])
        
    def handle_waiting(self, message: Dict[str, Any]):
        print(f"⏳ {message['message']}")
    
    def handle_battle_start(self, message: Dict[str, Any]):
        self.in_battle = True
        print(f"\n⚔️ {message['message']}")
        print("\n=== ĐỘI HÌNH CỦA BẠN ===")
        self.show_team_info(message['your_team'])
        print("\n=== ĐỘI HÌNH ĐỐI THỦ ===")
        self.show_team_info(message['enemy_team'])
        print("\n🎬 Trận đấu đang diễn ra...")
    
    def handle_battle_result(self, message: Dict[str, Any]):
        self.in_battle = False
        result = message['your_result']
        
        print("\n" + "="*50)
        print("🏆 KẾT QUẢ TRẬN ĐẤU 🏆")
        print("="*50)
        
        if result == 'win':
            print("🎉 BẠN THẮNG! 🎉")
        elif result == 'lose':
            print("😭 BẠN THUA! 😭")
        else:
            print("🤝 HÒA! 🤝")
        
        print("\n📜 LOG TRẬN ĐẤU:")
        for log_line in message['battle_log']:
            print(log_line)
        
        print("\n=== TRẠNG THÁI CUỐI TRẬN ===")
        print("Đội của bạn:")
        self.show_team_info(message['your_team_final'])
        print("\nĐội đối thủ:")
        self.show_team_info(message['enemy_team_final'])
        
        print("\n" + "="*50)
        self.show_main_menu()
    
    def handle_error(self, message: Dict[str, Any]):
        print(f"❌ Lỗi: {message['message']}")
    
    def show_main_menu(self):
        print("\n1. Xem danh sách tướng")
        print("2. Chọn đội hình (4 tướng)")
        print("3. Sẵn sàng chiến đấu")
        print("4. Thoát")
    
    def show_champions_list(self):
        print("\n📋 DANH SÁCH TƯỚNG CÓ SẴN:")
        print("-" * 60)
        print(f"{'STT':<3} {'Tên':<12} {'HP':<4} {'DMG':<4} {'Range':<6} {'Mô tả'}")
        print("-" * 60)
        
        for i, champion in enumerate(self.available_champions, 1):
            description = self.get_champion_description(champion)
            print(f"{i:<3} {champion['name']:<12} {champion['hp']:<4} {champion['dmg']:<4} {champion['range']:<6} {description}")
        print("-" * 60)
    
    def get_champion_description(self, champion: Dict[str, Any]) -> str:
        descriptions = {
            'Warrior': 'Front line, High DMG',
            'Mage': 'Back line, High magic DMG, Low HP',
            'Archer': 'Back line, High DMG, Low HP',
            'Tank': 'Front line, Low DMG. High HP',
            'Assassin': 'Front line, High DMG, Low HP',
            'Healer': 'Back line, Low DMG, Low HP',
            'Knight': 'Front line, Balance',
            'Wizard': 'Back line, Magic DMG, Low HP'
        }
        return descriptions.get(champion['name'], 'Tướng đặc biệt')
    
    def select_team(self):
        print("\n🎯 CHỌN ĐỘI HÌNH (4 tướng)")
        print("Nhập số thứ tự của 4 tướng (cách nhau bởi dấu cách)")
        print("Ví dụ: 1 3 5 7")
        
        self.show_champions_list()
        
        while True:
            try:
                input_str = input("\nNhập đội hình: ").strip()
                if not input_str:
                    print("❌ Vui lòng nhập lựa chọn!")
                    continue
            
                indices = [int(x) - 1 for x in input_str.split()]
            
                if len(indices) != 4:
                    print("❌ Bạn phải chọn đúng 4 tướng!")
                    continue
            
                if any(i < 0 or i >= len(self.available_champions) for i in indices):
                    print("❌ Số thứ tự không hợp lệ!")
                    continue
            
                selected_names = [self.available_champions[i]['name'] for i in indices]
                self.selected_team = selected_names
            
                print(f"✅ Đã chọn: {', '.join(selected_names)}")
            
                message = {
                    'type': 'select_team',
                    'team': selected_names
                }
                self.send_message(message)
            
            except ValueError:
                print("❌ Vui lòng nhập số hợp lệ!")
            except Exception as e:
                print(f"❌ Lỗi: {e}")
            time.sleep(3)
            break
    def ready_to_battle(self):
        if not self.selected_team:
            print("❌ Bạn chưa chọn đội hình!")
            return
        
        message = {
            'type': 'ready_to_battle'
        }
        self.send_message(message)
        print("⏳ Đang tìm đối thủ...")
    
    def show_team_info(self, team: List[Dict[str, Any]]):
        """Hiển thị thông tin đội hình"""
        print("-" * 50)
        for i, champion in enumerate(team, 1):
            status = "💀" if not champion['alive'] else "❤️"
            print(f"{i}. {champion['name']:<12} - HP: {champion['hp']:>2}/{champion['max_hp']:<2} | DMG: {champion['dmg']:>2} | Range: {champion['range']} {status}")
        print("-" * 50)
    
    def send_message(self, message: Dict[str, Any]):
        """Gửi tin nhắn đến server"""
        try:
            data = json.dumps(message, ensure_ascii=False)
            self.socket.send(data.encode('utf-8'))
        except Exception as e:
            print(f"❌ Lỗi khi gửi tin nhắn: {e}")
    
    def disconnect(self):
        """Ngắt kết nối"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("👋 Đã ngắt kết nối")
    
    def run(self):
        """Chạy client"""
        if not self.connect_to_server():
            return
        
        try:
            while self.connected:

                if self.in_battle:
                    time.sleep(1)
                    continue

                try:
                    time.sleep(1)
                    self.show_main_menu()
                    choice = input("\nNhập lựa chọn (1-4): ").strip()
                    
                    if choice == '1':
                        self.show_champions_list()
                    elif choice == '2':
                        self.select_team()
                    elif choice == '3':
                        self.ready_to_battle()
                    elif choice == '4':
                        print("👋 Tạm biệt!")
                        break
                    else:
                        print("❌ Lựa chọn không hợp lệ!")
                
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"❌ Lỗi: {e}")
        
        finally:
            self.disconnect()

def main():
    print("🎮 Battle Chess Client")
    print("Nhập địa chỉ server (Enter để dùng localhost:8888):")
    
    try:
        server_input = input("Server (host:port): ").strip()
        
        if server_input:
            if ':' in server_input:
                host, port = server_input.split(':', 1)
                port = int(port)
            else:
                host = server_input
                port = 8888
        else:
            host = 'localhost'
            port = 8888
        
        client = GameClient(host, port)
        client.run()
        
    except ValueError:
        print("❌ Port không hợp lệ!")
    except KeyboardInterrupt:
        print("\n👋 Tạm biệt!")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()
