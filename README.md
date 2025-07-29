# Raspberry Pi Projects with Hailo AI

This repository contains a collection of Raspberry Pi projects that leverage **Hailo AI** for edge computing and artificial intelligence applications. Hailo provides powerful AI acceleration capabilities that enable real-time computer vision, object detection, pose estimation, and more on the Raspberry Pi platform.

## 🚀 What is Hailo?

**Hailo** is an AI processor company that specializes in edge AI computing. Their processors are designed to run AI models efficiently at the edge (like on Raspberry Pi) without requiring cloud connectivity, providing:

- **High Performance**: Up to 26 TOPS (Trillion Operations Per Second) of AI processing power
- **Low Power**: Energy-efficient AI processing suitable for embedded devices
- **Real-time Processing**: Sub-millisecond latency for AI inference
- **Edge Computing**: AI processing happens locally, ensuring privacy and reducing bandwidth requirements

### Key Features of Hailo AI:
- **Object Detection**: Identify and locate objects in images/video
- **Pose Estimation**: Track human body poses and movements
- **Instance Segmentation**: Pixel-level object segmentation
- **Depth Estimation**: 3D depth mapping from 2D images
- **Multi-object Tracking**: Track multiple objects across frames
- **Custom Model Support**: Run your own trained AI models

## 📁 Project Structure

```
Raspberry-Pi-Projects/
├── Vision/                          # Main vision processing application
│   ├── main.py                      # Enhanced people counting with CSV logging
│   ├── debug_csv.py                 # CSV functionality testing
│   └── README.md                    # Vision-specific documentation
├── Resources/
│   └── hailo-rpi5-examples-main/    # Hailo official examples
│       ├── basic_pipelines/         # Core AI pipeline examples
│       └── community_projects/      # Community-built applications
├── config.yaml                      # Configuration files
├── requirements.txt                 # Python dependencies
└── install.sh                       # Installation script
```

## 🎯 Current Applications

### 1. Vision People Counter (`Vision/main.py`)
**Enhanced with AI-powered people counting and analytics**

**Features:**
- Real-time people detection using Hailo AI
- Unique individual tracking to avoid double counting
- Minute-by-minute CSV logging of people counts
- Visual display of current and total counts on video feed
- Thread-safe CSV operations with error handling

**Technical Details:**
- Uses Hailo's object detection pipeline
- Tracks unique individuals via track IDs
- Logs data to `people_count_log.csv` every minute
- Displays statistics on video frames in real-time

**CSV Output Format:**
```csv
Timestamp,Minute,People_Count,Total_Unique_People
2024-01-15 14:30:00,1234567,3,5
2024-01-15 14:31:00,1234568,2,7
```

## 🔧 Hailo Basic Pipelines

The `Resources/hailo-rpi5-examples-main/basic_pipelines/` directory contains core AI pipeline examples:

### 1. **Object Detection** (`detection.py`)
- Detects objects in real-time video streams
- Supports multiple object classes (person, car, etc.)
- Provides bounding boxes and confidence scores
- Includes object tracking capabilities

### 2. **Pose Estimation** (`pose_estimation.py`)
- Tracks human body poses and keypoints
- Enables gesture recognition and movement analysis
- Used in gaming and interactive applications

### 3. **Instance Segmentation** (`instance_segmentation.py`)
- Pixel-level object segmentation
- Precise object boundaries and masks
- Advanced computer vision applications

### 4. **Depth Estimation** (`depth.py`)
- 3D depth mapping from 2D images
- Spatial understanding and navigation
- Robotics and autonomous systems

## 🌟 Community Projects

The `Resources/hailo-rpi5-examples-main/community_projects/` directory showcases advanced applications:

### **Gaming & Entertainment**
- **Fruit Ninja**: Hand-tracking game using pose estimation
- **HailoGames (Sailted Fish)**: "Red Light, Green Light" pose-based game

### **Robotics & Automation**
- **TAILO**: Smart pet monitoring and interaction system
- **NavigAItor**: Autonomous robot navigation using visual landmarks
- **ChessMate**: Robotic chess system with AI-powered gameplay

### **Creative & Interactive**
- **TEMPO**: Biofeedback AI music generation based on heart rate
- **WLED Display**: LED matrix visualization of AI processing results
- **Dynamic Captioning**: Real-time image captioning with Florence2

### **Specialized Applications**
- **Traffic Sign Detection**: Road sign recognition with GPS integration
- **NeoPixel Control**: LED control based on AI detections
- **Detection Cropper**: Automated image cropping based on detections

## 🛠️ Installation & Setup

### Prerequisites
- Raspberry Pi 5 (recommended)
- Hailo AI processor/accelerator
- Python 3.8+
- GStreamer 1.0

