# Web-Based Intelligent Physiotherapy Monitoring System

A comprehensive full-stack web application that integrates computer vision, machine learning, voice assistance, and AI chatbot for intelligent physiotherapy monitoring and guidance.

## 🎯 Features

### Core Functionality
- **Real-time Camera Tracking**: Advanced computer vision with MediaPipe pose estimation
- **AI Exercise Recognition**: Machine learning models for automatic exercise detection
- **Exercise-Specific Mode**: Focus on selected exercises to prevent overlapping detections
- **Voice Guidance**: Text-to-speech feedback for posture correction and motivation
- **AI Chatbot Assistant**: Context-aware physiotherapy guidance and safety tips
- **Progress Tracking**: Comprehensive dashboard with exercise history and analytics

### Backend Technologies
- **FastAPI**: Modern, fast web framework for building APIs
- **WebSockets**: Real-time bidirectional communication
- **SQLAlchemy**: Database ORM with SQLite/PostgreSQL support
- **JWT Authentication**: Secure user authentication and authorization
- **MediaPipe**: Google's pose estimation solution
- **OpenCV**: Computer vision and image processing
- **scikit-learn**: Machine learning models for exercise classification

### Frontend Technologies
- **HTML5/CSS3/JavaScript**: Modern responsive web design
- **WebRTC**: Browser camera access
- **WebSocket Client**: Real-time communication with backend
- **Font Awesome**: Professional icons and UI elements

## 🤖 ML Model Training

### Pre-trained Models
The system includes comprehensive ML models trained on physiotherapy datasets:

**Supported Algorithms:**
- **SVM (Support Vector Machine)**: RBF, polynomial, and linear kernels
- **Random Forest**: Ensemble method with feature importance
- **MLP (Multi-Layer Perceptron)**: Neural network with hidden layers

**Training Datasets:**
- **KIMORE**: Kinect-based motion capture (20 exercises, full-body)
- **UI-PMRD**: Upper limb rehabilitation (clinical population)

### Quick Model Training
```bash
# Train ML models with synthetic data
python train_ml_models.py

# Advanced training with real datasets
cd backend
python ml_training/train_and_evaluate.py \
    --kimore-path /path/to/kimore \
    --ui-pmrd-path /path/to/ui_pmrd
```

### Model Features
- **Exercise Recognition**: 88-95% accuracy on test data
- **Real-time Processing**: Optimized for live camera feeds
- **Confidence Scoring**: Probability estimates for predictions
- **Cross-validation**: 5-fold CV for robust evaluation

### Model Evaluation
```bash
# Evaluate existing models
cd backend
python ml_training/train_and_evaluate.py --evaluate-only --test-data /path/to/test

# View evaluation reports
ls models/evaluation/
cat models/evaluation/evaluation_report.json
```

### Expected Performance
- **SVM**: 85-92% accuracy
- **Random Forest**: 87-94% accuracy  
- **MLP**: 88-95% accuracy

*Models are automatically selected based on cross-validation performance*

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher (for frontend development)
- Modern web browser with camera support
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd physio-web
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   # Create .env file in backend directory
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Database Initialization**
   ```bash
   # The database will be created automatically on first run
   # SQLite: ./physio_monitoring.db
   # PostgreSQL: Set DATABASE_URL in .env
   ```

5. **Start Backend Server**
   ```bash
   cd backend
   python app.py
   # or
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Frontend Setup**
   ```bash
   cd frontend
   # No build process required - serve static files
   # Use any static file server or Python's built-in server
   python -m http.server 3000
   ```

7. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
physio-web/
├── backend/
│   ├── app.py                  # FastAPI main application
│   ├── auth.py                 # Authentication logic
│   ├── database.py             # Database models and configuration
│   ├── models.py               # Pydantic models
│   ├── requirements.txt        # Python dependencies
│   ├── voice/
│   │   └── tts_engine.py       # Text-to-speech engine
│   ├── chatbot/
│   │   └── chatbot_engine.py   # AI chatbot logic
│   └── exercise_engine/
│       └── engine.py           # Exercise processing engine
├── frontend/
│   ├── index.html              # Main HTML file
│   ├── style.css               # Styling
│   ├── script.js               # Frontend JavaScript
│   └── static/                 # Static assets
└── README.md                   # This file
```

## 🔧 Configuration

### Backend Environment Variables (.env)
```env
# Database
DATABASE_URL=sqlite:///./physio_monitoring.db
# DATABASE_URL=postgresql://user:password@localhost/physio_db

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# Optional: External services
# TTS_SERVICE=gtts  # Default: pyttsx3
```

### Frontend Configuration
- Update `API_BASE` in `script.js` if backend runs on different host/port
- Ensure HTTPS for production camera access

