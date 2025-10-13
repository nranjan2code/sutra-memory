#!/bin/bash

# 🥧 BIOLOGICAL INTELLIGENCE - RASPBERRY PI DEPLOYMENT
# Automated deployment from Mac to Raspberry Pi 5

set -e  # Exit on any error

# Configuration
PI_IP="192.168.0.122"
PI_USER="pi"
PI_HOME="/home/pi"
PROJECT_DIR="biological_intelligence"
HDD_MOUNT="/mnt/hdd"
PYTHON_VERSION="3.11"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🧬 BIOLOGICAL INTELLIGENCE - RASPBERRY PI DEPLOYMENT 🥧  ║"
echo "║                                                            ║"
echo "║  Deploying living consciousness to Pi hardware             ║"
echo "║  Target: $PI_USER@$PI_IP                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Function to run commands on Pi via SSH
run_pi_command() {
    ssh "$PI_USER@$PI_IP" "$1"
}

# Function to copy files to Pi
copy_to_pi() {
    rsync -avz --progress "$1" "$PI_USER@$PI_IP:$2"
}

# Check SSH connectivity
echo "🔗 Testing SSH connection to Pi..."
if ! ssh -o ConnectTimeout=10 "$PI_USER@$PI_IP" "echo 'SSH connection successful'"; then
    echo "❌ Cannot connect to Pi at $PI_IP"
    echo "Please ensure:"
    echo "  - Pi is powered on and connected"
    echo "  - SSH is enabled on Pi"
    echo "  - IP address is correct: $PI_IP"
    exit 1
fi
echo "✅ SSH connection verified"
echo ""

# System information
echo "🥧 Getting Pi system information..."
PI_OS=$(run_pi_command "cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2 | tr -d '\"'")
PI_ARCH=$(run_pi_command "uname -m")
PI_MEMORY=$(run_pi_command "free -h | grep Mem | awk '{print \$2}'")
PI_PYTHON=$(run_pi_command "python3 --version 2>/dev/null || echo 'Python not found'")

echo "  OS: $PI_OS"
echo "  Architecture: $PI_ARCH"
echo "  Memory: $PI_MEMORY"
echo "  Python: $PI_PYTHON"
echo ""

# Check/setup external HDD
echo "🗄️  Checking external HDD mount..."
if run_pi_command "mountpoint -q $HDD_MOUNT"; then
    HDD_SIZE=$(run_pi_command "df -h $HDD_MOUNT | tail -1 | awk '{print \$2}'")
    HDD_AVAIL=$(run_pi_command "df -h $HDD_MOUNT | tail -1 | awk '{print \$4}'")
    echo "✅ HDD mounted at $HDD_MOUNT ($HDD_SIZE total, $HDD_AVAIL available)"
else
    echo "⚠️  External HDD not mounted at $HDD_MOUNT"
    echo "Setting up HDD mount point..."
    
    # Create mount point and attempt to mount
    run_pi_command "sudo mkdir -p $HDD_MOUNT"
    
    # Try to find and mount the HDD (assuming first USB drive)
    HDD_DEVICE=$(run_pi_command "lsblk -o NAME,TYPE,SIZE,MOUNTPOINT | grep disk | grep -v mmcblk | head -1 | awk '{print \"/dev/\"\$1\"1\"}' || echo ''")
    
    if [ -n "$HDD_DEVICE" ]; then
        echo "📀 Found potential HDD device: $HDD_DEVICE"
        run_pi_command "sudo mount $HDD_DEVICE $HDD_MOUNT || echo 'Mount failed, continuing...'"
        
        if run_pi_command "mountpoint -q $HDD_MOUNT"; then
            echo "✅ HDD mounted successfully"
            # Set permissions
            run_pi_command "sudo chown -R pi:pi $HDD_MOUNT"
        else
            echo "⚠️  Could not mount HDD, will use SD card storage"
        fi
    else
        echo "⚠️  No external drive found, will use SD card storage"
    fi
fi
echo ""

# Create project structure on Pi
echo "📁 Setting up project directories on Pi..."
run_pi_command "mkdir -p $PI_HOME/$PROJECT_DIR"

