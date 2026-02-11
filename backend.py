"""
FLASK BACKEND SERVER - Handles web requests and MongoDB operations
"""
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, render_template_string
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import psutil
import platform
import socket
import pyautogui
import cv2
import mss
import time
import threading
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import imageio
import sqlite3
from bson import ObjectId
import secrets
from functools import wraps

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# ⚠️ Load from .env file ⚠️
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'YourSecurePassword123')
SUPER_ADMIN_PASSWORD = os.getenv('SUPER_ADMIN_PASSWORD', 'SuperAdmin@2026')

# Secret key for sessions
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))

# MongoDB Connection from .env
MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = "child_monitoring"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
parents_col = db["parents"]  # Store parent accounts
devices_col = db["devices"]  # Store connected devices
commands_col = db["commands"]  # Store commands to execute
results_col = db["results"]  # Store command results
keystrokes_col = db["keystrokes"]  # Store keystroke logs
screenshots_col = db["screenshots"]  # Store screenshots

# Global variables
keylogger_running = False
captured_text = ""

# ==================== LOGIN SYSTEM ====================

def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip login for login endpoints and API calls from authenticated clients
        if 'user_id' not in session and request.method == 'GET':
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def check_logged_in():
    """Check if user is logged in for protected routes"""
    # Public routes that don't require authentication
    public_routes = ['/login', '/logout', '/static']
    
    # Client-facing API endpoints that don't require web session authentication
    client_endpoints = ['/api/register-device', '/api/commands/pending', '/api/command/executed']
    
    # Allow public routes
    for route in public_routes:
        if request.path.startswith(route):
            return None
    
    # Allow client endpoints without authentication
    for endpoint in client_endpoints:
        if request.path.startswith(endpoint):
            return None
    
    # All other routes require authentication
    if 'user_id' not in session:
        if request.path.startswith('/api/'):
            return jsonify({"error": "Not authenticated"}), 401
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for both admin and parents"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Check if Super Admin
        if username == 'admin' and password == SUPER_ADMIN_PASSWORD:
            session['user_id'] = 'admin'
            session['user_type'] = 'admin'
            session['login_time'] = datetime.now().isoformat()
            return redirect('/admin')
        
        # Check if Parent (legacy: direct password match)
        if not username and password == ADMIN_PASSWORD:
            session['user_id'] = 'parent_default'
            session['user_type'] = 'parent'
            session['login_time'] = datetime.now().isoformat()
            return redirect('/')
        
        # Check if Parent (username/password)
        if username:
            parent = parents_col.find_one({"username": username})
            if parent and parent.get('password') == password:
                session['user_id'] = str(parent['_id'])
                session['user_type'] = 'parent'
                session['username'] = username
                session['parent_name'] = parent.get('name', username)
                session['login_time'] = datetime.now().isoformat()
                return redirect('/')
        
        return render_template_string(LOGIN_HTML, error="❌ Wrong credentials! Try again.")
    
    return render_template_string(LOGIN_HTML, error="")

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect('/login')

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """Get current user profile information"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    user_info = {
        "user_id": session.get('user_id'),
        "user_type": session.get('user_type'),
        "username": session.get('username', 'admin' if session.get('user_type') == 'admin' else 'parent'),
        "name": session.get('parent_name', 'Administrator' if session.get('user_type') == 'admin' else 'Parent'),
        "login_time": session.get('login_time', '')
    }
    
    print(f"[{datetime.now().isoformat()}] 👤 Profile retrieved for user: {user_info['username']}")
    return jsonify(user_info)

# ==================== ADMIN PANEL ====================

@app.route('/admin')
def admin_panel():
    """Admin panel - manage parents and view all devices"""
    if session.get('user_type') != 'admin':
        return redirect('/login')
    
    # Get all parents
    parents = list(parents_col.find())
    for parent in parents:
        parent['_id'] = str(parent['_id'])
        # Count devices for each parent
        parent['device_count'] = devices_col.count_documents({"parent_id": parent['_id']})
    
    # Get all devices
    all_devices = list(devices_col.find())
    for device in all_devices:
        device['_id'] = str(device['_id'])
        # Get parent name if assigned
        if device.get('parent_id'):
            parent = parents_col.find_one({"_id": ObjectId(device['parent_id'])})
            device['parent_name'] = parent.get('name', 'Unknown') if parent else 'Unassigned'
        else:
            device['parent_name'] = 'Unassigned'
    
    return render_template_string(ADMIN_PANEL_HTML, parents=parents, devices=all_devices)

@app.route('/api/admin/parents', methods=['GET'])
def get_parents():
    """Get all parents (Admin only)"""
    if session.get('user_type') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    parents = list(parents_col.find())
    for parent in parents:
        parent['_id'] = str(parent['_id'])
        parent['device_count'] = devices_col.count_documents({"parent_id": parent['_id']})
    
    return jsonify(parents)

@app.route('/api/admin/parent', methods=['POST'])
def add_parent():
    """Add new parent (Admin only)"""
    if session.get('user_type') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    parent_doc = {
        "name": data.get('name', ''),
        "email": data.get('email', ''),
        "username": data.get('username', ''),
        "password": data.get('password', ''),
        "phone": data.get('phone', ''),
        "created_at": datetime.now()
    }
    
    # Check if username already exists
    if parents_col.find_one({"username": parent_doc['username']}):
        print(f"[{datetime.now().isoformat()}] ⚠️ Parent creation failed: Username '{parent_doc['username']}' already exists")
        return jsonify({"error": "Username already exists"}), 400
    
    result = parents_col.insert_one(parent_doc)
    parent_id = str(result.inserted_id)
    print(f"[{datetime.now().isoformat()}] ✓ New parent created: {parent_doc['name']} (ID: {parent_id})")
    return jsonify({"status": "success", "parent_id": parent_id})

@app.route('/api/admin/parent/<parent_id>', methods=['PUT'])
def update_parent(parent_id):
    """Update parent (Admin only)"""
    if session.get('user_type') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    update_data = {
        "name": data.get('name'),
        "email": data.get('email'),
        "phone": data.get('phone'),
    }
    
    # Only update password if provided
    if data.get('password'):
        update_data['password'] = data.get('password')
    
    parents_col.update_one(
        {"_id": ObjectId(parent_id)},
        {"$set": update_data}
    )
    
    return jsonify({"status": "success"})

@app.route('/api/admin/parent/<parent_id>', methods=['DELETE'])
def delete_parent(parent_id):
    """Delete parent (Admin only)"""
    if session.get('user_type') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    # Unassign all devices from this parent
    devices_col.update_many(
        {"parent_id": parent_id},
        {"$unset": {"parent_id": ""}}
    )
    
    # Delete parent
    parents_col.delete_one({"_id": ObjectId(parent_id)})
    
    return jsonify({"status": "success"})

@app.route('/api/admin/device/<device_id>/assign', methods=['POST'])
def assign_device_to_parent(device_id):
    """Assign device to parent (Admin only)"""
    if session.get('user_type') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    parent_id = data.get('parent_id')
    
    if parent_id:
        parent = parents_col.find_one({"_id": ObjectId(parent_id)})
        parent_name = parent.get('name', 'Unknown') if parent else 'Unknown'
        devices_col.update_one(
            {"device_id": device_id},
            {"$set": {"parent_id": parent_id, "assigned_at": datetime.now()}}
        )
        print(f"[{datetime.now().isoformat()}] ✓ Device '{device_id}' assigned to parent '{parent_name}' (ID: {parent_id})")
    else:
        devices_col.update_one(
            {"device_id": device_id},
            {"$unset": {"parent_id": ""}, "$set": {"unassigned_at": datetime.now()}}
        )
        print(f"[{datetime.now().isoformat()}] ✓ Device '{device_id}' unassigned from parent")
    
    return jsonify({"status": "success"})

# HTML for login page
LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Child Monitor - Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .login-container {
            background: white;
            padding: 50px;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 400px;
            animation: slideIn 0.5s ease;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
            font-size: 28px;
        }
        
        .subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        
        input[type="password"],
        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input[type="password"]:focus,
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .error {
            background: #fee2e2;
            color: #991b1b;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #ef4444;
            text-align: center;
        }
        
        .info {
            background: #dbeafe;
            color: #1e3a8a;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #3b82f6;
            font-size: 13px;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>👶 Child Monitor</h1>
        <p class="subtitle">Parental Control System</p>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        <div class="info">
            🔒 <strong>Admin:</strong> username=admin, Super Admin password<br>
            🔒 <strong>Parent:</strong> Enter your username and password
        </div>
        
        <form method="post">
            <div class="form-group">
                <label for="username">Username (optional for legacy access)</label>
                <input 
                    type="text" 
                    name="username" 
                    id="username" 
                    placeholder="Enter your username"
                    autofocus
                >
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input 
                    type="password" 
                    name="password" 
                    id="password" 
                    placeholder="Enter your password"
                    required
                >
            </div>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
'''

ADMIN_PANEL_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - Parent Management</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 28px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: transform 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .btn-logout {
            background: white;
            color: #667eea;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-success {
            background: #10b981;
            color: white;
        }
        
        .btn-danger {
            background: #ef4444;
            color: white;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .section {
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .section h2 {
            margin-bottom: 20px;
            color: #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        table th, table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        
        table th {
            background: #f9fafb;
            font-weight: 600;
            color: #374151;
        }
        
        table tr:hover {
            background: #f9fafb;
        }
        
        .badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .badge-success {
            background: #d1fae5;
            color: #065f46;
        }
        
        .badge-warning {
            background: #fed7aa;
            color: #92400e;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 10px;
            width: 90%;
            max-width: 500px;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #374151;
            font-weight: 500;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 10px;
            border: 2px solid #e5e7eb;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn-group {
            display: flex;
            gap: 10px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .stat-card h3 {
            color: #6b7280;
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        .stat-card .number {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>👑 Admin Panel</h1>
            <p>Manage parents and monitor all devices</p>
        </div>
        <a href="/logout" class="btn btn-logout">Logout</a>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <h3>Total Parents</h3>
                <div class="number">{{ parents|length }}</div>
            </div>
            <div class="stat-card">
                <h3>Total Devices</h3>
                <div class="number">{{ devices|length }}</div>
            </div>
            <div class="stat-card">
                <h3>Assigned Devices</h3>
                <div class="number">{{ devices|selectattr('parent_id')|list|length }}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>
                👨‍👩‍👧‍👦 Parents Management
                <button class="btn btn-primary" onclick="showAddParentModal()">+ Add Parent</button>
            </h2>
            <table id="parentsTable">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Phone</th>
                        <th>Devices</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for parent in parents %}
                    <tr>
                        <td>{{ parent.name }}</td>
                        <td>{{ parent.username }}</td>
                        <td>{{ parent.email or '-' }}</td>
                        <td>{{ parent.phone or '-' }}</td>
                        <td><span class="badge badge-success">{{ parent.device_count }} devices</span></td>
                        <td class="btn-group">
                            <button class="btn btn-primary" onclick="editParent('{{ parent._id }}')">Edit</button>
                            <button class="btn btn-danger" onclick="deleteParent('{{ parent._id }}')">Delete</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>💻 All Monitored Devices</h2>
            <table>
                <thead>
                    <tr>
                        <th>Device Name</th>
                        <th>Device ID</th>
                        <th>Status</th>
                        <th>Assigned To</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for device in devices %}
                    <tr>
                        <td>{{ device.device_name }}</td>
                        <td>{{ device.device_id }}</td>
                        <td><span class="badge badge-success">{{ device.status }}</span></td>
                        <td>
                            <select onchange="assignDevice('{{ device.device_id }}', this.value)" style="padding: 5px;">
                                <option value="">-- Unassigned --</option>
                                {% for parent in parents %}
                                <option value="{{ parent._id }}" {% if device.parent_id == parent._id %}selected{% endif %}>
                                    {{ parent.name }}
                                </option>
                                {% endfor %}
                            </select>
                        </td>
                        <td>
                            <button class="btn btn-primary" onclick="window.location.href='/?device={{ device.device_id }}'">Monitor</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- Add Parent Modal -->
    <div id="addParentModal" class="modal">
        <div class="modal-content">
            <h2>Add New Parent</h2>
            <form id="addParentForm">
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" name="name" required>
                </div>
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email">
                </div>
                <div class="form-group">
                    <label>Phone</label>
                    <input type="tel" name="phone">
                </div>
                <div class="btn-group">
                    <button type="submit" class="btn btn-success">Add Parent</button>
                    <button type="button" class="btn" onclick="closeModal()">Cancel</button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        function showAddParentModal() {
            document.getElementById('addParentModal').style.display = 'flex';
        }
        
        function closeModal() {
            document.getElementById('addParentModal').style.display = 'none';
            document.getElementById('addParentForm').reset();
        }
        
        document.getElementById('addParentForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/api/admin/parent', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    alert('✅ Parent added successfully!');
                    location.reload();
                } else {
                    const error = await response.json();
                    alert('❌ Error: ' + error.error);
                }
            } catch (error) {
                alert('❌ Error: ' + error.message);
            }
        });
        
        async function deleteParent(parentId) {
            if (!confirm('Are you sure you want to delete this parent?')) return;
            
            try {
                const response = await fetch('/api/admin/parent/' + parentId, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    alert('✅ Parent deleted successfully!');
                    location.reload();
                } else {
                    alert('❌ Failed to delete parent');
                }
            } catch (error) {
                alert('❌ Error: ' + error.message);
            }
        }
        
        async function assignDevice(deviceId, parentId) {
            try {
                const response = await fetch('/api/admin/device/' + deviceId + '/assign', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({parent_id: parentId})
                });
                
                if (response.ok) {
                    alert('✅ Device assigned successfully!');
                } else {
                    alert('❌ Failed to assign device');
                }
            } catch (error) {
                alert('❌ Error: ' + error.message);
            }
        }
    </script>
</body>
</html>
'''

# ==================== UTILITY FUNCTIONS ====================

def get_pc_info():
    """Fetch system information"""
    uname = platform.uname()
    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    ip_address = socket.gethostbyname(socket.gethostname())

    pc_info = {
        "system": f"{uname.system} {uname.release}",
        "machine": uname.machine,
        "processor": uname.processor,
        "cpu_usage": cpu_usage,
        "ram_used": ram.used // (1024 ** 2),
        "ram_total": ram.total // (1024 ** 2),
        "disk_used": disk.used // (1024 ** 3),
        "disk_total": disk.total // (1024 ** 3),
        "ip_address": ip_address
    }
    return pc_info

def verify_device_access(device_id):
    """Verify if current user has access to this device"""
    # Admin has access to all devices
    if session.get('user_type') == 'admin':
        return True
    
    # Parent users - check if device is assigned to them
    if session.get('user_type') == 'parent':
        # Legacy parent_default has access to all devices
        if session.get('user_id') == 'parent_default':
            return True
        
        # Check if device is assigned to this parent
        device = devices_col.find_one({"device_id": device_id})
        if device and device.get('parent_id') == session.get('user_id'):
            return True
    
    return False

def store_command(device_id, command, params=None):
    """Store command in MongoDB for client to fetch"""
    command_doc = {
        "device_id": device_id,
        "command": command,
        "params": params or {},
        "created_at": datetime.now(),
        "status": "pending",
        "executed": False
    }
    result = commands_col.insert_one(command_doc)
    return str(result.inserted_id)

def store_result(device_id, command_id, result_data, success=True):
    """Store command result in MongoDB"""
    result_doc = {
        "device_id": device_id,
        "command_id": command_id,
        "result": result_data,
        "success": success,
        "created_at": datetime.now()
    }
    results_col.insert_one(result_doc)

# ==================== API ENDPOINTS ====================

@app.route('/')
@login_required
def index():
    """Serve the parent monitoring dashboard"""
    print(f"[{datetime.now().isoformat()}] ✓ Dashboard loaded for user: {session.get('user_id')}")
    return render_template('index.html')

@app.route('/api/register-device', methods=['POST'])
def register_device():
    """Register a new monitoring device"""
    data = request.json
    device_doc = {
        "device_name": data.get('device_name', 'Unknown'),
        "device_id": data.get('device_id', socket.gethostname()),
        "status": "online",
        "registered_at": datetime.now(),
        "last_seen": datetime.now(),
        "pc_info": get_pc_info()
    }
    
    # Check if device already exists, update if yes
    existing = devices_col.find_one({"device_id": device_doc["device_id"]})
    if existing:
        devices_col.update_one({"device_id": device_doc["device_id"]}, {"$set": {**device_doc, "last_updated": datetime.now()}})
        print(f"[{datetime.now().isoformat()}] ✓ Device updated: {device_doc['device_name']} ({device_doc['device_id']})")
        return jsonify({"status": "updated", "device_id": device_doc["device_id"]})
    
    result = devices_col.insert_one(device_doc)
    device_id = device_doc["device_id"]
    print(f"[{datetime.now().isoformat()}] ✓ Device registered: {device_doc['device_name']} ({device_id})")
    return jsonify({"status": "registered", "device_id": str(result.inserted_id)})

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get all registered devices (filtered by parent for parent users)"""
    query = {}
    
    # If parent user, only show their assigned devices
    if session.get('user_type') == 'parent' and session.get('user_id') != 'parent_default':
        query['parent_id'] = session.get('user_id')
    
    devices = list(devices_col.find(query, {"_id": 1, "device_id": 1, "device_name": 1, "status": 1, "last_seen": 1, "registered_at": 1, "last_updated": 1}))
    for device in devices:
        device["_id"] = str(device["_id"])
        device["last_seen"] = str(device.get("last_seen", ""))
        device["registered_at"] = str(device.get("registered_at", ""))
        device["last_updated"] = str(device.get("last_updated", ""))
    
    print(f"[{datetime.now().isoformat()}] 📱 Devices list retrieved ({len(devices)} devices)")
    return jsonify(devices)

