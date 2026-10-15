import os
import psycopg
from google import genai

# 1. Initialize Gemini client
client = genai.Client()

# 2. Database connection parameters (Using the updated working database URL)
DB_URL = "postgresql://postgres:majid1214@localhost:5432/postgres"

print(" Connecting to database...")
with psycopg.connect(DB_URL) as conn:
    with conn.cursor() as cur:
        
        # Step 1: Fetch rows where embedding is NULL
        cur.execute("""
            SELECT id, content 
            FROM rag_documents 
            WHERE embedding IS NULL;
        """)
        rows = cur.fetchall()

        if not rows:
            print("No pending rows found. All vectors are already up to date!")
            exit()

        print(f"Found {len(rows)} rows to process. Starting vector generation...")

        # Step 2: Loop over every row
        for row_id, text_content in rows:
            print(f"Generating embedding for row ID: {row_id}...")
            
            try:
                # Target Google latest gemini model
                response = client.models.embed_content(
                    model="gemini-embedding-2",
                    contents=text_content,
                    config={"output_dimensionality": 128}
                )
            
                # response.embeddings ek list hoti hai jiska pehla object array content hold karta hai
                vector = response.embeddings[0].values

                # Step 3: Direct float array update back to row UUID via cast
                cur.execute("""
                    UPDATE rag_documents 
                    SET embedding = %s::float4[] 
                    WHERE id = %s;
                """, (vector, row_id))
                
                print(f"💾 Vector successfully saved for ID: {row_id}")
                
            except Exception as e:
                print(f"Error processing row {row_id}: {e}")

        # Commit transactions permanently to postgres disk
        conn.commit()
        print("\nSuccess! All 8 contents converted and permanently stored.")


