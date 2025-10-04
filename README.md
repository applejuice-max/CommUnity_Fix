# CommUnityFix - Barangay Union

A modern Streamlit web application for community issue reporting and management in Barangay Union.

## Features

### For Citizens
- 📝 **Easy Issue Reporting**: Submit community problems with photos and detailed descriptions
- 📞 **Emergency Contacts**: Quick access to emergency services and contact information
- 🛠️ **Helpful Tips**: Guidance for minor problems and emergency procedures
- 📊 **Progress Dashboard**: Track the status of community reports and see resolution progress
- 📱 **Mobile-Friendly**: Responsive design works on all devices

### For Administrators
- 📊 **Dashboard**: Comprehensive overview of all reports with statistics
- 🗂️ **Report Organization**: Organize reports by status, priority, date, or issue type
- 🔍 **Advanced Search**: Find reports by name, location, type, status, priority, or date range
- 🛠️ **Report Management**: Update status, assign tasks, and add comments with quick actions
- ⚡ **Quick Actions**: Refresh data, backup, export, and view analytics
- 📥 **Export Data**: Download reports as CSV for record-keeping
- 💾 **Data Persistence**: Automatic backup and data storage

### For Everyone
- 📈 **Progress Tracking**: Visual charts and analytics for report progress
- 🕒 **Recent Activity**: Real-time updates on community issues
- 🔍 **Issue Analysis**: Detailed breakdown by issue type and resolution rates
- 💡 **Performance Insights**: Recommendations and performance metrics

## Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   python3.13 -m pip install -r requirements.txt
   ```
   Or if you have Python in your PATH:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Option 1: Using the provided scripts
- **Windows**: Double-click `run_app.bat`
- **Linux/Mac**: Run `./run_app.sh`

### Option 2: Manual command
1. **Start the Streamlit app**:
   ```bash
   python3.13 -m streamlit run communityfix_app.py
   ```
   Or if you have Python in your PATH:
   ```bash
   streamlit run communityfix_app.py
   ```

2. **Open your browser** and go to `http://localhost:8501`

## Usage

### For Citizens
1. Navigate to **"Report Issue"** to submit a new problem
2. Fill in all required fields (marked with *)
3. Upload a photo if available
4. Submit your report and note the Report ID
5. Check **"Progress Dashboard"** to track your report's status
6. Use **"Emergency Contacts"** for urgent situations

### For Administrators
1. Go to **"Admin Login"** (default password: `admin123`)
2. Access the **"Admin Dashboard"** to view all reports
3. Use search and filters to find specific reports
4. Update report status and add comments
5. Export data for record-keeping

## Data Storage

- Reports are automatically saved to `reports_data.json`
- Data persists between sessions
- Backup functionality available in admin dashboard

## Security

- Change the default admin password in the code
- Consider implementing user authentication for production use
- Regular data backups recommended

## Customization

- Update emergency contacts in the `EMERGENCY_CONTACTS` dictionary
- Modify issue types in the report form
- Customize styling in the CSS section
- Add new features as needed

## Support

For technical support or feature requests, contact the development team.

---

**CommUnityFix** - Making Barangay Union better, one report at a time! 🏘️
