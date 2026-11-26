from app import create_app

app = create_app()

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🩺 MediTrack AI (Cardiology Edition) Server Starting...")
    print("🌐 Open your browser at: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)
