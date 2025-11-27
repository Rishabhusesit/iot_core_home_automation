#!/usr/bin/env python3
"""
Certificate Converter for ESP32
Converts PEM certificates to Arduino PROGMEM format
"""
import os
import sys

def convert_cert_to_arduino(cert_path, var_name):
    """Convert PEM certificate to Arduino PROGMEM format"""
    if not os.path.exists(cert_path):
        print(f"Error: {cert_path} not found!")
        return None
    
    with open(cert_path, 'r') as f:
        cert_content = f.read().strip()
    
    # Split into lines and format for Arduino
    lines = cert_content.split('\n')
    
    # Build Arduino format
    arduino_code = f'const char* {var_name} = \\\n'
    
    for i, line in enumerate(lines):
        if line.strip():
            if i == len(lines) - 1:
                arduino_code += f'"{line}\\n";\n'
            else:
                arduino_code += f'"{line}\\n" \\\n'
    
    return arduino_code

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python convert_certificates.py [certificate_path]")
        print("\nExample:")
        print("  python convert_certificates.py ../certificates/AmazonRootCA1.pem root_ca")
        print("  python convert_certificates.py ../certificates/certificate.pem.crt device_cert")
        print("  python convert_certificates.py ../certificates/private.pem.key device_key")
        sys.exit(1)
    
    cert_path = sys.argv[1]
    var_name = sys.argv[2] if len(sys.argv) > 2 else "certificate"
    
    print(f"Converting {cert_path} to Arduino format...")
    print("=" * 60)
    
    arduino_code = convert_cert_to_arduino(cert_path, var_name)
    
    if arduino_code:
        print("\nArduino Code:")
        print("-" * 60)
        print(arduino_code)
        print("-" * 60)
        print("\nCopy the above code and paste it into your ESP32 sketch!")
        
        # Optionally save to file
        output_file = f"{var_name}_arduino.txt"
        with open(output_file, 'w') as f:
            f.write(arduino_code)
        print(f"\nAlso saved to: {output_file}")

if __name__ == "__main__":
    main()