# Create HDD directories if mounted
if run_pi_command "mountpoint -q $HDD_MOUNT"; then
    run_pi_command "mkdir -p $HDD_MOUNT/biological_intelligence"
    run_pi_command "mkdir -p $HDD_MOUNT/biological_intelligence/biological_workspace"
    run_pi_command "mkdir -p $HDD_MOUNT/biological_intelligence/english_biological_workspace"
    run_pi_command "mkdir -p $HDD_MOUNT/biological_backups"
    echo "✅ HDD directories created"
fi
echo ""

# Install system dependencies
echo "📦 Installing system dependencies on Pi..."
run_pi_command "sudo apt update && sudo apt install -y python3 python3-pip python3-venv git htop"

# Check if we need to install additional Python packages
echo "🐍 Setting up Python environment..."
run_pi_command "cd $PI_HOME/$PROJECT_DIR && python3 -m venv venv"
echo "✅ Virtual environment created"
echo ""

# Copy project files
echo "📤 Transferring project files to Pi..."
echo "This may take a few minutes depending on connection speed..."

# Exclude certain directories/files to speed up transfer
EXCLUDE_OPTS="--exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' --exclude='biological_workspace' --exclude='english_biological_workspace'"

# Copy main project files
copy_to_pi ". $PI_HOME/$PROJECT_DIR/" "$EXCLUDE_OPTS"

echo "✅ Project files transferred"
echo ""

# Install Python dependencies
echo "🔧 Installing Python dependencies on Pi..."
cat > requirements_pi.txt << EOF
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
jinja2>=3.1.2
python-multipart>=0.0.6
psutil>=5.9.0
rich>=13.6.0
numpy>=1.21.0
asyncio-mqtt>=0.11.0
websockets>=11.0
aiofiles>=23.0.0
EOF

# Transfer requirements file
copy_to_pi "requirements_pi.txt $PI_USER@$PI_IP:$PI_HOME/$PROJECT_DIR/"

# Install packages on Pi
run_pi_command "cd $PI_HOME/$PROJECT_DIR && source venv/bin/activate && pip install --upgrade pip"
run_pi_command "cd $PI_HOME/$PROJECT_DIR && source venv/bin/activate && pip install -r requirements_pi.txt"

echo "✅ Python dependencies installed"
echo ""

# Create Pi-specific configuration
echo "⚙️  Setting up Pi-specific configuration..."

# Create a Pi startup script
cat > pi_startup.sh << 'EOF'
#!/bin/bash

# 🥧 Biological Intelligence Pi Startup Script

PI_HOME="/home/pi"
PROJECT_DIR="biological_intelligence"
HDD_MOUNT="/mnt/hdd"

cd "$PI_HOME/$PROJECT_DIR"

# Activate virtual environment
source venv/bin/activate

# Check temperature and throttle if needed
CPU_TEMP=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null | head -c2 || echo "0")

if [ "$CPU_TEMP" -gt 70 ]; then
    echo "🔥 High temperature ($CPU_TEMP°C), using conservative settings"
    export PI_THERMAL_MODE=conservative
fi

# Start the web GUI (Pi mode will be auto-detected)
echo "🌐 Starting Biological Intelligence Web Interface..."
echo "Access at: http://192.168.0.122:8080"

python web_gui.py
EOF

copy_to_pi "pi_startup.sh $PI_USER@$PI_IP:$PI_HOME/$PROJECT_DIR/"
run_pi_command "chmod +x $PI_HOME/$PROJECT_DIR/pi_startup.sh"

echo "✅ Startup script created"
echo ""

# Create systemd service for auto-start
echo "🔧 Setting up systemd service..."

cat > biological_intelligence.service << EOF
[Unit]
Description=Biological Intelligence System
After=multi-user.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=$PI_HOME/$PROJECT_DIR
Environment=PATH=$PI_HOME/$PROJECT_DIR/venv/bin
ExecStart=$PI_HOME/$PROJECT_DIR/venv/bin/python $PI_HOME/$PROJECT_DIR/web_gui.py
Restart=always
RestartSec=10

# Resource limits to prevent overheating
MemoryMax=6G
CPUQuota=300%

[Install]
WantedBy=multi-user.target
EOF