### Quick Start
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Raspberry-Pi-Projects
   ```

2. **Install dependencies:**
   ```bash
   ./install.sh
   ```

3. **Set up Hailo environment:**
   ```bash
   ./setup_env.sh
   ```

4. **Run the people counter:**
   ```bash
   cd Vision
   python main.py
   ```

## 🔍 How Hailo AI Works

### Pipeline Architecture
```
Video Input → GStreamer Pipeline → Hailo AI Processor → Post-processing → Output
```

### Key Components:
1. **GStreamer Pipeline**: Handles video capture and processing
2. **Hailo AI Processor**: Runs AI models for inference
3. **Post-processing**: Analyzes AI results and applies business logic
4. **Output**: Displays results and logs data

### AI Model Integration
- Pre-trained models for common tasks (detection, pose estimation)
- Custom model support via Hailo Model Zoo
- Real-time inference with sub-millisecond latency
- Multi-model pipeline support

## 📊 Performance & Capabilities

### Processing Power
- **26 TOPS** of AI processing power
- **Real-time** video processing at 30+ FPS
- **Low latency** inference (<1ms)
- **Energy efficient** operation

### Supported Tasks
- ✅ Object Detection & Classification
- ✅ Multi-object Tracking
- ✅ Pose Estimation & Keypoint Detection
- ✅ Instance Segmentation
- ✅ Depth Estimation
- ✅ Custom AI Models
- ✅ Real-time Video Processing

## 🎮 Use Cases & Applications

### **Smart Home & IoT**
- People counting and occupancy monitoring
- Security and surveillance systems
- Smart pet monitoring and interaction
- Gesture-based home automation

### **Gaming & Entertainment**
- Motion-controlled games
- Interactive installations
- VR/AR applications
- Fitness tracking and analysis

### **Robotics & Automation**
- Autonomous navigation
- Object manipulation
- Quality control and inspection
- Agricultural monitoring

### **Healthcare & Wellness**
- Heart rate monitoring
- Activity tracking
- Fall detection
- Rehabilitation assistance

## 🔧 Development & Customization

### Adding New AI Features
1. **Choose a pipeline**: Select from basic pipelines or create custom
2. **Modify callback function**: Add your processing logic
3. **Integrate with existing code**: Use the user_data class for state management
4. **Test and deploy**: Use the provided testing framework

### Custom Model Integration
- Convert your models to Hailo format
- Optimize for edge deployment
- Integrate with GStreamer pipeline
- Add custom post-processing logic

## 📈 Monitoring & Analytics

### CSV Logging System
- Automatic data collection every minute
- Thread-safe file operations
- Error handling and recovery
- Configurable logging intervals

### Debug Tools
- `debug_csv.py`: Test CSV functionality independently
- Debug prints for troubleshooting
- Performance monitoring capabilities
- Error logging and reporting

## 🤝 Contributing

### Adding New Projects
1. Create a new directory in the appropriate location
2. Include a comprehensive README
3. Add installation and usage instructions
4. Test thoroughly on Raspberry Pi 5

### Community Projects
- Follow the community project guidelines
- Include video demonstrations when possible
- Document hardware requirements
- Provide clear setup instructions

## 📚 Resources & Documentation

### Official Hailo Resources
- [Hailo Documentation](https://hailo.ai/documentation/)
- [Hailo Model Zoo](https://hailo.ai/model-zoo/)
- [Hailo Community](https://community.hailo.ai/)

### Raspberry Pi Resources
- [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/)
- [Raspberry Pi Camera Setup](https://www.raspberrypi.org/documentation/usage/camera/)
- [GStreamer on Raspberry Pi](https://gstreamer.freedesktop.org/documentation/)

### Related Technologies
- **GStreamer**: Multimedia framework for video processing
- **OpenCV**: Computer vision library
- **NumPy**: Numerical computing
- **CSV**: Data logging and analytics

## 🐛 Troubleshooting

### Common Issues
1. **CSV not writing**: Check file permissions and disk space
2. **AI detection not working**: Verify Hailo hardware connection
3. **Performance issues**: Check system resources and cooling
4. **Video not displaying**: Verify camera connection and drivers

### Debug Commands
```bash
# Test CSV functionality
python Vision/debug_csv.py

# Check system resources
htop
df -h

# Verify Hailo installation
python -c "import hailo; print('Hailo installed successfully')"
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Hailo AI** for providing the AI acceleration technology
- **Raspberry Pi Foundation** for the amazing single-board computer
- **Community contributors** for the diverse range of applications
- **Open source community** for the supporting libraries and tools

---

**Happy coding with Hailo AI on Raspberry Pi! 🚀**