@app.route('/api/device/<device_id>', methods=['GET'])
@login_required
def get_device(device_id):
    """Get specific device info"""
    # Verify access
    if not verify_device_access(device_id):
        print(f"[{datetime.now().isoformat()}] ⚠️ Unauthorized access attempt to device: {device_id} by user: {session.get('user_id')}")
        return jsonify({"error": "Unauthorized: You don't have access to this device"}), 403
    
    device = devices_col.find_one({"device_id": device_id})
    if not device:
        return jsonify({"error": "Device not found"}), 404
    
    device["_id"] = str(device["_id"])
    device["registered_at"] = str(device.get("registered_at", ""))
    device["last_seen"] = str(device.get("last_seen", ""))
    device["last_updated"] = str(device.get("last_updated", ""))
    
    print(f"[{datetime.now().isoformat()}] 📱 Device details retrieved: {device_id}")
    return jsonify(device)

# ==================== COMMAND ENDPOINTS ====================

@app.route('/api/command/pcinfo', methods=['POST'])
def cmd_pcinfo():
    """Get PC information"""
    data = request.json
    device_id = data.get('device_id')
    
    pc_info = get_pc_info()
    command_id = store_command(device_id, "pcinfo")
    store_result(device_id, command_id, pc_info)
    
    print(f"[{datetime.now().isoformat()}] ℹ️  PC Info requested for device: {device_id}")
    return jsonify({"status": "success", "data": pc_info})
    return jsonify({"status": "success", "data": pc_info})

