import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_app.settings')
django.setup()

from django.contrib.auth import get_user_model
from chats.models import Conversation, Message

User = get_user_model()

def create_test_data():
    print("Creating test data...")
    
    # Create test users
    users = []
    for i in range(3):
        user, created = User.objects.get_or_create(
            username=f'testuser{i+1}',
            defaults={
                'email': f'testuser{i+1}@example.com',
                'first_name': f'Test{i+1}',
                'last_name': f'User{i+1}',
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"✅ Created user: {user.username} (password: testpass123)")
        else:
            print(f"✅ User already exists: {user.username}")
        users.append(user)
    
    # Check if conversations already exist
    existing_conversations = Conversation.objects.all()
    
    if not existing_conversations.exists():
        # Create test conversations only if none exist
        conv1 = Conversation.objects.create()
        conv1.participants.add(users[0], users[1])
        print(f"✅ Created conversation 1 with users: testuser1, testuser2")
        
        # Create test messages for pagination
        for i in range(25):
            Message.objects.create(
                conversation=conv1,
                sender=users[i % 2],
                message_body=f"Test message {i+1} from {users[i % 2].username}"
            )
        print("✅ Created 25 test messages for pagination testing")
        
        conv2 = Conversation.objects.create()
        conv2.participants.add(users[0], users[2])
        print(f"✅ Created conversation 2 with users: testuser1, testuser3")
        
        for i in range(5):
            Message.objects.create(
                conversation=conv2,
                sender=users[0],
                message_body=f"Hello testuser3, message {i+1}"
            )
        print("✅ Created 5 test messages in conversation 2")
    else:
        print(f"✅ Conversations already exist: {existing_conversations.count()} conversations found")
        
        # Add users to existing conversations if they're not already participants
        for i, conv in enumerate(existing_conversations):
            # Use conversation_id or pk instead of id
            conv_id = getattr(conv, 'conversation_id', conv.pk)
            
            if i == 0:
                if users[0] not in conv.participants.all():
                    conv.participants.add(users[0], users[1])
                    print(f"✅ Added testuser1 and testuser2 to conversation {conv_id}")
                else:
                    print(f"✅ Conversation {conv_id} already has participants")
            elif i == 1:
                if users[0] not in conv.participants.all():
                    conv.participants.add(users[0], users[2]) 
                    print(f"✅ Added testuser1 and testuser3 to conversation {conv_id}")
                else:
                    print(f"✅ Conversation {conv_id} already has participants")
    
    print("\n🎯 TEST USERS:")
    print("testuser1 / testpass123")
    print("testuser2 / testpass123")  
    print("testuser3 / testpass123")
    print("\n✅ Test data setup completed!")

if __name__ == "__main__":
    create_test_data()