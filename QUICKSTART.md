# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start MongoDB
Make sure MongoDB is installed and running on your system.

**Windows:**
```bash
net start MongoDB
```

**macOS:**
```bash
brew services start mongodb-community
```

**Linux:**
```bash
sudo systemctl start mongod
```

### Step 3: Setup Database
```bash
python setup.py
```

### Step 4: Add Your Dataset
Place the `healthcare-dataset-stroke-data.csv` file in the `data/` folder.

### Step 5: Run the Application
```bash
python run.py
```

### Step 6: Access the Application
Open your browser and go to: **http://localhost:5000**

### Step 7: First Time Use
1. Click "Register" and create an account
2. Login with your credentials
3. Click "Load Dataset from CSV" on the dashboard
4. Start managing patient data!

## 🎯 Main Features

- **Dashboard**: View statistics and quick actions
- **Patients**: Browse all patient records (paginated)
- **Add Patient**: Create new patient records
- **Search**: Find specific patients quickly
- **Edit/Delete**: Manage existing records

## 🧪 Run Tests
```bash
python -m pytest tests/ -v
```


## 🆘 Troubleshooting

**MongoDB Connection Error:**
- Make sure MongoDB is running
- Check if MongoDB is on default port 27017

**Module Not Found Error:**
- Activate virtual environment
- Reinstall requirements: `pip install -r requirements.txt`

**Port Already in Use:**
- Change port in `run.py` (line 7)
- Or kill the process using port 5000
