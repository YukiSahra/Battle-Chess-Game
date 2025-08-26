#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Battle Chess Server - Multi Client Server
Nhóm 13
"""

import socket
import threading
import json
import time
import random
from typing import List, Dict, Any

class Champion:
    def __init__(self, name: str, hp: int, dmg: int, range_val: int = 1):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.dmg = dmg
        self.range = range_val
        self.alive = True
    
    def take_damage(self, damage: int):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
    
    def attack(self, target: 'Champion') -> str:
        if not self.alive:
            return f"{self.name} đã chết, không thể tấn công"
        
        if not target.alive:
            return f"Mục tiêu {target.name} đã chết"
        
        target.take_damage(self.dmg)
        result = f"{self.name} tấn công {target.name} gây {self.dmg} sát thương"
        
        if not target.alive:
            result += f" - {target.name} đã bị tiêu diệt!"
        else:
            result += f" - {target.name} còn {target.hp}/{target.max_hp} HP"
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'dmg': self.dmg,
            'range': self.range,
            'alive': self.alive
        }

class BattleEngine:
    
    @staticmethod
    def simulate_battle(team1: List[Champion], team2: List[Champion]) -> Dict[str, Any]:
        battle_log = []
        round_num = 1
        
        # Reset trạng thái tất cả tướng
        for champion in team1 + team2:
            champion.hp = champion.max_hp
            champion.alive = True
        
        battle_log.append("=== TRẬN ĐẤU BẮT ĐẦU ===")
        battle_log.append(f"Team 1: {', '.join([c.name for c in team1])}")
        battle_log.append(f"Team 2: {', '.join([c.name for c in team2])}")
        battle_log.append("")
        
        while True:
            # Kiểm tra điều kiện kết thúc
            team1_alive = [c for c in team1 if c.alive]
            team2_alive = [c for c in team2 if c.alive]
            
            if not team1_alive:
                battle_log.append("🏆 Team 2 THẮNG!")
                return {
                    'winner': 2,
                    'log': battle_log,
                    'team1_final': [c.to_dict() for c in team1],
                    'team2_final': [c.to_dict() for c in team2]
                }
            
            if not team2_alive:
                battle_log.append("🏆 Team 1 THẮNG!")
                return {
                    'winner': 1,
                    'log': battle_log,
                    'team1_final': [c.to_dict() for c in team1],
                    'team2_final': [c.to_dict() for c in team2]
                }
            
            battle_log.append(f"--- ROUND {round_num} ---")
            
            battle_log.append("Team 1 tấn công:")
            for attacker in team1_alive:
                if team2_alive:
                    target = team2_alive[0]
                    result = attacker.attack(target)
                    battle_log.append(f"  {result}")
                    
                    team2_alive = [c for c in team2 if c.alive]
            
            if not team2_alive:
                continue
            
            battle_log.append("Team 2 phản công:")
            for attacker in team2_alive:
                if team1_alive:
                    target = team1_alive[0]
                    result = attacker.attack(target)
                    battle_log.append(f"  {result}")
                    
                    team1_alive = [c for c in team1 if c.alive]
            
            battle_log.append("")
            round_num += 1
            
            if round_num > 50:
                battle_log.append("Trận đấu kéo dài quá lâu - HÒA!")
                return {
                    'winner': 0,
                    'log': battle_log,
                    'team1_final': [c.to_dict() for c in team1],
                    'team2_final': [c.to_dict() for c in team2]
                }

class GameServer:
    
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.clients = {}  # {client_id: {'socket': socket, 'team': []}}
        self.waiting_clients = []
        self.client_counter = 0
        
        self.available_champions = [
            {'name': 'Warrior', 'hp': 12, 'dmg': 4, 'range': 1},
            {'name': 'Mage', 'hp': 6, 'dmg': 5, 'range': 2},
            {'name': 'Archer', 'hp': 8, 'dmg': 4, 'range': 3},
            {'name': 'Tank', 'hp': 20, 'dmg': 2, 'range': 1},
            {'name': 'Assassin', 'hp': 6, 'dmg': 7, 'range': 1},
            {'name': 'Healer', 'hp': 9, 'dmg': 1, 'range': 2},
            {'name': 'Knight', 'hp': 15, 'dmg': 3, 'range': 1},
            {'name': 'Wizard', 'hp': 7, 'dmg': 6, 'range': 2}
        ]
    
    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(10)
            print(f"🎮 Battle Chess Server đang chạy tại {self.host}:{self.port}")
            print("Đang chờ client kết nối...")
            
            while True:
                client_socket, addr = server_socket.accept()
                self.client_counter += 1
                client_id = f"client_{self.client_counter}"
                
                print(f"✅ Client {client_id} kết nối từ {addr}")
                
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_id)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except Exception as e:
            print(f"❌ Lỗi server: {e}")
        finally:
            server_socket.close()
    
    def handle_client(self, client_socket: socket.socket, client_id: str):
        try:
            self.clients[client_id] = {'socket': client_socket, 'team': []}
            
            welcome_msg = {
                'type': 'welcome',
                'message': f'Chào mừng {client_id}!',
                'champions': self.available_champions
            }
            self.send_message(client_socket, welcome_msg)
            
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode('utf-8'))
                    self.process_message(client_id, message)
                except json.JSONDecodeError:
                    self.send_message(client_socket, {
                        'type': 'error',
                        'message': 'Định dạng JSON không hợp lệ'
                    })
                
        except Exception as e:
            print(f"❌ Lỗi khi xử lý client {client_id}: {e}")
        finally:
            self.disconnect_client(client_id)
    
    def process_message(self, client_id: str, message: Dict[str, Any]):
        msg_type = message.get('type')
        
        if msg_type == 'select_team':
            self.handle_team_selection(client_id, message.get('team', []))
        elif msg_type == 'ready_to_battle':
            self.handle_ready_to_battle(client_id)
        else:
            self.send_message(self.clients[client_id]['socket'], {
                'type': 'error',
                'message': f'Loại tin nhắn không hợp lệ: {msg_type}'
            })
    
    def handle_team_selection(self, client_id: str, selected_team: List[str]):
        if len(selected_team) != 4:
            self.send_message(self.clients[client_id]['socket'], {
                'type': 'error',
                'message': 'Bạn phải chọn đúng 4 tướng!'
            })
            return
        
        team = []
        champion_names = [c['name'] for c in self.available_champions]
        
        for champion_name in selected_team:
            if champion_name not in champion_names:
                self.send_message(self.clients[client_id]['socket'], {
                    'type': 'error',
                    'message': f'Tướng {champion_name} không tồn tại!'
                })
                return
            
            champion_info = next(c for c in self.available_champions if c['name'] == champion_name)
            champion = Champion(
                champion_info['name'],
                champion_info['hp'],
                champion_info['dmg'],
                champion_info['range']
            )
            team.append(champion)
        
        self.clients[client_id]['team'] = team
        
        self.send_message(self.clients[client_id]['socket'], {
            'type': 'team_confirmed',
            'message': f'Đã chọn đội hình: {", ".join(selected_team)}',
            'team': [c.to_dict() for c in team]
        })
    
    def handle_ready_to_battle(self, client_id: str):
        """Xử lý khi client sẵn sàng chiến đấu"""
        if not self.clients[client_id]['team']:
            self.send_message(self.clients[client_id]['socket'], {
                'type': 'error',
                'message': 'Bạn chưa chọn đội hình!'
            })
            return
        
        if client_id not in self.waiting_clients:
            self.waiting_clients.append(client_id)
        
        self.send_message(self.clients[client_id]['socket'], {
            'type': 'waiting',
            'message': f'Đang chờ đối thủ... ({len(self.waiting_clients)}/2)'
        })
        
        if len(self.waiting_clients) >= 2:
            self.start_battle()
    
    def start_battle(self):
        """Bắt đầu trận đấu giữa 2 client"""
        client1_id = self.waiting_clients.pop(0)
        client2_id = self.waiting_clients.pop(0)
        
        client1 = self.clients[client1_id]
        client2 = self.clients[client2_id]
        
        print(f"⚔️ Bắt đầu trận đấu: {client1_id} vs {client2_id}")
        
        for client_id, opponent_id in [(client1_id, client2_id), (client2_id, client1_id)]:
            self.send_message(self.clients[client_id]['socket'], {
                'type': 'battle_start',
                'message': f'Trận đấu bắt đầu! Đối thủ: {opponent_id}',
                'your_team': [c.to_dict() for c in self.clients[client_id]['team']],
                'enemy_team': [c.to_dict() for c in self.clients[opponent_id]['team']]
            })
        
        battle_result = BattleEngine.simulate_battle(client1['team'], client2['team'])
        
        self.send_battle_result(client1_id, client2_id, battle_result)
    
    def send_battle_result(self, client1_id: str, client2_id: str, result: Dict[str, Any]):
        winner = result['winner']
        
        client1_result = {
            'type': 'battle_result',
            'winner': winner,
            'your_result': 'win' if winner == 1 else 'lose' if winner == 2 else 'draw',
            'battle_log': result['log'],
            'your_team_final': result['team1_final'],
            'enemy_team_final': result['team2_final']
        }
        self.send_message(self.clients[client1_id]['socket'], client1_result)
        
        client2_result = {
            'type': 'battle_result',
            'winner': winner,
            'your_result': 'win' if winner == 2 else 'lose' if winner == 1 else 'draw',
            'battle_log': result['log'],
            'your_team_final': result['team2_final'],
            'enemy_team_final': result['team1_final']
        }
        self.send_message(self.clients[client2_id]['socket'], client2_result)
        
        print(f"✅ Trận đấu kết thúc: {client1_id} vs {client2_id} - Winner: Team {winner}")
    
    def send_message(self, client_socket, message):
        try:
            client_socket.sendall((json.dumps(message) + "\n").encode())
        except:
            print("Lỗi khi gửi tin nhắn")
    
    def disconnect_client(self, client_id: str):
        if client_id in self.clients:
            try:
                self.clients[client_id]['socket'].close()
            except:
                pass
            del self.clients[client_id]
        
        if client_id in self.waiting_clients:
            self.waiting_clients.remove(client_id)
        
        print(f"❌ Client {client_id} đã ngắt kết nối")

if __name__ == "__main__":
    server = GameServer()
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Server đã dừng")