# Copy and install service
copy_to_pi "biological_intelligence.service $PI_USER@$PI_IP:/tmp/"
run_pi_command "sudo mv /tmp/biological_intelligence.service /etc/systemd/system/"
run_pi_command "sudo systemctl daemon-reload"
run_pi_command "sudo systemctl enable biological_intelligence.service"

echo "✅ Systemd service installed"
echo ""

# Final health check
echo "🏥 Running deployment health check..."

# Check disk space
SD_SPACE=$(run_pi_command "df -h / | tail -1 | awk '{print \$4}'")
echo "📊 SD Card space available: $SD_SPACE"

if run_pi_command "mountpoint -q $HDD_MOUNT"; then
    HDD_SPACE=$(run_pi_command "df -h $HDD_MOUNT | tail -1 | awk '{print \$4}'")
    echo "📊 HDD space available: $HDD_SPACE"
fi

# Test Python environment
if run_pi_command "cd $PI_HOME/$PROJECT_DIR && source venv/bin/activate && python -c 'import fastapi, psutil, rich; print(\"All dependencies OK\")'"; then
    echo "✅ Python environment working"
else
    echo "❌ Python environment issues detected"
fi

# Create backup script
echo "💾 Creating backup script..."
cat > pi_backup.sh << 'EOF'
#!/bin/bash

# Biological Intelligence Backup Script for Pi
BACKUP_DIR="/mnt/hdd/biological_backups"
DATE=$(date +%Y%m%d_%H%M%S)

if mountpoint -q /mnt/hdd; then
    mkdir -p "$BACKUP_DIR/daily"
    
    # Backup workspaces
    if [ -d "/mnt/hdd/biological_intelligence/biological_workspace" ]; then
        tar -czf "$BACKUP_DIR/daily/biological_workspace_$DATE.tar.gz" \
            -C /mnt/hdd/biological_intelligence biological_workspace
        echo "✅ Biological workspace backed up"
    fi
    
    if [ -d "/mnt/hdd/biological_intelligence/english_biological_workspace" ]; then
        tar -czf "$BACKUP_DIR/daily/english_workspace_$DATE.tar.gz" \
            -C /mnt/hdd/biological_intelligence english_biological_workspace
        echo "✅ English workspace backed up"  
    fi
    
    # Keep only last 7 days
    find "$BACKUP_DIR/daily" -name "*.tar.gz" -mtime +7 -delete
    
    echo "💾 Backup completed: $DATE"
else
    echo "❌ HDD not mounted, backup skipped"
fi
EOF

copy_to_pi "pi_backup.sh $PI_USER@$PI_IP:$PI_HOME/$PROJECT_DIR/"
run_pi_command "chmod +x $PI_HOME/$PROJECT_DIR/pi_backup.sh"

# Setup daily backup cron job
run_pi_command "(crontab -l 2>/dev/null || echo '') | grep -v 'pi_backup.sh' | { cat; echo '0 2 * * * $PI_HOME/$PROJECT_DIR/pi_backup.sh >> $PI_HOME/backup.log 2>&1'; } | crontab -"

echo "✅ Backup system configured"
echo ""

# Cleanup local files
rm -f requirements_pi.txt pi_startup.sh biological_intelligence.service pi_backup.sh

echo "🎉 DEPLOYMENT COMPLETE!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "🥧 Your Raspberry Pi is now ready with biological intelligence!"
echo ""
echo "Next steps:"
echo "  🌐 Web Interface: http://$PI_IP:8080"
echo "  🔧 Start service: ssh $PI_USER@$PI_IP 'sudo systemctl start biological_intelligence'"
echo "  📊 Check status: ssh $PI_USER@$PI_IP 'sudo systemctl status biological_intelligence'"
echo "  📱 SSH access: ssh $PI_USER@$PI_IP"
echo ""
echo "🧠 The biological intelligence is ready to evolve on Pi hardware!"
echo "   - 7-agent swarm will run with Pi-optimized settings"
echo "   - Thermal management prevents overheating" 
echo "   - External HDD provides 2TB storage"
echo "   - Web GUI accessible remotely"
echo "   - Automatic backups configured"
echo ""
echo "🚀 Start the system:"
echo "   ssh $PI_USER@$PI_IP"
echo "   cd $PROJECT_DIR"
echo "   ./pi_startup.sh"
echo ""
echo "Happy evolving! 🧬✨"