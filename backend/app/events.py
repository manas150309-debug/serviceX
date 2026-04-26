from flask_socketio import emit, join_room, leave_room
from app import get_db
from bson import ObjectId
from datetime import datetime


def setup_events(socketio):
    """Setup SocketIO events."""
    
    # Track connected users
    connected_users = {}
    
    @socketio.on('connect')
    def handle_connect(auth):
        """Handle user connection."""
        user_id = auth.get('user_id') if auth else None
        if user_id:
            connected_users[user_id] = request.sid
            print(f"User {user_id} connected")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle user disconnection."""
        # Remove user from connected users
        user_id = None
        for uid, sid in list(connected_users.items()):
            if sid == request.sid:
                user_id = uid
                del connected_users[uid]
                break
        if user_id:
            print(f"User {user_id} disconnected")
    
    @socketio.on('booking_update')
    def handle_booking_update(data):
        """Broadcast booking status update."""
        booking_id = data.get('booking_id')
        status = data.get('status')
        user_id = data.get('user_id')
        
        db = get_db()
        db.booking_notifications.insert_one({
            'booking_id': booking_id,
            'status': status,
            'timestamp': datetime.utcnow()
        })
        
        # Emit to specific user if connected
        if user_id in connected_users:
            emit('booking_status_changed', {
                'booking_id': booking_id,
                'status': status,
                'timestamp': datetime.utcnow().isoformat()
            }, room=connected_users[user_id])
    
    @socketio.on('provider_location_update')
    def handle_location_update(data):
        """Handle provider location update."""
        provider_id = data.get('provider_id')
        location = data.get('location')
        booking_id = data.get('booking_id')
        
        db = get_db()
        db.location_updates.insert_one({
            'provider_id': provider_id,
            'booking_id': booking_id,
            'location': location,
            'timestamp': datetime.utcnow()
        })
        
        # Broadcast location to user
        booking = db.bookings.find_one({'_id': ObjectId(booking_id)})
        if booking:
            user_id = str(booking['user_id'])
            if user_id in connected_users:
                emit('provider_location_updated', {
                    'provider_id': provider_id,
                    'location': location,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=connected_users[user_id])
    
    @socketio.on('request_notification')
    def handle_notification_request(data):
        """Send notification to user."""
        recipient_id = data.get('recipient_id')
        notification = data.get('notification')
        
        if recipient_id in connected_users:
            emit('notification', {
                'message': notification,
                'timestamp': datetime.utcnow().isoformat()
            }, room=connected_users[recipient_id])
    
    @socketio.on('join_booking_room')
    def on_join_booking(data):
        """Join a booking-specific room for real-time updates."""
        booking_id = data.get('booking_id')
        room = f'booking_{booking_id}'
        join_room(room)
        emit('message', {
            'data': f'User joined booking {booking_id}'
        }, room=room)
    
    @socketio.on('leave_booking_room')
    def on_leave_booking(data):
        """Leave booking room."""
        booking_id = data.get('booking_id')
        room = f'booking_{booking_id}'
        leave_room(room)
        emit('message', {
            'data': f'User left booking {booking_id}'
        }, room=room)
    
    @socketio.on('broadcast_to_booking')
    def broadcast_to_booking(data):
        """Broadcast message to all users in a booking room."""
        booking_id = data.get('booking_id')
        message = data.get('message')
        room = f'booking_{booking_id}'
        
        emit('booking_message', {
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room)


from flask import request
