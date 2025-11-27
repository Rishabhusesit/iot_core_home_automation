# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up AWS IoT (Choose One)

#### Option A: Automated Setup
```bash
chmod +x setup_aws_iot.sh
./setup_aws_iot.sh
```

#### Option B: Manual Setup
Follow the detailed instructions in [README.md](README.md)

### 3. Configure Environment

```bash
# Copy the example file
cp env.example .env

# Edit .env with your AWS IoT endpoint and Thing name
nano .env
```

### 4. Run Your Device

**Publisher (sends data):**
```bash
python device_publisher.py
```

**Subscriber (receives commands):**
```bash
python device_subscriber.py
```

**Bidirectional (both):**
```bash
python device_bidirectional.py
```

## ✅ Verify It Works

1. Run `python device_publisher.py`
2. Go to AWS IoT Console → Test → MQTT test client
3. Subscribe to topic: `devices/MyIoTDevice/data`
4. You should see messages appearing!

## 📖 Need More Help?

See [README.md](README.md) for detailed documentation.







