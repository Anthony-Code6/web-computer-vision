import os
from supabase import create_client

SUPABASE_URL = "https://ptmhxjbqghsylnxexchk.supabase.co" 
#os.getenv("SUPABASE_URL", "https://ptmhxjbqghsylnxexchk.supabase.co")
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB0bWh4amJxZ2hzeWxueGV4Y2hrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYxNDI4MTcsImV4cCI6MjA2MTcxODgxN30.rOwrsSqcEmqGvf95SUTSRoP5FlJ7heGboF2CChuqkyI"
#os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

# BUCKET_MODELOS = "model"
BUCKET_HONGO = "detecciones"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