## 🏃‍♂️ Usage Guide

### 1. User Registration and Login
1. Click "Login" button
2. Register new account or login with existing credentials
3. User data is isolated and secure

### 2. Exercise Selection
1. Navigate to "Exercises" page
2. Select body part category (Shoulder, Elbow, Knee, etc.)
3. Choose specific exercise from the list
4. Click "Start Exercise"

### 3. Exercise Session
1. Allow camera access when prompted
2. Position yourself in full view of camera
3. Follow voice guidance and on-screen feedback
4. Monitor:
   - Repetition count
   - Joint angles
   - Posture correctness
   - Quality score
5. Use "Reset" to restart counting
6. Click "Exit Exercise" when finished

### 4. Progress Tracking
1. Visit "Dashboard" page
2. View:
   - Total sessions and repetitions
   - Average quality scores
   - Recent exercise history
   - Progress trends

### 5. Chatbot Assistance
1. Navigate to "Chatbot" page
2. Ask questions about:
   - Exercise instructions
   - Safety tips
   - Posture guidance
   - General physiotherapy advice

## 🎯 Supported Exercises

### Shoulder Exercises
- Shoulder Flexion
- Shoulder Extension
- Shoulder Abduction
- Shoulder Adduction
- Shoulder Internal Rotation
- Shoulder External Rotation
- Shoulder Horizontal Abduction
- Shoulder Horizontal Adduction
- Shoulder Circumduction

### Other Exercises
- Elbow Flexion/Extension
- Knee Flexion
- Hip Abduction

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- User data isolation
- CORS protection
- Input validation and sanitization
- Secure WebSocket connections

## 📊 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /token` - User login
- `GET /users/me` - Get current user info

### Exercises
- `GET /exercises` - Get all exercises
- `GET /exercises/category/{category}` - Get exercises by category
- `GET /exercises/categories` - Get all categories

### Sessions
- `POST /sessions` - Create exercise session
- `GET /sessions` - Get user sessions
- `GET /sessions/{exercise_name}` - Get sessions for specific exercise

### Chatbot
- `POST /chatbot` - Chat with AI assistant
- `GET /chatbot/exercises` - Get exercise list
- `GET /chatbot/safety-tip` - Get safety tip

### WebSocket
- `WS /ws/{user_id}` - Real-time exercise tracking

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
# Run browser tests
python -m http.server 3000
# Access http://localhost:3000 in browser
```

### Integration Tests
1. Start backend server
2. Start frontend server
3. Test complete user flow:
   - Registration → Login → Exercise → Dashboard

## 🚀 Deployment

### Backend Deployment
```bash
# Using Docker
docker build -t physio-backend .
docker run -p 8000:8000 physio-backend

# Using systemd (Linux)
sudo cp physio-backend.service /etc/systemd/system/
sudo systemctl enable physio-backend
sudo systemctl start physio-backend
```

### Frontend Deployment
```bash
# Deploy to any static file server
# nginx, Apache, S3, Netlify, Vercel, etc.
cp -r frontend/* /var/www/html/
```

### Production Considerations
- Use HTTPS for camera access
- Set strong SECRET_KEY
- Use PostgreSQL for production database
- Configure CORS properly
- Set up reverse proxy (nginx)
- Monitor logs and performance

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 Development Notes

### Exercise Engine Integration
- Original Python modules are imported from `../Physio-Monitoring/src`
- Fallback implementations provided when original modules unavailable
- Exercise-specific mode prevents overlapping detections

### Voice Feedback
- Uses pyttsx3 for offline TTS
- gTTS available as alternative
- Async processing prevents blocking

### ML Models
- Pre-trained models expected in `../Physio-Monitoring/models/`
- Automatic loading with fallback to biomechanics
- Confidence thresholds for reliable detection

## 🐛 Troubleshooting

### Common Issues

1. **Camera not working**
   - Check browser permissions
   - Use HTTPS in production
   - Ensure no other app is using camera

2. **WebSocket connection failed**
   - Check backend server is running
   - Verify user authentication
   - Check firewall settings

3. **Exercise detection not working**
   - Ensure good lighting
   - Position camera for full body view
   - Check ML models are loaded

4. **Voice feedback not playing**
   - Check system audio settings
   - Verify TTS engine initialization
   - Check browser audio permissions

### Debug Mode
```bash
# Backend debug mode
uvicorn app:app --reload --log-level debug

# Frontend debug
# Open browser developer tools
# Check console for errors
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- MediaPipe team for pose estimation
- FastAPI framework contributors
- OpenCV community
- Medical professionals for exercise guidance

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review API documentation at `/docs`

---

**Built with ❤️ for better physiotherapy monitoring and patient care**
