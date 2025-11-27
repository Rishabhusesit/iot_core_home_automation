"""
Setup Verification Script
Checks if all required files and configurations are in place
"""
import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"⚠️  {description}: {dirpath} - NOT FOUND (will be created during setup)")
        return False

def main():
    print("=" * 60)
    print("AWS IoT Project Setup Verification")
    print("=" * 60)
    print()
    
    all_good = True
    
    # Check Python files
    print("📁 Checking Project Files:")
    print("-" * 60)
    files_to_check = [
        ("config.py", "Configuration module"),
        ("device_publisher.py", "Device publisher"),
        ("device_subscriber.py", "Device subscriber"),
        ("device_bidirectional.py", "Bidirectional device"),
        ("requirements.txt", "Python dependencies"),
        ("setup_aws_iot.sh", "Setup script"),
        ("README.md", "Documentation"),
        ("QUICKSTART.md", "Quick start guide"),
        (".gitignore", "Git ignore file"),
    ]
    
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_good = False
    
    print()
    
    # Check environment file
    print("⚙️  Checking Configuration:")
    print("-" * 60)
    if check_file_exists(".env", "Environment variables"):
        print("   ✅ .env file found")
    else:
        if check_file_exists("env.example", "Environment template"):
            print("   ⚠️  .env file not found. Copy env.example to .env")
        else:
            print("   ❌ env.example not found")
            all_good = False
    
    print()
    
    # Check certificates directory
    print("🔐 Checking Certificates:")
    print("-" * 60)
    cert_dir_exists = check_directory_exists("certificates", "Certificates directory")
    
    if cert_dir_exists:
        cert_files = [
            ("certificates/AmazonRootCA1.pem", "Root CA"),
            ("certificates/certificate.pem.crt", "Device certificate"),
            ("certificates/private.pem.key", "Private key"),
        ]
        
        for filepath, description in cert_files:
            if not check_file_exists(filepath, description):
                print(f"   ⚠️  {description} will be created during AWS IoT setup")
    
    print()
    
    # Check Python dependencies
    print("🐍 Checking Python Environment:")
    print("-" * 60)
    try:
        import boto3
        print("✅ boto3 installed")
    except ImportError:
        print("❌ boto3 not installed - run: pip install -r requirements.txt")
        all_good = False
    
    try:
        from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
        print("✅ AWSIoTPythonSDK installed")
    except ImportError:
        print("❌ AWSIoTPythonSDK not installed - run: pip install -r requirements.txt")
        all_good = False
    
    try:
        import dotenv
        print("✅ python-dotenv installed")
    except ImportError:
        print("❌ python-dotenv not installed - run: pip install -r requirements.txt")
        all_good = False
    
    print()
    print("=" * 60)
    
    if all_good:
        print("✅ All core files are in place!")
        print()
        print("Next steps:")
        print("1. Set up AWS IoT Core (run ./setup_aws_iot.sh or follow README.md)")
        print("2. Configure .env file with your AWS IoT endpoint")
        print("3. Run: python device_publisher.py")
    else:
        print("⚠️  Some files or dependencies are missing.")
        print("Please install dependencies: pip install -r requirements.txt")
    
    print("=" * 60)

if __name__ == "__main__":
    main()