@app.route('/api/command/lock', methods=['POST'])
@login_required
def cmd_lock():
    """Lock PC"""
    data = request.json
    device_id = data.get('device_id')
    
    # Verify access
    if not verify_device_access(device_id):
        print(f"[{datetime.now().isoformat()}] ⚠️ Unauthorized command attempt on device: {device_id} by user: {session.get('user_id')}")
        return jsonify({"error": "Unauthorized: You don't have access to this device"}), 403
    
    command_id = store_command(device_id, "lock")
    try:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        store_result(device_id, command_id, "PC locked successfully")
        print(f"[{datetime.now().isoformat()}] 🔒 PC locked command executed for device: {device_id}")
        return jsonify({"status": "success", "message": "PC locked"})
    except Exception as e:
        store_result(device_id, command_id, str(e), success=False)
        print(f"[{datetime.now().isoformat()}] ❌ Lock command failed for device {device_id}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/command/shutdown', methods=['POST'])
def cmd_shutdown():
    """Shutdown PC"""
    data = request.json
    device_id = data.get('device_id')
    
    command_id = store_command(device_id, "shutdown")
    try:
        os.system("shutdown /s /t 10")
        store_result(device_id, command_id, "Shutdown initiated")
        print(f"[{datetime.now().isoformat()}] 🛑 PC shutdown command executed for device: {device_id}")
        return jsonify({"status": "success", "message": "Shutdown initiated"})
    except Exception as e:
        store_result(device_id, command_id, str(e), success=False)
        print(f"[{datetime.now().isoformat()}] ❌ Shutdown command failed for device {device_id}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/command/restart', methods=['POST'])
def cmd_restart():
    """Restart PC"""
    data = request.json
    device_id = data.get('device_id')
    
    command_id = store_command(device_id, "restart")
    try:
        os.system("shutdown /r /t 10")
        store_result(device_id, command_id, "Restart initiated")
        print(f"[{datetime.now().isoformat()}] 🔄 PC restart command executed for device: {device_id}")
        return jsonify({"status": "success", "message": "Restart initiated"})
    except Exception as e:
        store_result(device_id, command_id, str(e), success=False)
        print(f"[{datetime.now().isoformat()}] ❌ Restart command failed for device {device_id}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/command/logout', methods=['POST'])
def cmd_logout():
    """Logout user"""
    data = request.json
    device_id = data.get('device_id')
    
    command_id = store_command(device_id, "logout")
    try:
        os.system("shutdown -l")
        store_result(device_id, command_id, "Logout initiated")
        print(f"[{datetime.now().isoformat()}] 👤 Logout command executed for device: {device_id}")
        return jsonify({"status": "success", "message": "Logout initiated"})
    except Exception as e:
        store_result(device_id, command_id, str(e), success=False)
        print(f"[{datetime.now().isoformat()}] ❌ Logout command failed for device {device_id}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

# Generic command router
@app.route('/api/command/execute', methods=['POST'])
@login_required
def execute_command():
    """Generic command executor that creates pending commands"""
    data = request.json
    device_id = data.get('device_id')
    command = data.get('command')
    params = data.get('params', {})
    
    if not device_id or not command:
        return jsonify({"error": "Missing device_id or command"}), 400
    
    # Verify access
    if not verify_device_access(device_id):
        print(f"[{datetime.now().isoformat()}] ⚠️ Unauthorized command attempt on device: {device_id} by user: {session.get('user_id')}")
        return jsonify({"error": "Unauthorized: You don't have access to this device"}), 403
    
    # Valid commands
    valid_commands = [
        'lock', 'shutdown', 'restart', 'logout', 
        'screenshot', 'webcam', 'chromehistory', 
        'popup_alert', 'block_site', 'unblock_site',
        'block_app', 'unblock_app', 'time_restriction'
    ]
    
    if command not in valid_commands:
        return jsonify({"error": f"Unknown command: {command}"}), 400
    
    try:
        # Create pending command for the client to execute
        command_id = store_command(device_id, command, params)
        print(f"[{datetime.now().isoformat()}] 📤 Command queued: {command} for device {device_id} (ID: {command_id})")
        return jsonify({"status": "success", "message": f"Command {command} sent to device", "command_id": command_id})
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ❌ Command execution failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/command/screenshot', methods=['POST'])
@login_required
def cmd_screenshot():
    """Take screenshot"""
    data = request.json
    device_id = data.get('device_id')
    
    # Verify access
    if not verify_device_access(device_id):
        print(f"[{datetime.now().isoformat()}] ⚠️ Unauthorized command attempt on device: {device_id} by user: {session.get('user_id')}")
        return jsonify({"error": "Unauthorized: You don't have access to this device"}), 403
    
    command_id = store_command(device_id, "screenshot")
    try:
        screenshot = pyautogui.screenshot()
        
        # Convert to base64 for storage
        img_byte_arr = BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        img_base64 = base64.b64encode(img_byte_arr).decode('utf-8')
        
        # Store screenshot in MongoDB
        screenshot_doc = {
            "device_id": device_id,
            "command_id": command_id,
            "image_base64": img_base64,
            "created_at": datetime.now()
        }
        screenshots_col.insert_one(screenshot_doc)
        
        store_result(device_id, command_id, "Screenshot captured")
        print(f"[{datetime.now().isoformat()}] 📸 Screenshot captured for device: {device_id}")
        
        return jsonify({"status": "success", "image": img_base64})
    except Exception as e:
        store_result(device_id, command_id, str(e), success=False)
        print(f"[{datetime.now().isoformat()}] ❌ Screenshot failed for device {device_id}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/command/webcam', methods=['POST'])
def cmd_webcam():
    """Capture webcam image"""
    data = request.json
    device_id = data.get('device_id')
    
    command_id = store_command(device_id, "webcam")
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to base64
            _, img_encoded = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(img_encoded.tobytes()).decode('utf-8')
            
            store_result(device_id, command_id, "Webcam captured")
            print(f"[{datetime.now().isoformat()}] 📷 Webcam captured for device: {device_id}")
            
            return jsonify({"status": "success", "image": img_base64})
        else:
            store_result(device_id, command_id, "Unable to capture webcam", success=False)
            print(f"[{datetime.now().isoformat()}] ❌ Webcam not available for device: {device_id}")
            return jsonify({"status": "error", "message": "Unable to capture webcam"}), 400
    except Exception as e:
        store_result(device_id, command_id, str(e), success=False)
        print(f"[{datetime.now().isoformat()}] ❌ Webcam capture failed for device {device_id}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/command/chromehistory', methods=['POST'])
def cmd_chrome_history():
    """Get Chrome browsing history"""
    data = request.json
    device_id = data.get('device_id')
    
    command_id = store_command(device_id, "chromehistory")
    try:
        chrome_history_path = os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data\Default\History"
        temp_history_db = "temp_chrome_history.db"
        
        # Copy the locked DB file
        os.system(f'copy "{chrome_history_path}" "{temp_history_db}"')
        
        conn = sqlite3.connect(temp_history_db)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title FROM urls ORDER BY last_visit_time DESC LIMIT 20")
        history = cursor.fetchall()
        conn.close()
        os.remove(temp_history_db)
        
        # Format history with timestamps
        history_data = []
        for url, title in history:
            history_data.append({
                "url": url,
                "title": title,
                "timestamp": datetime.now().isoformat()
            })
        
        store_result(device_id, command_id, "Chrome history retrieved")
        print(f"[{datetime.now().isoformat()}] 🌐 Chrome history retrieved for device: {device_id} ({len(history_data)} items)")
        
        return jsonify({"status": "success", "history": history_data})
    except Exception as e:
        store_result(device_id, command_id, str(e), success=False)
        print(f"[{datetime.now().isoformat()}] ❌ Chrome history failed for device {device_id}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/command/record', methods=['POST'])
def cmd_record():
    """Record screen"""
    data = request.json
    device_id = data.get('device_id')
    duration = data.get('duration', 10)
    
    command_id = store_command(device_id, "record", {"duration": duration})
    try:
        frames = []
        with mss.mss() as sct:
            start_time = time.time()
            while time.time() - start_time < duration:
                screenshot = sct.grab(sct.monitors[1])
                frame = np.array(screenshot)
                frames.append(frame)
                time.sleep(0.1)
        
        output = "screen_record.mp4"
        imageio.mimsave(output, frames, fps=10)
        
        store_result(device_id, command_id, f"Screen recorded for {duration} seconds")
        print(f"[{datetime.now().isoformat()}] 🎬 Screen recording completed for device: {device_id} ({duration}s)")
        
        return send_file(output, mimetype='video/mp4', as_attachment=True)
    except Exception as e:
        store_result(device_id, command_id, str(e), success=False)
        print(f"[{datetime.now().isoformat()}] ❌ Screen recording failed for device {device_id}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/screenshots/<device_id>', methods=['GET'])
@login_required
def get_screenshots(device_id):
    """Get stored screenshots"""
    # Verify access
    if not verify_device_access(device_id):
        print(f"[{datetime.now().isoformat()}] ⚠️ Unauthorized access attempt to device: {device_id} by user: {session.get('user_id')}")
        return jsonify({"error": "Unauthorized: You don't have access to this device"}), 403
    
    screenshots = list(screenshots_col.find(
        {"device_id": device_id},
        sort=[("created_at", -1)],
        limit=20
    ))
    
    for ss in screenshots:
        ss["_id"] = str(ss["_id"])
        ss["created_at"] = str(ss["created_at"])
    
    print(f"[{datetime.now().isoformat()}] 📸 Screenshots retrieved for device: {device_id} ({len(screenshots)} images)")
    return jsonify(screenshots)

@app.route('/api/commands/pending/<device_id>', methods=['GET'])
def get_pending_commands(device_id):
    """Get pending commands for client"""
    commands = list(commands_col.find(
        {"device_id": device_id, "executed": False}
    ))
    
    for cmd in commands:
        cmd["_id"] = str(cmd["_id"])
        cmd["created_at"] = str(cmd["created_at"]) if "created_at" in cmd else str(datetime.now())
    
    if commands:
        print(f"[{datetime.now().isoformat()}] 📋 {len(commands)} pending command(s) for device: {device_id}")
    
    return jsonify(commands)

@app.route('/api/command/block_website', methods=['POST'])
def cmd_block_website():
    """Block specific websites"""
    data = request.json
    device_id = data.get('device_id')
    websites = data.get('websites', [])
    
    command_id = store_command(device_id, "block_website", {"websites": websites})
    store_result(device_id, command_id, f"Blocking websites: {', '.join(websites)}")
    
    return jsonify({"status": "success", "message": f"Blocking {len(websites)} website(s)"})

@app.route('/api/command/unblock_website', methods=['POST'])
def cmd_unblock_website():
    """Unblock specific websites"""
    data = request.json
    device_id = data.get('device_id')
    websites = data.get('websites', [])
    
    command_id = store_command(device_id, "unblock_website", {"websites": websites})
    store_result(device_id, command_id, f"Unblocking websites: {', '.join(websites)}")
    
    return jsonify({"status": "success", "message": f"Unblocking {len(websites)} website(s)"})

@app.route('/api/command/block_exe', methods=['POST'])
def cmd_block_exe():
    """Block specific executable/application"""
    data = request.json
    device_id = data.get('device_id')
    exe_name = data.get('exe_name', '')
    
    command_id = store_command(device_id, "block_exe", {"exe_name": exe_name})
    store_result(device_id, command_id, f"Blocking application: {exe_name}")
    
    return jsonify({"status": "success", "message": f"Blocking {exe_name}"})

@app.route('/api/command/unblock_exe', methods=['POST'])
def cmd_unblock_exe():
    """Unblock specific executable/application"""
    data = request.json
    device_id = data.get('device_id')
    exe_name = data.get('exe_name', '')
    
    command_id = store_command(device_id, "unblock_exe", {"exe_name": exe_name})
    store_result(device_id, command_id, f"Unblocking application: {exe_name}")
    
    return jsonify({"status": "success", "message": f"Unblocking {exe_name}"})

@app.route('/api/location/<device_id>', methods=['GET'])
def get_device_location(device_id):
    """Get latest device location"""
    location = db["locations"].find_one(
        {"device_id": device_id},
        sort=[("timestamp", -1)]
    )
    
    if location:
        location["_id"] = str(location["_id"])
        return jsonify(location)
    return jsonify({"error": "No location data available"}), 404

@app.route('/api/command/fetch_location', methods=['POST'])
def cmd_fetch_location():
    """Trigger location fetch from device"""
    data = request.json
    device_id = data.get('device_id')
    
    command_id = store_command(device_id, "get_location", {})
    
    return jsonify({"status": "success", "message": "Location fetch requested"})

@app.route('/api/command/result/<command_id>', methods=['POST'])
def receive_command_result(command_id):
    """Receive result from client"""
    data = request.json
    result = data.get('result', {})
    
    commands_col.update_one(
        {"_id": ObjectId(command_id)},
        {"$set": {"result": result, "status": "completed"}}
    )
    
    return jsonify({"status": "success"})

@app.route('/api/command/executed/<command_id>', methods=['POST'])
def mark_executed(command_id):
    """Mark command as executed"""
    commands_col.update_one(
        {"_id": ObjectId(command_id)},
        {"$set": {"executed": True, "status": "completed"}}
    )
    return jsonify({"status": "marked as executed"})

# ==================== USER & PROFILE ====================

@app.route('/api/keystrokes/<device_id>', methods=['GET'])
@login_required
def get_keystrokes(device_id):
    """Get keystrokes for a device"""
    # Verify access
    if not verify_device_access(device_id):
        print(f"[{datetime.now().isoformat()}] ⚠️ Unauthorized access attempt to device: {device_id} by user: {session.get('user_id')}")
        return jsonify({"error": "Unauthorized: You don't have access to this device"}), 403
    
    keystrokes = list(keystrokes_col.find({"device_id": device_id}).sort("_id", -1).limit(100))
    result = []
    for k in keystrokes:
        result.append({
            "_id": str(k.get("_id")),
            "text": k.get("text", ""),
            "created_at": str(k.get("created_at", ""))
        })
    print(f"[{datetime.now().isoformat()}] ⌨️ Keystrokes retrieved for device: {device_id} ({len(result)} entries)")
    return jsonify(result)

@app.route('/api/history/<device_id>', methods=['GET'])
@login_required
def get_browser_history(device_id):
    """Get browser history for a device"""
    # Verify access
    if not verify_device_access(device_id):
        print(f"[{datetime.now().isoformat()}] ⚠️ Unauthorized access attempt to device: {device_id} by user: {session.get('user_id')}")
        return jsonify({"error": "Unauthorized: You don't have access to this device"}), 403
    
    results = list(results_col.find(
        {"device_id": device_id, "result": {"$ne": None}}
    ).sort("created_at", -1).limit(50))
    
    history = []
    for r in results:
        # Include result data with timestamp
        history_item = r.get('result') if isinstance(r.get('result'), dict) else {"title": str(r.get('result', ''))}
        history_item["created_at"] = str(r.get("created_at", ""))
        history_item["success"] = r.get("success", True)
        history.append(history_item)
    
    print(f"[{datetime.now().isoformat()}] 📜 Browser history retrieved for device: {device_id} ({len(history)} entries)")
    return jsonify(history)

@app.route('/api/time-restrictions/<device_id>', methods=['GET'])
@login_required
def get_time_restrictions(device_id):
    """Get time restrictions for a device"""
    restrictions = list(db["time_restrictions"].find(
        {"device_id": device_id}
    ).sort("_id", -1).limit(50))
    
    result = []
    for r in restrictions:
        result.append({
            "_id": str(r.get("_id")),
            "type": r.get("type", ""),
            "name": r.get("name", ""),
            "start_time": r.get("start_time", ""),
            "end_time": r.get("end_time", ""),
            "days": r.get("days", []),
            "created_at": str(r.get("created_at", ""))
        })
    
    print(f"[{datetime.now().isoformat()}] 📋 Time restrictions retrieved for device: {device_id}")
    return jsonify(result)

@app.route('/api/app-usage/<device_id>', methods=['GET'])
@login_required
def get_app_usage(device_id):
    """Get app usage statistics for a device"""
    app_usage = list(db["app_usage"].find(
        {"device_id": device_id}
    ).sort("created_at", -1).limit(100))
    
    result = []
    for app in app_usage:
        result.append({
            "_id": str(app.get("_id")),
            "app_name": app.get("app_name", "Unknown"),
            "duration": app.get("duration", 0),
            "created_at": str(app.get("created_at", app.get("timestamp", ""))),
            "category": app.get("category", "Other")
        })
    
    print(f"[{datetime.now().isoformat()}] 📊 App usage retrieved for device: {device_id} ({len(result)} apps)")
    return jsonify(result)

if __name__ == '__main__':
    # Create indexes for better performance
    devices_col.create_index("device_id", unique=True)
    commands_col.create_index("device_id")
    results_col.create_index("device_id")
    keystrokes_col.create_index("device_id")
    screenshots_col.create_index("device_id")
    
    # Startup logging
    print("\n" + "="*60)
    print("🚀 ParentEye Monitoring System Starting")
    print("="*60)
    print(f"[{datetime.now().isoformat()}] ✓ MongoDB Atlas connected")
    print(f"[{datetime.now().isoformat()}] ✓ Database: {DB_NAME}")
    print(f"[{datetime.now().isoformat()}] ✓ Collections: 6 (parents, devices, commands, results, keystrokes, screenshots)")
    print(f"[{datetime.now().isoformat()}] 🌐 Server starting on http://0.0.0.0:5000")
    print(f"[{datetime.now().isoformat()}] 🔐 Admin panel: http://localhost:5000/admin")
    print(f"[{datetime.now().isoformat()}] 👁️  Parent dashboard: http://localhost:5000/")
    print(f"[{datetime.now().isoformat()}] 📝 Logging all operations to console with timestamps")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)