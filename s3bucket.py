from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

if supabase_client:
    print("✅ Supabase client initialized successfully")
else: 
    print("❌ Failed to initialize Supabase client")
    